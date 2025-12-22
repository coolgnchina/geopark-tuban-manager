from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, send_from_directory, abort, session
from datetime import datetime
from models import db
from models.tuban import Tuban
from models.rectify_record import RectifyRecord
from models.dictionary import Dictionary
from models.tuban_image import TubanImage
from utils.helpers import parse_date, calculate_overdue_status, get_overdue_days, allowed_file
from utils.excel_handler import import_tubans_from_excel, export_tubans_to_excel
import os
import uuid

tuban_bp = Blueprint('tuban', __name__)

@tuban_bp.route('/list')
def list():
    """图斑列表"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    search_keyword = request.args.get('search', '', type=str)
    park_name = request.args.get('park_name', '', type=str)
    problem_type = request.args.get('problem_type', '', type=str)
    rectify_status = request.args.get('rectify_status', '', type=str)
    func_zone = request.args.get('func_zone', '', type=str)

    # 构建查询
    query = Tuban.query.filter_by(is_deleted=0)

    # 搜索条件
    if search_keyword:
        query = query.filter(
            db.or_(
                Tuban.tuban_code.contains(search_keyword),
                Tuban.facility_name.contains(search_keyword),
                Tuban.build_unit.contains(search_keyword)
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

    # 分页
    per_page = current_app.config['TUBANS_PER_PAGE']
    pagination = query.order_by(Tuban.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # 获取筛选选项
    park_names = db.session.query(Tuban.park_name).distinct().all()
    problem_types = db.session.query(Tuban.problem_type).distinct().all()
    rectify_statuses = db.session.query(Tuban.rectify_status).distinct().all()
    func_zones = db.session.query(Tuban.func_zone).distinct().all()

    return render_template('tuban_list.html',
                         pagination=pagination,
                         search_keyword=search_keyword,
                         park_name=park_name,
                         problem_type=problem_type,
                         rectify_status=rectify_status,
                         func_zone=func_zone,
                         park_names=park_names,
                         problem_types=problem_types,
                         rectify_statuses=rectify_statuses,
                         func_zones=func_zones)

@tuban_bp.route('/detail/<int:id>')
def detail(id):
    """图斑详情"""
    tuban = Tuban.query.get_or_404(id)

    # 获取整改跟踪记录
    rectify_records = RectifyRecord.query.filter_by(tuban_id=id).order_by(RectifyRecord.record_time.desc()).all()

    # 检查是否超期
    is_overdue = calculate_overdue_status(tuban.rectify_deadline, tuban.rectify_status)
    overdue_days = get_overdue_days(tuban.rectify_deadline) if is_overdue else 0

    return render_template('tuban_detail.html',
                         tuban=tuban,
                         rectify_records=rectify_records,
                         is_overdue=is_overdue,
                         overdue_days=overdue_days)

@tuban_bp.route('/add', methods=['GET', 'POST'])
def add():
    """添加图斑"""
    if request.method == 'POST':
        try:
            # 创建新图斑
            tuban = Tuban()

            # 基本信息
            tuban.tuban_code = request.form.get('tuban_code')
            tuban.park_name = request.form.get('park_name')
            tuban.func_zone = request.form.get('func_zone')
            tuban.facility_name = request.form.get('facility_name')
            tuban.longitude = request.form.get('longitude', type=float)
            tuban.latitude = request.form.get('latitude', type=float)
            tuban.area = request.form.get('area', type=float)
            tuban.image_date = parse_date(request.form.get('image_date'))

            # 建设主体信息
            tuban.build_unit = request.form.get('build_unit')
            tuban.build_time = parse_date(request.form.get('build_time'))
            tuban.has_approval = request.form.get('has_approval')
            tuban.approval_no = request.form.get('approval_no')

            # 发现与核查信息
            tuban.discover_time = parse_date(request.form.get('discover_time'))
            tuban.discover_method = request.form.get('discover_method')
            tuban.check_time = parse_date(request.form.get('check_time'))
            tuban.check_person = request.form.get('check_person')
            tuban.check_result = request.form.get('check_result')

            # 问题与违法信息
            tuban.problem_type = request.form.get('problem_type')
            tuban.problem_desc = request.form.get('problem_desc')
            tuban.geo_heritage_type = request.form.get('geo_heritage_type')
            tuban.impact_level = request.form.get('impact_level')
            tuban.is_illegal = request.form.get('is_illegal')
            tuban.violated_law = request.form.get('violated_law')

            # 整改信息
            tuban.rectify_measure = request.form.get('rectify_measure')
            tuban.rectify_deadline = parse_date(request.form.get('rectify_deadline'))
            tuban.rectify_status = request.form.get('rectify_status', '未整改')
            tuban.rectify_verify_time = parse_date(request.form.get('rectify_verify_time'))
            tuban.verify_person = request.form.get('verify_person')
            tuban.is_closed = request.form.get('is_closed', '否')

            # 处罚信息
            tuban.is_punished = request.form.get('is_punished')
            tuban.punish_type = request.form.get('punish_type')
            tuban.fine_amount = request.form.get('fine_amount', type=float)
            tuban.punish_doc_no = request.form.get('punish_doc_no')

            # 管理信息
            tuban.data_source = request.form.get('data_source')
            tuban.is_patrol_point = request.form.get('is_patrol_point')
            tuban.responsible_dept = request.form.get('responsible_dept')

            # 处理附件上传
            if 'attachment_file' in request.files:
                file = request.files['attachment_file']
                if file and file.filename != '':
                    # 检查文件类型
                    allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'zip', 'rar'}
                    if allowed_file(file.filename, allowed_extensions):
                        # 生成唯一文件名
                        filename = f"attachment_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                        # 确保上传目录存在
                        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

                        # 保存文件
                        file.save(filepath)

                        # 保存相对路径
                        tuban.attachments = filename
                    else:
                        flash('附件格式不支持，请上传PDF、Word、图片或压缩包文件', 'warning')
                        tuban.attachments = request.form.get('attachments')  # 保持原有值
                else:
                    tuban.attachments = request.form.get('attachments')
            else:
                tuban.attachments = request.form.get('attachments')

            tuban.remark = request.form.get('remark')

            # 处理附件（支持多附件，用逗号分隔）
            tuban.attachments = request.form.get('attachments', '')

            # 保存到数据库
            db.session.add(tuban)
            db.session.commit()

            flash('图斑添加成功！', 'success')
            return redirect(url_for('tuban.detail', id=tuban.id))

        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
            return redirect(url_for('tuban.add'))

    # GET请求时，获取字典数据
    func_zones = Dictionary.query.filter_by(dict_type='func_zone').order_by(Dictionary.sort_order).all()

    return render_template('tuban_form.html', action='add', func_zones=func_zones)

@tuban_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """编辑图斑"""
    tuban = Tuban.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # 更新图斑信息
            # 基本信息
            tuban.tuban_code = request.form.get('tuban_code')
            tuban.park_name = request.form.get('park_name')
            tuban.func_zone = request.form.get('func_zone')
            tuban.facility_name = request.form.get('facility_name')
            tuban.longitude = request.form.get('longitude', type=float)
            tuban.latitude = request.form.get('latitude', type=float)
            tuban.area = request.form.get('area', type=float)
            tuban.image_date = parse_date(request.form.get('image_date'))

            # 建设主体信息
            tuban.build_unit = request.form.get('build_unit')
            tuban.build_time = parse_date(request.form.get('build_time'))
            tuban.has_approval = request.form.get('has_approval')
            tuban.approval_no = request.form.get('approval_no')

            # 发现与核查信息
            tuban.discover_time = parse_date(request.form.get('discover_time'))
            tuban.discover_method = request.form.get('discover_method')
            tuban.check_time = parse_date(request.form.get('check_time'))
            tuban.check_person = request.form.get('check_person')
            tuban.check_result = request.form.get('check_result')

            # 问题与违法信息
            tuban.problem_type = request.form.get('problem_type')
            tuban.problem_desc = request.form.get('problem_desc')
            tuban.geo_heritage_type = request.form.get('geo_heritage_type')
            tuban.impact_level = request.form.get('impact_level')
            tuban.is_illegal = request.form.get('is_illegal')
            tuban.violated_law = request.form.get('violated_law')

            # 整改信息
            tuban.rectify_measure = request.form.get('rectify_measure')
            tuban.rectify_deadline = parse_date(request.form.get('rectify_deadline'))
            tuban.rectify_status = request.form.get('rectify_status')
            tuban.rectify_verify_time = parse_date(request.form.get('rectify_verify_time'))
            tuban.verify_person = request.form.get('verify_person')
            tuban.is_closed = request.form.get('is_closed')

            # 处罚信息
            tuban.is_punished = request.form.get('is_punished')
            tuban.punish_type = request.form.get('punish_type')
            tuban.fine_amount = request.form.get('fine_amount', type=float)
            tuban.punish_doc_no = request.form.get('punish_doc_no')

            # 管理信息
            tuban.data_source = request.form.get('data_source')
            tuban.is_patrol_point = request.form.get('is_patrol_point')
            tuban.responsible_dept = request.form.get('responsible_dept')

            # 处理附件上传
            if 'attachment_file' in request.files:
                file = request.files['attachment_file']
                if file and file.filename != '':
                    # 检查文件类型
                    allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'zip', 'rar'}
                    if allowed_file(file.filename, allowed_extensions):
                        # 生成唯一文件名
                        filename = f"attachment_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                        # 确保上传目录存在
                        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

                        # 保存文件
                        file.save(filepath)

                        # 保存相对路径
                        tuban.attachments = filename
                    else:
                        flash('附件格式不支持，请上传PDF、Word、图片或压缩包文件', 'warning')
                        tuban.attachments = request.form.get('attachments')  # 保持原有值
                else:
                    tuban.attachments = request.form.get('attachments')
            else:
                tuban.attachments = request.form.get('attachments')

            tuban.remark = request.form.get('remark')

            # 处理附件（支持多附件，用逗号分隔）
            tuban.attachments = request.form.get('attachments', '')

            db.session.commit()

            flash('图斑更新成功！', 'success')
            return redirect(url_for('tuban.detail', id=tuban.id))

        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
            return redirect(url_for('tuban.edit', id=id))

    # GET请求时，获取字典数据
    func_zones = Dictionary.query.filter_by(dict_type='func_zone').order_by(Dictionary.sort_order).all()

    return render_template('tuban_form.html', action='edit', tuban=tuban, func_zones=func_zones)

@tuban_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """删除图斑（软删除）"""
    tuban = Tuban.query.get_or_404(id)

    try:
        tuban.is_deleted = 1
        db.session.commit()
        flash('图斑已删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')

    return redirect(url_for('tuban.list'))

@tuban_bp.route('/add_rectify_record/<int:id>', methods=['POST'])
def add_rectify_record(id):
    """添加整改跟踪记录"""
    tuban = Tuban.query.get_or_404(id)

    try:
        record = RectifyRecord(
            tuban_id=id,
            status=request.form.get('status'),
            content=request.form.get('content'),
            operator=request.form.get('operator'),
            record_time=datetime.now()
        )

        # 如果状态是"已整改"，更新图斑的整改状态
        if request.form.get('status') == '已整改':
            tuban.rectify_status = '已整改'
            tuban.rectify_verify_time = datetime.now().date()
            tuban.verify_person = request.form.get('operator')
            tuban.is_closed = '是'

        db.session.add(record)
        db.session.commit()

        flash('整改记录添加成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'添加失败：{str(e)}', 'error')

    return redirect(url_for('tuban.detail', id=id))

@tuban_bp.route('/export_excel')
def export_excel():
    """导出Excel"""
    # 获取查询参数（与列表页相同）
    search_keyword = request.args.get('search', '', type=str)
    park_name = request.args.get('park_name', '', type=str)
    problem_type = request.args.get('problem_type', '', type=str)
    rectify_status = request.args.get('rectify_status', '', type=str)
    func_zone = request.args.get('func_zone', '', type=str)

    # 构建查询（与列表页相同逻辑）
    query = Tuban.query.filter_by(is_deleted=0)

    if search_keyword:
        query = query.filter(
            db.or_(
                Tuban.tuban_code.contains(search_keyword),
                Tuban.facility_name.contains(search_keyword),
                Tuban.build_unit.contains(search_keyword)
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

@tuban_bp.route('/import', methods=['POST'])
def import_excel():
    """导入Excel"""
    if 'file' not in request.files:
        flash('请选择文件', 'error')
        return redirect(url_for('tuban.list'))

    file = request.files['file']
    if file.filename == '':
        flash('请选择文件', 'error')
        return redirect(url_for('tuban.list'))

    if file and allowed_file(file.filename, current_app.config['EXCEL_ALLOWED_EXTENSIONS']):
        try:
            # 保存上传的文件
            filename = f"import_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # 导入数据
            count = import_tubans_from_excel(filepath)

            flash(f'成功导入 {count} 条图斑数据！', 'success')

            # 删除临时文件
            os.remove(filepath)

        except Exception as e:
            flash(f'导入失败：{str(e)}', 'error')
    else:
        flash('文件格式不正确，请上传Excel文件', 'error')

    return redirect(url_for('tuban.list'))

@tuban_bp.route('/upload_attachment', methods=['POST'])
def upload_attachment():
    """AJAX上传附件"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})

    try:
        # 检查文件类型
        allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'zip', 'rar'}
        if not allowed_file(file.filename, allowed_extensions):
            return jsonify({'success': False, 'message': '文件格式不支持'})

        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > current_app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'success': False, 'message': '文件大小超过16MB限制'})

        # 生成唯一文件名
        filename = f"attachment_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # 确保上传目录存在
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        # 保存文件
        file.save(filepath)

        return jsonify({'success': True, 'filename': filename})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@tuban_bp.route('/download/<filename>')
