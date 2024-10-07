from flask import Flask, request, render_template_string, jsonify, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import Base, Category, Activity, ActivityLog
from logger import logger

app = Flask(__name__)

# Database setup
DATABASE_URL = "sqlite:///activity_db.sqlite3"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db_session():
    return Session()

@app.route('/')
def home():
    logger.info("Home endpoint called")
    session = get_db_session()
    categories = session.query(Category).all()
    activities = session.query(Activity).all()
    session.close()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>Activity Tracker Home</title>
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center">Activity Tracker</h1>
            <p class="text-center">Welcome to the Activity Tracker! Below are the available actions:</p>
            <ul class="list-group">
                                <li class="list-group-item"><a href="/add_category_activity">Add a New Category and Activity</a></li>
                <li class="list-group-item"><a href="/log_activity">Log an Activity</a></li>
                <li class="list-group-item"><a href="/analytics">View Analytics</a></li>
            </ul>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', categories=categories)

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
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <title>Add Category and Activity</title>
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">Add Category and Activity</h1>
                <form method="post" class="mt-4">
                    <div class="mb-3">
                        <label for="existing_category" class="form-label">Select Existing Category (Optional):</label>
                        <select name="existing_category" id="existing_category" class="form-select" onchange="toggleCategoryInput()">
                            <option value="" selected>Select a category</option>
                            {% for category in categories %}
                            <option value="{{ category.name }}">{{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="category_name" class="form-label">Or Enter New Category Name:</label>
                        <input type="text" class="form-control" id="category_name" name="category_name">
                    </div>
                    <div class="mb-3">
                        <label for="activity_name" class="form-label">Activity Name:</label>
                        <input type="text" class="form-control" id="activity_name" name="activity_name" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Add Category and Activity</button>
                </form>
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-secondary w-100">Back to Home</a>
                </div>
            </div>

            <script>
                function toggleCategoryInput() {
                    const existingCategory = document.getElementById('existing_category').value;
                    const categoryInput = document.getElementById('category_name');
                    if (existingCategory) {
                        categoryInput.disabled = true;
                        categoryInput.value = "";
                    } else {
                        categoryInput.disabled = false;
                    }
                }
            </script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
    ''', categories=categories)

@app.route('/log_activity', methods=['GET', 'POST'])
def log_activity():
    logger.info("Log activity endpoint called")
    session = get_db_session()
    categories = session.query(Category).all()
    session.close()
    if request.method == 'POST':
        activity_id = request.form['activity']
        session = get_db_session()
        notes = request.form.get('notes')
        activity = session.query(Activity).filter_by(id=activity_id).first()
        category = activity.category
        activity_log = ActivityLog(
            activity_id=activity_id,
            activity_name=activity.name,
            category_id=category.id,
            category_name=category.name,
            notes=notes
        )
        session.add(activity_log)
        session.commit()
        session.close()
        logger.info("Activity logged successfully")
        return redirect(url_for('home'))
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <title>Log Activity</title>
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">Log Activity</h1>
                <form method="post" class="mt-4">
                    <div class="mb-3">
                        <label for="category" class="form-label">Select Category:</label>
                        <select name="category" id="category" class="form-select" onchange="fetchActivities(this.value)">
                            <option value="" disabled selected>Select a category</option>
                            {% for category in categories %}
                            <option value="{{ category.id }}">{{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="activity" class="form-label">Select Activity:</label>
                        <select name="activity" id="activity" class="form-select" disabled>
                            <option value="" disabled selected>Select a category first</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="notes" class="form-label">Notes (Optional):</label>
                        <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 d-block mx-auto">Log Activity</button>
                </form>
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-secondary w-100">Back to Home</a>
                </div>
            </div>

            <script>
                async function fetchActivities(categoryId) {
                    const activitySelect = document.getElementById('activity');
                    activitySelect.innerHTML = '<option value="" disabled selected>Loading activities...</option>';
                    activitySelect.disabled = true;

                    const response = await fetch(`/get_activities?category_id=${categoryId}`);
                    const activities = await response.json();

                    activitySelect.innerHTML = '<option value="" disabled selected>Select an activity</option>';
                    activities.forEach(activity => {
                        const option = document.createElement('option');
                        option.value = activity.id;
                        option.textContent = activity.name;
                        activitySelect.appendChild(option);
                    });
                    activitySelect.disabled = false;
                }
            </script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
    ''', categories=categories)

@app.route('/get_activities')
def get_activities():
    category_id = request.args.get('category_id')
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
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <title>Analytics</title>
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">View Analytics</h1>
                <form method="post" class="mt-4">
                    <div class="mb-3">
                        <label for="category" class="form-label">Select Category:</label>
                        <select name="category" id="category" class="form-select" onchange="this.form.submit()">
                            <option value="" disabled selected>Select a category</option>
                            {% for category in categories %}
                            <option value="{{ category.id }}" {% if request.form.category == category.id|string %}selected{% endif %}>{{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    {% if activities %}
                    <div class="mb-3">
                        <label for="activity" class="form-label">Select Activity (Optional):</label>
                        <select name="activity" id="activity" class="form-select" onchange="this.form.submit()">
                            <option value="" selected>All Activities</option>
                            {% for activity in activities %}
                            <option value="{{ activity.id }}" {% if request.form.activity == activity.id|string %}selected{% endif %}>{{ activity.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    {% endif %}
                </form>
                {% if results %}
                <table class="table table-striped mt-4">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Activity</th>
                            <th>Timestamp</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in results %}
                        <tr>
                            <td>{{ log.category_name }}</td>
                            <td>{{ log.activity_name }}</td>
                            <td>{{ log.timestamp }}</td>
                            <td>{{ log.notes }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-secondary w-100">Back to Home</a>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
    ''', categories=categories, activities=activities, results=results)

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)