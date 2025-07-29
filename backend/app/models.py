from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# --- User Model ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'admin' or 'user'
    flagged = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reservations = db.relationship('Reservation', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

# --- ParkingLot Model ---
class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)  # price per hour
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    occupied = db.Column(db.Integer, default=0)  # Number of occupied spots
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    spots = db.relationship('ParkingSpot', back_populates='lot', cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', foreign_keys='Reservation.parking_lot_id')

    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'

# --- ParkingSpot Model ---
class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)  
    status = db.Column(db.String(1), nullable=False, default='A')  # 'A' = Available, 'O' = Occupied
    is_occupied = db.Column(db.Boolean, default=False)  
    floor = db.Column(db.Integer, default=1)  # Floor number
    current_reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lot = db.relationship('ParkingLot', back_populates='spots')
    reservations = db.relationship(
        'Reservation',
        back_populates='spot',
        cascade='all, delete-orphan',
        foreign_keys='Reservation.spot_id'
    )
    current_reservation = db.relationship(
        'Reservation',
        foreign_keys=[current_reservation_id],
        post_update=True
    )

    __table_args__ = (
        db.UniqueConstraint('lot_id', 'spot_number', name='unique_spot_per_lot'),
    )

    def __repr__(self):
        return f'<ParkingSpot Lot:{self.lot_id} Spot:{self.spot_number}>'

# --- Reservation Model ---
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='Active')  # 'Active' or 'Completed'
    vehicle_number = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    remarks = db.Column(db.String(200), nullable=True)

    user = db.relationship('User', back_populates='reservations')
    spot = db.relationship(
        'ParkingSpot',
        back_populates='reservations',
        foreign_keys=[spot_id]
    )
    lot = db.relationship('ParkingLot', foreign_keys=[parking_lot_id])

    def __repr__(self):
        return f'<Reservation User:{self.user_id} Spot:{self.spot_id}>'
