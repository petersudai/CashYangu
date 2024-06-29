import csv, requests
from io import BytesIO, TextIOWrapper
from flask import render_template, url_for, flash, redirect, request, jsonify, session, make_response, send_file
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Event, FinancialData
from datetime import datetime, timezone, timedelta
import pytz
import json
import os
import uuid
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# Helper function to get the time in UTC
def get_current_time():
    return datetime.now(timezone.utc)

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# Create a temporary user ID for demo purposes
DEMO_USER_ID = 'demo_user'

def is_demo_user():
    return session.get('user_id') == DEMO_USER_ID

def generate_demo_id():
    return str(uuid.uuid4())

def get_demo_user():
    if is_demo_user():
        return {
            'id': DEMO_USER_ID,
            'username': 'Demo User',
            'email': 'demo@cashyangu.com',
            'timezone': 'UTC'
        }
    return None

@app.before_request
def load_demo_user():
    if is_demo_user():
        session['user'] = get_demo_user()

@app.route("/demo_mode")
def demo_mode():
    session['user_id'] = DEMO_USER_ID
    session['demo_user'] = True
    session['demo_events'] = json.dumps([])  # Initialize demo events
    session['demo_financial_data'] = json.dumps([])  # Initialize demo financial data
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    flash("You are in demo mode. Your data will not be saved permanently.", "info")
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    if is_demo_user() or current_user.is_authenticated:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

@app.route("/logout")
def logout():
    logout_user()
    if is_demo_user():
        session.clear()
    return redirect(url_for('home'))

# Profile section
@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if is_demo_user():
        if request.method == 'POST':
            flash("Profile changes are not allowed in demo mode.", "warning")
        timezones = pytz.all_timezones
        return render_template('profile.html', timezones=timezones)
    
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        current_user.timezone = request.form['timezone']
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    timezones = pytz.all_timezones
    return render_template('profile.html', timezones=timezones)

@app.route("/update_profile", methods=['POST'])
def update_profile():
    if is_demo_user():
        return jsonify({'status': 'error', 'message': 'Profile changes are not allowed in demo mode'})
    
    current_user.username = request.json['username']
    current_user.email = request.json['email']
    current_user.timezone = request.json['timezone']
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Profile updated successfully'})

@app.route("/change_password", methods=['POST'])
def change_password():
    if is_demo_user():
        return jsonify({'status': 'error', 'message': 'Password changes are not allowed in demo mode'})
    
    data = request.json
    if not bcrypt.check_password_hash(current_user.password, data['current_password']):
        return jsonify({'status': 'error', 'message': 'Current password is incorrect'})
    current_user.password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Password changed successfully'})


@app.route("/reports")
def reports():
    if is_demo_user():
        demo_data = json.loads(session.get('demo_financial_data', '[]'))
        return render_template('reports.html', data=demo_data)

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    user_id = current_user.id
    data = FinancialData.query.filter_by(user_id=user_id).all()
    return render_template('reports.html', data=data)

@app.route("/download_report")
@login_required
def download_report():
    user_id = current_user.id
    data = FinancialData.query.filter_by(user_id=user_id).all()

    output = BytesIO()
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Date", "Type", "Amount", "Category"])

    for item in data:
        writer.writerow([item.date, item.type, item.amount, item.category or ''])

    output.seek(0)
    
    return send_file(output, download_name="financial_report.csv", as_attachment=True, mimetype='text/csv')

# Resources
@app.route("/resources")
def resources_page():
    return render_template('resources.html')

# Page that shows the registered user. This is only for development purposes
@app.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', title='Users', users=users)

