from datetime import datetime
from . import db

class RectifyRecord(db.Model):
    __tablename__ = 'rectify_records'

    id = db.Column(db.Integer, primary_key=True)
    tuban_id = db.Column(db.Integer, db.ForeignKey('tubans.id'), nullable=False, comment='关联图斑ID')
    record_time = db.Column(db.DateTime, default=datetime.now, comment='记录时间')
    status = db.Column(db.String(20), comment='状态')
    content = db.Column(db.Text, comment='跟踪内容')
    operator = db.Column(db.String(50), comment='操作人')

    def __repr__(self):
        return f'<RectifyRecord {self.id}:{self.status}>'