from flask import render_template, url_for, flash, redirect, request, jsonify, session
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Event, FinancialData
from datetime import datetime

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

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html')

@app.route("/reports")
@login_required
def reports():
    return render_template('reports.html')

@app.route("/support")
@login_required
def support():
    return render_template('support.html')

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
        data = FinancialData.query.filter_by(user_id=user_id).all()

        # Calculate totals and handle cases with no data
        earnings = sum(item.amount for item in data if item.type == 'earnings')
        expenses = sum(item.amount for item in data if item.type == 'expenses')
        savings = sum(item.amount for item in data if item.type == 'savings')
        budget_goals = sum(item.amount for item in data if item.type == 'budgetGoals')

        # Handle target values safely
        earnings_target = max((item.target for item in data if item.type == 'earnings' and item.target is not None), default=0)
        expenses_target = max((item.target for item in data if item.type == 'expenses' and item.target is not None), default=0)
        savings_target = max((item.target for item in data if item.type == 'savings' and item.target is not None), default=0)
        budget_goals_target = max((item.target for item in data if item.type == 'budgetGoals' and item.target is not None), default=0)
        
        return jsonify({
            'earnings': earnings,
            'expenses': expenses,
            'savings': savings,
            'budgetGoals': budget_goals,
            'earningsTarget': earnings_target,
            'expensesTarget': expenses_target,
            'savingsTarget': savings_target,
            'budgetGoalsTarget': budget_goals_target
        })

    if request.method == 'POST':
        data = request.get_json()
        financial_data = FinancialData(
            user_id=current_user.id,
            type=data['type'],
            amount=data['amount'],
            date=datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S') if 'date' in data else datetime.now(),
            target=data.get('target')
        )

        db.session.add(financial_data)
        db.session.commit()

        return jsonify({'message': 'Financial data added successfully'}), 201