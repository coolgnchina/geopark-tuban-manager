"""
地图展示路由
提供图斑地图可视化功能，集成天地图
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from models import db
from models.tuban import Tuban
from models.event import Event
from models.tuban_event import tuban_events
from utils.helpers import cache_get, cache_set

map_bp = Blueprint("map", __name__)


@map_bp.route("/")
def index():
    """地图主页面"""
    # 获取筛选选项数据
    # 功能区列表
    func_zones = (
        db.session.query(Tuban.func_zone)
        .filter(Tuban.is_deleted == 0, Tuban.func_zone.isnot(None))
        .distinct()
        .all()
    )
    func_zones = [z[0] for z in func_zones if z[0]]

    # 问题类型列表
    problem_types = (
        db.session.query(Tuban.problem_type)
        .filter(Tuban.is_deleted == 0, Tuban.problem_type.isnot(None))
        .distinct()
        .all()
    )
    problem_types = [p[0] for p in problem_types if p[0]]

    # 整改状态列表
    rectify_statuses = ["未整改", "整改中", "已整改"]

    # 事件列表
    events = (
        db.session.query(Event)
        .filter_by(is_active=1)
        .order_by(Event.issue_date.desc())
        .all()
    )

    return render_template(
        "map.html",
        func_zones=func_zones,
        problem_types=problem_types,
        rectify_statuses=rectify_statuses,
        events=events,
    )


@map_bp.route("/api/tubans")
def api_tubans():
    """
    获取图斑坐标数据API
    支持筛选参数：
    - func_zone: 功能区
    - problem_type: 问题类型
    - rectify_status: 整改状态
    - event_id: 事件ID
    """
    func_zone = request.args.get("func_zone")
    problem_type = request.args.get("problem_type")
    rectify_status = request.args.get("rectify_status")
    event_id = request.args.get("event_id")

    cache_key = "map:tubans:{}:{}:{}:{}".format(
        func_zone or "",
        problem_type or "",
        rectify_status or "",
        event_id or "",
    )
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    # 构建查询
    query = Tuban.query.filter(
        Tuban.is_deleted == 0, Tuban.longitude.isnot(None), Tuban.latitude.isnot(None)
    )

    # 应用筛选条件
    if func_zone:
        query = query.filter(Tuban.func_zone == func_zone)

    if problem_type:
        query = query.filter(Tuban.problem_type == problem_type)

    if rectify_status:
        query = query.filter(Tuban.rectify_status == rectify_status)

    # 事件筛选
    if event_id:
        query = query.join(tuban_events).filter(
            tuban_events.c.event_id == int(event_id)
        )

    # 执行查询
    tubans = query.all()

    # 转换为GeoJSON格式
    features = []
    for tuban in tubans:
        # 根据整改状态确定颜色
        if tuban.is_closed == "是":
            color = "#28a745"  # 绿色 - 已销号
            status_text = "已销号"
        elif tuban.rectify_status == "整改中":
            color = "#ffc107"  # 黄色 - 整改中
            status_text = "整改中"
        elif tuban.rectify_status == "已整改":
            color = "#17a2b8"  # 蓝色 - 已整改待验收
            status_text = "已整改"
        else:
            color = "#dc3545"  # 红色 - 未整改
            status_text = "未整改"

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(tuban.longitude), float(tuban.latitude)],
            },
            "properties": {
                "id": tuban.id,
                "tuban_code": tuban.tuban_code,
                "park_name": tuban.park_name or "",
                "func_zone": tuban.func_zone or "",
                "facility_name": tuban.facility_name or "",
                "problem_type": tuban.problem_type or "",
                "problem_desc": tuban.problem_desc or "",
                "rectify_status": status_text,
                "is_closed": tuban.is_closed or "否",
                "area": float(tuban.area) if tuban.area else None,
                "color": color,
                "rectify_deadline": tuban.rectify_deadline.isoformat()
                if tuban.rectify_deadline
                else None,
            },
        }
        features.append(feature)

    payload = {
        "type": "FeatureCollection",
        "features": features,
        "total": len(features),
    }
    cache_set(cache_key, payload, current_app.config["MAP_CACHE_TTL"])
    return jsonify(payload)


@map_bp.route("/api/stats")
def api_stats():
    """获取地图统计数据"""
    cache_key = "map:stats"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    # 统计各状态数量
    total = Tuban.query.filter(
        Tuban.is_deleted == 0, Tuban.longitude.isnot(None), Tuban.latitude.isnot(None)
    ).count()

    pending = Tuban.query.filter(
        Tuban.is_deleted == 0,
        Tuban.longitude.isnot(None),
        Tuban.rectify_status == "未整改",
    ).count()

    in_progress = Tuban.query.filter(
        Tuban.is_deleted == 0,
        Tuban.longitude.isnot(None),
        Tuban.rectify_status == "整改中",
    ).count()

    closed = Tuban.query.filter(
        Tuban.is_deleted == 0, Tuban.longitude.isnot(None), Tuban.is_closed == "是"
    ).count()

    payload = {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "closed": closed,
    }
    cache_set(cache_key, payload, current_app.config["MAP_CACHE_TTL"])
    return jsonify(payload)
