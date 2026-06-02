import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Login Page
@app.route('/')
def login():
    return render_template('login.html')


# Dashboard Page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# Student Page
@app.route('/students')
def students():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students_data = cursor.fetchall()

    conn.close()

    return render_template("student.html", students=students_data)


# Add Student Page
@app.route('/add-student', methods=['GET', 'POST'])
def add_student():

    if request.method == 'POST':

        name = request.form['name']
        department = request.form['department']
        email = request.form['email']

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO students (name, department, email) VALUES (?, ?, ?)",
            (name, department, email)
        )

        conn.commit()
        conn.close()

        return redirect('/students')

    return render_template('add_student.html')
@app.route('/delete-student/<int:id>')
def delete_student(id):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect('/students')
@app.route('/edit-student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        department = request.form['department']
        email = request.form['email']

        cursor.execute(
            "UPDATE students SET name=?, department=?, email=? WHERE id=?",
            (name, department, email, id)
        )

        conn.commit()
        conn.close()

        return redirect('/students')

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()

    conn.close()

    return render_template('edit_student.html', student=student)

    if request.method == 'POST':
        return redirect('/students')

    return render_template('edit_student.html')
if __name__ == '__main__':
    app.run(debug=True)
    