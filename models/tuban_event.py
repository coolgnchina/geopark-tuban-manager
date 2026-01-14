from datetime import datetime
from . import db

# 图斑-事件关联表
tuban_events = db.Table(
    "tuban_events",
    db.Column("tuban_id", db.Integer, db.ForeignKey("tubans.id"), primary_key=True),
    db.Column("event_id", db.Integer, db.ForeignKey("events.id"), primary_key=True),
    db.Column("added_at", db.DateTime, default=datetime.now, comment="关联时间"),
)
