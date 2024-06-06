import json
from random import randint, uniform
from datetime import datetime, timedelta

def generate_random_date(start, end):
    return start + timedelta(
        seconds=randint(0, int((end - start).total_seconds())),
    )

def generate_user_data(user_id):
    financial_data = []
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 5, 31)
    
    for _ in range(30):  # Generate 30 financial data entries per user
        financial_data.append({
            'user_id': user_id,
            'type': 'earnings',
            'amount': round(uniform(100, 5000), 2),
            'date': generate_random_date(start_date, end_date).isoformat()
        })
        financial_data.append({
            'user_id': user_id,
            'type': 'expenses',
            'amount': round(uniform(50, 4000), 2),
            'date': generate_random_date(start_date, end_date).isoformat(),
            'category': 'Food'
        })
        financial_data.append({
            'user_id': user_id,
            'type': 'savings',
            'amount': round(uniform(50, 2000), 2),
            'date': generate_random_date(start_date, end_date).isoformat()
        })
        financial_data.append({
            'user_id': user_id,
            'type': 'budgetGoals',
            'amount': round(uniform(1000, 6000), 2),
            'date': generate_random_date(start_date, end_date).isoformat()
        })
    
    return {
        'id': user_id,
        'username': f'user{user_id}',
        'email': f'user{user_id}@example.com',
        'password': 'hashed_password',  # Use the same hashed password for simplicity
        'financial_data': financial_data
    }

# Assume the existing highest user ID is known and is 10
starting_user_id = 11

# Generate data for 10 users starting from the next available ID
users_data = [generate_user_data(user_id) for user_id in range(starting_user_id, starting_user_id + 10)]

# Save the generated data to a JSON file
with open('sample_users_data.json', 'w') as f:
    json.dump(users_data, f, indent=4)
