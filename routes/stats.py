from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime, timedelta
from models import db
from models.tuban import Tuban
from models.rectify_record import RectifyRecord
from utils.helpers import cache_get, cache_set

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/")
def index():
    """统计分析页面"""
    return render_template("stats.html")


@stats_bp.route("/api/overview")
def api_overview():
    """概览数据API"""
    cache_key = "stats:overview"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    # 基础统计
    total_count = Tuban.query.filter_by(is_deleted=0).count()
    pending_count = Tuban.query.filter_by(is_deleted=0, rectify_status="未整改").count()
    in_progress_count = Tuban.query.filter_by(
        is_deleted=0, rectify_status="整改中"
    ).count()
    closed_count = Tuban.query.filter_by(is_deleted=0, is_closed="是").count()

    # 超期统计
    overdue_count = Tuban.query.filter(
        Tuban.is_deleted == 0,
        Tuban.rectify_deadline < datetime.now().date(),
        Tuban.rectify_status.in_(["未整改", "整改中"]),
    ).count()

    payload = {
        "total_count": total_count,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "closed_count": closed_count,
        "overdue_count": overdue_count,
    }
    cache_set(cache_key, payload, current_app.config["STATS_CACHE_TTL"])
    return jsonify(payload)


@stats_bp.route("/api/problem_types")
def api_problem_types():
    """问题类型统计API"""
    cache_key = "stats:problem_types"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    stats = (
        db.session.query(Tuban.problem_type, db.func.count(Tuban.id).label("count"))
        .filter_by(is_deleted=0)
        .group_by(Tuban.problem_type)
        .all()
    )

    payload = [
        {"name": stat.problem_type or "未分类", "value": stat.count} for stat in stats
    ]
    cache_set(cache_key, payload, current_app.config["STATS_CACHE_TTL"])
    return jsonify(payload)


@stats_bp.route("/api/func_zones")
def api_func_zones():
    """功能区统计API"""
    cache_key = "stats:func_zones"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    stats = (
        db.session.query(Tuban.func_zone, db.func.count(Tuban.id).label("count"))
        .filter_by(is_deleted=0)
        .group_by(Tuban.func_zone)
        .all()
    )

    payload = [
        {"name": stat.func_zone or "未分类", "value": stat.count} for stat in stats
    ]
    cache_set(cache_key, payload, current_app.config["STATS_CACHE_TTL"])
    return jsonify(payload)


@stats_bp.route("/api/rectify_progress")
def api_rectify_progress():
    """整改进展统计API"""
    cache_key = "stats:rectify_progress"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    stats = (
        db.session.query(Tuban.rectify_status, db.func.count(Tuban.id).label("count"))
        .filter_by(is_deleted=0)
        .group_by(Tuban.rectify_status)
        .all()
    )

    payload = [
        {"name": stat.rectify_status or "未分类", "value": stat.count} for stat in stats
    ]
    cache_set(cache_key, payload, current_app.config["STATS_CACHE_TTL"])
    return jsonify(payload)


@stats_bp.route("/api/monthly_trend")
def api_monthly_trend():
    """月度趋势统计API"""
    cache_key = "stats:monthly_trend"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    # 获取最近12个月的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # 按月统计发现的问题
    monthly_stats = (
        db.session.query(
            db.func.strftime("%Y-%m", Tuban.discover_time).label("month"),
            db.func.count(Tuban.id).label("count"),
        )
        .filter(
            Tuban.is_deleted == 0,
            Tuban.discover_time >= start_date.date(),
            Tuban.discover_time <= end_date.date(),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    # 按月统计整改完成
    monthly_closed = (
        db.session.query(
            db.func.strftime("%Y-%m", Tuban.rectify_verify_time).label("month"),
            db.func.count(Tuban.id).label("count"),
        )
        .filter(
            Tuban.is_deleted == 0,
            Tuban.rectify_verify_time >= start_date.date(),
            Tuban.rectify_verify_time <= end_date.date(),
            Tuban.is_closed == "是",
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    # 构建完整的12个月数据
    months = []
    discovered = []
    closed = []

    current_month = start_date.replace(day=1)
    while current_month <= end_date:
        month_str = current_month.strftime("%Y-%m")
        months.append(month_str)

        # 查找发现数量
        found = next((s.count for s in monthly_stats if s.month == month_str), 0)
        discovered.append(found)

        # 查找完成数量
        completed = next((s.count for s in monthly_closed if s.month == month_str), 0)
        closed.append(completed)

        current_month = (current_month.replace(day=28) + timedelta(days=4)).replace(
            day=1
        )

    payload = {"months": months, "discovered": discovered, "closed": closed}
    cache_set(cache_key, payload, current_app.config["STATS_CACHE_TTL"])
    return jsonify(payload)


@stats_bp.route("/api/park_ranking")
def api_park_ranking():
    """地质公园排名统计API"""
    cache_key = "stats:park_ranking"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    stats = (
        db.session.query(
            Tuban.park_name,
            db.func.count(Tuban.id).label("total_count"),
            db.func.sum(db.case((Tuban.rectify_status == "未整改", 1), else_=0)).label(
                "pending_count"
            ),
            db.func.sum(db.case((Tuban.rectify_status == "整改中", 1), else_=0)).label(
                "in_progress_count"
            ),
            db.func.sum(db.case((Tuban.is_closed == "是", 1), else_=0)).label(
                "closed_count"
            ),
        )
        .filter_by(is_deleted=0)
        .group_by(Tuban.park_name)
        .all()
    )

    payload = [
        {
            "park_name": stat.park_name,
            "total_count": stat.total_count,
            "pending_count": stat.pending_count,
            "in_progress_count": stat.in_progress_count,
            "closed_count": stat.closed_count,
        }
        for stat in stats
    ]
    cache_set(cache_key, payload, current_app.config["STATS_CACHE_TTL"])
    return jsonify(payload)


@stats_bp.route("/api/overdue_list")
def api_overdue_list():
    """超期图斑列表API"""
    cache_key = "stats:overdue_list"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    overdue_tubans = (
        Tuban.query.filter(
            Tuban.is_deleted == 0,
            Tuban.rectify_deadline < datetime.now().date(),
            Tuban.rectify_status.in_(["未整改", "整改中"]),
        )
        .order_by(Tuban.rectify_deadline)
        .all()
    )

    payload = [
        {
            "id": tuban.id,
            "tuban_code": tuban.tuban_code,
            "park_name": tuban.park_name,
            "facility_name": tuban.facility_name,
            "problem_type": tuban.problem_type,
            "rectify_deadline": tuban.rectify_deadline.isoformat()
            if tuban.rectify_deadline
            else None,
            "overdue_days": (datetime.now().date() - tuban.rectify_deadline).days
            if tuban.rectify_deadline
            else 0,
        }
        for tuban in overdue_tubans
    ]
    cache_set(cache_key, payload, current_app.config["STATS_CACHE_TTL"])
    return jsonify(payload)


@stats_bp.route("/api/impact_analysis")
def api_impact_analysis():
    """影响程度分析API"""
    cache_key = "stats:impact_analysis"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    stats = (
        db.session.query(Tuban.impact_level, db.func.count(Tuban.id).label("count"))
        .filter_by(is_deleted=0)
        .group_by(Tuban.impact_level)
        .all()
    )

    payload = [
        {"impact_level": stat.impact_level or "未分类", "count": stat.count}
        for stat in stats
    ]
    cache_set(cache_key, payload, current_app.config["STATS_CACHE_TTL"])
    return jsonify(payload)
