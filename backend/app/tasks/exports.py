from app import create_app
from app.models import User
from celery import current_app
import csv
from datetime import datetime
import os

@current_app.task
def export_users_csv():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(app.instance_path, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Phone Number', 'Address', 'Role', 'Flagged'])
            for user in users:
                writer.writerow([
                    user.id,
                    user.username,
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.phone_number,
                    user.address,
                    user.role,
                    user.flagged
                ])
        
        print(f"[CSV EXPORT] Exported {len(users)} users to {filepath}")
        return filepath 
