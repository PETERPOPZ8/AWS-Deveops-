import html
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "students.db"))
STATIC_DIR = BASE_DIR / "static"
APP_HOST = os.environ.get("APP_HOST", "127.0.0.1")
APP_PORT = int(os.environ.get("APP_PORT", "5000"))


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                address TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """
        )

        if connection.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            connection.executemany(
                """
                INSERT INTO students (name, department, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    ("Ananya Sharma", "Computer Science", "ananya@example.com", "9876543210", "Chennai"),
                    ("Rahul Kumar", "Mechanical", "rahul@example.com", "9876543211", "Bengaluru"),
                    ("Meera Nair", "Electronics", "meera@example.com", "9876543212", "Kochi"),
                ],
            )

        if connection.execute("SELECT COUNT(*) FROM staff").fetchone()[0] == 0:
            connection.executemany(
                "INSERT INTO staff (name, department, email) VALUES (?, ?, ?)",
                [
                    ("Priya Menon", "Computer Science", "priya.staff@example.com"),
                    ("Arun Das", "Mechanical", "arun.staff@example.com"),
                    ("Kavya Rao", "Electronics", "kavya.staff@example.com"),
                ],
            )


def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def nav(active):
    items = [
        ("dashboard", "/dashboard", "fa-house", "Dashboard"),
        ("students", "/students", "fa-user-graduate", "Students"),
        ("courses", "/courses", "fa-book", "Courses"),
        ("settings", "/settings", "fa-gear", "Settings"),
    ]
    links = "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">'
        f'<i class="fa-solid {icon}"></i>{label}</a>'
        for key, href, icon, label in items
    )
    return f'<aside class="sidebar"><div class="brand">EduFlow</div><nav class="nav">{links}</nav></aside>'


def page(title, active, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <link rel="stylesheet" href="/static/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
</head>
<body>
    <div class="app-shell">
        {nav(active)}
        <main class="main-content">{body}</main>
    </div>
</body>
</html>"""


def login_page():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EduFlow Login</title>
    <link rel="stylesheet" href="/static/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
</head>
<body>
    <main class="login-page">
        <section class="login-box">
            <h1>EduFlow</h1>
            <p>Sign in to manage students, departments, and staff records.</p>
            <form action="/dashboard" method="post">
                <div class="field">
                    <label for="email">Email Address</label>
                    <div class="input-box">
                        <i class="fa-regular fa-envelope"></i>
                        <input id="email" name="email" type="email" placeholder="admin@eduflow.com" required>
                    </div>
                </div>
                <div class="field">
                    <label for="password">Password</label>
                    <div class="input-box">
                        <i class="fa-solid fa-lock"></i>
                        <input id="password" name="password" type="password" placeholder="Password" required>
                    </div>
                </div>
                <button class="primary-btn" type="submit">
                    <i class="fa-solid fa-right-to-bracket"></i> Sign In
                </button>
            </form>
        </section>
    </main>
</body>
</html>"""


def dashboard_page():
    with get_connection() as connection:
        total_students = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        total_staff = connection.execute("SELECT COUNT(*) FROM staff").fetchone()[0]
        departments = connection.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT department FROM students
                UNION
                SELECT department FROM staff
            )
            """
        ).fetchone()[0]
        recent = connection.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5").fetchall()

    rows = "".join(
        f"<tr><td>{student['id']}</td><td>{esc(student['name'])}</td>"
        f"<td>{esc(student['department'])}</td><td>{esc(student['email'])}</td></tr>"
        for student in recent
    ) or '<tr><td class="empty" colspan="4">No students added yet.</td></tr>'

    body = f"""
<div class="top-bar">
    <div><h1>Dashboard</h1><p class="muted">Overview of your student management system.</p></div>
    <a class="add-btn" href="/add-student"><i class="fa-solid fa-plus"></i>Add Student</a>
</div>
<section class="cards">
    <article class="card"><h2>{total_students}</h2><p>Total Students</p></article>
    <article class="card"><h2>{departments}</h2><p>Departments</p></article>
    <article class="card"><h2>{total_staff}</h2><p>Staff Members</p></article>
