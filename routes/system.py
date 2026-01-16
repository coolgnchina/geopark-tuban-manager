from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import db
from models.dictionary import Dictionary
from models.tuban import Tuban

system_bp = Blueprint("system", __name__)


@system_bp.route("/dictionaries")
def dictionaries():
    """字典管理"""
    # 获取所有字典类型
    dict_types = db.session.query(Dictionary.dict_type).distinct().all()
    dict_types = [t.dict_type for t in dict_types]

    # 获取当前选中的类型
    current_type = request.args.get("type", dict_types[0] if dict_types else "")

    # 获取字典项
    items = []
    if current_type:
        items = (
            Dictionary.query.filter_by(dict_type=current_type)
            .order_by(Dictionary.sort_order, Dictionary.id)
            .all()
        )

    return render_template(
        "dictionaries.html",
        dict_types=dict_types,
        current_type=current_type,
        items=items,
    )


@system_bp.route("/dictionaries/add", methods=["POST"])
def add_dictionary():
    """添加字典项"""
    dict_type = request.form.get("dict_type")
    dict_code = request.form.get("dict_code")
    dict_value = request.form.get("dict_value")
    sort_order = request.form.get("sort_order", 0, type=int)

    try:
        # 检查是否已存在
        existing = Dictionary.query.filter_by(
            dict_type=dict_type, dict_code=dict_code
        ).first()
        if existing:
            flash("该字典代码已存在！", "error")
            return redirect(url_for("system.dictionaries", type=dict_type))

        # 创建新字典项
        item = Dictionary()
        item.dict_type = dict_type
        item.dict_code = dict_code
        item.dict_value = dict_value
        item.sort_order = sort_order

        db.session.add(item)
        db.session.commit()

        flash("字典项添加成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"添加失败：{str(e)}", "error")

    return redirect(url_for("system.dictionaries", type=dict_type))


@system_bp.route("/dictionaries/edit/<int:id>", methods=["POST"])
def edit_dictionary(id):
    """编辑字典项"""
    item = Dictionary.query.get_or_404(id)

    try:
        item.dict_code = request.form.get("dict_code")
        item.dict_value = request.form.get("dict_value")
        item.sort_order = request.form.get("sort_order", 0, type=int)

        db.session.commit()

        flash("字典项更新成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"更新失败：{str(e)}", "error")

    return redirect(url_for("system.dictionaries", type=item.dict_type))


@system_bp.route("/dictionaries/delete/<int:id>", methods=["POST"])
def delete_dictionary(id):
    """删除字典项"""
    item = Dictionary.query.get_or_404(id)
    dict_type = item.dict_type

    try:
        # 检查是否被使用
        # 这里可以根据实际情况检查各个字段
        db.session.delete(item)
        db.session.commit()

        flash("字典项删除成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"删除失败：{str(e)}", "error")

    return redirect(url_for("system.dictionaries", type=dict_type))


@system_bp.route("/api/dictionaries/<string:dict_type>")
def api_dictionaries(dict_type):
    """获取字典项API"""
    items = (
        Dictionary.query.filter_by(dict_type=dict_type)
        .order_by(Dictionary.sort_order)
        .all()
    )
    return jsonify(
        [{"dict_code": item.dict_code, "dict_value": item.dict_value} for item in items]
    )


@system_bp.route("/settings")
def settings():
    """系统设置"""
    return render_template("settings.html")


@system_bp.route("/logs")
def logs():
    """操作日志"""
    return render_template("logs.html")


@system_bp.route("/about")
def about():
    """关于系统"""
    return render_template("about.html")
