"""
图斑图片模型
用于存储图斑相关的现场照片和卫星影像
"""
from datetime import datetime
from . import db


class TubanImage(db.Model):
    """图斑图片表"""
    __tablename__ = 'tuban_images'

    id = db.Column(db.Integer, primary_key=True)
    tuban_id = db.Column(db.Integer, db.ForeignKey('tubans.id'), nullable=False, comment='关联图斑ID')
    
    # 图片信息
    image_type = db.Column(db.String(20), nullable=False, comment='图片类型: photo(现场照片)/satellite(卫片)')
    filename = db.Column(db.String(255), nullable=False, comment='存储的文件名')
    original_name = db.Column(db.String(255), comment='原始文件名')
    description = db.Column(db.String(200), comment='图片说明')
    file_size = db.Column(db.Integer, comment='文件大小(字节)')
    
    # 系统字段
    uploaded_at = db.Column(db.DateTime, default=datetime.now, comment='上传时间')
    uploaded_by = db.Column(db.String(50), comment='上传人')
    is_deleted = db.Column(db.Integer, default=0)

    # 关联关系
    tuban = db.relationship('Tuban', backref=db.backref('images', lazy='dynamic'))

    def __repr__(self):
        return f'<TubanImage {self.id}: {self.image_type}>'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'tuban_id': self.tuban_id,
            'image_type': self.image_type,
            'filename': self.filename,
            'original_name': self.original_name,
            'description': self.description,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'uploaded_by': self.uploaded_by
        }
