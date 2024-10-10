from flask import request, render_template, jsonify, redirect, url_for
from database import get_db_session
from models import Category, Activity, ActivityLog
from logger import logger
from sqlalchemy.orm import joinedload
from datetime import datetime
from zoneinfo import ZoneInfo

PREFERRED_TIMEZONE = 'America/Los_Angeles'

def configure_routes(app):
    @app.route('/')
    def home():
        logger.info("Home endpoint called")

        session = get_db_session()
        categories = session.query(Category).options(joinedload(Category.activities)).all()

        # Pre-calculate instance count for each activity and store it in a dictionary
        category_data = []
        for category in categories:
            activities_data = []
            for activity in category.activities:
                instance_count = session.query(ActivityLog).filter_by(activity_id=activity.id).count()
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

        session.close()
        return render_template('home.html', categories=category_data)

    @app.route('/add_category_activity', methods=['GET', 'POST'])
    def add_category_activity():
        logger.info("Add category and activity endpoint called")

        session = get_db_session()
        categories = session.query(Category).all()
        if request.method == 'POST':
            existing_category_name = request.form.get('existing_category')
            category_name = request.form.get('category_name')
            category_name = existing_category_name if existing_category_name else category_name
            activity_name = request.form['activity_name']
            existing_category = session.query(Category).filter_by(name=category_name).first()

            if existing_category:
                new_category = existing_category
            else:
                new_category = Category(name=category_name)
                session.add(new_category)
                session.commit()

            existing_activity = session.query(Activity).filter_by(name=activity_name, category_id=new_category.id).first()

            if existing_activity:
                raise ValueError(f"Activity '{activity_name}' already exists in category '{new_category.name}'")

            new_activity = Activity(name=activity_name, category_id=new_category.id)

            session.add(new_activity)
            session.commit()
            session.close()

            logger.info(f"Category '{category_name}' and Activity '{activity_name}' added successfully")

            return redirect(url_for('home'))

        return render_template('add_category_activity.html', categories=categories)

    @app.route('/log_activity', methods=['GET', 'POST'])
    def log_activity():
        logger.info("Log activity endpoint called")

        session = get_db_session()
        categories = session.query(Category).all()
        category_id = request.args.get('category_id', type=int)
        selected_category = None
        if category_id:
            selected_category = session.query(Category).filter_by(id=category_id).first()
        session.close()

        if request.method == 'POST':
            activity_id = request.form['activity']
            timestamp_str = request.form.get('timestamp')
            notes = request.form.get('notes')

            # Use the provided timestamp if available, otherwise use current time in preferred timezone
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
            else:
                timestamp = datetime.now(ZoneInfo(PREFERRED_TIMEZONE))

            session = get_db_session()
            activity = session.query(Activity).filter_by(id=activity_id).first()
            category = activity.category
            activity_log = ActivityLog(
                activity_id=activity_id,
                activity_name=activity.name,
                category_id=category.id,
                category_name=category.name,
                notes=notes,
                timestamp=timestamp
            )

            session.add(activity_log)
            session.commit()
            session.close()

            logger.info("Activity logged successfully")

            return redirect(url_for('home'))

        return render_template('log_activity.html', categories=categories, selected_category=selected_category)

    @app.route('/get_activities')
    def get_activities():
        category_id = request.args.get('category_id', type=int)

        session = get_db_session()
        activities = session.query(Activity).filter_by(category_id=category_id).all()
        session.close()

        return jsonify([{'id': activity.id, 'name': activity.name} for activity in activities])

    @app.route('/analytics', methods=['GET', 'POST'])
    def analytics():
        logger.info("Analytics endpoint called")

        session = get_db_session()
        categories = session.query(Category).all()
        activities = []
        results = []

        if request.method == 'POST':
            category_id = request.form['category']
            activity_id = request.form.get('activity')
            activities = session.query(Activity).filter_by(category_id=category_id).all()
            query = session.query(ActivityLog).join(Activity).filter(Activity.category_id == category_id).options(joinedload(ActivityLog.activity))

            if activity_id:
                query = query.filter(ActivityLog.activity_id == activity_id)

            results = query.order_by(ActivityLog.timestamp).all()

        session.close()

        return render_template('analytics.html', categories=categories, activities=activities, results=results)