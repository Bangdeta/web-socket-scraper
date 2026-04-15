"""
PENGENALAN FLASK FRAMEWORK
Membandingkan dengan socket server sebelumnya
"""

from flask import Flask, request, jsonify, render_template_string

# Buat instance Flask
app = Flask(__name__)

# ============================================================
# ROUTING DASAR
# ============================================================

@app.route('/')
def home():
    """Halaman utama - routing otomatis oleh Flask"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask Demo</title>
        <style>
            body { font-family: Arial; margin: 50px; }
            .card { background: #f0f0f0; padding: 20px; border-radius: 10px; }
            .code { background: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>🔥 Flask Framework</h1>
        <div class="card">
            <p>Ini adalah web server menggunakan <strong>Flask</strong> (Python Web Framework).</p>
            <p>Bandigkan dengan server socket yang dibuat sebelumnya:</p>
            <ul>
                <li>✅ Routing otomatis - tidak perlu if/else manual</li>
                <li>✅ Parsing parameter otomatis</li>
                <li>✅ Debug mode dengan auto-reload</li>
                <li>✅ Error handling yang baik</li>
            </ul>
        </div>
        <h3>📌 Coba endpoint berikut:</h3>
        <ul>
            <li><a href="/hello/Andi">/hello/Andi</a> - Dynamic routing</li>
            <li><a href="/query?nama=Budi&umur=20">/query?nama=Budi&umur=20</a> - Query parameter</li>
            <li><a href="/api/data">/api/data</a> - JSON response</li>
            <li><a href="/user/123">/user/123</a> - URL parameter</li>
        </ul>
    </body>
    </html>
    """

# ============================================================
# DYNAMIC ROUTING (URL Parameter)
# ============================================================

@app.route('/hello/<name>')
def say_hello(name):
    """Mengambil parameter dari URL secara otomatis"""
    return f"""
    <h1>Hello {name}!</h1>
    <p>Flask otomatis menangkap parameter <code>name</code> dari URL.</p>
    <p><a href="/">Kembali</a></p>
    """

@app.route('/user/<int:user_id>')
def get_user(user_id):
    """Parameter dengan tipe data (integer)"""
    # Contoh data user (biasanya dari database)
    users = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@example.com"},
        3: {"name": "Charlie", "email": "charlie@example.com"}
    }
    
    user = users.get(user_id)
    if user:
        return f"""
        <h1>User Profile</h1>
        <p>ID: {user_id}</p>
        <p>Name: {user['name']}</p>
        <p>Email: {user['email']}</p>
        <a href="/">Back</a>
        """
    else:
        return f"<h1>User {user_id} not found</h1>", 404

# ============================================================
# QUERY PARAMETERS (GET)
# ============================================================

@app.route('/query')
def handle_query():
    """Mengambil query parameter (otomatis parsing!)"""
    # request.args adalah dictionary dari query string
    nama = request.args.get('nama', 'Guest')  # Default 'Guest'
    umur = request.args.get('umur', '?')
    
    # Dapatkan semua parameter
    all_params = dict(request.args)
    
    return f"""
    <h1>Query Parameters</h1>
    <p>Nama: {nama}</p>
    <p>Umur: {umur}</p>
    <p>Semua parameter: {all_params}</p>
    <p><small>Flask otomatis parsing query string! Tidak perlu manual split &amp; loop.</small></p>
    <a href="/">Back</a>
    """

# ============================================================
# FORM HANDLING (POST)
# ============================================================

@app.route('/form', methods=['GET', 'POST'])
def handle_form():
    """Menampilkan form dan memproses submission"""
    if request.method == 'POST':
        # Flask otomatis parsing form data!
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        return f"""
        <h1>Form Submitted!</h1>
        <p>Name: {name}</p>
        <p>Email: {email}</p>
        <p>Message: {message}</p>
        <a href="/form">Back to Form</a>
        """
    
    # Tampilkan form (GET request)
    return """
    <h1>Contact Form</h1>
    <form method="POST">
        <p>Name: <input type="text" name="name" required></p>
        <p>Email: <input type="email" name="email" required></p>
        <p>Message: <textarea name="message" rows="4" cols="30"></textarea></p>
        <p><input type="submit" value="Send"></p>
    </form>
    <a href="/">Home</a>
    """

# ============================================================
# JSON API (REST API)
# ============================================================

@app.route('/api/data')
def api_data():
    """Mengembalikan response JSON (bukan HTML)"""
    data = {
        "status": "success",
        "message": "Ini adalah response JSON dari Flask",
        "data": {
            "framework": "Flask",
            "version": "2.3.x",
            "features": ["Routing", "Templating", "Request Parsing"]
        }
    }
    # Flask otomatis mengubah dictionary menjadi JSON
    # dan set header Content-Type: application/json
    return jsonify(data)

@app.route('/api/echo', methods=['POST'])
def api_echo():
    """Menerima JSON dan mengembalikannya kembali"""
    if not request.is_json:
        return jsonify({"error": "Request harus JSON"}), 400
    
    data = request.get_json()  # Flask otomatis parsing JSON!
    return jsonify({
        "status": "echo",
        "received": data
    })

# ============================================================
# ERROR HANDLING
# ============================================================

@app.errorhandler(404)
def page_not_found(error):
    """Custom halaman 404"""
    return """
    <h1>404 - Halaman Tidak Ditemukan</h1>
    <p>URL yang Anda cari tidak tersedia.</p>
    <a href="/">Kembali ke Home</a>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    """Custom halaman 500"""
    return """
    <h1>500 - Internal Server Error</h1>
    <p>Terjadi kesalahan pada server.</p>
    <a href="/">Kembali ke Home</a>
    """, 500

# ============================================================
# MENJALANKAN SERVER
# ============================================================

if __name__ == '__main__':
    # debug=True memberikan:
    # 1. Auto-reload saat kode berubah
    # 2. Error page yang informatif di browser
    # 3. Debugger interaktif
    app.run(debug=True, host='localhost', port=5000)