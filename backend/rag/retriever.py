from typing import List
from db import db_session
from models import Recipe
from config import Settings
from langchain_google_vertexai import VertexAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

_settings = Settings()
_embedder = None
_pc = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = VertexAIEmbeddings(
            model_name=_settings.VERTEX_EMBED_MODEL,    # "text-embedding-004"
            project=_settings.GOOGLE_CLOUD_PROJECT,
            location=_settings.VERTEX_LOCATION,
        )
    return _embedder

def init_pinecone():
    global _pc
    if _pc is None:
        _pc = Pinecone(api_key=_settings.PINECONE_API_KEY)
    return _pc

def pinecone_index():
    pc = init_pinecone()
    idx_name = _settings.PINECONE_INDEX
    # For text-embedding-004, dimension is 3072
    if idx_name not in [i['name'] for i in pc.list_indexes()]:
        pc.create_index(
            name=idx_name,
            dimension=3072,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    return pc.Index(idx_name)

def lexical_search(query: str, diet_type: str | None, top_k: int = 30):
    q = db_session.query(Recipe)
    if diet_type:
        q = q.filter(Recipe.diet_type == diet_type)
    q = q.filter(Recipe.title.ilike(f'%{query}%') | Recipe.ingredients.ilike(f'%{query}%') | Recipe.directions.ilike(f'%{query}%'))
    return q.limit(top_k).all()

def vector_search(query: str, diet_type: str | None, top_k: int = 30):
    emb = get_embedder().embed_query(query)
    idx = pinecone_index()
    flt = {'diet_type': diet_type} if diet_type else None
    res = idx.query(vector=emb, top_k=top_k, include_metadata=True, filter=flt, namespace=_settings.PINECONE_NAMESPACE)
    ids = [int(m['id']) for m in res.get('matches', [])]
    if not ids:
        return []
    recs = db_session.query(Recipe).filter(Recipe.id.in_(ids)).all()
    by_id = {r.id: r for r in recs}
    return [by_id[i] for i in ids if i in by_id]

def hybrid_retrieve(query: str, diet_type: str | None, excludes: list[str] | None, top_k: int = 40) -> List[Recipe]:
    lex = lexical_search(query, diet_type, top_k=top_k//2)
    vec = vector_search(query, diet_type, top_k=top_k)
    pool = {r.id: r for r in lex}
    for r in vec:
        pool[r.id] = r
    results = list(pool.values())
    if excludes:
        lowered = [e.lower() for e in excludes]
        def ok(r: Recipe):
            text = f"{r.title}\n{r.ingredients}\n{r.directions}".lower()
            return not any(e in text for e in lowered)
        results = [r for r in results if ok(r)]
    return results[:top_k]

def get_stratified_onboarding_cards(diet_type: str, k: int = 12):
    q = db_session.query(Recipe).filter(Recipe.diet_type == diet_type)
    recs = q.limit(500).all() or db_session.query(Recipe).limit(500).all()
    recs = [r for r in recs if r.energy_kcal is not None]
    recs.sort(key=lambda r: r.energy_kcal)
    import numpy as np
    buckets = np.array_split(recs, k) if len(recs)>=k else [recs]
    out = []
    for b in buckets:
        if not len(b): continue
        r = b[len(b)//2]
        out.append({'recipe_id': r.id,'title': r.title,'kcal': r.energy_kcal,'diet_type': r.diet_type,'ingredients_preview': (r.ingredients or '').split('\n')[:5]})
    return out[:k]
