import base64
import hashlib
import socket
import struct
import threading
import requests
from bs4 import BeautifulSoup

# Gunakan port yang berbeda jika 8081 masih error/dipakai
HOST = '127.0.0.1'
PORT = 8081

def fetch_news():
    """Fungsi Web Scraping dengan penanganan error yang lebih baik"""
    try:
        url = "https://www.bbc.com/indonesia"
        # Header agar tidak diblokir oleh server BBC
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari tag h2 untuk berita utama
        headlines = soup.find_all('h2', limit=5)
        
        if not headlines:
            return "<p>Tidak ada berita ditemukan. Selector mungkin berubah.</p>"
            
        result = "<ul>"
        for h in headlines:
            result += f"<li style='margin-bottom:10px;'>{h.get_text().strip()}</li>"
        result += "</ul>"
        return result
    except Exception as e:
        return f"<p style='color:red;'>Error saat scraping: {str(e)}</p>"


def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            return None
        data += more
    return data


def recv_http_request(sock):
    request_data = b''
    while b'\r\n\r\n' not in request_data:
        chunk = sock.recv(1024)
        if not chunk:
            break
        request_data += chunk
    return request_data.decode('utf-8', errors='ignore')


def parse_http_request(request_text):
    lines = request_text.split('\r\n')
    request_line = lines[0].split(' ') if lines else ['GET', '/']
    method = request_line[0] if len(request_line) > 0 else 'GET'
    path = request_line[1] if len(request_line) > 1 else '/'
    headers = {}
    for line in lines[1:]:
        if not line:
            break
        parts = line.split(':', 1)
        if len(parts) == 2:
            headers[parts[0].strip().lower()] = parts[1].strip()
    return method, path, headers


def make_ws_accept(key):
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    accept = base64.b64encode(hashlib.sha1((key + magic).encode('utf-8')).digest())
    return accept.decode('utf-8')


def send_ws_message(sock, message):
    payload = message.encode('utf-8')
    header = bytearray()
    header.append(0x81)
    length = len(payload)

    if length <= 125:
        header.append(length)
    elif length <= 65535:
        header.append(126)
        header.extend(struct.pack('!H', length))
    else:
        header.append(127)
        header.extend(struct.pack('!Q', length))

    sock.sendall(header + payload)


def recv_ws_message(sock):
    first_two = recv_all(sock, 2)
    if not first_two:
        return None

    b1, b2 = first_two
    opcode = b1 & 0x0F
    masked = b2 & 0x80
    payload_len = b2 & 0x7F

    if payload_len == 126:
        raw_len = recv_all(sock, 2)
        if not raw_len:
            return None
        payload_len = struct.unpack('!H', raw_len)[0]
    elif payload_len == 127:
        raw_len = recv_all(sock, 8)
        if not raw_len:
            return None
        payload_len = struct.unpack('!Q', raw_len)[0]

    mask_key = recv_all(sock, 4) if masked else None
    payload_data = recv_all(sock, payload_len) if payload_len > 0 else b''
    if payload_data is None:
        return None

    if masked and mask_key:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload_data))
    else:
        payload = payload_data

    if opcode == 8:
        return None
    return payload.decode('utf-8', errors='ignore')


def handle_websocket(client_socket, client_address):
    try:
        while True:
            message = recv_ws_message(client_socket)
            if not message:
                break
            print(f"[*] WebSocket pesan dari {client_address}: {message}")
            if message.strip().lower() == 'scrape':
                content = fetch_news()
                html_response = (
                    '<h1>Hasil Scraping BBC Indonesia</h1>'
                    '<hr>'
                    f'{content}'
                    '<p>Tekan tombol lagi untuk memperbarui berita.</p>'
                )
                send_ws_message(client_socket, html_response)
            else:
                send_ws_message(client_socket, "Perintah tidak dikenal. Kirim 'scrape' untuk mengambil berita.")
    except Exception as e:
        print(f"[!] Error WebSocket: {e}")
    finally:
        client_socket.close()


