from faker import Faker

from app.models.user import User
from config.database import get_session
from datetime import datetime, timedelta


def run():
    db = get_session()
    fake = Faker()

    current_time = datetime.now()
    two_months_ago = current_time - timedelta(days=60)

    for x in range(0, 30):
        user = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
            "created_at": fake.date_time_between(start_date=two_months_ago, end_date=current_time),
            "updated_at": fake.date_time_between(start_date=two_months_ago, end_date=current_time),
        }
        user = User(**user)
        db.add(user)
        db.commit()
        db.refresh(user)
