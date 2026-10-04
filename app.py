from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = "paria-demo-secret-change-this"
DB = "paria.db"
ADMIN_PASSWORD = "1234"  # رمز نمونه؛ برای استفاده واقعی عوضش کنید.


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            package TEXT NOT NULL,
            project_type TEXT,
            description TEXT,
            amount INTEGER DEFAULT 0,
            payment_status TEXT DEFAULT 'در انتظار پرداخت',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return render_template("index.html")


@app.post("/submit")
def submit():
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    package = request.form.get("package", "").strip()
    project_type = request.form.get("project_type", "").strip()
    description = request.form.get("description", "").strip()

    if not full_name or not phone or not package or not description:
        flash("لطفاً اطلاعات ضروری را کامل کنید.", "error")
        return redirect(url_for("home") + "#contact")

    prices = {"پایه": 8900000, "حرفه‌ای": 14900000, "اختصاصی": 0}
    amount = prices.get(package, 0)
    con = db()
    cur = con.execute(
        "INSERT INTO requests(full_name, phone, package, project_type, description, amount, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (full_name, phone, package, project_type, description, amount, "در انتظار پرداخت")
    )
    request_id = cur.lastrowid
    con.commit()
    con.close()
    return redirect(url_for("payment", request_id=request_id))


@app.route("/payment/<int:request_id>")
def payment(request_id):
    con = db()
    r = con.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    con.close()
    if not r:
        return "درخواست پیدا نشد.", 404
    return render_template("payment.html", r=r)


@app.post("/payment/<int:request_id>/demo")
def demo_payment(request_id):
    con = db()
    r = con.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not r:
        con.close()
        return "درخواست پیدا نشد.", 404
    con.execute("UPDATE requests SET payment_status = 'پرداخت آزمایشی موفق' WHERE id = ?", (request_id,))
    con.commit()
    con.close()
    return redirect(url_for("payment_success", request_id=request_id))


@app.route("/payment/<int:request_id>/success")
def payment_success(request_id):
    con = db()
    r = con.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    con.close()
    if not r:
        return "درخواست پیدا نشد.", 404
    return render_template("payment_success.html", r=r)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        flash("رمز ورود صحیح نیست.", "error")
    return render_template("admin_login.html")


@app.route("/admin")
@admin_required
def admin():
    con = db()
    requests = con.execute("SELECT * FROM requests ORDER BY id DESC").fetchall()
    con.close()
    return render_template("admin.html", requests=requests)


@app.post("/admin/delete/<int:request_id>")
@admin_required
def delete_request(request_id):
    con = db()
    con.execute("DELETE FROM requests WHERE id = ?", (request_id,))
    con.commit()
    con.close()
    return redirect(url_for("admin"))


@app.get("/admin/logout")
@admin_required
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/portfolio/atrisaa")
def atrisaa():
    return render_template("atrisaa.html")


@app.route("/portfolio/ark")
def ark():
    return render_template("ark.html")


@app.route("/portfolio/rosha")
def rosha():
    return render_template("rosha.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
