from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models import db
from models.event import Event
from models.tuban import Tuban
from models.tuban_event import tuban_events
from utils.helpers import parse_date


event_bp = Blueprint("event", __name__)


@event_bp.route("/events")
def list():
    """事件列表"""
    # 获取查询参数
    search_keyword = request.args.get("search", "", type=str)
    event_type = request.args.get("event_type", "", type=str)

    # 构建查询
    query = Event.query.filter_by(is_active=1)

    if search_keyword:
        query = query.filter(Event.event_name.contains(search_keyword))
    if event_type:
        query = query.filter_by(event_type=event_type)

    events = query.order_by(Event.issue_date.desc()).all()

    # 事件类型统计
    event_types = ["卫片下发", "专项督查", "日常巡查", "群众举报", "其他"]

    return render_template(
        "event_list.html",
        events=events,
        search_keyword=search_keyword,
        event_type=event_type,
        event_types=event_types,
    )


@event_bp.route("/events/add", methods=["GET", "POST"])
def add():
    """添加事件"""
    if request.method == "POST":
        try:
            event = Event()
            event.event_name = request.form.get("event_name")
            event.event_type = request.form.get("event_type")
            event.issue_date = parse_date(request.form.get("issue_date"))
            event.description = request.form.get("description")

            db.session.add(event)
            db.session.commit()

            flash("事件添加成功！", "success")
            return redirect(url_for("event.list"))

        except Exception as e:
            db.session.rollback()
            flash(f"添加失败：{str(e)}", "error")

    event_types = ["卫片下发", "专项督查", "日常巡查", "群众举报", "其他"]
    return render_template("event_form.html", action="add", event_types=event_types)


@event_bp.route("/events/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    """编辑事件"""
    event = Event.query.get_or_404(id)

    if request.method == "POST":
        try:
            event.event_name = request.form.get("event_name")
            event.event_type = request.form.get("event_type")
            event.issue_date = parse_date(request.form.get("issue_date"))
            event.description = request.form.get("description")

            db.session.commit()

            flash("事件更新成功！", "success")
            return redirect(url_for("event.list"))

        except Exception as e:
            db.session.rollback()
            flash(f"更新失败：{str(e)}", "error")

    event_types = ["卫片下发", "专项督查", "日常巡查", "群众举报", "其他"]
    return render_template(
        "event_form.html", action="edit", event=event, event_types=event_types
    )


@event_bp.route("/events/delete/<int:id>", methods=["POST"])
def delete(id):
    """删除事件（软删除）"""
    event = Event.query.get_or_404(id)

    try:
        event.is_active = 0
        db.session.commit()
        flash("事件已删除！", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"删除失败：{str(e)}", "error")

    return redirect(url_for("event.list"))


@event_bp.route("/events/<int:id>")
def detail(id):
    """事件详情 - 查看关联的图斑"""
    event = Event.query.get_or_404(id)

    # 获取关联的图斑
    tubans = (
        Tuban.query.join(tuban_events)
        .filter(tuban_events.c.event_id == id, Tuban.is_deleted == 0)
        .all()
    )

    return render_template("event_detail.html", event=event, tubans=tubans)


@event_bp.route("/events/<int:id>/tubans", methods=["GET"])
def tubans_by_event(id):
    """获取事件关联的图斑列表（JSON）"""
    event = Event.query.get_or_404(id)

    tubans = (
        Tuban.query.join(tuban_events)
        .filter(tuban_events.c.event_id == id, Tuban.is_deleted == 0)
        .all()
    )

    return jsonify(
        {
            "success": True,
            "event": event.to_dict(),
            "tubans": [t.to_dict() for t in tubans],
            "count": len(tubans),
        }
    )


@event_bp.route("/events/api/list")
def api_list():
    """获取事件列表（JSON，供下拉选择用）"""
    events = Event.query.filter_by(is_active=1).order_by(Event.issue_date.desc()).all()
    return jsonify({"success": True, "events": [e.to_dict() for e in events]})
