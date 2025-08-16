from typing import Dict, Any
import json
from backend.db import db_session
from backend.models import Plan, PlanItem, Recipe, UserPreference
from backend.rag.retriever import hybrid_retrieve
from backend.rag.llm import simple_completion
from backend.rag.prompts import PLAN_SYSTEM, PLAN_USER_TEMPLATE

def _recipe_to_candidate(r: Recipe) -> Dict[str, Any]:
    return {
        'id': r.id,
        'title': r.title,
        'kcal': r.energy_kcal or 0,
        'protein': r.protein_g or 0,
        'carbs': r.carbs_g or 0,
        'fat': r.fat_g or 0,
        'diet_type': r.diet_type,
        'ingredients_text': (r.ingredients or '')[:2000],
    }

def generate_plan(user_id: int, days: int, meals_per_day: int, allow_repeats: bool) -> Plan:
    # Build candidate pool with hybrid retrieval
    prefs = db_session.query(UserPreference).filter_by(user_id=user_id).first()
    candidates = hybrid_retrieve("healthy recipe", prefs.diet_type, prefs.exclude_ingredients, top_k=60)
    cand_objs = [_recipe_to_candidate(r) for r in candidates]

    user_prompt = PLAN_USER_TEMPLATE.format(
        days=days,
        meals_per_day=meals_per_day,
        allow_repeats=str(allow_repeats).lower(),
        diet_type=prefs.diet_type,
        excludes=', '.join(prefs.exclude_ingredients or []),
        kcal=prefs.calorie_target,
        protein=prefs.protein_target or "null",
        carbs=prefs.carb_target or "null",
        fat=prefs.fat_target or "null",
        candidates_json=json.dumps(cand_objs)[:120000],
    )
    raw = simple_completion(PLAN_SYSTEM, user_prompt)
    try:
        plan_array = json.loads(raw)
    except Exception:
        # Fallback: naive grid fill
        plan_array = [[{'recipe_id': cand_objs[(i*meals_per_day+j)%len(cand_objs)]['id'], 'portion': 1.0}
                       for j in range(meals_per_day)] for i in range(days)]
    plan = Plan(user_id=user_id, days=days, meals_per_day=meals_per_day)
    db_session.add(plan); db_session.flush()
    for i, day in enumerate(plan_array):
        for j, item in enumerate(day):
            rid = int(item.get('recipe_id')); portion = float(item.get('portion', 1.0))
            db_session.add(PlanItem(plan_id=plan.id, day_index=i, meal_index=j, recipe_id=rid, portion=portion))
    return plan

def swap_plan_item(user_id: int, plan_id: int, day_index: int, meal_index: int):
    prefs = db_session.query(UserPreference).filter_by(user_id=user_id).first()
    candidates = hybrid_retrieve("healthy lunch", prefs.diet_type, prefs.exclude_ingredients, top_k=30)
    rep = candidates[0]
    item = db_session.query(PlanItem).filter_by(plan_id=plan_id, day_index=day_index, meal_index=meal_index).first()
    item.recipe_id = rep.id; item.portion = 1.0
    return item.as_dict()
