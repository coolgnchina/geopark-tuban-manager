from datetime import datetime, timedelta
from app import create_app, db
from models.tuban import Tuban
from models.dictionary import Dictionary
from models.rectify_record import RectifyRecord

def init_dictionaries():
    """初始化字典数据"""
    dictionaries = [
        # 功能区
        {'dict_type': 'func_zone', 'dict_code': 'core', 'dict_value': '核心区', 'sort_order': 1},
        {'dict_type': 'func_zone', 'dict_code': 'buffer', 'dict_value': '缓冲区', 'sort_order': 2},
        {'dict_type': 'func_zone', 'dict_code': 'experiment', 'dict_value': '实验区', 'sort_order': 3},

        # 发现方式
        {'dict_type': 'discover_method', 'dict_code': 'remote', 'dict_value': '遥感监测', 'sort_order': 1},
        {'dict_type': 'discover_method', 'dict_code': 'patrol', 'dict_value': '日常巡查', 'sort_order': 2},
        {'dict_type': 'discover_method', 'dict_code': 'report', 'dict_value': '群众举报', 'sort_order': 3},
        {'dict_type': 'discover_method', 'dict_code': 'assign', 'dict_value': '上级交办', 'sort_order': 4},

        # 问题类型
        {'dict_type': 'problem_type', 'dict_code': 'construction', 'dict_value': '违规建设', 'sort_order': 1},
        {'dict_type': 'problem_type', 'dict_code': 'mining', 'dict_value': '采矿', 'sort_order': 2},
        {'dict_type': 'problem_type', 'dict_code': 'farming', 'dict_value': '开垦', 'sort_order': 3},
        {'dict_type': 'problem_type', 'dict_code': 'pollution', 'dict_value': '污染', 'sort_order': 4},

        # 影响程度
        {'dict_type': 'impact_level', 'dict_code': 'serious', 'dict_value': '严重', 'sort_order': 1},
        {'dict_type': 'impact_level', 'dict_code': 'normal', 'dict_value': '一般', 'sort_order': 2},
        {'dict_type': 'impact_level', 'dict_code': 'slight', 'dict_value': '轻微', 'sort_order': 3},

        # 整改进展
        {'dict_type': 'rectify_status', 'dict_code': 'not_started', 'dict_value': '未整改', 'sort_order': 1},
        {'dict_type': 'rectify_status', 'dict_code': 'in_progress', 'dict_value': '整改中', 'sort_order': 2},
        {'dict_type': 'rectify_status', 'dict_code': 'completed', 'dict_value': '已整改', 'sort_order': 3},

        # 处罚形式
        {'dict_type': 'punish_type', 'dict_code': 'fine', 'dict_value': '罚款', 'sort_order': 1},
        {'dict_type': 'punish_type', 'dict_code': 'stop_work', 'dict_value': '责令停工', 'sort_order': 2},
        {'dict_type': 'punish_type', 'dict_code': 'detention', 'dict_value': '行政拘留', 'sort_order': 3},
    ]

    for item in dictionaries:
        if not Dictionary.query.filter_by(dict_type=item['dict_type'], dict_code=item['dict_code']).first():
            dict_item = Dictionary(**item)
            db.session.add(dict_item)

