import http.server
import socketserver
import urllib.parse
import mysql.connector
from mysql.connector import Error
import os

# ===============================
# SETTINGS
# ===============================
PORT = 8000
BASE_DIR = r"C:\Users\bhise\OneDrive\Desktop\Medicine_tracker"
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

DB_CONFIG = {
    "host": "localhost",
    "user": "root",              # your MySQL username
    "password": "newpassword",   # your MySQL password
    "database": "medicine_tracker"
}

# ===============================
# DATABASE INITIALIZATION
# ===============================
def init_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        c = conn.cursor()
        c.execute("CREATE DATABASE IF NOT EXISTS medicine_tracker")
        conn.commit()
        conn.close()

        conn = mysql.connector.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS pharmacists (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pharmacy_name VARCHAR(255) NOT NULL,
                owner_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20) NOT NULL,
                address TEXT NOT NULL,
                license_no VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pharmacist_id INT NOT NULL,
                medicine_name VARCHAR(255) NOT NULL,
                price FLOAT NOT NULL,
                quantity INT NOT NULL,
                manufacturer_name VARCHAR(255) NOT NULL,
                expiry_date VARCHAR(50) NOT NULL,
                FOREIGN KEY (pharmacist_id) REFERENCES pharmacists(id)
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    except Error as e:
        print("❌ Database error:", e)

init_db()

# ===============================
# HELPER FUNCTIONS
# ===============================
def parse_post_data(handler):
    length = int(handler.headers.get('Content-Length', 0))
    post_data = handler.rfile.read(length).decode()
    return urllib.parse.parse_qs(post_data)

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ===============================
# REQUEST HANDLER
# ===============================
class MedicineHandler(http.server.SimpleHTTPRequestHandler):
    # ===== GET REQUESTS =====
    def do_GET(self):
        routes = {
            "/": "index.html",
            "/pharmacist/register": "pharmacist_register.html",
            "/pharmacist/login": "pharmacist_login.html",
            "/pharmacist/forgot_password": "forgot_password.html",
            "/pharmacist/add_medicine": "add_medicine.html",
        }
        if self.path in routes:
            filepath = os.path.join(TEMPLATES_DIR, routes[self.path])
            self.serve_file(filepath)
        elif self.path == "/pharmacist/dashboard":
            self.serve_dashboard()
        elif self.path.startswith("/pharmacist/edit_medicine"):
            self.serve_edit_medicine_page()
        elif self.path.startswith("/pharmacist/delete_medicine"):
            self.handle_delete_medicine()
        elif self.path.startswith("/static/"):
            static_path = self.path.lstrip("/")
            static_file = os.path.join(BASE_DIR, static_path)
            if os.path.exists(static_file):
                self.serve_file(static_file)
            else:
                self.send_error(404, "Static file not found")
        else:
            self.send_error(404, "Page Not Found")

    # ===== POST REQUESTS =====
    def do_POST(self):
        if self.path == "/pharmacist/register":
            self.handle_register()
        elif self.path == "/pharmacist/login":
            self.handle_login()
        elif self.path == "/pharmacist/forgot_password":
            self.handle_forgot_password()
        elif self.path == "/pharmacist/add_medicine":
            self.handle_add_medicine()
        elif self.path.startswith("/pharmacist/edit_medicine"):
            self.handle_edit_medicine()
        elif self.path == "/search":
            self.handle_search()
        else:
            self.send_error(404, "Page Not Found")

    # ===============================
    # SEARCH HANDLER
    # ===============================
    def handle_search(self):
        data = parse_post_data(self)
        medicine = data.get("medicine", [""])[0].strip()
        city = data.get("city", [""])[0].strip()

        if not medicine or not city:
            self.respond_message("❌ Both medicine and city are required", error=True)
            return

        medicine_lower = medicine.lower()
        city_lower = city.lower()

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT p.pharmacy_name, p.owner_name, p.phone, p.email, p.address, m.quantity, m.price
            FROM pharmacists p
            JOIN medicines m ON p.id = m.pharmacist_id
            WHERE LOWER(m.medicine_name) = %s
              AND LOWER(p.address) LIKE %s
              AND m.quantity > 0
        """, (medicine_lower, f"%{city_lower}%"))
        results = c.fetchall()
        conn.close()

        if not results:
            self.respond_message(f"No pharmacies found with '{medicine}' in '{city}'.", error=True)
            return

        rows_html = ""
        for (pharmacy_name, owner, phone, email, address, qty, price) in results:
            rows_html += f"""
                <tr>
                    <td>{pharmacy_name}</td>
                    <td>{owner}</td>
                    <td>{phone}</td>
                    <td>{email}</td>
                    <td>{address}</td>
                    <td>{qty}</td>
                    <td>₹{price:.2f}</td>
                </tr>
            """

        html = f"""
