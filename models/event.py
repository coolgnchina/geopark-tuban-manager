from datetime import datetime
from . import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False, comment="事件名称")
    event_type = db.Column(
        db.String(50), comment="事件类型：卫片下发/专项督查/日常巡查/群众举报/其他"
    )
    issue_date = db.Column(db.Date, comment="下发/发现日期")
    description = db.Column(db.Text, comment="事件描述")
    is_active = db.Column(db.Integer, default=1, comment="是否启用")

    # 系统字段
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    tubans = db.relationship("Tuban", secondary="tuban_events", back_populates="events")

    def __repr__(self):
        return f"<Event {self.event_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "event_name": self.event_name,
            "event_type": self.event_type,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
