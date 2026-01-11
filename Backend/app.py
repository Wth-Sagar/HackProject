from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import db, EmergencyService, City
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app)

# Initialize database
db.init_app(app)

# Serve frontend files
@app.route('/')
def serve_index():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, path)

# API Routes
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Emergency Helpline API is running",
        "version": "1.0.0"
    })

@app.route('/api/test-connection')
def test_connection():
    try:
        # Try to connect to database
        count = EmergencyService.query.count()
        return jsonify({
            "success": True,
            "message": "Backend connected successfully!",
            "database": "Connected",
            "services_count": count
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Database connection error: {str(e)}"
        }), 500

@app.route('/api/services')
def get_all_services():
    try:
        # Get query parameters
        city = request.args.get('city')
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = EmergencyService.query
        
        # Apply filters
        if city and city.lower() != 'all':
            query = query.filter_by(city=city)
        
        if category and category.lower() != 'all':
            query = query.filter_by(category=category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (EmergencyService.name.ilike(search_term)) |
                (EmergencyService.city.ilike(search_term)) |
                (EmergencyService.address.ilike(search_term))
            )
        
        # Get only verified services
        query = query.filter_by(verified=True)
        
        services = query.all()
        
        return jsonify({
            "success": True,
            "count": len(services),
            "services": [service.to_dict() for service in services]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/services/<int:service_id>')
def get_service(service_id):
    try:
        service = EmergencyService.query.get(service_id)
        if not service:
            return jsonify({"success": False, "error": "Service not found"}), 404
        
        return jsonify({
            "success": True,
            "service": service.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cities')
def get_cities():
    try:
        cities = City.query.all()
        return jsonify({
            "success": True,
            "cities": [city.to_dict() for city in cities]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cities/<city_name>')
def get_city_services(city_name):
    try:
        services = EmergencyService.query.filter_by(city=city_name, verified=True).all()
        city = City.query.filter_by(name=city_name).first()
        
        return jsonify({
            "success": True,
            "city": city.to_dict() if city else None,
            "services": [service.to_dict() for service in services],
            "count": len(services)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/categories')
def get_categories():
    try:
        categories = db.session.query(EmergencyService.category).distinct().all()
        return jsonify({
            "success": True,
            "categories": [cat[0] for cat in categories if cat[0]]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/category/<category_name>')
def get_category_services(category_name):
    try:
        services = EmergencyService.query.filter_by(category=category_name, verified=True).all()
        return jsonify({
            "success": True,
            "category": category_name,
            "services": [service.to_dict() for service in services],
            "count": len(services)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/search')
def search_services():
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({"success": False, "error": "Search query required"}), 400
        
        services = EmergencyService.query.filter(
            (EmergencyService.name.ilike(f'%{query}%')) |
            (EmergencyService.city.ilike(f'%{query}%')) |
            (EmergencyService.address.ilike(f'%{query}%')) |
            (EmergencyService.phone.ilike(f'%{query}%'))
        ).filter_by(verified=True).all()
        
        return jsonify({
            "success": True,
            "query": query,
            "results": [service.to_dict() for service in services],
            "count": len(services)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/add', methods=['POST'])
def add_service():
    try:
        # In production, add proper authentication here
        data = request.json
        
        required_fields = ['name', 'category', 'phone', 'address', 'city']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"{field} is required"}), 400
        
        # Create new service
        service = EmergencyService(
            name=data['name'],
            category=data['category'],
            phone=data['phone'],
            alternate_phone=data.get('alternate_phone'),
            email=data.get('email'),
            address=data['address'],
            city=data['city'],
            state=data.get('state', 'Maharashtra'),
            pincode=data.get('pincode'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            website=data.get('website'),
            operational_hours=data.get('operational_hours', '24x7'),
            verified=data.get('verified', False),
            source=data.get('source', 'User Submitted')
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Service added successfully",
            "service": service.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# Statistics endpoint
@app.route('/api/stats')
def get_stats():
    try:
        total_services = EmergencyService.query.count()
        verified_services = EmergencyService.query.filter_by(verified=True).count()
        cities_count = City.query.count()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_services": total_services,
                "verified_services": verified_services,
                "cities_count": cities_count,
                "national_services": 8,
                "response_time": "< 10 minutes",
                "last_updated": "2024-01-15"
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Create database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    print("🚀 Emergency Helpline Backend Started!")
    print("📊 Database initialized")
    print("🌐 API available at: http://localhost:5000")
    print("🔗 Frontend: http://localhost:5000")
    print("🩺 Health check: http://localhost:5000/api/health")
    print("🔧 Test connection: http://localhost:5000/api/test-connection")
    
    app.run(debug=True, port=5000)