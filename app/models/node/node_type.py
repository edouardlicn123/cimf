# Node Type Model
from datetime import datetime
from app import db

class NodeType(db.Model):
    """节点类型"""
    __tablename__ = 'node_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(500))
    icon = db.Column(db.String(50), default='bi-folder')
    fields_config = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
