# Vehicle Parking App

A multi-user parking management system built with Flask, Vue.js, and SQLite for managing vehicle parking lots and reservations.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vue.js with Bootstrap
- **Database**: SQLite
- **Caching**: Redis
- **Background Jobs**: Celery with Redis broker
- **Authentication**: JWT-based
- **UI Framework**: Bootstrap 5

## Project Structure

```
└── 📁vehicle_parking_app
    └── 📁backend
        └── app.py
        └── celery_worker.py
        └── celery_beat.sh
        └── celery_worker.sh
        └── requirements.txt
        └── 📁app
            └── __init__.py
            └── config.py
            └── models.py
            └── 📁api
                └── admin.py
                └── auth.py
                └── user.py
            └── 📁tasks
                └── exports.py
                └── reminders.py
                └── reports.py
            └── 📁templates
        └── 📁instance
            └── parking.db
    └── 📁frontend
        └── package.json
        └── 📁public
            └── index.html
            └── manifest.json
            └── service-worker.js
        └── 📁src
            └── App.vue
            └── main.js
            └── 📁components
                └── NavBar.vue
                └── ParkingAnalytics.vue
                └── UserAnalytics.vue
            └── 📁router
                └── index.js
            └── 📁services
                └── ApiService.js
            └── 📁views
                └── AdminDashboard.vue
                └── Home.vue
                └── Login.vue
                └── NotFound.vue
                └── Profile.vue
                └── RecentHistory.vue
                └── Register.vue
                └── UserDashboard.vue
```

## Core Features

### Authentication

- Role-based access (Admin/User)
- JWT-based authentication
- Session management

### Admin Features

- Parking lot CRUD operations
- Spot management
- User management
- Analytics dashboard
- Export functionality

### User Features

- Real-time spot booking
- Active reservations tracking
- Booking history
- Profile management

### Background Jobs

- Daily email reminders
- Monthly PDF reports
- CSV exports for user data

## Setup Requirements

- Install backend dependencies:
  ```powershell
  pip install -r requirements.txt
  ```
- Install frontend dependencies:
  ```powershell
  cd frontend
  npm install
  ```
- Set up `.env` file with required environment variables

## Environment Variables

Create a `.env` file in the backend directory:

```
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASS=your-password
SMTP_FROM=your-email@example.com
```

## Running the Project

To run the full stack locally, you'll need **five separate terminals**:
First activate virtual environment. Followingly:

1. **Backend Terminal**

   ```powershell
   cd backend
   python app.py
   ```

2. **Frontend Terminal**

   ```powershell
   cd frontend
   npm run serve
   ```

3. **Redis Terminal**

   ```powershell
   docker pull redis
   docker run --name redis -p 6379:6379 redis
   # If Redis is already created:
   docker start redis
   ```

4. **Celery Worker Terminal**

   ```powershell
   cd backend
   celery -A app.celery worker --loglevel=info
   ```

5. **Celery Beat Terminal**
   ```powershell
   cd backend
   celery -A app.celery beat --loglevel=info
   ```

## Development Notes

- For mobile testing, use `npm run serve -- --host 0.0.0.0`
- Check terminal logs for any errors during setup
- Ensure Redis is running before starting Celery workers
