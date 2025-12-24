from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "college_secret_key"
DB_NAME = "database.db"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_tables()

# ---------- LOGIN ----------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        role = request.form['role']

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE userid=? AND password=? AND role=?",
            (userid, password, role)
        ).fetchone()
        conn.close()

        if user:
            session['userid'] = userid
            session['role'] = role
            return redirect(url_for('dashboard'))

        return render_template('login.html', error="Invalid login details")

    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'userid' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', role=session['role'])

# ---------- CREATE USER ----------
@app.route('/admin/create', methods=['GET', 'POST'])
def admin_create_user():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    msg = ""
    if request.method == 'POST':
        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (userid,password,role) VALUES (?,?,?)",
                (request.form['userid'], request.form['password'], request.form['role'])
            )
            conn.commit()
            conn.close()
            msg = "User created successfully"
        except:
            msg = "User ID already exists"

    return render_template("admin_create_user.html", msg=msg)

# ---------- VIEW USERS ----------
@app.route('/admin/users')
def admin_users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return render_template("admin_users.html", users=users)

# ---------- DELETE USER ----------
@app.route('/admin/delete/<int:id>')
def delete_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_users'))

# ---------- EDIT USER ----------
@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()

    if request.method == 'POST':
        conn.execute("""
            UPDATE users SET userid=?, password=?, role=? WHERE id=?
        """, (
            request.form['userid'],
            request.form['password'],
            request.form['role'],
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_users'))

    user = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("admin_edit_user.html", user=user)

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