# Event routes
@app.route('/api/events', methods=['GET', 'POST'])
def manage_events():
    if is_demo_user():
        if request.method == 'GET':
            demo_events = json.loads(session.get('demo_events', '[]'))
            return jsonify(demo_events)
        if request.method == 'POST':
            data = request.get_json()
            demo_events = json.loads(session.get('demo_events', '[]'))
            new_event = {
                'id': generate_demo_id(),
                'title': data.get('title'),
                'start': data.get('start'),
                'end': data.get('end'),
                'allDay': data.get('allDay', True)
            }
            demo_events.append(new_event)
            session['demo_events'] = json.dumps(demo_events)
            return jsonify({'message': 'Event added successfully'}), 201

    if not current_user.is_authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    if request.method == 'GET':
        events = Event.query.filter_by(user_id=current_user.id).all()
        events_data = [{
            'id': event.id,
            'title': event.title,
            'start': event.start.isoformat(),
            'end': event.end.isoformat() if event.end else None,
            'allDay': event.all_day
        } for event in events]

        return jsonify(events_data)

    if request.method == 'POST':
        data = request.get_json()
        new_event = Event(
            user_id=current_user.id,
            title=data.get('title'),
            start=datetime.fromisoformat(data.get('start')),
            end=datetime.fromisoformat(data.get('end')) if data.get('end') else None,
            all_day=data.get('allDay', True)
        )
        db.session.add(new_event)
        db.session.commit()

        return jsonify({'message': 'Event added successfully'}), 201

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if is_demo_user():
        demo_events = json.loads(session.get('demo_events', '[]'))
        demo_events = [event for event in demo_events if event['id'] != event_id]
        session['demo_events'] = json.dumps(demo_events)
        return jsonify({'message': 'Event deleted successfully'})

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    event = Event.query.get(event_id)
    if event and event.user_id == current_user.id:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    return jsonify({'message': 'Event not found or unauthorized'}), 404

# Fetch financial data
@app.route('/api/financial', methods=['GET', 'POST'])
def manage_financial_data():
    if is_demo_user():
        if request.method == 'GET':
            demo_data = json.loads(session.get('demo_financial_data', '[]'))
            earnings = sum(item['amount'] for item in demo_data if item['type'] == 'earnings')
            expenses = sum(item['amount'] for item in demo_data if item['type'] == 'expenses')
            savings = sum(item['amount'] for item in demo_data if item['type'] == 'savings')
            budget_goals = sum(item['amount'] for item in demo_data if item['type'] == 'budgetGoals')
            available_balance = earnings - expenses
            expense_categories = {}
            for item in demo_data:
                if item['type'] == 'expenses':
                    if item['category'] not in expense_categories:
                        expense_categories[item['category']] = 0
                    expense_categories[item['category']] += item['amount']
            response_data = {
                'earnings': earnings or 0,
                'expenses': expenses or 0,
                'savings': savings or 0,
                'budgetGoals': budget_goals or 0,
                'availableBalance': available_balance or 0,
                'expenseCategories': {k: v or 0 for k, v in expense_categories.items()}
            }
            return jsonify(response_data)
        if request.method == 'POST':
            data = request.get_json()
            demo_data = json.loads(session.get('demo_financial_data', '[]'))
            new_data = {
                'id': generate_demo_id(),
                'date': datetime.now().isoformat(),
                'type': data.get('type'),
                'amount': data.get('amount'),
                'category': data.get('category')
            }
            demo_data.append(new_data)
            session['demo_financial_data'] = json.dumps(demo_data)
            return jsonify({'message': 'Financial data added/adjusted successfully'}), 201
    
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        user_id = current_user.id
        current_month = datetime.now().month
        current_year = datetime.now().year
        data = FinancialData.query.filter_by(user_id=user_id).filter(
            db.extract('month', FinancialData.date) == current_month,
            db.extract('year', FinancialData.date) == current_year
        ).all()

        earnings = sum(item.amount for item in data if item.type == 'earnings')
        expenses = sum(item.amount for item in data if item.type == 'expenses')
        savings = sum(item.amount for item in data if item.type == 'savings')
        budget_goals = sum(item.amount for item in data if item.type == 'budgetGoals')

        # Calculate available balance
        available_balance = earnings - expenses

        # Calculate expenses by category
        expense_categories = {}
        for item in data:
            if item.type == 'expenses':
                if item.category not in expense_categories:
                    expense_categories[item.category] = 0
                expense_categories[item.category] += item.amount

        # Ensure all values are properly formatted and not None
        response_data = {
            'earnings': earnings or 0,
            'expenses': expenses or 0,
            'savings': savings or 0,
            'budgetGoals': budget_goals or 0,
            'availableBalance': available_balance or 0,
            'expenseCategories': {k: v or 0 for k, v in expense_categories.items()}
        }

        return jsonify(response_data)

    if request.method == 'POST':
        data = request.get_json()
        user_id = current_user.id

        # Ensure the amount is not None and is a number
        amount = data.get('amount')
        if amount is None or not isinstance(amount, (int, float)):
            return jsonify({'message': 'Invalid amount'}), 400

        # Determine the financial type and category
        financial_type = data.get('type')
        category = data.get('category')

        if amount < 0:
            # Handle negative values by adjusting the existing amount
            existing_record = FinancialData.query.filter_by(user_id=user_id, type=financial_type, category=category).first()
            if existing_record:
                existing_record.amount += amount
                if existing_record.amount < 0:
                    existing_record.amount = 0  # Prevent negative totals
            else:
                return jsonify({'message': 'No existing record to adjust'}), 400
        else:
            # Handle positive values normally
            existing_record = FinancialData.query.filter_by(user_id=user_id, type=financial_type, category=category).first()
            if existing_record:
                existing_record.amount += amount
            else:
                financial_data = FinancialData(
                    user_id=user_id,
                    type=financial_type,
                    amount=amount,
                    date=datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S') if 'date' in data else datetime.now(),
                    category=category
                )
                db.session.add(financial_data)

        db.session.commit()

        return jsonify({'message': 'Financial data added/adjusted successfully'}), 201


