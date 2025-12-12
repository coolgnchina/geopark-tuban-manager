from datetime import datetime

def format_date(date_obj, format='%Y-%m-%d'):
    """格式化日期"""
    if not date_obj:
        return ''
    return date_obj.strftime(format)

def format_datetime(datetime_obj, format='%Y-%m-%d %H:%M:%S'):
    """格式化日期时间"""
    if not datetime_obj:
        return ''
    return datetime_obj.strftime(format)

def get_status_color(status):
    """获取状态对应的颜色"""
    colors = {
        '未整改': 'danger',
        '整改中': 'warning',
        '已整改': 'success',
        '是': 'success',
        '否': 'danger',
        '严重': 'danger',
        '一般': 'warning',
        '轻微': 'info'
    }
    return colors.get(status, 'secondary')

def parse_date(date_str):
    """解析日期字符串"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def get_dict_value(dict_type, dict_code):
    """根据字典类型和代码获取值"""
    from models.dictionary import Dictionary
    dict_item = Dictionary.query.filter_by(dict_type=dict_type, dict_code=dict_code).first()
    return dict_item.dict_value if dict_item else dict_code

def get_dict_options(dict_type):
    """获取字典选项列表"""
    from models.dictionary import Dictionary
    items = Dictionary.query.filter_by(dict_type=dict_type).order_by(Dictionary.sort_order).all()
    return [(item.dict_code, item.dict_value) for item in items]

def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def calculate_overdue_status(deadline, status):
    """计算是否超期"""
    if not deadline or status in ['已整改', '已销号']:
        return False
    from datetime import date
    return deadline < date.today()

def get_overdue_days(deadline):
    """获取超期天数"""
    if not deadline:
        return 0
    from datetime import date
    delta = date.today() - deadline
    return delta.days if delta.days > 0 else 0