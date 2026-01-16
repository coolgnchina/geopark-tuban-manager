from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from datetime import datetime
import json
from models import db
from models.project import Project, ProjectDocument, ProjectTimeline, project_tubans
from models.tuban import Tuban
from utils.helpers import parse_date, sanitize_filename, safe_join_upload, allowed_file
from utils.ai_summary import generate_summary
from utils.document_extract import extract_from_upload
import os
from werkzeug.utils import secure_filename

project_bp = Blueprint("project", __name__)
APPROVAL_STATUS = [
    ("立项审批中", "立项审批中"),
    ("已审批", "已审批"),
    ("未审批", "未审批"),
]


def parse_float(value):
    if value in (None, ""):
        return None
    return float(value)


PROJECT_STATUS = [
    ("筹备", "筹备"),
    ("在建", "在建"),
    ("已完工", "已完工"),
    ("停工", "停工"),
    ("废弃", "废弃"),
]
TIMELINE_EVENTS = [
    ("停工通知", "停工通知"),
    ("征求意见", "征求意见"),
    ("批复", "批复"),
    ("函件往来", "函件往来"),
    ("会议纪要", "会议纪要"),
    ("现场检查", "现场检查"),
    ("整改要求", "整改要求"),
    ("验收通过", "验收通过"),
    ("验收不通过", "验收不通过"),
    ("行政处罚", "行政处罚"),
    ("其他", "其他"),
]
DOCUMENT_TYPES = [
    ("立项文件", "立项文件"),
    ("可研报告", "可研报告"),
    ("规划方案", "规划方案"),
    ("环境影响评价", "环境影响评价"),
    ("地质灾害评估", "地质灾害评估"),
    ("建设工程规划许可证", "建设工程规划许可证"),
    ("施工许可证", "施工许可证"),
    ("竣工验收报告", "竣工验收报告"),
    ("监管部门批复", "监管部门批复"),
    ("其他部门批复", "其他部门批复"),
    ("协议/合同", "协议/合同"),
    ("其他", "其他"),
]


@project_bp.route("/projects")
def list():
    """项目列表"""
    search_keyword = request.args.get("search", "", type=str)
    approval_status = request.args.get("approval_status", "", type=str)
    project_status = request.args.get("project_status", "", type=str)

    query = Project.query.filter_by(is_active=1)

    if search_keyword:
        query = query.filter(Project.project_name.contains(search_keyword))
    if approval_status:
        query = query.filter_by(approval_status=approval_status)
    if project_status:
        query = query.filter_by(project_status=project_status)

    projects = query.order_by(Project.created_at.desc()).all()

    return render_template(
        "project_list.html",
        projects=projects,
        search_keyword=search_keyword,
        approval_status=approval_status,
        project_status=project_status,
        approval_statuses=[s[0] for s in APPROVAL_STATUS],
        project_statuses=[s[0] for s in PROJECT_STATUS],
    )


@project_bp.route("/projects/add", methods=["GET", "POST"])
def add():
    """新增项目"""
    if request.method == "POST":
        try:
            project = Project()
            project.project_name = request.form.get("project_name")
            project.project_type = request.form.get("project_type")
            project.legal_entity = request.form.get("legal_entity")
            project.contact_person = request.form.get("contact_person")
            project.contact_phone = request.form.get("contact_phone")
            project.location = request.form.get("location")
            project.func_zone = request.form.get("func_zone")

            project.longitude = parse_float(request.form.get("longitude"))
            project.latitude = parse_float(request.form.get("latitude"))
            project.area = parse_float(request.form.get("area"))

            project.approval_status = request.form.get("approval_status")
            project.approval_stage = request.form.get("approval_stage")
            project.approval_start_date = parse_date(
                request.form.get("approval_start_date")
            )
            project.approval_end_date = parse_date(
                request.form.get("approval_end_date")
            )

            project.project_status = request.form.get("project_status")
            project.start_date = parse_date(request.form.get("start_date"))
            project.actual_start_date = parse_date(
                request.form.get("actual_start_date")
            )
            project.end_date = parse_date(request.form.get("end_date"))
            project.actual_end_date = parse_date(request.form.get("actual_end_date"))

            project.description = request.form.get("description")
            project.remark = request.form.get("remark")

            db.session.add(project)
            db.session.commit()

            flash("项目添加成功！", "success")
            return redirect(url_for("project.list"))

        except Exception as e:
            db.session.rollback()
            flash("添加失败：" + str(e), "error")

    return render_template(
        "project_form.html",
        action="add",
        project=None,
        approval_statuses=APPROVAL_STATUS,
        project_statuses=PROJECT_STATUS,
    )


