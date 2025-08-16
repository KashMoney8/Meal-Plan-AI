from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from backend.config import Settings
from backend.db import db_session, init_db
from backend.models import User, Recipe, UserPreference, Rating, Plan, PlanItem
from backend.auth import hash_password, verify_password
from backend.rag.planner import generate_plan, swap_plan_item
from backend.rag.retriever import get_stratified_onboarding_cards
from backend.rag.recommender import record_rating_batch
from backend.analytics import log_event

app = Flask(__name__)
CORS(app)
settings = Settings()
app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET
jwt = JWTManager(app)

@app.before_first_request
def setup():
    init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.get('/health')
def health():
    return {'status': 'ok'}

# ---------- Auth ----------
@app.post('/auth/signup')
def signup():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400
    if db_session.query(User).filter_by(email=email).first():
        return jsonify({'error': 'email already registered'}), 400
    user = User(email=email, password_hash=hash_password(password))
    db_session.add(user)
    db_session.commit()
    token = create_access_token(identity=str(user.id))
    log_event('signup', {'user_id': user.id})
    return jsonify({'token': token}), 201

@app.post('/auth/login')
def login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    user = db_session.query(User).filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'invalid credentials'}), 401
    token = create_access_token(identity=str(user.id))
    log_event('login', {'user_id': user.id})
    return jsonify({'token': token})

@app.get('/me')
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    user = db_session.get(User, uid)
    prefs = db_session.query(UserPreference).filter_by(user_id=uid).first()
    return jsonify({
        'email': user.email,
        'preferences': prefs.as_dict() if prefs else None
    })

# ---------- Preferences ----------
@app.post('/preferences')
@jwt_required()
def set_preferences():
    uid = int(get_jwt_identity())
    data = request.json or {}
    calorie_target = data.get('calorie_target')
    if calorie_target is None:
        return jsonify({'error': 'calorie_target required'}), 400
    prefs = db_session.query(UserPreference).filter_by(user_id=uid).first()
    if not prefs:
        prefs = UserPreference(user_id=uid)
        db_session.add(prefs)
    prefs.calorie_target = int(calorie_target)
    prefs.protein_target = data.get('protein_target')  # grams/day avg (optional)
    prefs.carb_target = data.get('carb_target')
    prefs.fat_target = data.get('fat_target')
    prefs.diet_type = data.get('diet_type', 'No Restriction')
    prefs.allergens = data.get('allergens', [])
    prefs.exclude_ingredients = data.get('exclude_ingredients', [])
    prefs.units = data.get('units', 'us')
    prefs.share_anonymized = bool(data.get('share_anonymized', True))
    db_session.commit()
    log_event('set_preferences', {'user_id': uid})
    return jsonify({'ok': True})

# ---------- Onboarding ----------
@app.get('/onboarding/cards')
@jwt_required()
def onboarding_cards():
    diet = (request.args.get('diet_type') or 'No Restriction')
    cards = get_stratified_onboarding_cards(diet_type=diet, k=12)
    return jsonify({'cards': cards})

@app.post('/onboarding/ratings')
@jwt_required()
def onboarding_ratings():
    uid = int(get_jwt_identity())
    payload = request.json or {}
    ratings = payload.get('ratings', [])
    if len(ratings) != 12:
        return jsonify({'error': '12 ratings required'}), 400
    record_rating_batch(uid, ratings)
    log_event('onboarding_complete', {'user_id': uid})
    return jsonify({'ok': True})

# ---------- Plans ----------
@app.post('/plans/generate')
@jwt_required()
def plans_generate():
    uid = int(get_jwt_identity())
    data = request.json or {}
    days = int(data.get('days', 7))
    meals_per_day = int(data.get('meals_per_day', 3))
    allow_repeats = bool(data.get('allow_repeats', True))
    plan = generate_plan(uid, days, meals_per_day, allow_repeats)
    db_session.add(plan)
    db_session.commit()
    log_event('plan_generated', {'user_id': uid, 'plan_id': plan.id})
    return jsonify(plan.as_dict())

@app.get('/plans/<int:plan_id>')
@jwt_required()
def plans_get(plan_id):
    uid = int(get_jwt_identity())
    plan = db_session.get(Plan, plan_id)
    if not plan or plan.user_id != uid:
        return jsonify({'error': 'not found'}), 404
    return jsonify(plan.as_dict())

@app.post('/plans/<int:plan_id>/swap')
@jwt_required()
def plans_swap(plan_id):
    uid = int(get_jwt_identity())
    data = request.json or {}
    day_index = int(data['day_index'])
    meal_index = int(data['meal_index'])
    new_item = swap_plan_item(uid, plan_id, day_index, meal_index)
    db_session.commit()
    log_event('plan_swapped', {'user_id': uid, 'plan_id': plan_id})
    return jsonify(new_item)

# ---------- Shopping List ----------
@app.get('/shopping-list')
@jwt_required()
def shopping_list():
    uid = int(get_jwt_identity())
    plan_id = int((request.args.get('plan_id') or 0))
    plan = db_session.get(Plan, plan_id)
    if not plan or plan.user_id != uid:
        return jsonify({'error': 'not found'}), 404
    items = []
    for it in plan.items:
        r = db_session.get(Recipe, it.recipe_id)
        if r and r.ingredients:
            items.extend([line.strip() for line in r.ingredients.split('\n') if line.strip()])
    return jsonify({'items': items})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
