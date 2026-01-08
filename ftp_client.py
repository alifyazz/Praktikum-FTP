import ftplib
import os

FTP_HOST = "127.0.0.1"
FTP_PORT = 2122

# =============================
# UTILITAS TAMPILAN
# =============================
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def garis():
    print("=" * 60)

def pause():
    input("\nTekan ENTER untuk melanjutkan...")

# =============================
# 1. CEK KONEKSI SERVER
# =============================
def cek_koneksi():
    garis()
    print("CEK KONEKSI FTP SERVER")
    garis()
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=5)
        print("[STATUS] Server FTP TERHUBUNG")
        ftp.close()
        return True
    except:
        print("[STATUS] Server FTP TIDAK TERHUBUNG")
        return False

# =============================
# 2. LOGIN FTP
# =============================
def login_ftp():
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT)

    print("\nLOGIN FTP")
    user = input("Username : ")
    pwd = input("Password : ")

    try:
        ftp.login(user, pwd)
        print("[LOGIN BERHASIL]")
        print("Pesan Server:", ftp.getwelcome())
        return ftp
    except:
        print("[LOGIN GAGAL]")
        ftp.close()
        return None

# =============================
# MENU UTAMA
# =============================
def menu():
    garis()
    print("MENU FTP CLIENT")
    garis()
    print("1. Info direktori saat ini (PWD)")
    print("2. List file & folder di server")
    print("3. Pindah direktori server")
    print("4. Kembali ke HOME server")
    print("5. Download file server")
    print("6. Upload file ke server")
    print("7. Make Folder  di server")
    print("8. Delete file di server")
    print("0. Keluar")
    garis()

# =============================
# PROGRAM UTAMA
# =============================
def main():
    clear()

    # STEP 1: CEK KONEKSI
    status_login = cek_koneksi()
    pause()

    if not status_login:
        return

    clear()

    # STEP 2: LOGIN
    ftp = login_ftp()
    if not ftp:
        return

    home_dir = ftp.pwd()

    # STEP 3: MENU INTERAKTIF
    while True:
        clear()
        menu()
        pilihan = input("Pilih menu : ")

        # INFO DIREKTORI
        if pilihan == "1":
            print("\nINFO DIREKTORI")
            print("Direktori server saat ini:", ftp.pwd())

        # LIST FILE SERVER
        elif pilihan == "2":
            print("\nISI DIREKTORI SERVER")
            print("Lokasi:", ftp.pwd())
            garis()
            ftp.dir()

        # PINDAH DIREKTORI
        elif pilihan == "3":
            print("\nPINDAH DIREKTORI")
            print("Lokasi saat ini:", ftp.pwd())
            folder = input("Masukkan nama folder tujuan : ")
            try:
                ftp.cwd(folder)
                print("[BERHASIL] Sekarang di:", ftp.pwd())
            except:
                print("[GAGAL] Folder tidak ditemukan")

        # KEMBALI KE HOME
        elif pilihan == "4":
            ftp.cwd(home_dir)
            print("[HOME] Kembali ke direktori:", ftp.pwd())

        # DOWNLOAD FILE
        elif pilihan == "5":
            print("\nDOWNLOAD FILE")
            print("Direktori server:", ftp.pwd())
            garis()
            print("Daftar file & folder di server:")
            ftp.dir()
            garis()
            nama_file = input("Masukkan nama file yang akan di-download : ")

            try:
                with open(nama_file, "wb") as f:
                    ftp.retrbinary(f"RETR {nama_file}", f.write)
                print("[BERHASIL] File berhasil di-download")
            except:
                print("[GAGAL] File tidak dapat di-download")

        # UPLOAD FILE
        elif pilihan == "6":
            print("\nUPLOAD FILE")
            print("Direktori tujuan server:", ftp.pwd())
            garis()
            print("Daftar file lokal (client):")

            file_lokal = False
            for f in os.listdir():
                if os.path.isfile(f):
                    print("-", f)
                    file_lokal = True

            if not file_lokal:
                print("Tidak ada file lokal di direktori ini")

            garis()
            nama_file = input("Masukkan nama file lokal yang akan di-upload : ")

            if not os.path.exists(nama_file):
                print("[ERROR] File lokal tidak ditemukan")
            else:
                try:
                    with open(nama_file, "rb") as f:
                        ftp.storbinary(f"STOR {nama_file}", f)
                    print("[BERHASIL] File berhasil di-upload")
                except:
                    print("[GAGAL] Upload gagal")

        # KELUAR
        elif pilihan == "0":
            ftp.quit()
            print("\n[KELUAR] Koneksi FTP ditutup")
            break
        else:
            print("[ERROR] Pilihan tidak valid")

        pause()

# =============================
# EKSEKUSI
# =============================
if __name__ == "__main__":
    main()