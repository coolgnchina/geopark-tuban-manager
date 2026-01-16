from datetime import datetime, timedelta
import os
from app import create_app
from models import db
from models.tuban import Tuban
from models.dictionary import Dictionary
from models.rectify_record import RectifyRecord
from models.project import Project, ProjectDocument, ProjectTimeline
from models.user import User
from werkzeug.security import generate_password_hash


def init_dictionaries():
    """初始化字典数据"""
    dictionaries = [
        # 功能区
        {
            "dict_type": "func_zone",
            "dict_code": "level1",
            "dict_value": "一级保护区",
            "sort_order": 1,
        },
        {
            "dict_type": "func_zone",
            "dict_code": "level2",
            "dict_value": "二级保护区",
            "sort_order": 2,
        },
        {
            "dict_type": "func_zone",
            "dict_code": "level3",
            "dict_value": "三级保护区",
            "sort_order": 3,
        },
        {
            "dict_type": "func_zone",
            "dict_code": "tourism",
            "dict_value": "旅游服务区",
            "sort_order": 4,
        },
        {
            "dict_type": "func_zone",
            "dict_code": "resident",
            "dict_value": "居民保留区",
            "sort_order": 5,
        },
        {
            "dict_type": "func_zone",
            "dict_code": "ecology",
            "dict_value": "自然生态区",
            "sort_order": 6,
        },
        # 发现方式
        {
            "dict_type": "discover_method",
            "dict_code": "remote",
            "dict_value": "遥感监测",
            "sort_order": 1,
        },
        {
            "dict_type": "discover_method",
            "dict_code": "patrol",
            "dict_value": "日常巡查",
            "sort_order": 2,
        },
        {
            "dict_type": "discover_method",
            "dict_code": "report",
            "dict_value": "群众举报",
            "sort_order": 3,
        },
        {
            "dict_type": "discover_method",
            "dict_code": "assign",
            "dict_value": "上级交办",
            "sort_order": 4,
        },
        # 问题类型
        {
            "dict_type": "problem_type",
            "dict_code": "construction",
            "dict_value": "违规建设",
            "sort_order": 1,
        },
        {
            "dict_type": "problem_type",
            "dict_code": "mining",
            "dict_value": "采矿",
            "sort_order": 2,
        },
        {
            "dict_type": "problem_type",
            "dict_code": "farming",
            "dict_value": "开垦",
            "sort_order": 3,
        },
        {
            "dict_type": "problem_type",
            "dict_code": "pollution",
            "dict_value": "污染",
            "sort_order": 4,
        },
        # 影响程度
        {
            "dict_type": "impact_level",
            "dict_code": "serious",
            "dict_value": "严重",
            "sort_order": 1,
        },
        {
            "dict_type": "impact_level",
            "dict_code": "normal",
            "dict_value": "一般",
            "sort_order": 2,
        },
        {
            "dict_type": "impact_level",
            "dict_code": "slight",
            "dict_value": "轻微",
            "sort_order": 3,
        },
        # 整改进展
        {
            "dict_type": "rectify_status",
            "dict_code": "not_started",
            "dict_value": "未整改",
            "sort_order": 1,
        },
        {
            "dict_type": "rectify_status",
            "dict_code": "in_progress",
            "dict_value": "整改中",
            "sort_order": 2,
        },
        {
            "dict_type": "rectify_status",
            "dict_code": "completed",
            "dict_value": "已整改",
            "sort_order": 3,
        },
        # 处罚形式
        {
            "dict_type": "punish_type",
            "dict_code": "fine",
            "dict_value": "罚款",
            "sort_order": 1,
        },
        {
            "dict_type": "punish_type",
            "dict_code": "stop_work",
            "dict_value": "责令停工",
            "sort_order": 2,
        },
        {
            "dict_type": "punish_type",
            "dict_code": "detention",
            "dict_value": "行政拘留",
            "sort_order": 3,
        },
    ]

    for item in dictionaries:
        if not Dictionary.query.filter_by(
            dict_type=item["dict_type"], dict_code=item["dict_code"]
        ).first():
            dict_item = Dictionary(**item)
            db.session.add(dict_item)


