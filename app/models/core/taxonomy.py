# 文件路径：app/models/taxonomy.py
# 功能说明：Taxonomy 词汇表模型

from app import db
from datetime import datetime


class Taxonomy(db.Model):
    """词汇表"""
    __tablename__ = 'taxonomies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False, comment="词汇表名称")
    slug = db.Column(db.String(128), unique=True, nullable=False, index=True, comment="URL标识")
    description = db.Column(db.String(512), nullable=True, comment="描述")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = db.relationship('TaxonomyItem', backref='taxonomy', lazy='dynamic', cascade='all, delete-orphan', order_by='TaxonomyItem.weight')

    def __repr__(self):
        return f'<Taxonomy {self.name}>'


class TaxonomyItem(db.Model):
    """词汇项"""
    __tablename__ = 'taxonomy_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(256), nullable=False, comment="词汇名称")
    description = db.Column(db.String(512), nullable=True, comment="描述")
    weight = db.Column(db.Integer, default=0, nullable=False, comment="排序权重")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<TaxonomyItem {self.name}>'
