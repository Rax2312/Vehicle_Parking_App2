from app import create_app
from app.models import User, Reservation, ParkingLot
from celery import shared_task
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from io import BytesIO
from xhtml2pdf import pisa

@shared_task
def send_monthly_reports():
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
                # GET monthly stats
                now = datetime.now()
                month_start = datetime(now.year, now.month, 1)
                reservations = Reservation.query.filter(
                    Reservation.user_id == user.id,
                    Reservation.parking_timestamp >= month_start
                ).all()
                total_reservations = len(reservations)
                total_cost = sum(r.parking_cost or 0 for r in reservations)
                lot_counts = {}
                for r in reservations:
                    lot = ParkingLot.query.get(r.parking_lot_id)
                    lot_name = lot.prime_location_name if lot else 'Unknown'
                    lot_counts[lot_name] = lot_counts.get(lot_name, 0) + 1
                most_used_lot = max(lot_counts, key=lot_counts.get) if lot_counts else 'N/A'
                # HTML body
                html_body = f"""
                <h2>Monthly Parking Activity Report</h2>
                <p>Dear {user.first_name},</p>
                <p>Here is your parking activity summary for {now.strftime('%B %Y')}:</p>
                <ul>
                  <li><b>Total Reservations:</b> {total_reservations}</li>
                  <li><b>Total Amount Spent:</b> ₹{total_cost:.2f}</li>
                  <li><b>Most Used Parking Lot:</b> {most_used_lot}</li>
                </ul>
                <p>Thank you for using the Vehicle Parking App!</p>
                """
                # PDF generation
                pdf_buffer = BytesIO()
                pisa.CreatePDF(html_body, dest=pdf_buffer)
                pdf_buffer.seek(0)
                # Email
                msg = MIMEMultipart()
                msg['Subject'] = f"Monthly Parking Activity Report - {now.strftime('%B %Y')}"
                msg['From'] = formataddr(('Vehicle Parking App', smtp_from))
                msg['To'] = user.email
                msg.attach(MIMEText(html_body, 'html'))
                pdf_part = MIMEApplication(pdf_buffer.read(), _subtype='pdf')
                pdf_part.add_header('Content-Disposition', 'attachment', filename=f"Parking_Report_{now.strftime('%Y_%m')}.pdf")
                msg.attach(pdf_part)
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    if smtp_user and smtp_pass:
                        server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_from, [user.email], msg.as_string())
                print(f"[MONTHLY REPORT] Sent report to {user.email} at {datetime.now()}")
                sent_count += 1
            except Exception as e:
                print(f"[MONTHLY REPORT][ERROR] Failed to send to {user.email}: {e}")
        return f"Reports sent to {sent_count} users." 
