import os
import tempfile
import unittest

os.environ["DATABASE_PATH"] = tempfile.NamedTemporaryFile(delete=False).name

import app


class StudentManagementTests(unittest.TestCase):
    def setUp(self):
        app.init_db()

    def test_dashboard_renders(self):
        html = app.dashboard_page()
        self.assertIn("Dashboard", html)
        self.assertIn("Total Students", html)

    def test_student_crud(self):
        email = "devops.test@example.com"
        error = app.save_student(
            {
                "name": "DevOps Test",
                "department": "Cloud",
                "email": email,
                "phone": "9999999999",
                "address": "Test Address",
            }
        )
        self.assertEqual(error, "")

        with app.get_connection() as connection:
            student = connection.execute(
                "SELECT * FROM students WHERE email = ?", (email,)
            ).fetchone()

        self.assertIsNotNone(student)


if __name__ == "__main__":
    unittest.main()