</section>
<section class="panel">
    <div class="panel-heading"><h2>Recent Students</h2><a class="secondary-btn" href="/students"><i class="fa-solid fa-table-list"></i>View All</a></div>
    <table>
        <thead><tr><th>ID</th><th>Name</th><th>Department</th><th>Email</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
</section>"""
    return page("Dashboard | EduFlow", "dashboard", body)


def students_page(search=""):
    with get_connection() as connection:
        if search:
            students = connection.execute(
                """
                SELECT * FROM students
                WHERE name LIKE ? OR department LIKE ? OR email LIKE ?
                ORDER BY id DESC
                """,
                (f"%{search}%", f"%{search}%", f"%{search}%"),
            ).fetchall()
        else:
            students = connection.execute("SELECT * FROM students ORDER BY id DESC").fetchall()

    rows = ""
    for student in students:
        rows += f"""
<tr>
    <td>{student['id']}</td>
    <td>{esc(student['name'])}</td>
    <td>{esc(student['department'])}</td>
    <td>{esc(student['email'])}</td>
    <td>{esc(student['phone'] or "-")}</td>
    <td>
        <div class="actions">
            <a class="edit-btn" href="/edit-student/{student['id']}"><i class="fa-solid fa-pen"></i>Edit</a>
            <form class="inline-form" action="/delete-student/{student['id']}" method="post">
                <button class="delete-btn" type="submit" onclick="return confirm('Delete this student?')">
                    <i class="fa-solid fa-trash"></i>Delete
                </button>
            </form>
        </div>
    </td>
</tr>"""
    if not rows:
        rows = '<tr><td class="empty" colspan="6">No student records found.</td></tr>'

    body = f"""
<div class="top-bar">
    <div><h1>Student Management</h1><p class="muted">Add, edit, search, and delete student records.</p></div>
    <a class="add-btn" href="/add-student"><i class="fa-solid fa-plus"></i>Add Student</a>
</div>
<section class="panel">
    <div class="panel-heading">
        <form class="search-form" action="/students" method="get">
            <input name="search" type="search" value="{esc(search)}" placeholder="Search by name, department, or email">
            <button class="secondary-btn" type="submit"><i class="fa-solid fa-magnifying-glass"></i>Search</button>
        </form>
    </div>
    <table>
        <thead><tr><th>ID</th><th>Name</th><th>Department</th><th>Email</th><th>Phone</th><th>Action</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
</section>"""
    return page("Students | EduFlow", "students", body)


def student_form_page(student=None, error=""):
    title = "Edit Student" if student else "Add Student"
    action_text = "Save Student"
    name = esc(student["name"] if student else "")
    department = esc(student["department"] if student else "")
    email = esc(student["email"] if student else "")
    phone = esc(student["phone"] if student else "")
    address = esc(student["address"] if student else "")
    alert = f'<div class="alert">{esc(error)}</div>' if error else ""

    body = f"""
<div class="top-bar">
    <div><h1>{title}</h1><p class="muted">Keep student details accurate and easy to find.</p></div>
</div>
<section class="form-card">
    {alert}
    <form method="post">
        <div class="form-grid">
            <div class="field"><label for="name">Student Name</label><input id="name" name="name" value="{name}" required></div>
            <div class="field"><label for="department">Department</label><input id="department" name="department" value="{department}" required></div>
            <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" value="{email}" required></div>
            <div class="field"><label for="phone">Phone</label><input id="phone" name="phone" value="{phone}"></div>
            <div class="field full"><label for="address">Address</label><textarea id="address" name="address">{address}</textarea></div>
        </div>
        <div class="form-actions">
            <a class="secondary-btn" href="/students">Cancel</a>
            <button class="add-btn" type="submit"><i class="fa-solid fa-floppy-disk"></i>{action_text}</button>
        </div>
    </form>
