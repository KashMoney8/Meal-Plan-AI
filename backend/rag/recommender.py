from typing import List, Dict
from db import db_session
from models import Rating
def record_rating_batch(user_id: int, ratings: List[Dict]):
    for r in ratings:
        db_session.add(Rating(user_id=user_id, recipe_id=r['recipe_id'], rating=int(r['rating'])))
    db_session.commit()