def init_sample_data():
    """初始化示例数据"""
    # 检查是否已有数据
    if Tuban.query.first():
        return

    sample_tubans = [
        {
            'tuban_code': 'TB001',
            'park_name': '张家界世界地质公园',
            'func_zone': '核心区',
            'facility_name': '违规建设观景台',
            'longitude': 110.4833,
            'latitude': 29.3167,
            'area': 500.00,
            'image_date': datetime(2023, 5, 15).date(),
            'build_unit': '某旅游开发公司',
            'build_time': datetime(2022, 8, 1).date(),
            'has_approval': '否',
            'discover_time': datetime(2023, 6, 1).date(),
            'discover_method': '遥感监测',
            'check_time': datetime(2023, 6, 10).date(),
            'check_person': '张三',
            'check_result': '经核查，该观景台为违规建设，破坏了地质公园的自然景观',
            'problem_type': '违规建设',
            'problem_desc': '在未取得任何审批手续的情况下，擅自在地质公园核心区内建设观景台',
            'impact_level': '严重',
            'is_illegal': '是',
            'violated_law': '《地质遗迹保护管理规定》第二十条',
            'rectify_measure': '立即拆除违规建筑，恢复原地貌',
            'rectify_deadline': datetime(2023, 12, 31).date(),
            'rectify_status': '整改中',
            'is_punished': '是',
            'punish_type': '罚款',
            'fine_amount': 50000.00,
            'data_source': '遥感监测台账',
            'is_patrol_point': '是',
            'responsible_dept': '地质公园管理处'
        },
        {
            'tuban_code': 'TB002',
            'park_name': '嵩山世界地质公园',
            'func_zone': '缓冲区',
            'facility_name': '非法采矿点',
            'longitude': 112.9531,
            'latitude': 34.4864,
            'area': 1200.00,
            'image_date': datetime(2023, 7, 20).date(),
            'build_unit': '某矿业公司',
            'build_time': datetime(2023, 3, 1).date(),
            'has_approval': '否',
            'discover_time': datetime(2023, 8, 5).date(),
            'discover_method': '日常巡查',
            'check_time': datetime(2023, 8, 8).date(),
            'check_person': '李四',
            'check_result': '确认为非法采矿，破坏了地质公园地质遗迹',
            'problem_type': '采矿',
            'problem_desc': '在地质公园缓冲区内进行非法采矿活动，破坏了珍贵的地质剖面',
            'geo_heritage_type': '地层剖面',
            'impact_level': '严重',
            'is_illegal': '是',
            'violated_law': '《矿产资源法》第三条',
            'rectify_measure': '立即停止采矿，封堵矿口，恢复植被',
            'rectify_deadline': datetime(2023, 10, 31).date(),
            'rectify_status': '已整改',
            'rectify_verify_time': datetime(2023, 10, 25).date(),
            'verify_person': '王五',
            'is_closed': '是',
            'is_punished': '是',
            'punish_type': '罚款',
            'fine_amount': 200000.00,
            'punish_doc_no': '豫矿罚〔2023〕15号',
            'data_source': '巡查台账',
            'is_patrol_point': '是',
            'responsible_dept': '国土资源执法大队'
        },
        {
            'tuban_code': 'TB003',
            'park_name': '五大连池世界地质公园',
            'func_zone': '实验区',
            'facility_name': '农业种植',
            'longitude': 126.1667,
            'latitude': 48.7167,
            'area': 8000.00,
            'image_date': datetime(2023, 9, 1).date(),
            'build_unit': '当地农户',
            'build_time': datetime(2020, 4, 1).date(),
            'has_approval': '否',
            'discover_time': datetime(2023, 9, 10).date(),
            'discover_method': '群众举报',
            'check_time': datetime(2023, 9, 15).date(),
            'check_person': '赵六',
            'check_result': '实验区内违规开垦种植农作物',
            'problem_type': '开垦',
            'problem_desc': '在地质公园实验区内开垦种植大豆，改变了原有地貌',
            'impact_level': '一般',
            'is_illegal': '是',
            'violated_law': '《自然保护区条例》第二十六条',
            'rectify_measure': '退耕还草，恢复原有植被',
            'rectify_deadline': datetime(2024, 5, 1).date(),
            'rectify_status': '未整改',
            'is_punished': '否',
            'data_source': '举报台账',
            'is_patrol_point': '否',
            'responsible_dept': '农业执法大队'
        }
    ]

    for data in sample_tubans:
        tuban = Tuban(**data)
        db.session.add(tuban)

    # 添加整改跟踪记录
    db.session.flush()

    # 为TB001添加跟踪记录
    record1 = RectifyRecord(
        tuban_id=1,
        status='整改中',
        content='已制定整改方案，正在组织施工队伍',
        operator='张三',
        record_time=datetime(2023, 7, 1)
    )
    db.session.add(record1)

    # 为TB002添加跟踪记录
    record2 = RectifyRecord(
        tuban_id=2,
        status='已整改',
        content='已完成矿口封堵和植被恢复，通过验收',
        operator='李四',
        record_time=datetime(2023, 10, 20)
    )
    db.session.add(record2)

def main():
    """初始化数据库"""
    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()

        # 初始化字典数据
        init_dictionaries()

        # 初始化示例数据
        init_sample_data()

        # 提交事务
        db.session.commit()

        print("数据库初始化完成！")
        print(f"字典数据: {Dictionary.query.count()} 条")
        print(f"图斑数据: {Tuban.query.count()} 条")
        print(f"整改记录: {RectifyRecord.query.count()} 条")

if __name__ == '__main__':
    main()