def download_attachment(filename):
    """下载附件"""
    try:
        # 安全检查：防止路径遍历攻击
        if '..' in filename or filename.startswith('/'):
            abort(404)

        # 构建完整路径
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            abort(404)

        # 发送文件
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'],
            filename,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'下载失败：{str(e)}', 'error')
        return redirect(url_for('tuban.list'))


# ========== 图片管理API ==========

@tuban_bp.route('/<int:id>/images', methods=['GET'])
def get_images(id):
    """获取图斑的所有图片"""
    tuban = Tuban.query.get_or_404(id)
    
    images = TubanImage.query.filter_by(
        tuban_id=id, 
        is_deleted=0
    ).order_by(TubanImage.uploaded_at.desc()).all()
    
    # 按类型分组
    photos = [img.to_dict() for img in images if img.image_type == 'photo']
    satellites = [img.to_dict() for img in images if img.image_type == 'satellite']
    
    return jsonify({
        'success': True,
        'photos': photos,
        'satellites': satellites,
        'total': len(images)
    })


@tuban_bp.route('/<int:id>/images', methods=['POST'])
def upload_image(id):
    """上传图片到指定图斑"""
    tuban = Tuban.query.get_or_404(id)
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    # 获取图片类型
    image_type = request.form.get('image_type', 'photo')
    if image_type not in ['photo', 'satellite']:
        return jsonify({'success': False, 'message': '无效的图片类型'})
    
    try:
        # 检查文件类型
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
        if not allowed_file(file.filename, allowed_extensions):
            return jsonify({'success': False, 'message': '只支持图片格式(JPG/PNG/GIF/BMP/WEBP)'})
        
        # 检查文件大小 (5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            return jsonify({'success': False, 'message': '图片大小不能超过5MB'})
        
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{image_type}_{id}_{uuid.uuid4().hex[:8]}.{ext}"
        
        # 创建图片目录
        images_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        os.makedirs(images_folder, exist_ok=True)
        
        # 保存文件
        filepath = os.path.join(images_folder, unique_filename)
        file.save(filepath)
        
        # 保存到数据库
        image = TubanImage(
            tuban_id=id,
            image_type=image_type,
            filename=unique_filename,
            original_name=file.filename,
            description=request.form.get('description', ''),
            file_size=file_size,
            uploaded_by=session.get('username', 'unknown')
        )
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '上传成功',
            'image': image.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})


@tuban_bp.route('/images/<int:image_id>', methods=['DELETE'])
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
        
        return jsonify({'success': True, 'message': '删除成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


@tuban_bp.route('/images/<filename>')
def serve_image(filename):
    """提供图片访问"""
    try:
        # 安全检查
        if '..' in filename or filename.startswith('/'):
            abort(404)
        
        images_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        return send_from_directory(images_folder, filename)
        
    except Exception:
        abort(404)