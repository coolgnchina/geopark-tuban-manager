from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    current_app,
    send_file,
    abort,
    session,
)
from datetime import datetime
from models import db
from models.tuban import Tuban
from models.rectify_record import RectifyRecord
from models.dictionary import Dictionary
from models.tuban_image import TubanImage
from models.event import Event
from models.tuban_event import tuban_events
from utils.helpers import (
    parse_date,
    calculate_overdue_status,
    get_overdue_days,
    allowed_file,
    sanitize_filename,
    safe_join_upload,
)
from utils.excel_handler import import_tubans_from_excel, export_tubans_to_excel
import os
import uuid

tuban_bp = Blueprint("tuban", __name__)


@tuban_bp.route("/list")
def list():
    """图斑列表"""
    # 获取查询参数
    page = request.args.get("page", 1, type=int)
    search_keyword = request.args.get("search", "", type=str)
    park_name = request.args.get("park_name", "", type=str)
    problem_type = request.args.get("problem_type", "", type=str)
    rectify_status = request.args.get("rectify_status", "", type=str)
    func_zone = request.args.get("func_zone", "", type=str)
    event_id = request.args.get("event_id", "", type=str)

    # 构建查询
    query = Tuban.query.filter_by(is_deleted=0)

    # 搜索条件
    if search_keyword:
        query = query.filter(
            db.or_(
                Tuban.tuban_code.contains(search_keyword),
                Tuban.facility_name.contains(search_keyword),
                Tuban.build_unit.contains(search_keyword),
            )
        )

    # 筛选条件
    if park_name:
        query = query.filter(Tuban.park_name == park_name)
    if problem_type:
        query = query.filter(Tuban.problem_type == problem_type)
    if rectify_status:
        query = query.filter(Tuban.rectify_status == rectify_status)
    if func_zone:
        query = query.filter(Tuban.func_zone == func_zone)
    if event_id:
        query = query.join(tuban_events).filter(tuban_events.c.event_id == event_id)

    # 分页
    per_page = current_app.config["TUBANS_PER_PAGE"]
    pagination = query.order_by(Tuban.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # 获取筛选选项
    park_names = db.session.query(Tuban.park_name).distinct().all()
    problem_types = db.session.query(Tuban.problem_type).distinct().all()
    rectify_statuses = db.session.query(Tuban.rectify_status).distinct().all()
    func_zones = db.session.query(Tuban.func_zone).distinct().all()

    # 获取事件列表（用于筛选）
    events = Event.query.filter_by(is_active=1).order_by(Event.issue_date.desc()).all()

    return render_template(
        "tuban_list.html",
        pagination=pagination,
        search_keyword=search_keyword,
        park_name=park_name,
        problem_type=problem_type,
        rectify_status=rectify_status,
        func_zone=func_zone,
        event_id=event_id,
        park_names=park_names,
        problem_types=problem_types,
        rectify_statuses=rectify_statuses,
        func_zones=func_zones,
        events=events,
    )


@tuban_bp.route("/detail/<int:id>")
def detail(id):
    """图斑详情"""
    tuban = Tuban.query.get_or_404(id)
    return _render_detail(tuban)


@tuban_bp.route("/detail/by-code/<tuban_code>")
def detail_by_code(tuban_code):
    """图斑详情（按图斑编号访问）"""
    tuban = Tuban.query.filter_by(tuban_code=tuban_code, is_deleted=0).first_or_404()
    return _render_detail(tuban)


def _render_detail(tuban):
    """渲染图斑详情（内部函数）"""
    # 获取整改跟踪记录
    rectify_records = (
        RectifyRecord.query.filter_by(tuban_id=tuban.id)
        .order_by(RectifyRecord.record_time.desc())
        .all()
    )

    # 获取现场照片
    photos = TubanImage.query.filter_by(
        tuban_id=tuban.id, image_type="photo", is_deleted=0
    ).all()

    # 检查是否超期
    is_overdue = calculate_overdue_status(tuban.rectify_deadline, tuban.rectify_status)
    overdue_days = get_overdue_days(tuban.rectify_deadline) if is_overdue else 0

    # 获取当前日期（用于模板比较）
    today = datetime.now().date()

    return render_template(
        "tuban_detail.html",
        tuban=tuban,
        rectify_records=rectify_records,
        photos=photos,
        is_overdue=is_overdue,
        overdue_days=overdue_days,
        get_current_date=lambda: today,
    )


@tuban_bp.route("/add", methods=["GET", "POST"])
def add():
    """添加图斑"""
    if request.method == "POST":
        try:
            # 创建新图斑
            tuban = Tuban()

            # 基本信息
            tuban.tuban_code = request.form.get("tuban_code")
            tuban.park_name = request.form.get("park_name")
            tuban.func_zone = request.form.get("func_zone")
            tuban.facility_name = request.form.get("facility_name")
            tuban.longitude = request.form.get("longitude", type=float)
            tuban.latitude = request.form.get("latitude", type=float)
            tuban.area = request.form.get("area", type=float)
            tuban.image_date = parse_date(request.form.get("image_date"))

            # 建设主体信息
            tuban.build_unit = request.form.get("build_unit")
            tuban.build_time = parse_date(request.form.get("build_time"))
            tuban.has_approval = request.form.get("has_approval")
            tuban.approval_no = request.form.get("approval_no")

            # 发现与核查信息
            tuban.discover_time = parse_date(request.form.get("discover_time"))
            tuban.discover_method = request.form.get("discover_method")
            tuban.check_time = parse_date(request.form.get("check_time"))
            tuban.check_person = request.form.get("check_person")
            tuban.check_result = request.form.get("check_result")

            # 问题与违法信息
            tuban.problem_type = request.form.get("problem_type")
            tuban.problem_desc = request.form.get("problem_desc")
            tuban.geo_heritage_type = request.form.get("geo_heritage_type")
            tuban.impact_level = request.form.get("impact_level")
            tuban.is_illegal = request.form.get("is_illegal")
            tuban.violated_law = request.form.get("violated_law")

            # 整改信息
            tuban.rectify_measure = request.form.get("rectify_measure")
            tuban.rectify_deadline = parse_date(request.form.get("rectify_deadline"))
            tuban.rectify_status = request.form.get("rectify_status", "未整改")
            tuban.rectify_verify_time = parse_date(
                request.form.get("rectify_verify_time")
            )
            tuban.verify_person = request.form.get("verify_person")
            tuban.is_closed = request.form.get("is_closed", "否")

            # 处罚信息
            tuban.is_punished = request.form.get("is_punished")
            tuban.punish_type = request.form.get("punish_type")
            tuban.fine_amount = request.form.get("fine_amount", type=float)
            tuban.punish_doc_no = request.form.get("punish_doc_no")

            # 管理信息
            tuban.data_source = request.form.get("data_source")
            tuban.is_patrol_point = request.form.get("is_patrol_point")
            tuban.responsible_dept = request.form.get("responsible_dept")

            # 处理附件上传
            if "attachment_file" in request.files:
                file = request.files["attachment_file"]
                if file and file.filename:
                    # 检查文件类型
                    allowed_extensions = {
                        "pdf",
                        "doc",
                        "docx",
                        "jpg",
                        "jpeg",
                        "png",
                        "gif",
                        "bmp",
                        "zip",
                        "rar",
                    }
                    safe_name = sanitize_filename(file.filename)
                    if not safe_name:
                        flash("附件文件名无效", "warning")
                        tuban.attachments = request.form.get("attachments")
                    elif allowed_file(safe_name, allowed_extensions):
                        # 生成唯一文件名
                        filename = f"attachment_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
                        filepath = os.path.join(
                            current_app.config["UPLOAD_FOLDER"], filename
                        )

                        # 确保上传目录存在
                        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)

                        # 保存文件
                        file.save(filepath)

                        # 保存相对路径
                        tuban.attachments = filename
                    else:
                        flash(
                            "附件格式不支持，请上传PDF、Word、图片或压缩包文件",
                            "warning",
                        )
                        tuban.attachments = request.form.get("attachments")
                else:
                    tuban.attachments = request.form.get("attachments")
            else:
                tuban.attachments = request.form.get("attachments")

            tuban.remark = request.form.get("remark")

            # 处理附件（支持多附件，用逗号分隔）
            tuban.attachments = request.form.get("attachments", "")

            # 保存到数据库
            db.session.add(tuban)
            db.session.flush()  # 获取 tuban.id

            # 处理事件关联
            event_ids = request.form.getlist("event_ids")
            if event_ids:
                for event_id in event_ids:
                    if event_id.strip():
                        stmt = tuban_events.insert().values(
                            tuban_id=tuban.id, event_id=int(event_id)
                        )
                        db.session.execute(stmt)

            db.session.commit()

            flash("图斑添加成功！", "success")
            return redirect(url_for("tuban.detail", id=tuban.id))

        except Exception as e:
            db.session.rollback()
            flash(f"添加失败：{str(e)}", "error")
            return redirect(url_for("tuban.add"))

    # GET请求时，获取字典数据和事件列表
    func_zones = (
        Dictionary.query.filter_by(dict_type="func_zone")
        .order_by(Dictionary.sort_order)
        .all()
    )
    events = Event.query.filter_by(is_active=1).order_by(Event.issue_date.desc()).all()

    return render_template(
        "tuban_form.html", action="add", func_zones=func_zones, events=events
    )