@app.route('/api/financial_report', methods=['GET'])
def get_detailed_financial_data():
    if is_demo_user():
        demo_data = json.loads(session.get('demo_financial_data', '[]'))
        financial_data = [
            {
                'date': item['date'],
                'type': item['type'],
                'amount': item['amount'],
                'category': item['category']
            }
            for item in demo_data
        ]
        return jsonify(financial_data)

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    user_id = current_user.id
    data = FinancialData.query.filter_by(user_id=user_id).all()
    financial_data = [
        {
            'date': item.date.isoformat(),
            'type': item.type,
            'amount': item.amount,
            'category': item.category
        }
        for item in data
    ]
    return jsonify(financial_data)


@app.route('/api/expenses', methods=['POST'])
def add_expense():
    if is_demo_user():
        data = request.get_json()
        demo_data = json.loads(session.get('demo_financial_data', '[]'))
        new_data = {
            'id': generate_demo_id(),
            'date': datetime.now().isoformat(),
            'type': 'expenses',
            'amount': data['amount'],
            'category': data['category']
        }
        demo_data.append(new_data)
        session['demo_financial_data'] = json.dumps(demo_data)
        return jsonify({'message': 'Expense added successfully'}), 201

    if not current_user.is_authenticated:
        return jsonify({'message': 'Unauthorized'}), 401
 
    data = request.get_json()
    expense = FinancialData(
        user_id=current_user.id,
        type='expenses',
        amount=data['amount'],
        category=data['category'],
        date=datetime.now()
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify({'message': 'Expense added successfully'}), 201

# @app.route('/api/expenses/report', methods=['GET'])
# @login_required
# def generate_expense_report():
#     user_id = current_user.id
#     expenses = FinancialData.query.filter_by(user_id=user_id, type='expenses').all()

#     output = []
#     for expense in expenses:
#         output.append({
#             'Date': expense.date.strftime('%Y-%m-%d'),
#             'Category': expense.category,
#             'Amount': expense.amount
#         })

#     si = StringIO()
#     writer = csv.DictWriter(si, fieldnames=['Date', 'Category', 'Amount'])
#     writer.writeheader()
#     writer.writerows(output)

#     response = make_response(si.getvalue())
#     response.headers['Content-Disposition'] = 'attachment; filename=expense_report.csv'
#     response.headers['Content-type'] = 'text/csv'
#     return response


# Articles API

# Set the NLTK data directory
nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
nltk.data.path.append(nltk_data_path)

# Ensuring the vader_lexicon is available
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', download_dir=nltk_data_path)

API_KEY = '44fe38a257d34ca887e4c2bf26a2bc76'
API_URL = 'https://newsapi.org/v2/everything?q=finance&apiKey=' + API_KEY

def fetch_articles():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f'Error fetching articles: {e}')
        return []

