from flask import Flask, render_template, request, redirect, send_file, session
import sqlite3
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "secret123"   # required for login session

# ------------------ DATABASE ------------------
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        branch TEXT,
        rollno TEXT,
        email TEXT,
        phone TEXT,
        events TEXT,
        payment_status TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ------------------ HOME ------------------
@app.route('/')
def index():
    return render_template('index.html')

# ------------------ REGISTER ------------------
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    branch = request.form.get('branch')
    rollno = request.form.get('rollno')
    email = request.form.get('email')
    phone = request.form.get('phone')
    events_list = request.form.getlist('event')

    # Validation
    if not name or not branch or not rollno or not email or not phone:
        return "All fields are required!"

    if not events_list:
        return "Please select at least one event!"

    if len(phone) != 10 or not phone.isdigit():
        return "Enter valid 10-digit phone number!"

    events = ",".join(events_list)
    payment_status = "Paid"

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students(name,branch,rollno,email,phone,events,payment_status)
        VALUES(?,?,?,?,?,?,?)
    """, (name, branch, rollno, email, phone, events, payment_status))

    conn.commit()
    conn.close()

    return render_template('success.html',
                       name=name,
                       branch=branch,
                       rollno=rollno,
                       events=events)

# ------------------ CERTIFICATE ------------------
@app.route('/certificate/<name>/<branch>/<rollno>/<events>')
def certificate(name, branch, rollno, events):
    from fpdf import FPDF
    from datetime import datetime

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 10, "VIDYA JYOTHI INSTITUTION OF TECHNOLOGY", ln=True, align='C')

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 10, "Certificate of Participation", ln=True, align='C')

    pdf.ln(15)
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, "This is to certify that", ln=True, align='C')

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, name, ln=True, align='C')

    pdf.cell(200, 10, f"{branch} - {rollno}", ln=True, align='C')

    pdf.ln(10)
    pdf.cell(200, 10, "has participated in", ln=True, align='C')

    pdf.multi_cell(200, 10, events, align='C')

    pdf.ln(10)
    today = datetime.now().strftime("%d-%m-%Y")
    pdf.cell(200, 10, f"Date: {today}", ln=True, align='L')

    file_name = f"{name}_certificate.pdf"
    pdf.output(file_name)

    return send_file(file_name, as_attachment=True)
# ------------------ LOGIN PAGE ------------------
# ------------------ LOGIN PAGE ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # You need to catch the password from the form!

        # This looks for the password on the server settings, 
        # but uses "1856" as a backup (fallback)
        import os
        CORRECT_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1856')

        if username == "Akshaya" and password == CORRECT_PASSWORD:
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Invalid Login!"

    return render_template('login.html')
# ------------------ ADMIN PAGE ------------------
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    data = cur.fetchall()

    conn.close()
    return render_template('admin.html', data=data)

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)