\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Search Results - Pharmacy Finder</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

  <style>
    body {{
      background: linear-gradient(135deg, #d4bfff, #e6e6fa);
      font-family: "Poppins", sans-serif;
      min-height: 100vh;
    }}
    .container {{
      margin-top: 60px;
    }}
    h2 {{
      font-weight: 700;
      color: #4b0082;
      text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }}
    table {{
      border-radius: 10px;
      overflow: hidden;
    }}
    thead {{
      background-color: #6a0dad !important;
    }}
    th {{
      color: #fff;
      text-align: center;
      font-weight: 600;
    }}
    td {{
      vertical-align: middle;
      text-align: center;
    }}
    tbody tr:hover {{
      background-color: #f5e6ff;
      transition: background-color 0.3s ease-in-out;
    }}
    .card {{
      background: #ffffffb3;
      border-radius: 15px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      padding: 20px;
      backdrop-filter: blur(8px);
    }}
    .btn-secondary {{
      background-color: #6a0dad;
      border: none;
      transition: all 0.3s ease;
    }}
    .btn-secondary:hover {{
      background-color: #4b0082;
      transform: scale(1.05);
    }}
  </style>
</head>

<body>
  <div class="container">
    <div class="card">
      <h2 class="text-center mb-4">
        Pharmacies with <strong class="text-primary">{medicine}</strong> in <strong class="text-success">{city}</strong>
      </h2>
      <div class="table-responsive">
        <table class="table table-bordered table-striped align-middle">
          <thead>
            <tr>
              <th>Pharmacy</th>
              <th>Owner</th>
              <th>Phone</th>
              <th>Email</th>
              <th>Address</th>
              <th>Qty</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>

      <div class="text-center mt-4">
        <a href="/" class="btn btn-secondary btn-lg shadow">🔙 Back to Home</a>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
        self.respond_html(html)

    # ===============================
    # DASHBOARD HANDLER
    # ===============================
    def serve_dashboard(self):
        user_id = self.get_logged_in_user()
        if not user_id:
            self.redirect("/pharmacist/login")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT pharmacy_name FROM pharmacists WHERE id = %s", (user_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            self.respond_message("Pharmacist not found.", error=True)
            return
        pharmacy_name = row[0]

        c.execute("""
            SELECT id, medicine_name, quantity, expiry_date, price, manufacturer_name
            FROM medicines
            WHERE pharmacist_id = %s
        """, (user_id,))
        medicines = c.fetchall()
        conn.close()

        rows_html = ""
        for (med_id, name, qty, expiry, price, manufacturer) in medicines:
            rows_html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{qty}</td>
                    <td>{expiry}</td>
                    <td>₹{price:.2f}</td>
                    <td>{manufacturer}</td>
                    <td>
                        <a href='/pharmacist/edit_medicine?id={med_id}' class='btn btn-warning btn-sm'>Edit</a>
                        <a href='/pharmacist/delete_medicine?id={med_id}' class='btn btn-danger btn-sm' onclick="return confirm('Delete this medicine?');">Delete</a>
                    </td>
                </tr>
            """

        tpl_path = os.path.join(TEMPLATES_DIR, "pharmacist_dashboard.html")
        try:
            with open(tpl_path, "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            self.respond_message("Dashboard template not found.", error=True)
            return

        html = template.replace("{{pharmacy_name}}", pharmacy_name).replace("{{medicine_rows}}", rows_html)
        self.respond_html(html)

    # ===============================
    # AUTH HANDLERS
    # ===============================
    def handle_register(self):
        data = parse_post_data(self)
        fields = ["pharmacy_name", "owner_name", "email", "phone", "address", "license_no", "password", "confirm_password"]
        info = {field: data.get(field, [""])[0] for field in fields}

        if info["password"] != info["confirm_password"]:
            self.respond_message("❌ Passwords do not match.", error=True)
            return

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO pharmacists (pharmacy_name, owner_name, email, phone, address, license_no, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (info["pharmacy_name"], info["owner_name"], info["email"],
                  info["phone"], info["address"], info["license_no"], info["password"]))
            conn.commit()
            conn.close()
            self.redirect("/pharmacist/login")
        except Error as e:
            print("[ERROR]", e)
            self.respond_message("❌ Registration failed (maybe duplicate email)", error=True)

    def handle_login(self):
        data = parse_post_data(self)
        email = data.get("email", [""])[0]
        password = data.get("password", [""])[0]

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, password FROM pharmacists WHERE email = %s", (email,))
        user = c.fetchone()
        conn.close()

        if user and user[1] == password:
            self.send_response(302)
            self.send_header("Set-Cookie", f"user_id={user[0]}; Path=/")
            self.send_header("Location", "/pharmacist/dashboard")
            self.end_headers()
        else:
            self.respond_message("❌ Invalid credentials.", error=True)

    def handle_forgot_password(self):
        """Simple password reset: user provides email and new password (no email sending).
        This updates the password for the pharmacist if the email exists.
        """
        data = parse_post_data(self)
        email = data.get("email", [""])[0].strip()
        new_password = data.get("new_password", [""])[0]
        confirm_password = data.get("confirm_password", [""])[0]

        if not email:
            self.respond_message("❌ Email is required.", error=True)
            return
        if not new_password:
            self.respond_message("❌ New password is required.", error=True)
            return
        if new_password != confirm_password:
            self.respond_message("❌ Passwords do not match.", error=True)
            return

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT id FROM pharmacists WHERE email = %s", (email,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.respond_message("❌ No account found with that email.", error=True)
                return
            # Update password
            c.execute("UPDATE pharmacists SET password = %s WHERE email = %s", (new_password, email))
            conn.commit()
            conn.close()
            # Redirect to login page with a simple success message page
            self.respond_message("✅ Password updated. You can now login.")
        except Error as e:
            print("[ERROR] Forgot password failed:", e)
            self.respond_message("❌ Error updating password.", error=True)

    # ===============================
    # MEDICINE HANDLERS
    # ===============================
    def handle_add_medicine(self):
        user_id = self.get_logged_in_user()
        if not user_id:
            self.redirect("/pharmacist/login")
            return

        data = parse_post_data(self)
        name = data.get("medicine_name", [""])[0].strip()
        price = float(data.get("price", ["0.0"])[0])
        quantity = int(data.get("quantity", ["0"])[0])
        manufacturer = data.get("manufacturer_name", [""])[0].strip()
        expiry = data.get("expiry_date", [""])[0].strip()

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, quantity FROM medicines WHERE pharmacist_id = %s AND medicine_name = %s", (user_id, name))
        existing = c.fetchone()

        if existing:
            med_id, existing_qty = existing
            new_qty = existing_qty + quantity
            c.execute("""
                UPDATE medicines
                SET quantity=%s, price=%s, manufacturer_name=%s, expiry_date=%s
                WHERE id=%s AND pharmacist_id=%s
            """, (new_qty, price, manufacturer, expiry, med_id, user_id))
        else:
            c.execute("""
                INSERT INTO medicines (pharmacist_id, medicine_name, price, quantity, manufacturer_name, expiry_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, name, price, quantity, manufacturer, expiry))

        conn.commit()
        conn.close()
        self.redirect("/pharmacist/dashboard")

    # ===============================
    # EDIT / DELETE MEDICINE
    # ===============================
    def serve_edit_medicine_page(self):
        user_id = self.get_logged_in_user()
        if not user_id:
            self.redirect("/pharmacist/login")
            return

        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        med_id = query.get("id", [None])[0]

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT medicine_name, price, quantity, manufacturer_name, expiry_date
            FROM medicines
            WHERE id=%s AND pharmacist_id=%s
        """, (med_id, user_id))
        med = c.fetchone()
        conn.close()

        if not med:
            self.respond_message("Medicine not found or not owned by you.", error=True)
            return

        tpl_path = os.path.join(TEMPLATES_DIR, "edit_medicine.html")
        try:
            with open(tpl_path, "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            self.respond_message("Edit template not found.", error=True)
            return

        html = (template
                .replace("{{medicine_id}}", str(med_id))
                .replace("{{medicine_name}}", med[0])
                .replace("{{price}}", str(med[1]))
                .replace("{{quantity}}", str(med[2]))
                .replace("{{manufacturer_name}}", med[3])
                .replace("{{expiry_date}}", med[4]))
        self.respond_html(html)

    def handle_edit_medicine(self):
        user_id = self.get_logged_in_user()
        if not user_id:
            self.redirect("/pharmacist/login")
            return

        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        med_id = query.get("id", [None])[0]

        data = parse_post_data(self)
        name = data.get("medicine_name", [""])[0]
        price = float(data.get("price", ["0.0"])[0])
        quantity = int(data.get("quantity", ["0"])[0])
        manufacturer = data.get("manufacturer_name", [""])[0]
        expiry = data.get("expiry_date", [""])[0]

        if med_id:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                UPDATE medicines
                SET medicine_name=%s, price=%s, quantity=%s, manufacturer_name=%s, expiry_date=%s
                WHERE id=%s AND pharmacist_id=%s
            """, (name, price, quantity, manufacturer, expiry, med_id, user_id))
            conn.commit()
            conn.close()

        self.redirect("/pharmacist/dashboard")

    def handle_delete_medicine(self):
        user_id = self.get_logged_in_user()
        if not user_id:
            self.redirect("/pharmacist/login")
            return

        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        med_id = query.get("id", [None])[0]

        if med_id:
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM medicines WHERE id=%s AND pharmacist_id=%s", (med_id, user_id))
            conn.commit()
            conn.close()

        self.redirect("/pharmacist/dashboard")

    # ===============================
    # FILE / RESPONSE HANDLERS
    # ===============================
    def serve_file(self, filepath):
        try:
            with open(filepath, "rb") as f:
                self.send_response(200)
                if filepath.endswith(".html"):
                    self.send_header("Content-type", "text/html")
                elif filepath.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif filepath.lower().endswith((".jpg", ".jpeg")):
                    self.send_header("Content-type", "image/jpeg")
                elif filepath.lower().endswith(".png"):
                    self.send_header("Content-type", "image/png")
                else:
                    self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, f"File not found: {filepath}")

    def respond_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def respond_message(self, msg, error=False):
        color = "red" if error else "green"
        html = f"<h2 style='color:{color}; text-align:center; margin-top:50px;'>{msg}</h2>"
        self.respond_html(html)

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def get_logged_in_user(self):
        cookie = self.headers.get("Cookie")
        if cookie and "user_id=" in cookie:
            try:
                return int(cookie.split("user_id=")[1].split(";")[0])
            except:
                return None
        return None

# ===============================
# START SERVER
# ===============================
if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MedicineHandler) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}")
        httpd.serve_forever()