def filter_articles(articles):
    keywords = [
        'finance guru', 'cardone', 'buffet', 'ramsey', 'tony robbins', 'david bach', 'diary of a ceo', 'journaling', 'finance', 'expense', 'financial', 'investment', 'saving', 'budget', 'bond', 'frugal',
        'economy', 'stock', 'market', 'wealth', 'retirement', 'insurance', 'price', 'side hustle',
        'personal finance', 'financial planning', 'money management', 'crypto', 'tracking', 'income'
    ]
    unwanted_keywords = ['china', 'divorcee','russia', 'ukraine', 'politics', 'sports', 'gossip', 'army', 'president', 'trump']
    
    sid = SentimentIntensityAnalyzer()

    filtered_articles = []
    for article in articles:
        content = article['description'] if article['description'] else article['content']
        if any(keyword in (article['title'] + ' ' + content).lower() for keyword in keywords):
            if not any(unwanted in (article['title'] + ' ' + content).lower() for unwanted in unwanted_keywords):
                sentiment_score = sid.polarity_scores(content)['compound']
                if sentiment_score > 0:  # Consider only positive or neutral articles
                    filtered_articles.append({
                        'title': article['title'],
                        'content': content,
                        'imageUrl': article.get('urlToImage', 'default-image-url'),  # Fallback image URL if not available
                        'url': article['url'],
                        'score': sentiment_score
                    })
    filtered_articles.sort(key=lambda x: x['score'], reverse=True)  # Sort by sentiment score
    return filtered_articles

@app.route("/api/articles", methods=['GET'])
def get_articles():
    articles = fetch_articles()
    filtered_articles = filter_articles(articles)
    return jsonify(filtered_articles)


@app.route("/resources")
def resources():
    return render_template('resources.html')

# Feature to delete user financial entries.
@app.route('/api/financial/<id>', methods=['DELETE'])
def delete_financial_data(id):
    if is_demo_user():
        demo_data = json.loads(session.get('demo_financial_data', '[]'))
        demo_data = [item for item in demo_data if item.get('id') != id]
        session['demo_financial_data'] = json.dumps(demo_data)
        return jsonify({'message': 'Financial data deleted successfully'}), 200

    if not current_user.is_authenticated:
        return jsonify({'message': 'Unauthorized'}), 401
    
    try:
        user_id = current_user.id
        financial_data = FinancialData.query.filter_by(id=int(id), user_id=user_id).first()

        if not financial_data:
            return jsonify({'message': 'Financial data not found'}), 404

        db.session.delete(financial_data)
        db.session.commit()
    except ValueError:
        return jsonify({'message': 'Invalid ID format'}), 400

    return jsonify({'message': 'Financial data deleted successfully'}), 200


@app.route('/api/financial/all', methods=['DELETE'])
def delete_all_financial_data():
    if is_demo_user():
        session['demo_financial_data'] = json.dumps([])
        return jsonify({'message': 'All financial data deleted successfully'}), 200

    if not current_user.is_authenticated:
        return jsonify({'message': 'Unauthorized'}), 401
    
    user_id = current_user.id
    financial_data = FinancialData.query.filter_by(user_id=user_id).all()

    if not financial_data:
        return jsonify({'message': 'No financial data found'}), 404

    for item in financial_data:
        db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'All financial data deleted successfully'}), 200
