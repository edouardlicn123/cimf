# Node Main Table Model
from datetime import datetime
from app import db

class Node(db.Model):
    """节点主表 - 所有节点类型的公共字段"""
    __tablename__ = 'nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    node_type_id = db.Column(db.Integer, db.ForeignKey('node_types.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    node_type = db.relationship('NodeType', backref='nodes')
    creator = db.relationship('User', foreign_keys=[created_by])
    updater = db.relationship('User', foreign_keys=[updated_by])
