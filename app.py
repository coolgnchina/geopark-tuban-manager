from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Blueprint,
    current_app,
    url_for,
    flash,
    session,
    redirect,
    abort,
    send_file,
)
from datetime import datetime
from typing import cast
from config import Config
from models import db
from models.tuban import Tuban
from models.dictionary import Dictionary
from models.rectify_record import RectifyRecord
from models.event import Event
from models.tuban_event import tuban_events
from models.user import User
from routes.tuban import tuban_bp
from routes.stats import stats_bp
from routes.system import system_bp
from routes.map import map_bp
from routes.events import event_bp
from routes.project import project_bp
from utils.helpers import (
    format_date,
    format_datetime,
    get_status_color,
    safe_join_upload,
)
import os
import secrets
from test_icons import test_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(tuban_bp, url_prefix="/tuban")
    app.register_blueprint(stats_bp, url_prefix="/stats")
    app.register_blueprint(system_bp, url_prefix="/system")
    app.register_blueprint(map_bp, url_prefix="/map")
    app.register_blueprint(event_bp, url_prefix="/")
    app.register_blueprint(project_bp, url_prefix="/")
    app.register_blueprint(test_bp, url_prefix="/test")

    # 添加模板全局函数
    template_globals = cast(dict[str, object], app.jinja_env.globals)
    template_globals["format_date"] = format_date
    template_globals["format_datetime"] = format_datetime
    template_globals["get_status_color"] = get_status_color

    def get_csrf_token():
        token = session.get("_csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return token

    template_globals["csrf_token"] = get_csrf_token

    # 添加获取当前日期的函数供模板使用
    def get_current_date():
        return datetime.now().date()

    # 添加JSON解析过滤器
    @app.template_filter("json_parse")
    def json_parse_filter(s):
        import json

        try:
            if s and s.startswith("["):
                return json.loads(s)
            return []
        except:
            return []

    template_globals["get_current_date"] = get_current_date

    # 创建上传目录
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.route("/")
    def index():
        """首页仪表盘"""
        # 基础统计
        total_count = Tuban.query.filter_by(is_deleted=0).count()
        pending_count = Tuban.query.filter_by(
            is_deleted=0, rectify_status="未整改"
        ).count()
        in_progress_count = Tuban.query.filter_by(
            is_deleted=0, rectify_status="整改中"
        ).count()
        closed_count = Tuban.query.filter_by(is_deleted=0, is_closed="是").count()

        # 问题类型统计
        problem_stats = (
            db.session.query(Tuban.problem_type, db.func.count(Tuban.id).label("count"))
            .filter_by(is_deleted=0)
            .group_by(Tuban.problem_type)
            .all()
        )

        # 功能区统计
        zone_stats = (
            db.session.query(Tuban.func_zone, db.func.count(Tuban.id).label("count"))
            .filter_by(is_deleted=0)
            .group_by(Tuban.func_zone)
            .all()
        )

        # 超期预警（整改期限已过但未完成）
        overdue_count = Tuban.query.filter(
            Tuban.is_deleted == 0,
            Tuban.rectify_deadline < datetime.now().date(),
            Tuban.rectify_status.in_(["未整改", "整改中"]),
        ).count()

        # 本周待办（整改截止在本周内）
        from datetime import timedelta

        week_later = datetime.now().date() + timedelta(days=7)
        week_todo = Tuban.query.filter(
            Tuban.is_deleted == 0,
            Tuban.rectify_deadline <= week_later,
            Tuban.rectify_deadline >= datetime.now().date(),
            Tuban.rectify_status.in_(["未整改", "整改中"]),
        ).count()

        return render_template(
            "index.html",
            total_count=total_count,
            pending_count=pending_count,
            in_progress_count=in_progress_count,
            closed_count=closed_count,
            problem_stats=problem_stats,
            zone_stats=zone_stats,
            overdue_count=overdue_count,
            week_todo=week_todo,
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """登录页面（简化版）"""
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if not username or not password:
                flash("请输入用户名和密码", "error")
                return render_template("login.html")

            user = User.query.filter_by(username=username, is_active=1).first()
            if user and user.check_password(password):
                session["user_id"] = user.id
                session["username"] = user.username
                session["role"] = user.role
                return redirect(url_for("index"))

            flash("用户名或密码错误", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        """退出登录"""
        session.clear()
        return redirect(url_for("login"))

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        safe_path = safe_join_upload(app.config["UPLOAD_FOLDER"], filename)
        if not safe_path or not safe_path.exists():
            abort(404)
        return send_file(safe_path, as_attachment=True, download_name=safe_path.name)

    @app.before_request
    def before_request():
        """登录检查"""
        # 允许访问的端点
        allowed_endpoints = [
            "login",
            "static",
            "tuban.export_excel",
            "tuban.import_excel",
        ]
        if request.endpoint not in allowed_endpoints and "username" not in session:
            return redirect(url_for("login"))

        admin_only_blueprints = {"system"}
        if (
            request.blueprint in admin_only_blueprints
            and session.get("role") != "admin"
        ):
            abort(403)

        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            if request.endpoint is None:
                return None
            csrf_token = session.get("_csrf_token")
            submitted_token = request.form.get("_csrf_token") or request.headers.get(
                "X-CSRF-Token"
            )
            if not csrf_token or not submitted_token or csrf_token != submitted_token:
                abort(400)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