</section>"""
    return page(f"{title} | EduFlow", "students", body)


def courses_page():
    with get_connection() as connection:
        departments = connection.execute(
            "SELECT department, COUNT(*) AS total FROM students GROUP BY department ORDER BY department"
        ).fetchall()
    rows = "".join(
        f"<tr><td>{esc(row['department'])}</td><td>{row['total']}</td></tr>" for row in departments
    ) or '<tr><td class="empty" colspan="2">No departments found.</td></tr>'
    body = f"""
<div class="top-bar">
    <div><h1>Departments</h1><p class="muted">Student count grouped by department.</p></div>
</div>
<section class="panel">
    <table><thead><tr><th>Department</th><th>Total Students</th></tr></thead><tbody>{rows}</tbody></table>
</section>"""
    return page("Courses | EduFlow", "courses", body)


def settings_page():
    body = """
<div class="top-bar">
    <div><h1>Settings</h1><p class="muted">Local SQLite database is stored as students.db in this project folder.</p></div>
</div>
<section class="form-card">
    <h2>Project Status</h2>
    <p class="muted">Frontend, backend routes, and database tables are connected.</p>
</section>"""
    return page("Settings | EduFlow", "settings", body)


def parse_form(handler):
    length = int(handler.headers.get("Content-Length", 0))
    raw_body = handler.rfile.read(length).decode("utf-8")
    parsed = parse_qs(raw_body)
    return {key: values[0].strip() for key, values in parsed.items()}


class StudentManagementHandler(BaseHTTPRequestHandler):
    def send_html(self, content, status=200):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        query = parse_qs(parsed.query)

        if path == "/health":
            self.send_html("OK")
        elif path == "/static/style.css":
            css = (STATIC_DIR / "style.css").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(css)))
            self.end_headers()
            self.wfile.write(css)
        elif path == "/":
            self.send_html(login_page())
        elif path == "/dashboard":
            self.send_html(dashboard_page())
        elif path == "/students":
            self.send_html(students_page(query.get("search", [""])[0].strip()))
        elif path == "/add-student":
            self.send_html(student_form_page())
        elif path.startswith("/edit-student/"):
            student_id = path.rsplit("/", 1)[-1]
            with get_connection() as connection:
                student = connection.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
            self.send_html(student_form_page(student) if student else students_page())
        elif path == "/courses":
            self.send_html(courses_page())
        elif path == "/settings":
            self.send_html(settings_page())
        else:
            self.send_html(page("Not Found", "dashboard", "<h1>Page not found</h1>"), 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        form = parse_form(self)

        if path == "/dashboard":
            self.redirect("/dashboard")
        elif path == "/add-student":
            error = save_student(form)
            self.redirect("/students") if not error else self.send_html(student_form_page(error=error), 400)
        elif path.startswith("/edit-student/"):
            student_id = path.rsplit("/", 1)[-1]
            error = save_student(form, student_id)
            if error:
                with get_connection() as connection:
                    student = connection.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
                self.send_html(student_form_page(student, error), 400)
            else:
                self.redirect("/students")
        elif path.startswith("/delete-student/"):
            student_id = path.rsplit("/", 1)[-1]
            with get_connection() as connection:
                connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
            self.redirect("/students")
        else:
            self.send_html(page("Not Found", "dashboard", "<h1>Page not found</h1>"), 404)


def save_student(form, student_id=None):
    name = form.get("name", "")
    department = form.get("department", "")
    email = form.get("email", "")
    phone = form.get("phone", "")
    address = form.get("address", "")

    if not name or not department or not email:
        return "Name, department, and email are required."

    try:
        with get_connection() as connection:
            if student_id:
                connection.execute(
                    """
                    UPDATE students
                    SET name = ?, department = ?, email = ?, phone = ?, address = ?
                    WHERE id = ?
                    """,
                    (name, department, email, phone, address, student_id),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO students (name, department, email, phone, address)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (name, department, email, phone, address),
                )
    except sqlite3.IntegrityError:
        return "A student with this email already exists."
    return ""


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer((APP_HOST, APP_PORT), StudentManagementHandler)
    print(f"Student Management System running at http://{APP_HOST}:{APP_PORT}")
    server.serve_forever()
