from app import create_app
from app.models import User
from celery import shared_task
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

@shared_task
def send_daily_reminders():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        smtp_host = app.config.get('SMTP_HOST')
        smtp_port = app.config.get('SMTP_PORT')
        smtp_user = app.config.get('SMTP_USER')
        smtp_pass = app.config.get('SMTP_PASS')
        smtp_from = app.config.get('SMTP_FROM')
        sent_count = 0
        for user in users:
            try:
                msg = MIMEText(f"Dear {user.first_name},\n\nDon't forget to book your parking spot today!\n\n- Vehicle Parking App", 'plain')
                msg['Subject'] = 'Daily Parking Reminder'
                msg['From'] = formataddr(('Vehicle Parking App', smtp_from))
                msg['To'] = user.email
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    if smtp_user and smtp_pass:
                        server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_from, [user.email], msg.as_string())
                print(f"[DAILY REMINDER] Sent reminder to {user.email} at {datetime.now()}")
                sent_count += 1
            except Exception as e:
                print(f"[DAILY REMINDER][ERROR] Failed to send to {user.email}: {e}")
        return f"Reminders sent to {sent_count} users." 
