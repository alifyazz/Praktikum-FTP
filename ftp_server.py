import os
import logging
import sys
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def start_ftp_server():
    # Konfigurasi Logging sederhana
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("SERVER FTP LOKAL BERJALAN")
    print("=" * 60)

    # 1. MENYIAPKAN FOLDER SERVER (ftp_data)
    share_folder_name = "ftp_data"
    current_dir = os.getcwd()
    server_dir = os.path.join(current_dir, share_folder_name)

    # Buat folder utama
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)
        print(f"[+] Folder penyimpanan dibuat: {share_folder_name}")

    # MENYIAPKAN FILE dummy pertama kali
    dummy_file = os.path.join(server_dir, "baca_saya.txt")
    if not os.path.exists(dummy_file):
        with open(dummy_file, "w") as f:
            f.write("Halo! Ini adalah file tes dari server.\nSila=kan download file ini.")
        print("[+] File dummy dibuat otomatis.")

    # MENYIAPKAN sub-folder untuk simulasi navigasi
    sub_folder = os.path.join(server_dir, "Folder_Tes")
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)
        print("[+] Sub-folder Folder_Tes dibuat untuk simulasi navigasi.")

    print("[+] Path Fisik Server:", server_dir)

    # 2. AUTHORIZER
    authorizer = DummyAuthorizer()
    # User diizinkan (sudah ada) di dalam folder server_dir (ftp_data)
    authorizer.add_user("user", "12345", server_dir, perm="elradfm")

    # 3. HANDLER
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Selamat datang di Local FTP Server (Python)"

    # 4. RUN SERVER
    port = 2122
    address = ("127.0.0.1", port)

    try:
        server = FTPServer(address, handler)
        server.max_cons = 256
        server.max_cons_per_ip = 5

        print("=" * 60)
        print("[ SERVER SIAP MENERIMA KONEKSI ]")
        print(f"Alamat : ftp://127.0.0.1:{port}")
        print("User   : user")
        print("Pass   : 12345")
        print("=" * 60)
        print("TEKAN CTRL+C UNTUK MEMATIKAN SERVER\n")

        server.serve_forever()

    except OSError as e:
        print("[!] Gagal start server:", e)
        print("[!] Pastikan port", port, "tidak sedang dipakai aplikasi lain.")
    except KeyboardInterrupt:
        print("\n[!] Server dimatikan secara manual.")

if __name__ == "__main__":
    start_ftp_server()