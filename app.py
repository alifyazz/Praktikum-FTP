from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import ftplib
import io
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'rahasia_minimalis' # Kunci untuk session login

# Konfigurasi Server
FTP_HOST = "127.0.0.1"
FTP_PORT = 2122

# --- HELPER FUNCTIONS ---
def get_ftp_connection():
    if 'username' not in session: return None
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=5)
        ftp.login(session['username'], session['password'])
        return ftp
    except: return None

def format_size(size):
    # Format ukuran file simple (KB, MB)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024: return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def format_time(time_str):
    try:
        return datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%d-%m-%Y %H:%M")
    except: return time_str

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        try:
            # Cek login dulu
            ftp = ftplib.FTP()
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(user, pwd)
            ftp.quit()
            
            session['username'] = user
            session['password'] = pwd
            return redirect(url_for('dashboard'))
        except:
            flash('Login Failed', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    ftp = get_ftp_connection()
    if not ftp: return redirect(url_for('login'))

    path = request.args.get('path', '/')
    try:
        ftp.cwd(path)
        items = []
        
        # Gunakan MLSD agar detail dan menghindari error SIZE pada folder
        try:
            entries = list(ftp.mlsd())
            entries.sort(key=lambda x: (x[1].get('type') != 'dir', x[0])) # Folder di atas

            for name, facts in entries:
                if name in ['.', '..']: continue
                
                is_dir = facts.get('type') == 'dir'
                items.append({
                    'name': name,
                    'type': 'DIR' if is_dir else 'FILE',
                    'size': '-' if is_dir else format_size(int(facts.get('size', 0))),
                    'date': format_time(facts.get('modify', '')),
                    'icon': 'bi-folder-fill' if is_dir else 'bi-file-earmark-text'
                })
        except:
            flash("Server doesn't support MLSD", 'warning')

        parent_path = os.path.dirname(path)
        return render_template('dashboard.html', files=items, current_path=path, parent_path=parent_path)
    except:
        return redirect(url_for('login'))

@app.route('/download')
def download():
    ftp = get_ftp_connection()
    if not ftp: return redirect(url_for('login'))
    
    path = request.args.get('path')
    filename = request.args.get('filename')
    
    try:
        ftp.cwd(path)
        ftp.voidcmd('TYPE I') # Force Binary Mode
        
        mem_file = io.BytesIO()
        ftp.retrbinary(f"RETR {filename}", mem_file.write)
        mem_file.seek(0)
        
        return send_file(mem_file, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f"Error: {e}", 'danger')
        return redirect(url_for('dashboard', path=path))

@app.route('/upload', methods=['POST'])
def upload():
    ftp = get_ftp_connection()
    if not ftp: return redirect(url_for('login'))
    
    path = request.form['path']
    file = request.files['file']
    
    if file:
        try:
            ftp.cwd(path)
            ftp.voidcmd('TYPE I')
            ftp.storbinary(f"STOR {file.filename}", file.stream)
        except Exception as e:
            flash(f"Upload Error: {e}", 'danger')
            
    return redirect(url_for('dashboard', path=path))

@app.route('/create_folder', methods=['POST'])
def create_folder():
    ftp = get_ftp_connection()
    path = request.form['path']
    name = request.form['folder_name']
    try:
        ftp.cwd(path)
        ftp.mkd(name)
    except: pass
    return redirect(url_for('dashboard', path=path))

@app.route('/delete')
def delete():
    ftp = get_ftp_connection()
    path = request.args.get('path')
    name = request.args.get('filename')
    tipe = request.args.get('type')
    
    try:
        ftp.cwd(path)
        if tipe == 'DIR': ftp.rmd(name)
        else: ftp.delete(name)
    except: pass
    return redirect(url_for('dashboard', path=path))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)