@project_bp.route("/projects/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    """编辑项目"""
    project = Project.query.get_or_404(id)

    if request.method == "POST":
        try:
            project.project_name = request.form.get("project_name")
            project.project_type = request.form.get("project_type")
            project.legal_entity = request.form.get("legal_entity")
            project.contact_person = request.form.get("contact_person")
            project.contact_phone = request.form.get("contact_phone")
            project.location = request.form.get("location")
            project.func_zone = request.form.get("func_zone")

            project.longitude = parse_float(request.form.get("longitude"))
            project.latitude = parse_float(request.form.get("latitude"))
            project.area = parse_float(request.form.get("area"))

            project.approval_status = request.form.get("approval_status")
            project.approval_stage = request.form.get("approval_stage")
            project.approval_start_date = parse_date(
                request.form.get("approval_start_date")
            )
            project.approval_end_date = parse_date(
                request.form.get("approval_end_date")
            )

            project.project_status = request.form.get("project_status")
            project.start_date = parse_date(request.form.get("start_date"))
            project.actual_start_date = parse_date(
                request.form.get("actual_start_date")
            )
            project.end_date = parse_date(request.form.get("end_date"))
            project.actual_end_date = parse_date(request.form.get("actual_end_date"))

            project.description = request.form.get("description")
            project.remark = request.form.get("remark")

            db.session.commit()

            flash("项目更新成功！", "success")
            return redirect(url_for("project.detail", id=id))

        except Exception as e:
            db.session.rollback()
            flash("更新失败：" + str(e), "error")

    return render_template(
        "project_form.html",
        action="edit",
        project=project,
        approval_statuses=APPROVAL_STATUS,
        project_statuses=PROJECT_STATUS,
    )


@project_bp.route("/projects/delete/<int:id>", methods=["POST"])
def delete(id):
    """删除项目（软删除）"""
    project = Project.query.get_or_404(id)

    try:
        project.is_active = 0
        db.session.commit()
        flash("项目已删除！", "success")
    except Exception as e:
        db.session.rollback()
        flash("删除失败：" + str(e), "error")

    return redirect(url_for("project.list"))


@project_bp.route("/projects/<int:id>")
def detail(id):
    """项目详情"""
    project = Project.query.get_or_404(id)

    # 获取关联的图斑
    linked_tubans = (
        Tuban.query.join(project_tubans)
        .filter(project_tubans.c.project_id == id, Tuban.is_deleted == 0)
        .all()
    )

    # 获取公文时间线（按日期排序）
    timelines = (
        ProjectTimeline.query.filter_by(project_id=id)
        .order_by(ProjectTimeline.event_date.desc(), ProjectTimeline.created_at.desc())
        .all()
    )

    # 获取文档
    documents = (
        ProjectDocument.query.filter_by(project_id=id)
        .order_by(ProjectDocument.created_at.desc())
        .all()
    )

    return render_template(
        "project_detail.html",
        project=project,
        linked_tubans=linked_tubans,
        timelines=timelines,
        documents=documents,
        timeline_events=TIMELINE_EVENTS,
        document_types=DOCUMENT_TYPES,
    )


# ==================== 文档管理 ====================
@project_bp.route("/projects/<int:id>/documents/add", methods=["POST"])
def add_document(id):
    """添加文档"""
    project = Project.query.get_or_404(id)

    try:
        doc = ProjectDocument()
        doc.project_id = id
        doc.doc_type = request.form.get("doc_type")
        doc.doc_title = request.form.get("doc_title")
        doc.doc_date = parse_date(request.form.get("doc_date"))
        doc.description = request.form.get("description")
        doc.uploaded_by = request.form.get("uploaded_by", "管理员")

        # 处理文件上传
        if "doc_file" in request.files:
            file = request.files["doc_file"]
            if file and file.filename:
                safe_name = sanitize_filename(file.filename)
                if not safe_name:
                    flash("文件名无效", "error")
                    return redirect(url_for("project.detail", id=id))

                allowed_extensions = {"pdf", "doc", "docx", "txt", "md"}
                if not allowed_file(safe_name, allowed_extensions):
                    flash("仅支持PDF/Word/TXT/MD文件", "error")
                    return redirect(url_for("project.detail", id=id))

                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                if file_size > current_app.config.get("MAX_CONTENT_LENGTH", 0):
                    flash("文件大小超过16MB限制", "error")
                    return redirect(url_for("project.detail", id=id))

                filename = secure_filename(
                    "proj_"
                    + str(id)
                    + "_"
                    + datetime.now().strftime("%Y%m%d%H%M%S")
                    + "_"
                    + safe_name
                )
                upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
                project_folder = os.path.join(upload_folder, "projects", str(id))
                os.makedirs(project_folder, exist_ok=True)
                file.save(os.path.join(project_folder, filename))
                doc.doc_file = "projects/" + str(id) + "/" + filename

                # 提取文档内容（支持PDF/DOCX/TXT/MD）
                try:
                    extracted_text = extract_from_upload(file)
                    if extracted_text:
                        # 如果提取到内容，生成AI摘要
                        if len(extracted_text) > 10:
                            # 限制文本长度（智谱AI最大约8K tokens）
                            content_for_ai = extracted_text[:8000]
                            summary = generate_summary(content_for_ai)
                            if summary:
                                doc.ai_summary = summary
                                doc.ai_summary_status = "success"
                            else:
                                doc.ai_summary_status = "failed"
                        else:
                            doc.ai_summary_status = "failed"
                    else:
                        doc.ai_summary_status = "failed"
                except Exception as e:
                    print(f"文档提取失败: {e}")
                    doc.ai_summary_status = "failed"
            else:
                doc.ai_summary_status = "pending"
        else:
            doc.ai_summary_status = "pending"

        db.session.add(doc)
        db.session.commit()

        flash("文档添加成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash("添加失败：" + str(e), "error")

    return redirect(url_for("project.detail", id=id))


@project_bp.route("/documents/delete/<int:id>", methods=["POST"])
def delete_document(id):
    """删除文档"""
    doc = ProjectDocument.query.get_or_404(id)
    project_id = doc.project_id

    try:
        # 删除文件
        if doc.doc_file:
            safe_path = safe_join_upload(
                current_app.config.get("UPLOAD_FOLDER", "uploads"), doc.doc_file
            )
            if safe_path and safe_path.exists():
                os.remove(safe_path)

        db.session.delete(doc)
        db.session.commit()

        flash("文档已删除！", "success")
    except Exception as e:
        db.session.rollback()
        flash("删除失败：" + str(e), "error")

    return redirect(url_for("project.detail", id=project_id))


# ==================== 时间线管理 ====================
@project_bp.route("/projects/<int:id>/timeline/add", methods=["POST"])
def add_timeline(id):
    """添加公文时间线记录"""
    project = Project.query.get_or_404(id)

    try:
        timeline = ProjectTimeline()
        timeline.project_id = id
        timeline.event_type = request.form.get("event_type")
        timeline.event_title = request.form.get("event_title")
        timeline.event_date = parse_date(request.form.get("event_date"))
        timeline.opposite_party = request.form.get("opposite_party")
        timeline.created_by = request.form.get("created_by", "管理员")
        timeline.ai_summary_status = "pending"

        # 处理附件上传（支持多个）
        extracted_text = None
        attachment_files = request.files.getlist("attachments")
        uploaded_attachments = []

        if attachment_files and any(f and f.filename for f in attachment_files):
            upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
            project_folder = os.path.join(upload_folder, "projects", str(id))
            os.makedirs(project_folder, exist_ok=True)

            allowed_extensions = {"pdf", "doc", "docx", "txt", "md", "zip", "rar"}
            max_size = current_app.config.get("MAX_CONTENT_LENGTH", 0)

            for idx, file in enumerate(attachment_files):
                if file and file.filename:
                    # 安全处理文件名
                    safe_name = sanitize_filename(file.filename)
                    if not safe_name:
                        continue
                    if not allowed_file(safe_name, allowed_extensions):
                        continue

                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    if max_size and file_size > max_size:
                        continue

                    # 添加序号区分同名文件
                    filename = f"tl_{id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{idx}_{safe_name}"
                    file.save(os.path.join(project_folder, filename))
                    uploaded_attachments.append(f"projects/{str(id)}/{filename}")

                    # 从第一个附件提取文本（用于AI摘要）
                    if extracted_text is None:
                        try:
                            extracted_text = extract_from_upload(file)
                        except Exception as e:
                            print(f"附件文本提取失败: {e}")

            # 保存多个附件路径为JSON
            if uploaded_attachments:
                timeline.attachments = json.dumps(uploaded_attachments)

        # 确定内容来源：表单内容 > 附件提取文本
        form_content = request.form.get("content", "").strip()
        if form_content:
            timeline.content = form_content
        elif extracted_text:
            timeline.content = extracted_text
        else:
            timeline.content = ""

        db.session.add(timeline)
        db.session.commit()

        # 生成AI摘要
        if timeline.content:
            summary = generate_summary(timeline.content)
            if summary:
                timeline.ai_summary = summary
                timeline.ai_summary_status = "success"
            else:
                timeline.ai_summary_status = "failed"
            db.session.commit()

        flash("记录添加成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash("添加失败：" + str(e), "error")

    return redirect(url_for("project.detail", id=id))


@project_bp.route("/timeline/delete/<int:id>", methods=["POST"])
def delete_timeline(id):
    """删除时间线记录"""
    timeline = ProjectTimeline.query.get_or_404(id)
    project_id = timeline.project_id

    try:
        # 删除附件
        if timeline.attachments:
            upload_root = current_app.config.get("UPLOAD_FOLDER", "uploads")
            try:
                attachment_list = json.loads(timeline.attachments)
            except (TypeError, ValueError):
                attachment_list = []

            for attachment in attachment_list:
                safe_path = safe_join_upload(upload_root, attachment)
                if safe_path and safe_path.exists():
                    os.remove(safe_path)

        db.session.delete(timeline)
        db.session.commit()

        flash("记录已删除！", "success")
    except Exception as e:
        db.session.rollback()
        flash("删除失败：" + str(e), "error")

    return redirect(url_for("project.detail", id=project_id))


@project_bp.route("/timeline/<int:id>/regenerate_summary", methods=["POST"])
def regenerate_summary(id):
    """重新生成AI摘要"""
    timeline = ProjectTimeline.query.get_or_404(id)

    try:
        if timeline.content:
            summary = generate_summary(timeline.content)
            if summary:
                timeline.ai_summary = summary
                timeline.ai_summary_status = "success"
            else:
                timeline.ai_summary_status = "failed"
            db.session.commit()
            flash("AI摘要已更新！", "success")
        else:
            flash("无内容可生成摘要", "warning")
    except Exception as e:
        flash("生成失败：" + str(e), "error")

    return redirect(url_for("project.detail", id=timeline.project_id))


# ==================== 图斑关联 ====================
@project_bp.route("/projects/<int:id>/tubans", methods=["GET", "POST"])
def manage_tubans(id):
    """管理关联的图斑"""
    project = Project.query.get_or_404(id)

    if request.method == "POST":
        tuban_ids = request.form.getlist("tuban_ids")
        try:
            # 清除现有关联
            db.session.execute(
                project_tubans.delete().where(project_tubans.c.project_id == id)
            )

            # 添加新关联
            for tuban_id in tuban_ids:
                db.session.execute(
                    project_tubans.insert().values(
                        project_id=id, tuban_id=int(tuban_id)
                    )
                )

            db.session.commit()
            flash("图斑关联已更新！", "success")
        except Exception as e:
            db.session.rollback()
            flash("更新失败：" + str(e), "error")

    # 获取所有未删除的图斑
    all_tubans = (
        Tuban.query.filter_by(is_deleted=0).order_by(Tuban.tuban_code.desc()).all()
    )

    # 获取当前已关联的图斑ID
    linked_tuban_ids = [t.id for t in project.tubans]

    return render_template(
        "project_tubans.html",
        project=project,
        all_tubans=all_tubans,
        linked_tuban_ids=linked_tuban_ids,
    )


@project_bp.route("/projects/api/list")
def api_list():
    """获取项目列表（JSON）"""
    projects = (
        Project.query.filter_by(is_active=1).order_by(Project.created_at.desc()).all()
    )
    return jsonify({"success": True, "projects": [p.to_dict() for p in projects]})


@project_bp.route("/projects/api/<int:id>")
def api_detail(id):
    """获取项目详情（JSON）"""
    project = Project.query.get_or_404(id)
    return jsonify(
        {
            "success": True,
            "project": project.to_dict(),
            "tubans": [t.to_dict() for t in project.tubans],
            "documents": [d.to_dict() for d in project.documents],
            "timelines": [t.to_dict() for t in project.timelines],
        }
    )