def handle_client(client_socket, client_address):
    try:
        request_text = recv_http_request(client_socket)
        if not request_text:
            return

        method, path, headers = parse_http_request(request_text)

        if headers.get('upgrade', '').lower() == 'websocket' and path == '/ws':
            ws_key = headers.get('sec-websocket-key')
            if not ws_key:
                return

            accept_key = make_ws_accept(ws_key)
            handshake_response = (
                'HTTP/1.1 101 Switching Protocols\r\n'
                'Upgrade: websocket\r\n'
                'Connection: Upgrade\r\n'
                f'Sec-WebSocket-Accept: {accept_key}\r\n\r\n'
            )
            client_socket.sendall(handshake_response.encode('utf-8'))
            handle_websocket(client_socket, client_address)
            return

        if path == '/scrape':
            print(f"[*] Sedang melakukan scraping untuk {client_address}...")
            content = fetch_news()
            response_body = f"""
            <html>
                <head><title>Scraper Result</title></head>
                <body style='font-family: sans-serif; padding: 20px;'>
                    <h1>Hasil Scraping BBC Indonesia</h1>
                    <hr>
                    {content}
                    <br><a href="/">[ Kembali ke Home ]</a>
                </body>
            </html>
            """
        else:
            response_body = """
            <html>
                <head><title>Home</title></head>
                <body style='font-family: sans-serif; text-align: center; padding-top: 30px;'>
                    <h1>WebSocket + Web Scraping</h1>
                    <p>Gunakan WebSocket untuk meminta hasil scraping secara langsung.</p>
                    <button onclick=\"doScrape()\" style=\"padding: 12px 22px; font-size: 16px; border:none; border-radius:5px; background:#007bff; color:white; cursor:pointer;\">Ambil Berita</button>
                    <div id=\"log\" style=\"margin-top:20px; text-align:left; max-width:720px; margin-left:auto; margin-right:auto; padding:10px; border:1px solid #ddd; border-radius:8px; min-height:120px; font-family: sans-serif;\">Menunggu WebSocket...</div>
                    <script>
                        const log = document.getElementById('log');
                        const ws = new WebSocket('ws://' + window.location.host + '/ws');
                        ws.addEventListener('open', () => {
                            log.innerHTML = '<p style=\"color:green;\">WebSocket terhubung. Klik tombol untuk mengambil berita.</p>';
                        });
                        ws.addEventListener('message', event => {
                            log.innerHTML = event.data;
                        });
                        ws.addEventListener('close', () => {
                            log.innerHTML += '<p style=\"color:red;\">WebSocket terputus.</p>';
                        });
                        ws.addEventListener('error', () => {
                            log.innerHTML += '<p style=\"color:red;\">Tidak dapat terhubung ke WebSocket.</p>';
                        });
                        function doScrape() {
                            if (ws.readyState === WebSocket.OPEN) {
                                ws.send('scrape');
                                log.innerHTML = '<p>Meminta hasil scraping...</p>';
                            } else {
                                log.innerHTML = '<p style=\"color:red;\">WebSocket belum siap. Segera refresh halaman.</p>';
                            }
                        }
                    </script>
                </body>
            </html>
            """
        
        # Header HTTP yang standar
        response_header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        
        client_socket.sendall(response_header.encode('utf-8') + response_body.encode('utf-8'))
            
    except Exception as e:
        print(f"[!] Error Handling Client: {e}")
    finally:
        client_socket.close()

def run_server():
    # Menggunakan SO_REUSEADDR agar port bisa langsung dipakai lagi setelah restart
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[*] Server jalan di http://{HOST}:{PORT}")
        print("[*] Tekan Ctrl+C untuk mematikan server")
        
        while True:
            client_sock, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_sock, addr))
            thread.start()
    except Exception as e:
        print(f"[!] Gagal menjalankan server: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_server()