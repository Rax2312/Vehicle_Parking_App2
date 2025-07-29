from flask import Blueprint, request, jsonify, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import ParkingLot, ParkingSpot, Reservation, User, db
from datetime import datetime, timedelta
import pytz
from sqlalchemy import func, extract
from collections import defaultdict
import traceback
import os
from app.tasks.exports import export_users_csv

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/<path:path>', methods=['OPTIONS'])
def options_admin(path, **kwargs):
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response, 200

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        role = None
        if isinstance(identity, dict):
            role = identity.get('role')
        elif isinstance(identity, str) and ':' in identity:
            _, role = identity.split(':', 1)
        else:
            role = 'user'
        
        if role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@admin_bp.route('/parking-lots', methods=['GET'])
@admin_required
def get_parking_lots():
    try:
        lots = ParkingLot.query.all()
        lots_data = []
        
        for lot in lots:
            # Counting occupied spots
            occupied_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            
            lots_data.append({
                'id': lot.id,
                'name': lot.prime_location_name,
                'price_per_hour': lot.price,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'total_spots': lot.number_of_spots,
                'occupied': occupied_count,
                'created_at': lot.created_at.isoformat() if lot.created_at else None
            })
        
        return jsonify(lots_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots', methods=['POST'])
@admin_required
def create_parking_lot():
    try:
        data = request.get_json()
        lot = ParkingLot(
            prime_location_name=data.get('prime_location_name', ''),
            price=data.get('price', 0),
            address=data.get('address', ''),
            pin_code=data.get('pin_code', ''),
            number_of_spots=data.get('number_of_spots', 0)
        )
        db.session.add(lot)
        db.session.commit()

        # Creating spots for the lot
        for i in range(1, lot.number_of_spots + 1):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=i,
                status='A',
                is_occupied=False,
                floor=1  
            )
            db.session.add(spot)
        db.session.commit()

        return jsonify({'message': 'Parking lot created successfully', 'id': lot.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
@admin_required
def update_parking_lot(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        data = request.get_json()
        lot.prime_location_name = data.get('prime_location_name', lot.prime_location_name)
        lot.price = data.get('price', lot.price)
        lot.address = data.get('address', lot.address)
        lot.pin_code = data.get('pin_code', lot.pin_code)
        lot.number_of_spots = data.get('number_of_spots', lot.number_of_spots)
        db.session.commit()
        return jsonify({'message': 'Parking lot updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
@admin_required
def delete_parking_lot(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        if lot.occupied > 0:
            return jsonify({'error': 'Cannot delete parking lot with active reservations'}), 400
        
        db.session.delete(lot)
        db.session.commit()
        return jsonify({'message': 'Parking lot deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['GET'])
@admin_required
def view_parking_lot(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        return jsonify({
            'id': lot.id,
            'name': lot.prime_location_name,
            'price_per_hour': lot.price,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'total_spots': lot.number_of_spots,
            'occupied': lot.occupied,
            'created_at': lot.created_at.isoformat() if lot.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>/details', methods=['GET'])
@admin_required
def view_parking_lot_details(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        spots_data = [{
            'id': spot.id,
            'spot_number': spot.spot_number,
            'status': spot.status,
            'is_occupied': spot.is_occupied,
            'floor': spot.floor,
            'current_reservation_id': spot.current_reservation_id
        } for spot in spots]
        available_count = sum(1 for s in spots if s.status == 'A')
        occupied_count = sum(1 for s in spots if s.status == 'O')
        return jsonify({
            'id': lot.id,
            'name': lot.prime_location_name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'total_spots': lot.number_of_spots,
            'price_per_hour': lot.price,
            'occupied': occupied_count, 
            'available_spots': available_count,
            'occupied_spots': occupied_count,
            'spots': spots_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@admin_required
def get_parking_spots(lot_id):
    try:
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return jsonify([{
            'id': spot.id,
            'spot_number': spot.spot_number,
            'floor': spot.floor,
            'is_occupied': spot.is_occupied,
            'status': spot.status,
            'current_reservation_id': spot.current_reservation_id
        } for spot in spots])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-spots/<int:spot_id>/details', methods=['GET'])
@admin_required
def get_spot_details(spot_id):
    try:
        spot = ParkingSpot.query.get_or_404(spot_id)
        print(f"Getting details for spot {spot_id}: status={spot.status}, current_reservation_id={spot.current_reservation_id}")
        
        reservation_data = None
        
        # First try to get reservation from current_reservation_id
        if spot.current_reservation_id:
            reservation = Reservation.query.get(spot.current_reservation_id)
            print(f"Found reservation via current_reservation_id: {reservation}")
        else:
            # If no current_reservation_id, look for active reservation for this spot
            reservation = Reservation.query.filter_by(
                spot_id=spot_id,
                leaving_timestamp=None
            ).first()
            print(f"Found reservation via spot_id query: {reservation}")
        
        if reservation:
            user = User.query.get(reservation.user_id)
            print(f"Found user: {user}")
            
            # Calculate current cost based on time passed
            current_cost = None
            if reservation.parking_timestamp:
                from datetime import datetime
                ist = pytz.timezone('Asia/Kolkata')
                current_time = datetime.now(ist).replace(tzinfo=None)
                duration_hours = (current_time - reservation.parking_timestamp).total_seconds() / 3600
                lot = ParkingLot.query.get(reservation.parking_lot_id)
                if lot:
                    current_cost = round(duration_hours * lot.price, 2)
                    print(f"Cost calculation: duration={duration_hours}h, lot_price={lot.price}, cost={current_cost}")
                else:
                    print(f"Lot not found for lot_id: {reservation.parking_lot_id}")
            else:
                print("No parking_timestamp found in reservation")
            
            reservation_data = {
                'customer_id': reservation.user_id,
                'customer_name': f"{user.first_name} {user.last_name}" if user else 'Unknown',
                'vehicle_number': reservation.vehicle_number,
                'phone_number': user.phone_number if user else 'N/A',
                'parking_timestamp': reservation.parking_timestamp.isoformat() if reservation.parking_timestamp else None,
                'parking_cost': current_cost,
                'remarks': reservation.remarks if reservation.remarks else None
            }
            print(f"Reservation data: {reservation_data}")
        else:
            print("No reservation found for this spot")
        
        return jsonify({
            'id': spot.id,
            'spot_number': spot.spot_number,
            'status': spot.status,
            'is_occupied': spot.is_occupied,
            'floor': spot.floor,
            'lot_id': spot.lot_id,
            'reservation': reservation_data
        })
    except Exception as e:
        print(f"Error in get_spot_details: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'role': user.role
        } for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/details', methods=['GET'])
@admin_required
def get_user_details(user_id):
    try:
        user = User.query.get_or_404(user_id)
        # Fetch all reservations for this user
        reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.parking_timestamp.desc()).all()
        reservations_list = []
        for r in reservations:
            lot = ParkingLot.query.get(r.parking_lot_id)
            spot = ParkingSpot.query.get(r.spot_id)
            reservations_list.append({
                'id': r.id,
                'lot_name': lot.prime_location_name if lot else 'Unknown',
                'spot_number': spot.spot_number if spot else 'Unknown',
                'vehicle_number': r.vehicle_number,
                'parking_timestamp': r.parking_timestamp.isoformat() if r.parking_timestamp else None,
                'leaving_timestamp': r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
                'cost': r.parking_cost,
                'status': r.status
            })
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'role': user.role,
            'age': user.age,
            'address': user.address,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'flagged': getattr(user, 'flagged', False),
            'reservations': reservations_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/flag', methods=['POST'])
@admin_required
def flag_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if user.role == 'admin':
            return jsonify({'error': 'Cannot flag an admin user'}), 400
        user.flagged = True
        db.session.commit()
        return jsonify({'message': 'User flagged successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/unflag', methods=['POST'])
@admin_required
def unflag_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if user.role == 'admin':
            return jsonify({'error': 'Cannot unflag an admin user'}), 400
        user.flagged = False
        db.session.commit()
        return jsonify({'message': 'User unflagged successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/summary', methods=['GET'])
@admin_required
def get_analytics_summary():
    try:
        # Get total revenue from completed reservations
        total_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.leaving_timestamp.isnot(None)
        ).scalar() or 0
        
        # Get total reservations
        total_reservations = Reservation.query.count()
        
        # Get active reservations 
        active_reservations = Reservation.query.filter_by(leaving_timestamp=None).count()
        
        # Get completed reservations 
        completed_reservations = Reservation.query.filter(Reservation.leaving_timestamp.isnot(None)).count()
        
        # Get total occupied spots 
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        
        return jsonify({
            'total_revenue': float(total_revenue),
            'total_reservations': total_reservations,
            'active_reservations': active_reservations,
            'completed_reservations': completed_reservations,
            'occupied_spots': occupied_spots
        })
    except Exception as e:
        print(f"Error in get_analytics_summary: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/monthly', methods=['GET'])
@admin_required
def get_analytics_monthly():
    try:
        # Get current year
        current_year = datetime.now().year
        
        # Get monthly data for current year (only completed reservations for cost)
        monthly_data = db.session.query(
            extract('month', Reservation.parking_timestamp).label('month'),
            func.count(Reservation.id).label('count'),
            func.sum(Reservation.parking_cost).label('cost')
        ).filter(
            extract('year', Reservation.parking_timestamp) == current_year,
            Reservation.leaving_timestamp.isnot(None)  
        ).group_by(
            extract('month', Reservation.parking_timestamp)
        ).all()
        
        # dictionary format
        result = {}
        for month, count, cost in monthly_data:
            month_name = datetime(current_year, int(month), 1).strftime('%B')
            result[month_name] = {
                'count': count,
                'cost': float(cost or 0)
            }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/lot', methods=['GET'])
@admin_required
def get_analytics_lot():
    try:
        # Get lot performance data
        lots = ParkingLot.query.all()
        result = []
        
        for lot in lots:
            # Get actual occupied spots count for this lot
            occupied_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            
            # Get reservations for this lot
            reservations = Reservation.query.filter_by(parking_lot_id=lot.id).count()
            
            result.append({
                'name': lot.prime_location_name,
                'occupied': occupied_count,
                'total_spots': lot.number_of_spots,
                'reservations': reservations,
                'utilization_rate': (occupied_count / lot.number_of_spots * 100) if lot.number_of_spots > 0 else 0
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_analytics_lot: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/test-data', methods=['POST'])
@admin_required
def generate_test_data():
    try:
        # Create some sample reservations for testing
        from datetime import datetime, timedelta
        import random
        
        # Get existing lots and users
        lots = ParkingLot.query.all()
        users = User.query.filter(User.role != 'admin').all()
        
        if not lots or not users:
            return jsonify({'error': 'Need parking lots and users to generate test data'}), 400
        
        # Generate reservations for the last 6 months
        for i in range(30):  # 30 sample reservations
            lot = random.choice(lots)
            user = random.choice(users)
            
            # Get a random spot from this lot
            spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
            if not spots:
                continue
            spot = random.choice(spots)
            
            # Random date in last 6 months
            days_ago = random.randint(1, 180)
            start_time = datetime.now() - timedelta(days=days_ago)
            
            # Random duration (1-8 hours)
            duration_hours = random.randint(1, 8)
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Calculate cost
            cost = lot.price * duration_hours
            
            # Random status (most completed, some active)
            status = 'Completed' if random.random() > 0.2 else 'Active'
            
            reservation = Reservation(
                user_id=user.id,
                parking_lot_id=lot.id,
                spot_id=spot.id,
                vehicle_number=f"KA{random.randint(1, 99)}{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1000, 9999)}",
                parking_timestamp=start_time,
                leaving_timestamp=end_time if status == 'Completed' else None,
                parking_cost=cost if status == 'Completed' else None,
                status=status,
                remarks=f"Test reservation {i+1}"
            )
            
            db.session.add(reservation)
        
        db.session.commit()
        return jsonify({'message': 'Test data generated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-records', methods=['GET'])
@admin_required
def get_parking_records():
    try:
        records = []
        reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).all()
        for r in reservations:
            user = User.query.get(r.user_id)
            lot = ParkingLot.query.get(r.parking_lot_id)
            spot = ParkingSpot.query.get(r.spot_id)
            records.append({
                'id': r.id,
                'user_name': f"{user.first_name} {user.last_name}" if user else 'Unknown',
                'lot_name': lot.prime_location_name if lot else 'Unknown',
                'spot_number': spot.spot_number if spot else 'Unknown',
                'vehicle_number': r.vehicle_number,
                'parking_timestamp': r.parking_timestamp.isoformat() if r.parking_timestamp else None,
                'leaving_timestamp': r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
                'duration_hours': round(((r.leaving_timestamp - r.parking_timestamp).total_seconds() / 3600), 2) if r.leaving_timestamp else None,
                'cost': r.parking_cost,
                'status': r.status
            })
        return jsonify({'records': records})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/export-users-csv', methods=['POST'])
@admin_required
def trigger_export_users_csv():
    try:
        print("=== EXPORT CSV START ===")
        print("Importing task...")
        from app.tasks.exports import export_users_csv
        print("Task imported successfully")
        print("Calling task.delay()...")
        task = export_users_csv.delay()
        print(f"Task created with ID: {task.id}")
        return jsonify({'message': 'CSV export started', 'task_id': task.id}), 202
    except Exception as e:
        import traceback
        print("=== EXPORT CSV ERROR ===")
        print(f"Error: {e}")
        print("Full traceback:")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to start export: {str(e)}'}), 500

@admin_bp.route('/export-users-csv/<task_id>/status', methods=['GET'])
@admin_required
def get_export_status(task_id):
    try:
        task = export_users_csv.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            return jsonify({'state': 'SUCCESS'}), 200
        elif task.state == 'FAILURE':
            return jsonify({'state': 'FAILURE', 'error': str(task.info)}), 500
        else:
            return jsonify({'state': task.state}), 202
    except Exception as e:
        return jsonify({'error': f'Failed to check export status: {str(e)}'}), 500

@admin_bp.route('/export-users-csv/<task_id>/download', methods=['GET'])
@admin_required
def download_exported_csv(task_id):
    try:
        task = export_users_csv.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            filepath = task.result
            if os.path.exists(filepath):
                response = send_file(
                    filepath, 
                    as_attachment=True, 
                    download_name=os.path.basename(filepath),
                    mimetype='text/csv'
                )
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
            else:
                return jsonify({'error': 'Export file not found'}), 404
        elif task.state == 'FAILURE':
            return jsonify({'error': str(task.info)}), 500
        else:
            return jsonify({'error': 'Export not ready'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to download export: {str(e)}'}), 500

@admin_bp.route('/search/parking-lots', methods=['GET'])
@admin_required
def search_parking_lots():
    try:
        query = request.args.get('q', '').strip()
        print(f"=== PARKING LOTS SEARCH DEBUG ===")
        print(f"Query: '{query}'")
        
        if not query:
            print("Empty query, returning empty array")
            return jsonify([])
        
        # Checking what parking lots exist in the DB
        all_lots = ParkingLot.query.all()
        print(f"Total parking lots in DB: {len(all_lots)}")
        for lot in all_lots:
            print(f"Lot ID: {lot.id}, prime_location_name: '{lot.prime_location_name}', name: '{getattr(lot, 'name', 'N/A')}'")
        
        # Search functionality
        lots = ParkingLot.query.filter(
            db.or_(
                ParkingLot.prime_location_name.ilike(f'%{query}%'),
                ParkingLot.address.ilike(f'%{query}%'),
                ParkingLot.pin_code.ilike(f'%{query}%')
            )
        ).all()
        
        print(f"Search results count: {len(lots)}")
        for lot in lots:
            print(f"Found lot: ID={lot.id}, name='{lot.prime_location_name}'")
        
        lots_data = []
        for lot in lots:
            occupied_count = ParkingSpot.query.filter_by(lot_id=lot.id, is_occupied=True).count()
            lot_data = {
                'id': lot.id,
                'name': lot.prime_location_name,
                'price_per_hour': lot.price,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'total_spots': lot.number_of_spots,
                'occupied': occupied_count,
                'created_at': lot.created_at.isoformat() if lot.created_at else None
            }
            lots_data.append(lot_data)
            print(f"Added lot data: {lot_data}")
        
        print(f"Returning {len(lots_data)} results")
        return jsonify(lots_data)
    except Exception as e:
        print(f"Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/search/parking-spots', methods=['GET'])
@admin_required
def search_parking_spots():
    try:
        status = request.args.get('status', '').strip().lower()
        query = request.args.get('q', '').strip()
        spots_query = ParkingSpot.query
        if status:
            if status == 'available':
                spots_query = spots_query.filter(ParkingSpot.is_occupied == False)
            elif status == 'occupied':
                spots_query = spots_query.filter(ParkingSpot.is_occupied == True)
        if query:
            spots_query = spots_query.join(ParkingLot).filter(
                db.or_(
                    ParkingSpot.spot_number.ilike(f'%{query}%'),
                    ParkingLot.prime_location_name.ilike(f'%{query}%'),
                    ParkingLot.address.ilike(f'%{query}%')
                )
            )
        spots = spots_query.all()
        spots_data = []
        for spot in spots:
            lot = ParkingLot.query.get(spot.lot_id)
            spots_data.append({
                'id': spot.id,
                'spot_number': spot.spot_number,
                'status': spot.status,
                'is_occupied': spot.is_occupied,
                'floor': spot.floor,
                'lot_name': lot.prime_location_name if lot else 'Unknown',
                'lot_address': lot.address if lot else 'Unknown',
                'lot_id': spot.lot_id
            })
        return jsonify(spots_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/search/users', methods=['GET'])
@admin_required
def search_users():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([])
        users = User.query.filter(
            db.or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%'),
                User.phone_number.ilike(f'%{query}%'),
                User.first_name.ilike(f'%{query}%'),
                User.last_name.ilike(f'%{query}%')
            )
        ).all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'role': user.role,
                'flagged': user.flagged,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        return jsonify(users_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/debug/data', methods=['GET'])
@admin_required
def debug_data():
    """Debug endpoint to check what data exists in the database"""
    try:
        lots_count = ParkingLot.query.count()
        users_count = User.query.count()
        spots_count = ParkingSpot.query.count()
        
        # Getting first few items of each type
        lots = ParkingLot.query.limit(3).all()
        users = User.query.limit(3).all()
        spots = ParkingSpot.query.limit(3).all()
        
        return jsonify({
            'counts': {
                'parking_lots': lots_count,
                'users': users_count,
                'parking_spots': spots_count
            },
            'sample_lots': [{'id': lot.id, 'name': lot.prime_location_name} for lot in lots],
            'sample_users': [{'id': user.id, 'username': user.username, 'email': user.email} for user in users],
            'sample_spots': [{'id': spot.id, 'spot_number': spot.spot_number, 'status': spot.status} for spot in spots]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
