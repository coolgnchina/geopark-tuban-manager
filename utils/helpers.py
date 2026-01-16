from datetime import datetime
from pathlib import Path
import time

from werkzeug.utils import secure_filename


def format_date(date_obj, format="%Y-%m-%d"):
    """格式化日期"""
    if not date_obj:
        return ""
    return date_obj.strftime(format)


def format_datetime(datetime_obj, format="%Y-%m-%d %H:%M:%S"):
    """格式化日期时间"""
    if not datetime_obj:
        return ""
    return datetime_obj.strftime(format)


def get_status_color(status):
    """获取状态对应的颜色"""
    colors = {
        "未整改": "danger",
        "整改中": "warning",
        "已整改": "success",
        "是": "success",
        "否": "danger",
        "严重": "danger",
        "一般": "warning",
        "轻微": "info",
    }
    return colors.get(status, "secondary")


def parse_date(date_str):
    """解析日期字符串"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def get_dict_value(dict_type, dict_code):
    """根据字典类型和代码获取值"""
    from models.dictionary import Dictionary

    dict_item = Dictionary.query.filter_by(
        dict_type=dict_type, dict_code=dict_code
    ).first()
    return dict_item.dict_value if dict_item else dict_code


def get_dict_options(dict_type):
    """获取字典选项列表"""
    from models.dictionary import Dictionary

    items = (
        Dictionary.query.filter_by(dict_type=dict_type)
        .order_by(Dictionary.sort_order)
        .all()
    )
    return [(item.dict_code, item.dict_value) for item in items]


def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def sanitize_filename(filename: str) -> str | None:
    """生成安全文件名，支持中文"""
    if not filename:
        return None

    # 导入在函数内部避免循环导入
    import re
    from werkzeug.utils import secure_filename

    # 分离文件名和扩展名
    name_part = filename.rsplit(".", 1)[0]
    ext_part = filename.rsplit(".", 1)[1] if "." in filename else ""

    # 处理扩展名（保持原始扩展名）
    ext = ext_part.lower() if ext_part else ""

    # 处理文件名主体：先尝试 werkzeug 的 secure_filename
    # 如果结果为空（说明是纯中文文件名），则自定义处理
    safe_name_part = secure_filename(name_part)

    if not safe_name_part:
        # 自定义处理：保留中文，移除危险字符
        # 只保留中文、字母、数字、空格、点、连字符、下划线
        safe_name_part = re.sub(r"[^\w\u4e00-\u9fff\s\-_.]", "", name_part)
        safe_name_part = safe_name_part.strip()

    if not safe_name_part:
        return None

    # 重新组合文件名
    if ext:
        return f"{safe_name_part}.{ext}"
    return safe_name_part


def safe_join_upload(base_dir: str, relative_path: str) -> Path | None:
    """确保相对路径在上传目录内"""
    if not relative_path:
        return None
    base = Path(base_dir).resolve()
    candidate = (base / relative_path).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    return candidate


def calculate_overdue_status(deadline, status):
    """计算是否超期"""
    if not deadline or status in ["已整改", "已销号"]:
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


_cache_store = {}


def cache_get(key: str):
    """读取缓存（过期返回None）"""
    cached = _cache_store.get(key)
    if not cached:
        return None
    value, expires_at = cached
    if expires_at and expires_at < time.time():
        _cache_store.pop(key, None)
        return None
    return value


def cache_set(key: str, value, ttl_seconds: int):
    """写入缓存（秒级TTL）"""
    expires_at = time.time() + ttl_seconds if ttl_seconds else None
    _cache_store[key] = (value, expires_at)
