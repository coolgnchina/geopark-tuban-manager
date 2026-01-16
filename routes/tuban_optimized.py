from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    current_app,
)
from datetime import datetime
from models import db
from models.tuban import Tuban
from models.tuban_image import TubanImage
from models.rectify_record import RectifyRecord
from models.dictionary import Dictionary
from utils.helpers import (
    parse_date,
    calculate_overdue_status,
    get_overdue_days,
    allowed_file,
)
from utils.excel_handler import import_tubans_from_excel, export_tubans_to_excel
import os

tuban_bp = Blueprint("tuban", __name__)


@tuban_bp.route("/list", endpoint="list")
def list_view():
    """图斑列表 - 优化版本"""
    # 获取查询参数
    page = request.args.get("page", 1, type=int)
    search_keyword = request.args.get("search", "", type=str)
    park_name = request.args.get("park_name", "", type=str)
    problem_type = request.args.get("problem_type", "", type=str)
    rectify_status = request.args.get("rectify_status", "", type=str)
    func_zone = request.args.get("func_zone", "", type=str)

    # 构建查询 - 只选择需要的字段
    query = Tuban.query.filter_by(is_deleted=0)

    # 如果不需要所有字段，可以只选择显示的字段
    # query = query.with_entities(Tuban.id, Tuban.tuban_code, Tuban.park_name, ...)

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

    # 分页 - 使用更高效的查询
    per_page = current_app.config["TUBANS_PER_PAGE"]
    pagination = query.order_by(Tuban.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # 优化：一次性获取所有筛选选项
    # 使用单个查询获取所有distinct值
    filter_options = (
        db.session.query(
            Tuban.park_name, Tuban.problem_type, Tuban.rectify_status, Tuban.func_zone
        )
        .filter(Tuban.is_deleted == 0)
        .distinct()
        .all()
    )

    # 提取各个选项
    park_names = sorted(list(set([row[0] for row in filter_options if row[0]])))
    problem_types = sorted(list(set([row[1] for row in filter_options if row[1]])))
    rectify_statuses = sorted(list(set([row[2] for row in filter_options if row[2]])))
    func_zones = sorted(list(set([row[3] for row in filter_options if row[3]])))

    return render_template(
        "tuban_list.html",
        pagination=pagination,
        search_keyword=search_keyword,
        park_name=park_name,
        problem_type=problem_type,
        rectify_status=rectify_status,
        func_zone=func_zone,
        park_names=[(name,) for name in park_names],
        problem_types=[(type_,) for type_ in problem_types],
        rectify_statuses=[(status,) for status in rectify_statuses],
        func_zones=[(zone,) for zone in func_zones],
    )


@tuban_bp.route("/detail/<int:id>")
def detail(id):
    """图斑详情"""
    tuban = Tuban.query.get_or_404(id)

    # 获取整改跟踪记录 - 使用更高效的查询
    rectify_records = (
        RectifyRecord.query.filter_by(tuban_id=id)
        .order_by(RectifyRecord.record_time.desc())
        .all()
    )

    # 获取现场照片
    photos = TubanImage.query.filter_by(
        tuban_id=id, image_type="photo", is_deleted=0
    ).all()

    # 获取卫片影像
    satellites = TubanImage.query.filter_by(
        tuban_id=id, image_type="satellite", is_deleted=0
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
        satellites=satellites,
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
            tuban.attachments = request.form.get("attachments")
            tuban.remark = request.form.get("remark")

            # 保存到数据库
            db.session.add(tuban)
            db.session.commit()

            flash("图斑添加成功！", "success")
            return redirect(url_for("tuban.detail", id=tuban.id))

        except Exception as e:
            db.session.rollback()
            flash(f"添加失败：{str(e)}", "error")
            return redirect(url_for("tuban.add"))

    # GET请求时，获取字典数据
    func_zones = (
        Dictionary.query.filter_by(dict_type="func_zone")
        .order_by(Dictionary.sort_order)
        .all()
    )

    return render_template("tuban_form.html", action="add", func_zones=func_zones)


# 导出功能保持不变
@tuban_bp.route("/export_excel")
def export_excel():
    """导出Excel - 保持原有逻辑"""
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
