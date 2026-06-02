import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO students (name, department, email)
VALUES (?, ?, ?)
""", ("Mohamed", "BCA", "mohamed@gmail.com"))

conn.commit()
conn.close()

print("Student added successfully!")