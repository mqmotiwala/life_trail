from flask import request, render_template, jsonify, redirect, url_for, session, flash
from database import get_db_session
from models import User, Category, Activity, ActivityLog
from logger import logger
from sqlalchemy.orm import joinedload
from datetime import datetime
from zoneinfo import ZoneInfo
from functools import wraps

PREFERRED_TIMEZONE = 'America/Los_Angeles'

# Function to require login for specific routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to get the current user
def get_current_user():
    if 'user_id' in session:
        session_db = get_db_session()
        user = session_db.query(User).filter_by(id=session['user_id']).first()
        session_db.close()
        return user
    return None

def configure_routes(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        logger.info("Register endpoint called")
        session_db = get_db_session()
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            if session_db.query(User).filter_by(username=username).first():
                flash('Username already exists!', 'danger')
                return redirect(url_for('register'))

            user = User(first_name=first_name, last_name=last_name, username=username, email=email)
            user.set_password(password)
            session_db.add(user)
            session_db.commit()
            session_db.close()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        logger.info("Login endpoint called")
        session_db = get_db_session()
        error_message = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = session_db.query(User).filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                return redirect(url_for('home'))
            else:
                error_message = 'Invalid username or password!'

        session_db.close()
        return render_template('login.html', error_message=error_message)

    @app.route('/logout')
    def logout():
        logger.info("Logout endpoint called")
        session.pop('user_id', None)
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def home():
        logger.info("Home endpoint called")
        user = get_current_user()

        session_db = get_db_session()
        categories = session_db.query(Category).filter_by(user_id=user.id).options(joinedload(Category.activities)).all()

        # Pre-calculate instance count for each activity and store it in a dictionary
        category_data = []
        for category in categories:
            activities_data = []
            for activity in category.activities:
                instance_count = session_db.query(ActivityLog).filter_by(activity_id=activity.id).count()
                activities_data.append({
                    'id': activity.id,
                    'name': activity.name,
                    'instance_count': instance_count
                })
            category_data.append({
                'id': category.id,
                'name': category.name,
                'activities': activities_data
            })

        session_db.close()
        return render_template('home.html', categories=category_data, user=user)

    @app.route('/add_activity', methods=['GET', 'POST'])
    @login_required
    def add_activity():
        logger.info("Add activity endpoint called")
        user = get_current_user()

        session_db = get_db_session()
        categories = session_db.query(Category).filter_by(user_id=user.id).all()
        if request.method == 'POST':
            existing_category_name = request.form.get('existing_category')
            category_name = request.form.get('category_name')
            category_name = existing_category_name if existing_category_name else category_name
            activity_name = request.form['activity_name']
            existing_category = session_db.query(Category).filter_by(name=category_name, user_id=user.id).first()

            if existing_category:
                new_category = existing_category
            else:
                new_category = Category(name=category_name, user_id=user.id)
                session_db.add(new_category)
                session_db.commit()

            existing_activity = session_db.query(Activity).filter_by(name=activity_name, category_id=new_category.id).first()

            if existing_activity:
                raise ValueError(f"Activity '{activity_name}' already exists in category '{new_category.name}'")

            new_activity = Activity(name=activity_name, category_id=new_category.id, user_id=user.id)

            session_db.add(new_activity)
            session_db.commit()
            session_db.close()

            logger.info(f"Category '{category_name}' and Activity '{activity_name}' added successfully")

            return redirect(url_for('home'))

        return render_template('add_activity.html', categories=categories, user=user)

    @app.route('/log_activity', methods=['GET', 'POST'])
    @login_required
    def log_activity():
        logger.info("Log activity endpoint called")
        user = get_current_user()

        session_db = get_db_session()
        categories = session_db.query(Category).filter_by(user_id=user.id).all()
        category_id = request.args.get('category_id', type=int)
        selected_category = None
        if category_id:
            selected_category = session_db.query(Category).filter_by(id=category_id, user_id=user.id).first()
        session_db.close()

        if request.method == 'POST':
            activity_id = request.form['activity']
            timestamp_str = request.form.get('timestamp')
            notes = request.form.get('notes')

            # Use the provided timestamp if available, otherwise use current time in preferred timezone
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
            else:
                timestamp = datetime.now(ZoneInfo(PREFERRED_TIMEZONE))

            session_db = get_db_session()
            activity = session_db.query(Activity).filter_by(id=activity_id, user_id=user.id).first()
            if not activity:
                flash('Activity not found.', 'danger')
                return redirect(url_for('log_activity'))
            category = activity.category
            activity_log = ActivityLog(
                activity_id=activity_id,
                activity_name=activity.name,
                category_id=category.id,
                category_name=category.name,
                user_id=user.id,
                notes=notes,
                timestamp=timestamp
            )

            session_db.add(activity_log)
            session_db.commit()
            session_db.close()

            logger.info("Activity logged successfully")

            return redirect(url_for('home'))

        return render_template('log_activity.html', categories=categories, selected_category=selected_category, user=user)

    @app.route('/get_activities')
    @login_required
    def get_activities():
        category_id = request.args.get('category_id', type=int)
        user = get_current_user()

        session_db = get_db_session()
        activities = session_db.query(Activity).filter_by(category_id=category_id, user_id=user.id).all()
        session_db.close()

        return jsonify([{'id': activity.id, 'name': activity.name} for activity in activities])

    @app.route('/analytics', methods=['GET', 'POST'])
    @login_required
    def analytics():
        logger.info("Analytics endpoint called")
        user = get_current_user()

        session_db = get_db_session()
        categories = session_db.query(Category).filter_by(user_id=user.id).all()
        activities = []
        results = []

        if request.method == 'POST':
            category_id = request.form['category']
            activity_id = request.form.get('activity')
            activities = session_db.query(Activity).filter_by(category_id=category_id, user_id=user.id).all()
            query = session_db.query(ActivityLog).join(Activity).filter(Activity.category_id == category_id, Activity.user_id == user.id).options(joinedload(ActivityLog.activity))

            if activity_id:
                query = query.filter(ActivityLog.activity_id == activity_id)

            results = query.order_by(ActivityLog.timestamp).all()

        session_db.close()

        return render_template('analytics.html', categories=categories, activities=activities, results=results, user=user)