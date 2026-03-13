# Customer Fields Model
from datetime import datetime
from app import db

class CustomerFields(db.Model):
    """客户节点字段表"""
    __tablename__ = 'customer_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False, unique=True)
    
    customer_name = db.Column(db.String(200), nullable=False, unique=True)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.JSON)
    customer_type = db.Column(db.Integer, db.ForeignKey('taxonomy_items.id'))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    node = db.relationship('Node', backref='fields', uselist=False)
