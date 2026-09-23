from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("email_address")
EMAIL_APP_PASSWORD = os.getenv("password")

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, "students_accounts.db")


# ==============================
# DATABASE CONNECTION
# ==============================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ==============================
# LOGIN
# ==============================

@app.route("/", methods=["GET", "POST"])
def home():

    error = None

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        connection = get_db_connection()

        user = connection.execute(
                """
                SELECT *
                FROM data
                WHERE id_number = ?
                """,
                (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            # Store student information in session
            session["student_id"] = user["id_number"]
            session["student_name"] = user["name"]

            # Redirect to dashboard
            return redirect(url_for("dashboard"))

        else:

            error = "Invalid Student ID or Password"

    return render_template(
        "login.html",
        error=error
    )


# ==============================
# DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    # Check whether user is logged in
    if "student_id" not in session:
        return redirect(url_for("home"))

    return render_template(
        "dashboard.html",
        student_name=session["student_name"],
        student_id=session["student_id"]
    )


# ==============================
# PROFILE
# ==============================

@app.route("/profile")
def profile():

    # Check whether user is logged in
    if "student_id" not in session:
        return redirect(url_for("home"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT *
        FROM data
        WHERE id_number = ?
        """,
        (session["student_id"],)
    ).fetchone()

    connection.close()

    return render_template(
        "profile.html",
        student=student
    )

# ==============================
# VIEW ALL STUDENTS
# ==============================

@app.route("/students")
def students():

    # Check whether user is logged in
    if "student_id" not in session:
        return redirect(url_for("home"))

    connection = get_db_connection()

    students = connection.execute(
        """
        SELECT id_number, name, age, gender, phone_number, class, email
        FROM data
        ORDER BY id_number
        """
    ).fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=students
    )

# ==============================
# SEARCH STUDENT
# ==============================

@app.route("/search", methods=["GET", "POST"])
def search_student():

    # Check whether user is logged in
    if "student_id" not in session:
        return redirect(url_for("home"))

    students = []
    search_query = ""

    if request.method == "POST":

        search_query = request.form.get("search", "").strip()

        if search_query:

            connection = get_db_connection()

            students = connection.execute(
                """
                SELECT id_number, name, age, gender, phone_number, class, email
                FROM data
                WHERE id_number LIKE ?
                OR name LIKE ?
                ORDER BY id_number
                """,
                (
                    "%" + search_query + "%",
                    "%" + search_query + "%"
                )
            ).fetchall()

            connection.close()

    return render_template(
        "search.html",
        students=students,
        search_query=search_query
    )


# ==============================
# ADD STUDENT
# ==============================

@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    # Check whether user is logged in
    if "student_id" not in session:
        return redirect(url_for("home"))

    error = None
    success = None

    if request.method == "POST":

        student_id = request.form.get("id_number", "").strip()
        password = request.form.get("password", "").strip()
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone_number", "").strip()
        student_class = request.form.get("class", "").strip()
        email = request.form.get("email", "").strip()

        # Check required fields
        if not all([
            student_id,
            password,
            name,
            age,
            gender,
            phone,
            student_class,
            email
        ]):
            error = "Please fill all fields."

        else:

            try:

                connection = get_db_connection()

                # Check whether Student ID already exists
                existing_student = connection.execute(
                    """
                    SELECT id_number
                    FROM data
                    WHERE id_number = ?
                    """,
                    (student_id,)
                ).fetchone()

                if existing_student:

                    error = "Student ID already exists."

                else:

                    connection.execute(
                        """
                        INSERT INTO data
                        (
                            id_number,
                            password,
                            name,
                            age,
                            gender,
                            phone_number,
                            class,
                            email
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            student_id,
                            password,
                            name,
                            age,
                            gender,
                            phone,
                            student_class,
                            email
                        )
                    )

                    connection.commit()

                    success = "Student added successfully!"

                connection.close()

            except Exception as e:

                error = f"Error: {e}"

    return render_template(
        "add_student.html",
        error=error,
        success=success
    )


# ==============================
# EDIT STUDENT
# ==============================

@app.route("/edit-student/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    if "student_id" not in session:
        return redirect(url_for("home"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT *
        FROM data
        WHERE id_number = ?
        """,
        (student_id,)
    ).fetchone()

    if not student:
        connection.close()
        return "Student not found", 404

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone_number", "").strip()
        student_class = request.form.get("class", "").strip()
        email = request.form.get("email", "").strip()

        connection.execute(
            """
            UPDATE data
            SET name = ?,
                age = ?,
                gender = ?,
                phone_number = ?,
                class = ?,
                email = ?
            WHERE id_number = ?
            """,
            (
                name,
                age,
                gender,
                phone,
                student_class,
                email,
                student_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("students"))

    connection.close()

    return render_template(
        "edit_student.html",
        student=student
    )

# ==============================
# DELETE STUDENT
# ==============================

@app.route("/delete-student/<student_id>", methods=["GET", "POST"])
def delete_student(student_id):

    if "student_id" not in session:
        return redirect(url_for("home"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT *
        FROM data
        WHERE id_number = ?
        """,
        (student_id,)
    ).fetchone()

    if not student:
        connection.close()
        return "Student not found", 404

    # Show confirmation page
    if request.method == "GET":

        connection.close()

        return render_template(
            "delete_student.html",
            student=student
        )

    # Actually delete the student
    connection.execute(
        """
        DELETE FROM data
        WHERE id_number = ?
        """,
        (student_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("students"))


# ==============================
# STUDENT CARD
# ==============================

@app.route("/student-card")
def student_card():

    if "student_id" not in session:
        return redirect(url_for("home"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT *
        FROM data
        WHERE id_number = ?
        """,
        (session["student_id"],)
    ).fetchone()

    connection.close()

    if not student:
        return "Student not found", 404

    return render_template(
        "student_card.html",
        student=student
    )

# ==============================
# SEND EMAIL
# ==============================

@app.route("/send-email", methods=["GET", "POST"])
def send_email():

    if "student_id" not in session:
        return redirect(url_for("home"))

    error = None
    success = None

    if request.method == "POST":

        recipient = request.form.get("recipient", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not recipient or not subject or not message:

            error = "Please fill all fields."

        else:

            try:

                email = EmailMessage()

                email["From"] = EMAIL_ADDRESS
                email["To"] = recipient
                email["Subject"] = subject

                email.set_content(message)

                with smtplib.SMTP("smtp.gmail.com", 587) as smtp:

                    smtp.starttls()

                    smtp.login(
                        EMAIL_ADDRESS,
                        EMAIL_APP_PASSWORD
                    )

                    smtp.send_message(email)

                success = "Email sent successfully!"

            except Exception as e:

                error = f"Failed to send email: {str(e)}"

    return render_template(
        "send_email.html",
        error=error,
        success=success
    )

# ==============================
# SETTINGS
# ==============================

@app.route("/settings", methods=["GET", "POST"])
def settings():

    if "student_id" not in session:
        return redirect(url_for("home"))

    error = None
    success = None

    if request.method == "POST":

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        connection = get_db_connection()

        student = connection.execute(
            """
            SELECT *
            FROM data
            WHERE id_number = ?
            """,
            (session["student_id"],)
        ).fetchone()

        if not student:
            connection.close()
            return "Student not found", 404

        # Check current password
        if current_password != student["password"]:

            error = "Current password is incorrect."

        # Check new passwords
        elif new_password != confirm_password:

            error = "New passwords do not match."

        # Check password length
        elif len(new_password) < 6:

            error = "New password must contain at least 6 characters."

        else:

            hashed_password = generate_password_hash(new_password)

            connection.execute(         
                """
                UPDATE data
                SET password = ?
                WHERE id_number = ?
                """,
                (hashed_password, session["student_id"])
            )

            connection.commit()

            success = "Password changed successfully."

        connection.close()

    return render_template(
        "settings.html",
        error=error,
        success=success
    )


# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    # Remove all session data
    session.clear()

    return redirect(url_for("home"))


# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":
    app.run(debug=True)