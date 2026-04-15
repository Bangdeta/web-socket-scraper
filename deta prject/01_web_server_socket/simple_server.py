"""
WEB SERVER SEDERHANA DENGAN SOCKET
Bisa dihentikan dengan Ctrl+C
"""

import socket
import signal
import sys

# Konfigurasi server
HOST = 'localhost'
PORT = 8080

# Flag untuk mengontrol loop server
server_running = True

def signal_handler(sig, frame):
    """Handler untuk menangani Ctrl+C"""
    global server_running
    print("\n\n🛑 Menerima sinyal berhenti...")
    server_running = False
    sys.exit(0)

# Daftarkan handler untuk Ctrl+C (SIGINT)
signal.signal(signal.SIGINT, signal_handler)

def create_socket_server():
    """Membuat socket server TCP"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    # Set timeout agar bisa cek server_running secara periodik
    server_socket.settimeout(1.0)
    return server_socket

def handle_request(request_data):
    """Memproses request HTTP dan menghasilkan response"""
    request_lines = request_data.split('\r\n')
    request_line = request_lines[0] if request_lines else ""
    
    print(f"📥 Request: {request_line}")
    
    # Ekstrak method dan path
    parts = request_line.split(' ')
    if len(parts) >= 2:
        method = parts[0]
        path = parts[1]
    else:
        method = "GET"
        path = "/"
    
    # Routing
    if path == "/":
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Home - Socket Server</title>
            <style>
                body {{ font-family: Arial; margin: 50px; text-align: center; }}
                h1 {{ color: #3498db; }}
                .info {{ background: #ecf0f1; padding: 20px; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <h1>🚀 Web Server dari Socket!</h1>
            <div class="info">
                <p>Server ini dibuat <strong>tanpa framework</strong> menggunakan socket programming.</p>
                <p>Method: {method}</p>
                <p>Path: {path}</p>
            </div>
            <p><a href="/about">Ke Halaman About</a></p>
            <hr>
            <p><small>Tekan Ctrl+C di terminal untuk menghentikan server</small></p>
        </body>
        </html>
        """
        status_code = "200 OK"
        
    elif path == "/about":
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>About</title>
            <style>
                body { font-family: Arial; margin: 50px; text-align: center; }
                h1 { color: #2c3e50; }
            </style>
        </head>
        <body>
            <h1>📖 Tentang Server Ini</h1>
            <p>Server ini dibuat dengan Python Socket Programming.</p>
            <p>Setiap request diproses secara manual tanpa bantuan framework.</p>
            <p><a href="/">Kembali ke Home</a></p>
        </body>
        </html>
        """
        status_code = "200 OK"
        
    else:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 Not Found</title>
            <style>
                body {{ font-family: Arial; margin: 50px; text-align: center; }}
                h1 {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <h1>❌ 404 - Halaman Tidak Ditemukan</h1>
            <p>Path '{path}' tidak tersedia di server ini.</p>
            <p><a href="/">Kembali ke Home</a></p>
        </body>
        </html>
        """
        status_code = "404 Not Found"
    
    response = f"""\
HTTP/1.1 {status_code}
Content-Type: text/html; charset=utf-8
Content-Length: {len(html_content)}
Connection: close

{html_content}
"""
    
    return response.encode('utf-8')

def run_server():
    """Menjalankan web server"""
    global server_running
    
    print("=" * 50)
    print("🚀 SIMPLE WEB SERVER (SOCKET)")
    print("=" * 50)
    print(f"📍 Server: http://{HOST}:{PORT}")
    print("📡 Menunggu koneksi...")
    print("💡 Tekan Ctrl+C untuk menghentikan server")
    print("=" * 50)
    print()
    
    server_socket = create_socket_server()
    
    try:
        while server_running:
            try:
                # Terima koneksi dengan timeout
                client_socket, client_address = server_socket.accept()
                print(f"🔗 Client terhubung dari {client_address}")
                
                # Baca request
                request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
                
                if request_data:
                    response = handle_request(request_data)
                    client_socket.sendall(response)
                    print(f"📤 Response dikirim ke {client_address}\n")
                
                client_socket.close()
                
            except socket.timeout:
                # Timeout, lanjutkan loop untuk cek server_running
                continue
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\n🛑 Server dihentikan oleh user")
    finally:
        server_socket.close()
        print("🔒 Socket ditutup")
        print("👋 Server berhenti. Terima kasih!")

if __name__ == "__main__":
    run_server()