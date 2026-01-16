from datetime import datetime
from . import db


# 项目-图斑关联表
project_tubans = db.Table(
    "project_tubans",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
    db.Column("tuban_id", db.Integer, db.ForeignKey("tubans.id"), primary_key=True),
    db.Column("added_at", db.DateTime, default=datetime.now, comment="关联时间"),
)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)

    # 基础信息
    project_name = db.Column(
        db.String(200), nullable=False, comment="项目名称", index=True
    )
    project_type = db.Column(db.String(100), comment="项目类型")

    legal_entity = db.Column(db.String(200), comment="法人机构/单位名称")
    contact_person = db.Column(db.String(100), comment="联系人")
    contact_phone = db.Column(db.String(50), comment="联系电话")

    # 位置信息
    location = db.Column(db.String(200), comment="所在位置")
    func_zone = db.Column(db.String(50), comment="所在功能区")
    longitude = db.Column(db.Numeric(10, 6), comment="经度")
    latitude = db.Column(db.Numeric(10, 6), comment="纬度")
    area = db.Column(db.Numeric(12, 2), comment="占地面积(㎡)")

    # 审批流程状态
    approval_status = db.Column(db.String(20), comment="审批状态", index=True)
    approval_stage = db.Column(db.String(50), comment="当前审批阶段")

    approval_start_date = db.Column(db.Date, comment="开始审批日期")
    approval_end_date = db.Column(db.Date, comment="审批完成日期")

    # 项目状态
    project_status = db.Column(db.String(20), comment="项目状态", index=True)
    start_date = db.Column(db.Date, comment="计划开工日期")

    actual_start_date = db.Column(db.Date, comment="实际开工日期")
    end_date = db.Column(db.Date, comment="计划完工日期")
    actual_end_date = db.Column(db.Date, comment="实际完工日期")

    # 管理信息
    description = db.Column(db.Text, comment="项目描述")
    remark = db.Column(db.Text, comment="备注")
    is_active = db.Column(db.Integer, default=1, comment="是否启用", index=True)

    # 系统字段
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    documents = db.relationship(
        "ProjectDocument",
        backref="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    timelines = db.relationship(
        "ProjectTimeline",
        backref="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    tubans = db.relationship(
        "Tuban", secondary="project_tubans", back_populates="projects"
    )

    def __repr__(self):
        return f"<Project {self.project_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "legal_entity": self.legal_entity,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "location": self.location,
            "func_zone": self.func_zone,
            "longitude": float(self.longitude) if self.longitude else None,
            "latitude": float(self.latitude) if self.latitude else None,
            "area": float(self.area) if self.area else None,
            "approval_status": self.approval_status,
            "approval_stage": self.approval_stage,
            "approval_start_date": self.approval_start_date.isoformat()
            if self.approval_start_date
            else None,
            "approval_end_date": self.approval_end_date.isoformat()
            if self.approval_end_date
            else None,
            "project_status": self.project_status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "actual_start_date": self.actual_start_date.isoformat()
            if self.actual_start_date
            else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "actual_end_date": self.actual_end_date.isoformat()
            if self.actual_end_date
            else None,
            "description": self.description,
            "remark": self.remark,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ProjectDocument(db.Model):
    __tablename__ = "project_documents"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    # 文档信息
    doc_type = db.Column(db.String(50), comment="文档类型")
    doc_title = db.Column(db.String(200), comment="文档标题")
    doc_file = db.Column(db.String(500), comment="文件路径")
    doc_date = db.Column(db.Date, comment="文档日期")
    description = db.Column(db.Text, comment="文档描述")

    # AI摘要
    ai_summary = db.Column(db.Text, comment="AI生成的内容摘要")
    ai_summary_status = db.Column(db.String(20), comment="AI摘要状态")

    # 系统字段
    created_at = db.Column(db.DateTime, default=datetime.now)
    uploaded_by = db.Column(db.String(100), comment="上传人")

    def __repr__(self):
        return f"<ProjectDocument {self.doc_title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "doc_type": self.doc_type,
            "doc_title": self.doc_title,
            "doc_file": self.doc_file,
            "doc_date": self.doc_date.isoformat() if self.doc_date else None,
            "description": self.description,
            "ai_summary": self.ai_summary,
            "ai_summary_status": self.ai_summary_status,
            "created_at": self.created_at.isoformat(),
            "uploaded_by": self.uploaded_by,
        }


class ProjectTimeline(db.Model):
    __tablename__ = "project_timelines"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    # 事件信息
    event_type = db.Column(db.String(50), comment="事件类型")
    event_title = db.Column(db.String(200), comment="事件标题")
    event_date = db.Column(db.Date, comment="事件日期")
    opposite_party = db.Column(db.String(200), comment="对方单位")

    # 附件（JSON格式，存储多个附件路径）
    attachments = db.Column(db.Text, comment="附件路径列表(JSON)")

    # AI摘要
    ai_summary = db.Column(db.Text, comment="AI生成的内容摘要")
    ai_summary_status = db.Column(db.String(20), comment="AI摘要状态")

    # 详细内容
    content = db.Column(db.Text, comment="详细内容")

    # 系统字段
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.String(100), comment="记录人")

    def __repr__(self):
        return f"<ProjectTimeline {self.event_title}>"

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "project_id": self.project_id,
            "event_type": self.event_type,
            "event_title": self.event_title,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "opposite_party": self.opposite_party,
            "attachments": json.loads(self.attachments) if self.attachments else [],
            "ai_summary": self.ai_summary,
            "ai_summary_status": self.ai_summary_status,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
        }
