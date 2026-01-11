from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class EmergencyService(db.Model):
    __tablename__ = 'emergency_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # police, fire, ambulance, women, hospital, disaster
    phone = db.Column(db.String(20), nullable=False)
    alternate_phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), default='Maharashtra')
    pincode = db.Column(db.String(10))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    website = db.Column(db.String(200))
    operational_hours = db.Column(db.String(50), default='24x7')
    verified = db.Column(db.Boolean, default=True)
    source = db.Column(db.String(200), default='Government Website')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'phone': self.phone,
            'alternate_phone': self.alternate_phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'website': self.website,
            'operational_hours': self.operational_hours,
            'verified': self.verified,
            'source': self.source
        }

class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    state = db.Column(db.String(50), default='Maharashtra')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'latitude': self.latitude,
            'longitude': self.longitude
        }