def init_sample_data():
    """初始化示例数据"""
    # 检查是否已有数据
    if Tuban.query.first():
        return

    sample_tubans = [
        {
            "tuban_code": "TB001",
            "park_name": "张家界世界地质公园",
            "func_zone": "一级保护区",
            "facility_name": "违规建设观景台",
            "longitude": 110.4833,
            "latitude": 29.3167,
            "area": 500.00,
            "image_date": datetime(2023, 5, 15).date(),
            "build_unit": "某旅游开发公司",
            "build_time": datetime(2022, 8, 1).date(),
            "has_approval": "否",
            "discover_time": datetime(2023, 6, 1).date(),
            "discover_method": "遥感监测",
            "check_time": datetime(2023, 6, 10).date(),
            "check_person": "张三",
            "check_result": "经核查，该观景台为违规建设，破坏了地质公园的自然景观",
            "problem_type": "违规建设",
            "problem_desc": "在未取得任何审批手续的情况下，擅自在地质公园一级保护区内建设观景台",
            "impact_level": "严重",
            "is_illegal": "是",
            "violated_law": "《地质遗迹保护管理规定》第二十条",
            "rectify_measure": "立即拆除违规建筑，恢复原地貌",
            "rectify_deadline": datetime(2023, 12, 31).date(),
            "rectify_status": "整改中",
            "is_punished": "是",
            "punish_type": "罚款",
            "fine_amount": 50000.00,
            "data_source": "遥感监测台账",
            "is_patrol_point": "是",
            "responsible_dept": "地质公园管理处",
        },
        {
            "tuban_code": "TB002",
            "park_name": "嵩山世界地质公园",
            "func_zone": "二级保护区",
            "facility_name": "非法采矿点",
            "longitude": 112.9531,
            "latitude": 34.4864,
            "area": 1200.00,
            "image_date": datetime(2023, 7, 20).date(),
            "build_unit": "某矿业公司",
            "build_time": datetime(2023, 3, 1).date(),
            "has_approval": "否",
            "discover_time": datetime(2023, 8, 5).date(),
            "discover_method": "日常巡查",
            "check_time": datetime(2023, 8, 8).date(),
            "check_person": "李四",
            "check_result": "确认为非法采矿，破坏了地质公园地质遗迹",
            "problem_type": "采矿",
            "problem_desc": "在地质公园二级保护区内进行非法采矿活动，破坏了珍贵的地质剖面",
            "geo_heritage_type": "地层剖面",
            "impact_level": "严重",
            "is_illegal": "是",
            "violated_law": "《矿产资源法》第三条",
            "rectify_measure": "立即停止采矿，封堵矿口，恢复植被",
            "rectify_deadline": datetime(2023, 10, 31).date(),
            "rectify_status": "已整改",
            "rectify_verify_time": datetime(2023, 10, 25).date(),
            "verify_person": "王五",
            "is_closed": "是",
            "is_punished": "是",
            "punish_type": "罚款",
            "fine_amount": 200000.00,
            "punish_doc_no": "豫矿罚〔2023〕15号",
            "data_source": "巡查台账",
            "is_patrol_point": "是",
            "responsible_dept": "国土资源执法大队",
        },
        {
            "tuban_code": "TB003",
            "park_name": "五大连池世界地质公园",
            "func_zone": "三级保护区",
            "facility_name": "农业种植",
            "longitude": 126.1667,
            "latitude": 48.7167,
            "area": 8000.00,
            "image_date": datetime(2023, 9, 1).date(),
            "build_unit": "当地农户",
            "build_time": datetime(2020, 4, 1).date(),
            "has_approval": "否",
            "discover_time": datetime(2023, 9, 10).date(),
            "discover_method": "群众举报",
            "check_time": datetime(2023, 9, 15).date(),
            "check_person": "赵六",
            "check_result": "三级保护区内违规开垦种植农作物",
            "problem_type": "开垦",
            "problem_desc": "在地质公园三级保护区内开垦种植大豆，改变了原有地貌",
            "impact_level": "一般",
            "is_illegal": "是",
            "violated_law": "《自然保护区条例》第二十六条",
            "rectify_measure": "退耕还草，恢复原有植被",
            "rectify_deadline": datetime(2024, 5, 1).date(),
            "rectify_status": "未整改",
            "is_punished": "否",
            "data_source": "举报台账",
            "is_patrol_point": "否",
            "responsible_dept": "农业执法大队",
        },
    ]

    for data in sample_tubans:
        tuban = Tuban(**data)
        db.session.add(tuban)

    # 添加整改跟踪记录
    db.session.flush()

    # 为TB001添加跟踪记录
    record1 = RectifyRecord()
    record1.tuban_id = 1
    record1.status = "整改中"
    record1.content = "已制定整改方案，正在组织施工队伍"
    record1.operator = "张三"
    record1.record_time = datetime(2023, 7, 1)
    db.session.add(record1)

    # 为TB002添加跟踪记录
    record2 = RectifyRecord()
    record2.tuban_id = 2
    record2.status = "已整改"
    record2.content = "已完成矿口封堵和植被恢复，通过验收"
    record2.operator = "李四"
    record2.record_time = datetime(2023, 10, 20)
    db.session.add(record2)


