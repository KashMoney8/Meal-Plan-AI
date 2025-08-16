from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from backend.db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    calorie_target = Column(Integer, nullable=True)
    protein_target = Column(Float, nullable=True)
    carb_target = Column(Float, nullable=True)
    fat_target = Column(Float, nullable=True)
    diet_type = Column(String(64), default='No Restriction')
    allergens = Column(JSONB, default=list)  # list[str]
    exclude_ingredients = Column(JSONB, default=list)  # list[str]
    units = Column(String(16), default='us')
    share_anonymized = Column(Boolean, default=True)
    user = relationship('User', backref='preferences')

    def as_dict(self):
        return {
            'calorie_target': self.calorie_target,
            'protein_target': self.protein_target,
            'carb_target': self.carb_target,
            'fat_target': self.fat_target,
            'diet_type': self.diet_type,
            'allergens': self.allergens,
            'exclude_ingredients': self.exclude_ingredients,
            'units': self.units,
            'share_anonymized': self.share_anonymized,
        }

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    external_id = Column(String(128), index=True)  # from CSV if any
    title = Column(String(512), index=True, nullable=False)
    diet_type = Column(String(64), default='No Restriction')  # e.g., Vegetarian/Vegan/No Restriction
    ingredients = Column(Text)  # newline separated text
    directions = Column(Text)

    energy_kcal = Column(Float)
    protein_g = Column(Float)
    fat_g = Column(Float)
    carbs_g = Column(Float)

    # for hybrid lexical retrieval
    fts_vector = Column(Text)  # placeholder; use proper FTS in production

class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-10
    created_at = Column(DateTime, default=datetime.utcnow)

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    days = Column(Integer, nullable=False)
    meals_per_day = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship('PlanItem', cascade='all, delete-orphan')

    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'days': self.days,
            'meals_per_day': self.meals_per_day,
            'items': [i.as_dict() for i in self.items],
        }

class PlanItem(Base):
    __tablename__ = 'plan_items'
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    day_index = Column(Integer, nullable=False)
    meal_index = Column(Integer, nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    portion = Column(Float, default=1.0)  # e.g., 0.5 for half portion

    def as_dict(self):
        return {
            'day_index': self.day_index,
            'meal_index': self.meal_index,
            'recipe_id': self.recipe_id,
            'portion': self.portion,
        }

class AnalyticsEvent(Base):
    __tablename__ = 'analytics'
    id = Column(Integer, primary_key=True)
    event_type = Column(String(64), index=True)
    payload = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
