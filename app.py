from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import pandas as pd

from ml_model import model, accuracy

app = Flask(__name__)


# ==============================
# MYSQL DATABASE CONNECTION
# ==============================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ProjectDb@2026!K7",
        database="defence_db"
    )


# ==============================
# HOME PAGE
# ==============================
@app.route("/")
def home():
    return render_template(
        "index.html",
        prediction=None,
        accuracy=accuracy
    )


# ==============================
# PREDICT EQUIPMENT MAINTENANCE
# ==============================
@app.route("/predict", methods=["POST"])
def predict():
    conn = None
    cursor = None

    try:
        equipment_name = request.form.get("equipment_name", "").strip()
        temperature = float(request.form.get("temperature", ""))
        vibration = float(request.form.get("vibration", ""))
        operating_hours = float(request.form.get("operating_hours", ""))

        # Input validation
        if not equipment_name:
            return "Equipment name is required.", 400

        if not (-50 <= temperature <= 200):
            return "Invalid temperature. Enter a value from -50 to 200.", 400

        if not (0 <= vibration <= 100):
            return "Invalid vibration. Enter a value from 0 to 100.", 400

        if not (0 <= operating_hours <= 100000):
            return "Invalid operating hours.", 400

        # Generate ML prediction
        sample = pd.DataFrame(
            [[temperature, vibration, operating_hours]],
            columns=[
                "temperature",
                "vibration",
                "operating_hours"
            ]
        )

        result = model.predict(sample)[0]

        if result == 1:
            prediction = "Maintenance Required"
        else:
            prediction = "Normal"

        # Save prediction in MySQL
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO equipment
            (
                equipment_name,
                temperature,
                vibration,
                operating_hours,
                prediction
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            equipment_name,
            temperature,
            vibration,
            operating_hours,
            prediction
        )

        cursor.execute(query, values)
        conn.commit()

        # Show result on the front page
        return render_template(
            "index.html",
            prediction=prediction,
            accuracy=accuracy
        )

    except ValueError:
        return "Please enter valid numeric values in all measurement fields.", 400

    except mysql.connector.Error as error:
        if conn is not None:
            conn.rollback()

        print("MySQL Error:", error)
        return "Database error occurred. Check that MySQL is running and the database settings are correct.", 500

    except Exception as error:
        if conn is not None:
            conn.rollback()

        print("Prediction Error:", error)
        return "An error occurred while generating the prediction. Check the terminal for details.", 500

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


# ==============================
# DASHBOARD
# ==============================
@app.route("/dashboard")
def dashboard():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM equipment")
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM equipment "
            "WHERE prediction = %s",
            ("Maintenance Required",)
        )
        maintenance_count = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM equipment "
            "WHERE prediction = %s",
            ("Normal",)
        )
        normal_count = cursor.fetchone()["total"]

        return render_template(
            "dashboard.html",
            total=total,
            maintenance_count=maintenance_count,
            normal_count=normal_count,
            accuracy=accuracy
        )

    except mysql.connector.Error as error:
        print("Dashboard Database Error:", error)
        return "Unable to load dashboard. Check MySQL and database settings.", 500

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


# ==============================
# VIEW ALL EQUIPMENT RECORDS
# ==============================
@app.route("/records")
def records():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM equipment ORDER BY id DESC"
        )
        all_records = cursor.fetchall()

        return render_template(
            "records.html",
            records=all_records
        )

    except mysql.connector.Error as error:
        print("Records Database Error:", error)
        return "Unable to load equipment records. Check MySQL.", 500

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


# ==============================
# EDIT EQUIPMENT RECORD
# ==============================
@app.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == "POST":
            equipment_name = request.form.get("equipment_name", "").strip()

            if not equipment_name:
                return "Equipment name is required.", 400

            temperature = float(request.form.get("temperature", ""))
            vibration = float(request.form.get("vibration", ""))
            operating_hours = float(request.form.get("operating_hours", ""))

            if not (-50 <= temperature <= 200):
                return "Invalid temperature.", 400

            if not (0 <= vibration <= 100):
                return "Invalid vibration value.", 400

            if not (0 <= operating_hours <= 100000):
                return "Invalid operating hours.", 400

            cursor.execute(
                """
                UPDATE equipment
                SET equipment_name = %s,
                    temperature = %s,
                    vibration = %s,
                    operating_hours = %s
                WHERE id = %s
                """,
                (
                    equipment_name,
                    temperature,
                    vibration,
                    operating_hours,
                    record_id
                )
            )

            conn.commit()
            return redirect(url_for("records"))

        cursor.execute(
            "SELECT * FROM equipment WHERE id = %s",
            (record_id,)
        )
        record = cursor.fetchone()

        if record is None:
            return "Equipment record not found.", 404

        return render_template("edit.html", record=record)

    except ValueError:
        if conn is not None:
            conn.rollback()

        return "Please enter valid numeric values.", 400

    except mysql.connector.Error as error:
        if conn is not None:
            conn.rollback()

        print("Edit Database Error:", error)
        return "Unable to edit this record. Check MySQL.", 500

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


# ==============================
# DELETE EQUIPMENT RECORD
# ==============================
@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM equipment WHERE id = %s",
            (record_id,)
        )
        conn.commit()

        return redirect(url_for("records"))

    except mysql.connector.Error as error:
        if conn is not None:
            conn.rollback()

        print("Delete Database Error:", error)
        return "Unable to delete this record. Check MySQL.", 500

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


# ==============================
# RUN FLASK APPLICATION
# ==============================
if __name__ == "__main__":
    app.run(debug=True)