"""
APLIKASI CRUD LENGKAP DENGAN FLASK
- Create (Tambah data)
- Read (Lihat data)
- Update (Edit data)
- Delete (Hapus data)

Menggunakan list sebagai database sementara (untuk pembelajaran)
"""

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'rahasia_crud_123'  # Untuk flash message

# ============================================================
# DATABASE SEDERHANA (LIST OF DICTIONARY)
# ============================================================
# Dalam aplikasi nyata, ini akan diganti dengan database (MySQL, PostgreSQL, SQLite)
daftar_mahasiswa = [
    {"id": 1, "nama": "Andi Wijaya", "nim": "20230001", "jurusan": "Teknik Informatika", "angkatan": 2023},
    {"id": 2, "nama": "Budi Santoso", "nim": "20230002", "jurusan": "Sistem Informasi", "angkatan": 2023},
    {"id": 3, "nama": "Citra Dewi", "nim": "20230003", "jurusan": "Teknik Komputer", "angkatan": 2023},
]

# Helper untuk mendapatkan ID berikutnya
def get_next_id():
    if not daftar_mahasiswa:
        return 1
    return max(m["id"] for m in daftar_mahasiswa) + 1

# Helper untuk mencari mahasiswa berdasarkan ID
def find_mahasiswa_by_id(mahasiswa_id):
    for m in daftar_mahasiswa:
        if m["id"] == mahasiswa_id:
            return m
    return None

# ============================================================
# ROUTE: READ (Menampilkan semua data)
# ============================================================

@app.route('/')
def index():
    """Halaman utama - menampilkan semua data mahasiswa"""
    return render_template('index.html', mahasiswa=daftar_mahasiswa)

# ============================================================
# ROUTE: CREATE (Menambah data)
# ============================================================

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    """Form tambah data dan proses penyimpanan"""
    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form.get('nama', '').strip()
        nim = request.form.get('nim', '').strip()
        jurusan = request.form.get('jurusan', '').strip()
        angkatan = request.form.get('angkatan', '').strip()
        
        # Validasi sederhana
        if not nama or not nim or not jurusan or not angkatan:
            flash('Semua field harus diisi!', 'error')
            return redirect(url_for('tambah'))
        
        # Cek duplikasi NIM
        for m in daftar_mahasiswa:
            if m['nim'] == nim:
                flash(f'NIM {nim} sudah terdaftar!', 'error')
                return redirect(url_for('tambah'))
        
        # Buat data baru
        data_baru = {
            "id": get_next_id(),
            "nama": nama,
            "nim": nim,
            "jurusan": jurusan,
            "angkatan": int(angkatan) if angkatan.isdigit() else 2023
        }
        
        daftar_mahasiswa.append(data_baru)
        flash(f'Data mahasiswa {nama} berhasil ditambahkan!', 'success')
        return redirect(url_for('index'))
    
    # GET request - tampilkan form
    return render_template('create.html')

# ============================================================
# ROUTE: UPDATE (Mengedit data)
# ============================================================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Form edit data dan proses update"""
    mahasiswa = find_mahasiswa_by_id(id)
    
    if not mahasiswa:
        flash('Data mahasiswa tidak ditemukan!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Ambil data baru dari form
        nama = request.form.get('nama', '').strip()
        nim = request.form.get('nim', '').strip()
        jurusan = request.form.get('jurusan', '').strip()
        angkatan = request.form.get('angkatan', '').strip()
        
        # Validasi
        if not nama or not nim or not jurusan or not angkatan:
            flash('Semua field harus diisi!', 'error')
            return redirect(url_for('edit', id=id))
        
        # Cek duplikasi NIM (kecuali untuk data sendiri)
        for m in daftar_mahasiswa:
            if m['nim'] == nim and m['id'] != id:
                flash(f'NIM {nim} sudah digunakan oleh mahasiswa lain!', 'error')
                return redirect(url_for('edit', id=id))
        
        # Update data
        mahasiswa['nama'] = nama
        mahasiswa['nim'] = nim
        mahasiswa['jurusan'] = jurusan
        mahasiswa['angkatan'] = int(angkatan) if angkatan.isdigit() else 2023
        
        flash(f'Data mahasiswa {nama} berhasil diupdate!', 'success')
        return redirect(url_for('index'))
    
    # GET request - tampilkan form dengan data yang ada
    return render_template('edit.html', mhs=mahasiswa)

# ============================================================
# ROUTE: DELETE (Menghapus data)
# ============================================================

@app.route('/hapus/<int:id>')
def hapus(id):
    """Menghapus data mahasiswa berdasarkan ID"""
    mahasiswa = find_mahasiswa_by_id(id)
    
    if mahasiswa:
        nama = mahasiswa['nama']
        daftar_mahasiswa.remove(mahasiswa)
        flash(f'Data mahasiswa {nama} berhasil dihapus!', 'success')
    else:
        flash('Data tidak ditemukan!', 'error')
    
    return redirect(url_for('index'))

# ============================================================
# ROUTE TAMBAHAN: SEARCH
# ============================================================

@app.route('/search')
def search():
    """Mencari mahasiswa berdasarkan nama atau NIM"""
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return redirect(url_for('index'))
    
    results = []
    for m in daftar_mahasiswa:
        if keyword.lower() in m['nama'].lower() or keyword in m['nim']:
            results.append(m)
    
    return render_template('index.html', mahasiswa=results, search_keyword=keyword)

# ============================================================
# MENJALANKAN APLIKASI
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("📚 APLIKASI CRUD MAHASISWA")
    print("=" * 50)
    print(f"📍 Server: http://localhost:5000")
    print(f"📊 Data awal: {len(daftar_mahasiswa)} mahasiswa")
    print("=" * 50)
    app.run(debug=True, host='localhost', port=5000)