def init_project_data():
    """初始化项目示例数据"""
    # 检查是否已有数据
    if Project.query.first():
        return

    # 创建示例项目
    sample_projects = [
        {
            "project_name": "某度假区开发项目",
            "project_type": "旅游开发",
            "legal_entity": "某某旅游开发有限公司",
            "contact_person": "张三",
            "contact_phone": "13800138000",
            "location": "地质公园一级保护区",
            "func_zone": "一级保护区",
            "area": 50.5,
            "approval_status": "立项审批中",
            "approval_stage": "规划审批",
            "project_status": "筹备",
            "start_date": datetime(2024, 1, 1).date(),
            "end_date": datetime(2026, 12, 31).date(),
            "description": "建设集住宿、餐饮、娱乐一体的度假区项目",
            "remark": "需要重点关注项目进展",
        },
        {
            "project_name": "某某矿山开采项目",
            "project_type": "采矿",
            "legal_entity": "某某矿业集团",
            "contact_person": "李四",
            "contact_phone": "13900139000",
            "location": "地质公园二级保护区",
            "func_zone": "二级保护区",
            "area": 200.0,
            "approval_status": "未审批",
            "approval_stage": "",
            "project_status": "停工",
            "start_date": datetime(2023, 6, 1).date(),
            "end_date": datetime(2025, 6, 1).date(),
            "description": "石灰石开采项目，已被责令停工整改",
            "remark": "存在地质安全隐患，需进行地质灾害评估",
        },
        {
            "project_name": "某某道路建设项目",
            "project_type": "基础设施建设",
            "legal_entity": "某某交通建设有限公司",
            "contact_person": "王五",
            "contact_phone": "13700137000",
            "location": "地质公园旅游服务区",
            "func_zone": "旅游服务区",
            "area": 15.0,
            "approval_status": "已审批",
            "approval_stage": "建设审批",
            "project_status": "在建",
            "start_date": datetime(2024, 3, 1).date(),
            "end_date": datetime(2025, 9, 30).date(),
            "description": "园区内部道路建设项目，改善交通条件",
            "remark": "施工期间需注意保护地质遗迹",
        },
        {
            "project_name": "某某景区配套设施项目",
            "project_type": "旅游服务设施",
            "legal_entity": "某某旅游服务公司",
            "contact_person": "赵六",
            "contact_phone": "13600136000",
            "location": "地质公园旅游服务区",
            "func_zone": "旅游服务区",
            "area": 8.5,
            "approval_status": "建设审批中",
            "approval_stage": "建设审批",
            "project_status": "筹备",
            "start_date": datetime(2024, 8, 1).date(),
            "end_date": datetime(2025, 12, 31).date(),
            "description": "建设游客服务中心、停车场等配套设施",
            "remark": "需协调环保部门意见",
        },
        {
            "project_name": "某某生态修复项目",
            "project_type": "生态保护",
            "legal_entity": "某某生态修复工程有限公司",
            "contact_person": "钱七",
            "contact_phone": "13500135000",
            "location": "地质公园自然生态区",
            "func_zone": "自然生态区",
            "area": 120.0,
            "approval_status": "已审批",
            "approval_stage": "规划审批",
            "project_status": "在建",
            "start_date": datetime(2024, 2, 15).date(),
            "end_date": datetime(2026, 2, 15).date(),
            "description": "矿山地质环境恢复治理项目",
            "remark": "重点生态修复项目，需定期监测",
        },
    ]

    for data in sample_projects:
        project = Project(**data)
        db.session.add(project)

    db.session.flush()

    # 为示例项目添加公文记录
    timeline1 = ProjectTimeline()
    timeline1.project_id = 1
    timeline1.event_type = "停工通知"
    timeline1.event_title = "关于暂停某度假区开发项目的通知"
    timeline1.event_date = datetime(2023, 12, 1).date()
    timeline1.content = "经查，你单位在地质公园核心区内进行开发建设活动，未取得相关审批手续，现通知你单位立即停止一切建设活动，接受调查处理。"
    timeline1.created_by = "admin"
    db.session.add(timeline1)

    timeline2 = ProjectTimeline()
    timeline2.project_id = 1
    timeline2.event_type = "征求意见"
    timeline2.event_title = "关于征求某度假区项目规划意见的函"
    timeline2.event_date = datetime(2023, 12, 15).date()
    timeline2.content = (
        "现就某度假区项目规划方案征求贵单位意见，请于7个工作日内反馈书面意见。"
    )
    timeline2.created_by = "admin"
    db.session.add(timeline2)


def ensure_admin_user():
    existing = User.query.filter_by(username="admin").first()
    if existing:
        return

    admin = User()
    admin.username = "admin"
    admin.role = "admin"
    admin.is_active = 1
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    admin.password_hash = generate_password_hash(admin_password)
    db.session.add(admin)
    db.session.commit()


def main():
    """初始化数据库"""
    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()

        # 初始化字典数据
        init_dictionaries()

        # 初始化示例图斑数据
        init_sample_data()

        # 初始化默认管理员
        ensure_admin_user()

        print("数据库初始化完成！")

        print(f"字典数据: {Dictionary.query.count()} 条")
        print(f"图斑数据: {Tuban.query.count()} 条")
        print(f"整改记录: {RectifyRecord.query.count()} 条")
        print(f"项目数据: {Project.query.count()} 条")
        print(f"公文记录: {ProjectTimeline.query.count()} 条")


if __name__ == "__main__":
    main()
