import json
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "posters.db")


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{DB_PATH}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    return app


app = create_app()
db = SQLAlchemy(app)


class Poster(db.Model):
    __tablename__ = "posters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)  # 管理名称
    template = db.Column(db.String(64), default="crab")  # 模板标识
    data_json = db.Column(db.Text, nullable=False)  # 模板数据(JSON 字符串)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def data(self):
        try:
            return json.loads(self.data_json)
        except Exception:
            return {}


@app.route("/")
def index():
    return redirect(url_for("list_posters"))


@app.route("/posters")
def list_posters():
    posters = Poster.query.order_by(Poster.updated_at.desc()).all()
    return render_template("posters_list.html", posters=posters)


def default_crab_data():
    # 从现有 crab_poster.html 提炼的默认数据
    return {
        "title": "🦀 精品大闸蟹套餐价格表",
        "highlight": {
            "badge": "人气",
            "text": "尝鲜装,2.5公1.5母十只",
            "price": "108",
        },
        "sections": [
            {
                "variant": "mixed-8",
                "heading": "公母混合 · 8只装",
                "rows": [
                    {"spec": "3.0公2.0母（公母各4只）", "price": "168"},
                    {"spec": "3.5公2.5母（公母各4只）", "price": "218"},
                    {"spec": "3.5公2.8母（公母各4只）", "price": "258"},
                    {"spec": "4.0公3.0母（公母各4只）", "price": "328"},
                ],
            },
            {
                "variant": "mixed-10",
                "heading": "公母混合 · 10只装",
                "rows": [
                    {"spec": "3.0公2.0母（公母各5只）", "price": "188"},
                    {"spec": "3.5公2.5母（公母各5只）", "price": "258"},
                    {"spec": "3.5公2.8母（公母各5只）", "price": "298"},
                    {"spec": "4.0公3.0母（公母各5只）", "price": "398"},
                ],
            },
            {
                "variant": "female-8",
                "heading": "全母精品 · 8只装",
                "rows": [
                    {"spec": "2.0母（全母8只）", "price": "158"},
                    {"spec": "2.5母（全母8只）", "price": "198"},
                    {"spec": "2.8母（全母8只）", "price": "258"},
                    {"spec": "3.0母（全母8只）", "price": "308"},
                ],
            },
            {
                "variant": "female-10",
                "heading": "全母精品 · 10只装",
                "rows": [
                    {"spec": "2.0母（全母10只）", "price": "188"},
                    {"spec": "2.5母（全母10只）", "price": "238"},
                    {"spec": "2.8母（全母10只）", "price": "298"},
                    {"spec": "3.0母（全母10只）", "price": "368"},
                ],
            },
        ],
        "promises": [
            "🌟 灵活搭配：多种套餐可供选择，满足不同口味与送礼需求～私聊可定制套餐",
            "🚚 极速配送：顺丰特快冷链直达，新鲜美味不等待",
            "📦 发货时间：当天 19:00 前下单，次日早上或下午发货，保证新鲜现捞现发",
            "🎁 精美礼盒：礼盒包装，送礼更体面，自享更有仪式感",
            "🦀 售后无忧：签收后 12 小时内如有死蟹，凭照片或视频凭证全额赔付",
            "💰 运费政策：浙沪皖享运费减免（-15元)四川、重庆、广东、云南、贵州、广西、甘肃、宁夏、内蒙古、青海、海南（+8元）  黑龙江、吉林（+20元）  西藏、新疆（+30元）",
        ],
    }


@app.route("/posters/new", methods=["GET", "POST"])
def create_poster():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        template_name = request.form.get("template", "crab").strip() or "crab"
        data_text = request.form.get("data_json", "").strip()

        if not name:
            flash("名称必填", "danger")
            return render_template(
                "poster_edit.html",
                mode="create",
                name=name,
                template_name=template_name,
                data_json=data_text or json.dumps(default_crab_data(), ensure_ascii=False, indent=2),
            )

        # 校验 JSON
        try:
            parsed = json.loads(data_text) if data_text else default_crab_data()
        except json.JSONDecodeError as e:
            flash(f"JSON 解析失败: {e}", "danger")
            return render_template(
                "poster_edit.html",
                mode="create",
                name=name,
                template_name=template_name,
                data_json=data_text,
            )

        poster = Poster(name=name, template=template_name, data_json=json.dumps(parsed, ensure_ascii=False))
        db.session.add(poster)
        db.session.commit()
        flash("创建成功", "success")
        return redirect(url_for("list_posters"))

    return render_template(
        "poster_edit.html",
        mode="create",
        name="",
        template_name="crab",
        data_json=json.dumps(default_crab_data(), ensure_ascii=False, indent=2),
    )


@app.route("/posters/<int:poster_id>/edit", methods=["GET", "POST"])
def edit_poster(poster_id: int):
    poster = Poster.query.get_or_404(poster_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        template_name = request.form.get("template", "crab").strip() or "crab"
        data_text = request.form.get("data_json", "").strip()

        if not name:
            flash("名称必填", "danger")
            return render_template(
                "poster_edit.html",
                mode="edit",
                poster=poster,
                name=name,
                template_name=template_name,
                data_json=data_text,
            )

        try:
            parsed = json.loads(data_text)
        except json.JSONDecodeError as e:
            flash(f"JSON 解析失败: {e}", "danger")
            return render_template(
                "poster_edit.html",
                mode="edit",
                poster=poster,
                name=name,
                template_name=template_name,
                data_json=data_text,
            )

        poster.name = name
        poster.template = template_name
        poster.data_json = json.dumps(parsed, ensure_ascii=False)
        db.session.commit()
        flash("保存成功", "success")
        return redirect(url_for("list_posters"))

    return render_template(
        "poster_edit.html",
        mode="edit",
        poster=poster,
        name=poster.name,
        template_name=poster.template,
        data_json=json.dumps(poster.data, ensure_ascii=False, indent=2),
    )


@app.route("/posters/<int:poster_id>/delete", methods=["POST"])
def delete_poster(poster_id: int):
    poster = Poster.query.get_or_404(poster_id)
    db.session.delete(poster)
    db.session.commit()
    flash("已删除", "info")
    return redirect(url_for("list_posters"))


@app.route("/posters/<int:poster_id>/preview")
def preview_poster(poster_id: int):
    poster = Poster.query.get_or_404(poster_id)
    if poster.template == "crab":
        return render_template("poster_crab.html", data=poster.data, poster_id=poster.id)
    abort(404)


@app.route("/posters/<int:poster_id>/json")
def poster_json(poster_id: int):
    poster = Poster.query.get_or_404(poster_id)
    return poster.data


@app.route("/posters/<int:poster_id>/update-json", methods=["POST"])
def update_poster_json(poster_id: int):
    poster = Poster.query.get_or_404(poster_id)
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return {"ok": False, "error": f"invalid json: {e}"}, 400

    if not isinstance(payload, dict):
        return {"ok": False, "error": "payload must be a JSON object"}, 400

    poster.data_json = json.dumps(payload, ensure_ascii=False)
    db.session.commit()
    return {"ok": True}


if __name__ == "__main__":
    # 首次运行自动建库
    with app.app_context():
        db.create_all()
        # 若无数据，种子一条示例
        if Poster.query.count() == 0:
            demo = Poster(name="大闸蟹价目表(示例)", template="crab", data_json=json.dumps(default_crab_data(), ensure_ascii=False))
            db.session.add(demo)
            db.session.commit()
    app.run(host="0.0.0.0", port=5000, debug=True)
