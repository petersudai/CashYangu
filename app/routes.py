import csv, requests
from io import BytesIO, TextIOWrapper
from flask import render_template, url_for, flash, redirect, request, jsonify, session, make_response, send_file
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Event, FinancialData
from datetime import datetime, timezone
import pytz

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

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# Profile section
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
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
@login_required
def update_profile():
    current_user.username = request.json['username']
    current_user.email = request.json['email']
    current_user.timezone = request.json['timezone']
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Profile updated successfully'})

@app.route("/change_password", methods=['POST'])
@login_required
def change_password():
    data = request.json
    if not bcrypt.check_password_hash(current_user.password, data['current_password']):
        return jsonify({'status': 'error', 'message': 'Current password is incorrect'})
    current_user.password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Password changed successfully'})


@app.route("/reports")
@login_required
def reports():
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
@login_required
def resources_page():
    return render_template('resources.html')

# Page that shows the registered user. This is only for development purposes
@app.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', title='Users', users=users)

# Event routes
@app.route('/api/events', methods=['GET'])
@login_required
def get_events():
    events = Event.query.filter_by(user_id=current_user.id).all()
    events_data = [{
        'id': event.id,
        'title': event.title,
        'start': event.start.isoformat(),
        'end': event.end.isoformat() if event.end else None,
        'allDay': event.all_day
    } for event in events]

    return jsonify(events_data)

@app.route('/api/events', methods=['POST'])
@login_required
def add_event():
    data = request.get_json()
    title = data.get('title')
    start = datetime.fromisoformat(data.get('start'))
    end = datetime.fromisoformat(data.get('end')) if data.get('end') else None
    all_day = data.get('allDay', True)

    new_event = Event(user_id=current_user.id, title=title, start=start, end=end, all_day=all_day)
    db.session.add(new_event)
    db.session.commit()

    return jsonify({'message': 'Event added successfully'})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event and event.user_id == current_user.id:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'})
    return jsonify({'message': 'Event not found or unauthorized'}), 404

# Fetch financial data
@app.route('/api/financial', methods=['GET', 'POST'])
@login_required
def manage_financial_data():
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
@login_required
def get_detailed_financial_data():
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
@login_required
def add_expense():
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
API_KEY = '44fe38a257d34ca887e4c2bf26a2bc76'
API_URL = 'https://newsapi.org/v2/everything?q=finance&apiKey=' + API_KEY

@app.route("/api/articles", methods=['GET'])
def get_articles():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        articles = response.json().get('articles', [])

        financial_articles = [
            {
                'title': article['title'],
                'content': article['description'] if article['description'] else article['content'],
                'imageUrl': article.get('urlToImage', 'default-image-url'),  # Fallback image URL if not available
                'url': article['url']
            }
            for article in articles
            if 'finance' in article['title'].lower() or 'finance' in article['description'].lower()
            or 'financial' in article['title'].lower() or 'financial' in article['description'].lower()
            or 'investment' in article['title'].lower() or 'investment' in article['description'].lower()
            or 'saving' in article['title'].lower() or 'saving' in article['description'].lower()
            or 'budget' in article['title'].lower() or 'budget' in article['description'].lower()
        ]
        return jsonify(financial_articles)
    except requests.exceptions.RequestException as e:
        print(f'Error fetching articles: {e}')
        return jsonify({'error': 'Failed to fetch articles'}), 500

@app.route("/resources")
def resources():
    return render_template('resources.html')

# Feature to delete user financial entries.
@app.route('/api/financial/<int:id>', methods=['DELETE'])
@login_required
def delete_financial_data(id):
    user_id = current_user.id
    financial_data = FinancialData.query.filter_by(id=id, user_id=user_id).first()

    if not financial_data:
        return jsonify({'message': 'Financial data not found'}), 404

    db.session.delete(financial_data)
    db.session.commit()

    return jsonify({'message': 'Financial data deleted successfully'}), 200

@app.route('/api/financial/all', methods=['DELETE'])
@login_required
def delete_all_financial_data():
    user_id = current_user.id
    financial_data = FinancialData.query.filter_by(user_id=user_id).all()

    if not financial_data:
        return jsonify({'message': 'No financial data found'}), 404

    for item in financial_data:
        db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'All financial data deleted successfully'}), 200
