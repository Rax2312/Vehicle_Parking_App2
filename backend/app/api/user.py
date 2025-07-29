from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
import math
import pytz
import traceback
from app import cache

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/<path:path>', methods=['OPTIONS'])
def options_user(path, **kwargs):
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response, 200

def user_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            user_id = identity.get('user_id')
            role = identity.get('role')
        elif isinstance(identity, str) and ':' in identity:
            user_id, role = identity.split(':', 1)
            user_id = int(user_id)
        else:
            user_id = identity
            role = 'user'  
        
        if role not in ['user', 'admin']:
            return jsonify({'error': 'User access required'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def get_current_user_id():
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('user_id')
    elif isinstance(identity, str) and ':' in identity:
        user_id, role = identity.split(':', 1)
        return int(user_id)
    else:
        return int(identity.split(':')[0]) if ':' in str(identity) else identity

def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

@user_bp.route('/parking-lots', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, key_prefix='user_lots')
def list_lots():
    try:
        lots = ParkingLot.query.all()
        lots_data = []
        
        for lot in lots:
            # Count available spots
            available_spots = ParkingSpot.query.filter_by(
                lot_id=lot.id, 
                status='A'
            ).count()
            
            lots_data.append({
                'id': lot.id,
                'name': lot.prime_location_name,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'price_per_hour': lot.price,
                'total_spots': lot.number_of_spots,
                'available_spots': available_spots,
                'created_at': lot.created_at.isoformat() if lot.created_at else None
            })
        
        return jsonify({
            'success': True,
            'lots': lots_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get lot details with spot status
@user_bp.route('/parking-lots/<int:lot_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, key_prefix=lambda: f'user_lot_{request.view_args["lot_id"]}')
def get_lot_details(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        
        spots_data = []
        for spot in spots:
            spots_data.append({
                'id': spot.id,
                'spot_number': spot.spot_number,
                'status': spot.status,
                'is_occupied': spot.is_occupied,
                'is_available': spot.status == 'A'
            })
        
        return jsonify({
            'success': True,
            'lot': {
                'id': lot.id,
                'name': lot.prime_location_name,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'price_per_hour': lot.price,
                'total_spots': lot.number_of_spots,
                'spots': spots_data
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Reserve a spot in a lot
@user_bp.route('/parking-lots/<int:lot_id>/reserve', methods=['POST'])
@jwt_required()
def reserve_spot(lot_id):
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        # Check if user is flagged
        if user.flagged:
            admin = User.query.filter_by(role='admin').first()
            admin_phone = admin.phone_number if admin else 'N/A'
            return jsonify({'success': False, 'error': f'Your account is flagged. Please contact support: {admin_phone}'}), 403
        data = request.get_json()
        vehicle_number = data.get('vehicle_number')
        phone_number = data.get('phone_number', '')
        customer_name = data.get('customer_name', '')
        remarks = data.get('remarks', '')
        if not vehicle_number:
            return jsonify({'success': False, 'error': 'Vehicle number is required'}), 400
        lot = ParkingLot.query.get_or_404(lot_id)
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not available_spot:
            return jsonify({'success': False, 'error': 'No available spots in this parking lot'}), 400
        # Prevent second time booking if this vehicle is already parked
        active_reservation = Reservation.query.filter_by(vehicle_number=vehicle_number, leaving_timestamp=None).first()
        if active_reservation:
            return jsonify({'success': False, 'error': 'This vehicle already has an active reservation. Please release it first.'}), 400
        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=user_id,
            parking_lot_id=lot_id,
            parking_timestamp=get_ist_time(),
            vehicle_number=vehicle_number,
            phone_number=phone_number,
            customer_name=customer_name,
            remarks=remarks,
            status='Active'
        )
        # Update spot status
        spot = available_spot
        spot.status = 'O'
        spot.is_occupied = True
        spot.current_reservation_id = reservation.id
        # Update parking lot occupied count
        lot.occupied = ParkingSpot.query.filter_by(lot_id=lot_id, is_occupied=True).count()
        db.session.add(reservation)
        db.session.commit()
        cache.delete('user_lots')
        cache.delete(f'user_lot_{lot_id}')
        return jsonify({
            'success': True,
            'message': 'Spot reserved successfully',
            'reservation': {
                'id': reservation.id,
                'spot_number': available_spot.spot_number,
                'lot_name': lot.prime_location_name,
                'parking_timestamp': reservation.parking_timestamp.isoformat(),
                'vehicle_number': reservation.vehicle_number
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print("Error booking spot:", traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

# User's reservation history
@user_bp.route('/reservations', methods=['GET'])
@jwt_required()
def reservation_history():
    try:
        user_id = get_current_user_id()
        
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(
            Reservation.parking_timestamp.desc()
        ).all()
        
        reservations_data = []
        for reservation in reservations:
            # Get lot and spot details safely
            lot_name = "Unknown"
            spot_number = "Unknown"
            
            try:
                lot = ParkingLot.query.get(reservation.parking_lot_id)
                lot_name = lot.prime_location_name if lot else "Unknown"
            except Exception as e:
                print(f"Error getting lot for reservation {reservation.id}: {e}")
                lot_name = "Unknown"
            
            try:
                spot = ParkingSpot.query.get(reservation.spot_id)
                spot_number = spot.spot_number if spot else "Unknown"
            except Exception as e:
                print(f"Error getting spot for reservation {reservation.id}: {e}")
                spot_number = "Unknown"
            
            # Calculate duration and cost if its completed
            duration = None
            cost = None
            if reservation.leaving_timestamp:
                duration = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600  # hours
                cost = reservation.parking_cost
            
            reservations_data.append({
                'id': reservation.id,
                'spot_number': spot_number,
                'lot_name': lot_name,
                'vehicle_number': reservation.vehicle_number,
                'parking_timestamp': reservation.parking_timestamp.isoformat(),
                'leaving_timestamp': reservation.leaving_timestamp.isoformat() if reservation.leaving_timestamp else None,
                'duration_hours': round(duration, 2) if duration else None,
                'cost': cost,
                'status': 'Active' if not reservation.leaving_timestamp else 'Completed',
                'remarks': reservation.remarks
            })
        
        return jsonify({
            'success': True,
            'reservations': reservations_data
        }), 200
    except Exception as e:
        print(f"Error in reservation_history: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get active reservations
@user_bp.route('/reservations/active', methods=['GET'])
@jwt_required()
def get_active_reservation():
    try:
        user_id = get_current_user_id()
        print(f"Looking for active reservations for user_id: {user_id}")
        active_reservations = Reservation.query.filter_by(
            user_id=user_id,
            leaving_timestamp=None
        ).all()
        print(f"Found active reservations: {active_reservations}")
        if not active_reservations:
            return jsonify({
                'success': True,
                'active_reservations': []
            }), 200
        result = []
        for active_reservation in active_reservations:
            # Lot and spot details
            lot_name = "Unknown"
            spot_number = "Unknown"
            try:
                lot = ParkingLot.query.get(active_reservation.parking_lot_id)
                lot_name = lot.prime_location_name if lot else "Unknown"
            except Exception as e:
                print(f"Error getting lot: {e}")
                lot_name = "Unknown"
            try:
                spot = ParkingSpot.query.get(active_reservation.spot_id)
                spot_number = spot.spot_number if spot else "Unknown"
            except Exception as e:
                print(f"Error getting spot: {e}")
                spot_number = "Unknown"
            # Calculate duration
            now = get_ist_time().replace(tzinfo=None)
            duration = (now - active_reservation.parking_timestamp).total_seconds() / 3600  # hours
            result.append({
                'id': active_reservation.id,
                'spot_number': spot_number,
                'lot_name': lot_name,
                'vehicle_number': active_reservation.vehicle_number,
                'parking_timestamp': active_reservation.parking_timestamp.isoformat(),
                'duration_hours': round(duration, 2),
                'remarks': active_reservation.remarks
            })
        return jsonify({
            'success': True,
            'active_reservations': result
        }), 200
    except Exception as e:
        print(f"Error in get_active_reservation: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Release a spot
@user_bp.route('/reservations/<int:reservation_id>/release', methods=['POST'])
@jwt_required()
def release_spot(reservation_id):
    try:
        user_id = get_current_user_id()
        reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first_or_404()
        if reservation.leaving_timestamp:
            return jsonify({'success': False, 'error': 'This reservation has already been released'}), 400
        leaving_time = get_ist_time().replace(tzinfo=None)
        duration_hours = (leaving_time - reservation.parking_timestamp).total_seconds() / 3600
        cost = round(duration_hours * reservation.lot.price, 2)
        reservation.leaving_timestamp = leaving_time
        reservation.parking_cost = cost
        reservation.status = 'Completed'
        spot = reservation.spot
        spot.status = 'A'
        spot.is_occupied = False
        spot.current_reservation_id = None
        
        # Update parking lot occupied count
        lot = reservation.lot
        lot.occupied = ParkingSpot.query.filter_by(lot_id=lot.id, is_occupied=True).count()
        
        db.session.commit()
        cache.delete('user_lots')
        cache.delete(f'user_lot_{lot.id}')
        return jsonify({
            'success': True,
            'message': 'Spot released successfully',
            'reservation': {
                'id': reservation.id,
                'duration_hours': round(duration_hours, 2),
                'cost': cost,
                'leaving_timestamp': leaving_time.isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# User's charts
@user_bp.route('/summary', methods=['GET'])
@jwt_required()
def user_summary():
    try:
        user_id = get_current_user_id()
        
        # Get user's reservations
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        
        total_reservations = len(reservations)
        completed_reservations = len([r for r in reservations if r.leaving_timestamp])
        active_reservations = len([r for r in reservations if not r.leaving_timestamp])
        
        total_cost = sum([r.parking_cost or 0 for r in reservations])
        total_hours = sum([
            (r.leaving_timestamp - r.parking_timestamp).total_seconds() / 3600 
            for r in reservations if r.leaving_timestamp
        ])
        
        # Monthly breakdown
        monthly_data = {}
        for reservation in reservations:
            if reservation.leaving_timestamp:
                month = reservation.parking_timestamp.strftime('%Y-%m')
                if month not in monthly_data:
                    monthly_data[month] = {'count': 0, 'cost': 0, 'hours': 0}
                
                monthly_data[month]['count'] += 1
                monthly_data[month]['cost'] += reservation.parking_cost or 0
                monthly_data[month]['hours'] += (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
        
        return jsonify({
            'success': True,
            'summary': {
                'total_reservations': total_reservations,
                'completed_reservations': completed_reservations,
                'active_reservations': active_reservations,
                'total_cost': round(total_cost, 2),
                'total_hours': round(total_hours, 2),
                'average_cost_per_reservation': round(total_cost / completed_reservations, 2) if completed_reservations > 0 else 0,
                'monthly_breakdown': monthly_data
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@user_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def delete_reservation(reservation_id):
    try:
        user_id = get_current_user_id()
        
        reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first()
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation.leaving_timestamp:
            return jsonify({'error': 'Cannot delete active reservation'}), 400
        
        db.session.delete(reservation)
        db.session.commit()
        return jsonify({'message': 'Reservation deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/analytics', methods=['GET'])
@user_required
def get_user_analytics():
    try:
        user_id = get_current_user_id()
        
        # Get user's reservations
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        
        # Calculate summary
        total_cost = sum(r.parking_cost or 0 for r in reservations if r.leaving_timestamp)
        total_reservations = len(reservations)
        active_reservations = len([r for r in reservations if not r.leaving_timestamp])
        completed_reservations = len([r for r in reservations if r.leaving_timestamp])
        
        # Calculate total hours from completed reservations
        total_hours = sum([
            (r.leaving_timestamp - r.parking_timestamp).total_seconds() / 3600 
            for r in reservations if r.leaving_timestamp
        ])
        
        # Calculate monthly data
        monthly_data = {}
        
        for reservation in reservations:
            if reservation.parking_timestamp:
                month = reservation.parking_timestamp.strftime('%B')
                if month not in monthly_data:
                    monthly_data[month] = {'count': 0, 'cost': 0, 'hours': 0}
                
                monthly_data[month]['count'] += 1
                if reservation.leaving_timestamp:
                    monthly_data[month]['cost'] += reservation.parking_cost or 0
                    monthly_data[month]['hours'] += (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
        
        return jsonify({
            'summary': {
                'total_cost': round(total_cost, 2),
                'total_reservations': total_reservations,
                'active_reservations': active_reservations,
                'completed_reservations': completed_reservations,
                'total_hours': round(total_hours, 2),
                'average_cost_per_reservation': round(total_cost / completed_reservations, 2) if completed_reservations > 0 else 0
            },
            'monthly_data': monthly_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_current_user_id()
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'age': user.age,
        'address': user.address,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'role': user.role
    })

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_current_user_id()
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    # Allow only updating fields other than username
    for field in ['email', 'first_name', 'last_name', 'phone_number', 'age', 'address']:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

@user_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def update_password():
    user_id = get_current_user_id()
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'Current and new password required'}), 400
    if not user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Wrong password'}), 401
    user.set_password(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password updated successfully'}) 
