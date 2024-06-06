import json
from app import app, db
from app.models import User, FinancialData
from datetime import datetime

with app.app_context():
    # Get the highest existing user ID in the database
    highest_existing_id = db.session.query(db.func.max(User.id)).scalar() or 0

    with open('sample_users_data.json', 'r') as f:
        users_data = json.load(f)

    for user_data in users_data:
        new_user_id = highest_existing_id + user_data['id']

        # Check if the email already exists to avoid duplicates
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            continue  # Skip this user if they already exist

        user = User(
            id=new_user_id,
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']  # Make sure to hash the password appropriately
        )
        db.session.add(user)
        db.session.commit()

        for item in user_data['financial_data']:
            financial_data = FinancialData(
                user_id=new_user_id,
                type=item['type'],
                amount=item['amount'],
                date=datetime.fromisoformat(item['date']),
                category=item.get('category', None)
            )
            db.session.add(financial_data)

        db.session.commit()