@tuban_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    """编辑图斑"""
    tuban = Tuban.query.get_or_404(id)

    if request.method == "POST":
        try:
            # 更新图斑信息
            # 基本信息
            tuban.tuban_code = request.form.get("tuban_code")
            tuban.park_name = request.form.get("park_name")
            tuban.func_zone = request.form.get("func_zone")
            tuban.facility_name = request.form.get("facility_name")
            tuban.longitude = request.form.get("longitude", type=float)
            tuban.latitude = request.form.get("latitude", type=float)
            tuban.area = request.form.get("area", type=float)
            tuban.image_date = parse_date(request.form.get("image_date"))

            # 建设主体信息
            tuban.build_unit = request.form.get("build_unit")
            tuban.build_time = parse_date(request.form.get("build_time"))
            tuban.has_approval = request.form.get("has_approval")
            tuban.approval_no = request.form.get("approval_no")

            # 发现与核查信息
            tuban.discover_time = parse_date(request.form.get("discover_time"))
            tuban.discover_method = request.form.get("discover_method")
            tuban.check_time = parse_date(request.form.get("check_time"))
            tuban.check_person = request.form.get("check_person")
            tuban.check_result = request.form.get("check_result")

            # 问题与违法信息
            tuban.problem_type = request.form.get("problem_type")
            tuban.problem_desc = request.form.get("problem_desc")
            tuban.geo_heritage_type = request.form.get("geo_heritage_type")
            tuban.impact_level = request.form.get("impact_level")
            tuban.is_illegal = request.form.get("is_illegal")
            tuban.violated_law = request.form.get("violated_law")

            # 整改信息
            tuban.rectify_measure = request.form.get("rectify_measure")
            tuban.rectify_deadline = parse_date(request.form.get("rectify_deadline"))
            tuban.rectify_status = request.form.get("rectify_status")
            tuban.rectify_verify_time = parse_date(
                request.form.get("rectify_verify_time")
            )
            tuban.verify_person = request.form.get("verify_person")
            tuban.is_closed = request.form.get("is_closed")

            # 处罚信息
            tuban.is_punished = request.form.get("is_punished")
            tuban.punish_type = request.form.get("punish_type")
            tuban.fine_amount = request.form.get("fine_amount", type=float)
            tuban.punish_doc_no = request.form.get("punish_doc_no")

            # 管理信息
            tuban.data_source = request.form.get("data_source")
            tuban.is_patrol_point = request.form.get("is_patrol_point")
            tuban.responsible_dept = request.form.get("responsible_dept")

            # 处理附件上传
            if "attachment_file" in request.files:
                file = request.files["attachment_file"]
                if file and file.filename:
                    # 检查文件类型
                    allowed_extensions = {
                        "pdf",
                        "doc",
                        "docx",
                        "jpg",
                        "jpeg",
                        "png",
                        "gif",
                        "bmp",
                        "zip",
                        "rar",
                    }
                    safe_name = sanitize_filename(file.filename)
                    if not safe_name:
                        flash("附件文件名无效", "warning")
                        tuban.attachments = request.form.get("attachments")
                    elif allowed_file(safe_name, allowed_extensions):
                        # 生成唯一文件名
                        filename = f"attachment_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
                        filepath = os.path.join(
                            current_app.config["UPLOAD_FOLDER"], filename
                        )

                        # 确保上传目录存在
                        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)

                        # 保存文件
                        file.save(filepath)

                        # 保存相对路径
                        tuban.attachments = filename
                    else:
                        flash(
                            "附件格式不支持，请上传PDF、Word、图片或压缩包文件",
                            "warning",
                        )
                        tuban.attachments = request.form.get("attachments")
                else:
                    tuban.attachments = request.form.get("attachments")
            else:
                tuban.attachments = request.form.get("attachments")

            tuban.remark = request.form.get("remark")

            # 处理附件（支持多附件，用逗号分隔）
            tuban.attachments = request.form.get("attachments", "")

            # 处理事件关联 - 先删除旧关联
            db.session.execute(
                tuban_events.delete().where(tuban_events.c.tuban_id == tuban.id)
            )

            # 添加新的事件关联
            event_ids = request.form.getlist("event_ids")
            if event_ids:
                for event_id in event_ids:
                    if event_id.strip():
                        stmt = tuban_events.insert().values(
                            tuban_id=tuban.id, event_id=int(event_id)
                        )
                        db.session.execute(stmt)

            db.session.commit()

            flash("图斑更新成功！", "success")
            return redirect(url_for("tuban.detail", id=tuban.id))

        except Exception as e:
            db.session.rollback()
            flash(f"更新失败：{str(e)}", "error")
            return redirect(url_for("tuban.edit", id=id))

    # GET请求时，获取字典数据和事件列表
    func_zones = (
        Dictionary.query.filter_by(dict_type="func_zone")
        .order_by(Dictionary.sort_order)
        .all()
    )
    events = Event.query.filter_by(is_active=1).order_by(Event.issue_date.desc()).all()

    # 获取已关联的事件ID列表
    linked_event_ids = [e.id for e in tuban.events.all()]

    return render_template(
        "tuban_form.html",
        action="edit",
        tuban=tuban,
        func_zones=func_zones,
        events=events,
        linked_event_ids=linked_event_ids,
    )


