import argparse, pandas as pd
from db import db_session
from models import Recipe
from rag.retriever import get_embedder, pinecone_index
from config import Settings

def upsert_pinecone(vectors):
    idx = pinecone_index()
    idx.upsert(vectors=vectors, namespace=Settings().PINECONE_NAMESPACE)

def main(csv_path: str):
    df = pd.read_csv(csv_path)
    rename = {'Reclassified_Dietary_Category':'diet_type','Ingredients':'ingredients','Directions':'directions','Energy (kcal)':'energy_kcal','Protein (g)':'protein_g','Fat (g)':'fat_g','Carbs (g)':'carbs_g','Title':'title'}
    df = df.rename(columns={c: rename.get(c, c) for c in df.columns})
    df = df.dropna(subset=['title']).fillna('')

    recs = []
    for _, row in df.iterrows():
        r = Recipe(
            title=str(row.get('title'))[:512],
            diet_type=row.get('diet_type') or 'No Restriction',
            ingredients=str(row.get('ingredients')),
            directions=str(row.get('directions')),
            energy_kcal=float(row.get('energy_kcal') or 0) or None,
            protein_g=float(row.get('protein_g') or 0) or None,
            fat_g=float(row.get('fat_g') or 0) or None,
            carbs_g=float(row.get('carbs_g') or 0) or None,
        )
        db_session.add(r); recs.append(r)
    db_session.commit()

    emb = get_embedder()
    vectors = []
    for r in recs:
        text = f"{r.title}\n{r.ingredients}\n{r.directions}"
        vec = emb.embed_query(text)
        vectors.append((str(r.id), vec, {'diet_type': r.diet_type, 'title': r.title}))
    if vectors:
        upsert_pinecone(vectors)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--csv', required=True); args = ap.parse_args(); main(args.csv)
