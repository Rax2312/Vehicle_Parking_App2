import os

CELERY_BEAT_SCHEDULE = {
    'send-daily-reminders': {
        'task': 'app.tasks.reminders.send_daily_reminders',
        'schedule': 60 * 60 * 24,  # every 24 hours
        'options': {'expires': 60 * 60 * 2},
    },
    'send-monthly-reports': {
        'task': 'app.tasks.reports.send_monthly_reports',
        'schedule': 60 * 60 * 24 * 30,  # every 30 days (approx)
        'options': {'expires': 60 * 60 * 24},
    },
}

CELERY_TIMEZONE = 'Asia/Kolkata'

# SMTP configuration (read from environment variables for security)
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.example.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '22f3002775@ds.study.iitm.ac.in')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
SMTP_FROM = os.environ.get('SMTP_FROM', '22f3002775@ds.study.iitm.ac.in') 