@tuban_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    """删除图斑（软删除）"""
    tuban = Tuban.query.get_or_404(id)

    try:
        tuban.is_deleted = 1
        db.session.commit()
        flash("图斑已删除！", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"删除失败：{str(e)}", "error")

    return redirect(url_for("tuban.list"))


@tuban_bp.route("/add_rectify_record/<int:id>", methods=["POST"])
def add_rectify_record(id):
    """添加整改跟踪记录"""
    tuban = Tuban.query.get_or_404(id)

    try:
        record = RectifyRecord()
        record.tuban_id = id
        record.status = request.form.get("status")
        record.content = request.form.get("content")
        record.operator = request.form.get("operator")
        record.record_time = datetime.now()

        # 如果状态是"已整改"，更新图斑的整改状态
        if request.form.get("status") == "已整改":
            tuban.rectify_status = "已整改"
            tuban.rectify_verify_time = datetime.now().date()
            tuban.verify_person = request.form.get("operator")
            tuban.is_closed = "是"

        db.session.add(record)
        db.session.commit()

        flash("整改记录添加成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"添加失败：{str(e)}", "error")

    return redirect(url_for("tuban.detail", id=id))


@tuban_bp.route("/export_excel")
def export_excel():
    """导出Excel"""
    # 获取查询参数（与列表页相同）
    search_keyword = request.args.get("search", "", type=str)
    park_name = request.args.get("park_name", "", type=str)
    problem_type = request.args.get("problem_type", "", type=str)
    rectify_status = request.args.get("rectify_status", "", type=str)
    func_zone = request.args.get("func_zone", "", type=str)

    # 构建查询（与列表页相同逻辑）
    query = Tuban.query.filter_by(is_deleted=0)

    if search_keyword:
        query = query.filter(
            db.or_(
                Tuban.tuban_code.contains(search_keyword),
                Tuban.facility_name.contains(search_keyword),
                Tuban.build_unit.contains(search_keyword),
            )
        )

    if park_name:
        query = query.filter(Tuban.park_name == park_name)
    if problem_type:
        query = query.filter(Tuban.problem_type == problem_type)
    if rectify_status:
        query = query.filter(Tuban.rectify_status == rectify_status)
    if func_zone:
        query = query.filter(Tuban.func_zone == func_zone)

    tubans = query.all()

    # 导出Excel
    return export_tubans_to_excel(tubans)


@tuban_bp.route("/import", methods=["POST"])
def import_excel():
    """导入Excel"""
    if "file" not in request.files:
        flash("请选择文件", "error")
        return redirect(url_for("tuban.list"))

    file = request.files["file"]
    if not file.filename:
        flash("没有选择文件", "error")
        return redirect(url_for("tuban.list"))

    safe_name = sanitize_filename(file.filename)
    if not safe_name:
        flash("文件名无效", "error")
        return redirect(url_for("tuban.list"))

    allowed_extensions = current_app.config.get(
        "EXCEL_ALLOWED_EXTENSIONS", {"xlsx", "xls"}
    )
    if not allowed_file(safe_name, allowed_extensions):
        flash("只支持Excel文件（.xlsx/.xls）", "error")
        return redirect(url_for("tuban.list"))

    filepath = None
    try:
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        temp_name = f"import_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], temp_name)
        file.save(filepath)

        count = import_tubans_from_excel(filepath)
        flash(f"导入完成：成功导入 {count} 条记录", "success")
    except Exception as e:
        flash(f"导入失败：{str(e)}", "error")
    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass

    return redirect(url_for("tuban.list"))


@tuban_bp.route("/upload_attachment", methods=["POST"])
def upload_attachment():
    """上传附件"""
    if "file" not in request.files:
        return jsonify({"success": False, "message": "没有选择文件"})

    file = request.files["file"]
    if not file.filename:
        return jsonify({"success": False, "message": "没有选择文件"})

    safe_name = sanitize_filename(file.filename)
    if not safe_name:
        return jsonify({"success": False, "message": "文件名无效"})

    try:
        allowed_extensions = {
            "pdf",
            "doc",
            "docx",
            "jpg",
            "jpeg",
            "png",
            "gif",
            "bmp",
            "zip",
            "rar",
        }
        if not allowed_file(safe_name, allowed_extensions):
            return jsonify({"success": False, "message": "文件格式不支持"})

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > current_app.config["MAX_CONTENT_LENGTH"]:
            return jsonify({"success": False, "message": "文件大小超过16MB限制"})

        filename = f"attachment_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(filepath)

        return jsonify({"success": True, "filename": filename})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@tuban_bp.route("/download/<filename>")
def download_attachment(filename):
    """下载附件"""
    try:
        safe_path = safe_join_upload(current_app.config["UPLOAD_FOLDER"], filename)
        if not safe_path or not safe_path.exists():
            abort(404)

        return send_file(safe_path, as_attachment=True, download_name=safe_path.name)
    except Exception as e:
        flash(f"下载失败：{str(e)}", "error")
        return redirect(url_for("tuban.list"))


# ========== 图片管理API ==========


@tuban_bp.route("/<int:id>/images", methods=["GET"])
def get_images(id):
    """获取图斑的所有图片"""
    tuban = Tuban.query.get_or_404(id)

    images = (
        TubanImage.query.filter_by(tuban_id=id, is_deleted=0)
        .order_by(TubanImage.uploaded_at.desc())
        .all()
    )

    # 按类型分组
    photos = [img.to_dict() for img in images if img.image_type == "photo"]
    satellites = [img.to_dict() for img in images if img.image_type == "satellite"]

    return jsonify(
        {
            "success": True,
            "photos": photos,
            "satellites": satellites,
            "total": len(images),
        }
    )


@tuban_bp.route("/<int:id>/images", methods=["POST"])
def upload_image(id):
    """上传图片到指定图斑"""
    tuban = Tuban.query.get_or_404(id)

    if "file" not in request.files:
        return jsonify({"success": False, "message": "没有选择文件"})

    file = request.files["file"]
    if not file.filename:
        return jsonify({"success": False, "message": "没有选择文件"})

    safe_name = sanitize_filename(file.filename)
    if not safe_name:
        return jsonify({"success": False, "message": "文件名无效"})

    # 获取图片类型
    image_type = request.form.get("image_type", "photo")
    if image_type not in ["photo", "satellite"]:
        return jsonify({"success": False, "message": "无效的图片类型"})

    try:
        # 检查文件类型
        allowed_extensions = {"jpg", "jpeg", "png", "gif", "bmp", "webp"}
        if not allowed_file(safe_name, allowed_extensions):
            return jsonify(
                {"success": False, "message": "只支持图片格式(JPG/PNG/GIF/BMP/WEBP)"}
            )

        # 检查文件大小 (5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            return jsonify({"success": False, "message": "图片大小不能超过5MB"})

        # 生成唯一文件名
        ext = safe_name.rsplit(".", 1)[1].lower()
        unique_filename = f"{image_type}_{id}_{uuid.uuid4().hex[:8]}.{ext}"

        # 创建图片目录
        images_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "images")
        os.makedirs(images_folder, exist_ok=True)

        # 保存文件
        filepath = os.path.join(images_folder, unique_filename)
        file.save(filepath)

        # 保存到数据库
        image = TubanImage()
        image.tuban_id = id
        image.image_type = image_type
        image.filename = unique_filename
        image.original_name = safe_name
        image.description = request.form.get("description", "")
        image.file_size = file_size
        image.uploaded_by = session.get("username", "unknown")
        db.session.add(image)
        db.session.commit()

        return jsonify(
            {"success": True, "message": "上传成功", "image": image.to_dict()}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"上传失败: {str(e)}"})


@tuban_bp.route("/images/<int:image_id>", methods=["DELETE"])
def delete_image(image_id):
    """删除图片"""
    image = TubanImage.query.get_or_404(image_id)

    try:
        # 软删除
        image.is_deleted = 1
        db.session.commit()

        # 可选：删除物理文件
        # filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images', image.filename)
        # if os.path.exists(filepath):
        #     os.remove(filepath)

        return jsonify({"success": True, "message": "删除成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"删除失败: {str(e)}"})


@tuban_bp.route("/images/<filename>")
def serve_image(filename):
    """提供图片访问"""
    try:
        relative_path = os.path.join("images", filename)
        safe_path = safe_join_upload(current_app.config["UPLOAD_FOLDER"], relative_path)
        if not safe_path or not safe_path.exists():
            abort(404)

        return send_file(safe_path, as_attachment=False)

    except Exception:
        abort(404)
