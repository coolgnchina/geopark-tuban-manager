from datetime import datetime
from . import db

class Tuban(db.Model):
    __tablename__ = 'tubans'

    id = db.Column(db.Integer, primary_key=True)

    # 基础信息
    tuban_code = db.Column(db.String(50), nullable=False, unique=True, comment='图斑编号')
    park_name = db.Column(db.String(100), nullable=False, comment='所属地质公园名称')
    func_zone = db.Column(db.String(50), comment='所在功能区')
    facility_name = db.Column(db.String(200), comment='活动/设施名称')
    longitude = db.Column(db.Numeric(10, 6), comment='经度')
    latitude = db.Column(db.Numeric(10, 6), comment='纬度')
    area = db.Column(db.Numeric(12, 2), comment='占地面积')
    image_date = db.Column(db.Date, comment='影像时相')

    # 建设主体信息
    build_unit = db.Column(db.String(200), comment='建设单位')
    build_time = db.Column(db.Date, comment='建设时间')
    has_approval = db.Column(db.String(10), comment='是否有审批手续')
    approval_no = db.Column(db.String(100), comment='审批文号')

    # 发现与核查信息
    discover_time = db.Column(db.Date, comment='发现时间')
    discover_method = db.Column(db.String(50), comment='发现方式')
    check_time = db.Column(db.Date, comment='现场核查时间')
    check_person = db.Column(db.String(50), comment='核查人员')
    check_result = db.Column(db.Text, comment='核查结论')

    # 问题与违法信息
    problem_type = db.Column(db.String(50), comment='问题类型')
    problem_desc = db.Column(db.Text, comment='问题描述')
    geo_heritage_type = db.Column(db.String(100), comment='涉及地质遗迹类型')
    impact_level = db.Column(db.String(20), comment='影响程度')
    is_superior_focus = db.Column(db.String(10), comment='是否上级重点关注')
    is_illegal = db.Column(db.String(20), comment='是否违法违规')
    violated_law = db.Column(db.Text, comment='违反法规条款')

    # 整改信息
    rectify_measure = db.Column(db.Text, comment='整改措施')
    rectify_deadline = db.Column(db.Date, comment='整改时限')
    rectify_status = db.Column(db.String(20), comment='整改进展')
    rectify_verify_time = db.Column(db.Date, comment='整改验收时间')
    verify_person = db.Column(db.String(50), comment='验收人员')
    is_closed = db.Column(db.String(10), comment='是否销号')

    # 处罚信息
    is_punished = db.Column(db.String(10), comment='是否处罚')
    punish_type = db.Column(db.String(100), comment='处罚形式')
    fine_amount = db.Column(db.Numeric(10, 2), comment='罚款金额')
    punish_doc_no = db.Column(db.String(100), comment='处罚文书编号')

    # 管理信息
    data_source = db.Column(db.String(100), comment='台账来源')
    is_patrol_point = db.Column(db.String(10), comment='是否为巡查点')
    responsible_dept = db.Column(db.String(100), comment='责任部门/责任人')
    attachments = db.Column(db.Text, comment='附件材料路径')
    remark = db.Column(db.Text, comment='备注')

    # 系统字段
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_deleted = db.Column(db.Integer, default=0)

    # 关联关系
    rectify_records = db.relationship('RectifyRecord', backref='tuban', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Tuban {self.tuban_code}>'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'tuban_code': self.tuban_code,
            'park_name': self.park_name,
            'func_zone': self.func_zone,
            'facility_name': self.facility_name,
            'longitude': float(self.longitude) if self.longitude else None,
            'latitude': float(self.latitude) if self.latitude else None,
            'area': float(self.area) if self.area else None,
            'image_date': self.image_date.isoformat() if self.image_date else None,
            'build_unit': self.build_unit,
            'build_time': self.build_time.isoformat() if self.build_time else None,
            'has_approval': self.has_approval,
            'approval_no': self.approval_no,
            'discover_time': self.discover_time.isoformat() if self.discover_time else None,
            'discover_method': self.discover_method,
            'check_time': self.check_time.isoformat() if self.check_time else None,
            'check_person': self.check_person,
            'check_result': self.check_result,
            'problem_type': self.problem_type,
            'problem_desc': self.problem_desc,
            'geo_heritage_type': self.geo_heritage_type,
            'impact_level': self.impact_level,
            'is_superior_focus': self.is_superior_focus,
            'is_illegal': self.is_illegal,
            'violated_law': self.violated_law,
            'rectify_measure': self.rectify_measure,
            'rectify_deadline': self.rectify_deadline.isoformat() if self.rectify_deadline else None,
            'rectify_status': self.rectify_status,
            'rectify_verify_time': self.rectify_verify_time.isoformat() if self.rectify_verify_time else None,
            'verify_person': self.verify_person,
            'is_closed': self.is_closed,
            'is_punished': self.is_punished,
            'punish_type': self.punish_type,
            'fine_amount': float(self.fine_amount) if self.fine_amount else None,
            'punish_doc_no': self.punish_doc_no,
            'data_source': self.data_source,
            'is_patrol_point': self.is_patrol_point,
            'responsible_dept': self.responsible_dept,
            'attachments': self.attachments,
            'remark': self.remark,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }