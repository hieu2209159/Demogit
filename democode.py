import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar
import requests

class UserManager:
    def __init__(self, ten_file='users.json'):
        self.ten_file = ten_file
        self.nhap_du_lieu()

    def nhap_du_lieu(self):
        try:
            with open(self.ten_file, 'r', encoding='utf-8') as file:
                self.users = json.load(file)
        except FileNotFoundError:
            self.users = {}

    def luu_du_lieu(self):
        with open(self.ten_file, 'w', encoding='utf-8') as file:
            json.dump(self.users, file, indent=4)

    def tao_tai_khoan(self, username, password, role='user'):
        if username in self.users:
            return False  # Tên người dùng đã tồn tại
        self.users[username] = {'password': password, 'role': role}
        self.luu_du_lieu()
        return True

    def dang_nhap(self, username, password):
        user = self.users.get(username)
        return user and user['password'] == password, user['role'] if user else None

class QuanLyTaiChinh:
    def __init__(self, ten_file='du_lieu_tai_chinh.json'):
        self.ten_file = ten_file
        self.nhap_du_lieu()

    def nhap_du_lieu(self):
        try:
            with open(self.ten_file, 'r', encoding='utf-8') as file:
                du_lieu = json.load(file)
                self.giao_dich = du_lieu.get('giao_dich', [])
        except FileNotFoundError:
            self.giao_dich = []

    def luu_du_lieu(self):
        with open(self.ten_file, 'w', encoding='utf-8') as file:
            json.dump({'giao_dich': self.giao_dich}, file, indent=4)

    def them_giao_dich(self, so_tien, danh_muc, ngay=None):
        if ngay is None:
            ngay = datetime.now().strftime('%Y-%m-%d')
        self.giao_dich.append({'so_tien': so_tien, 'danh_muc': danh_muc, 'ngay': ngay})
        self.luu_du_lieu()

    def cap_nhat_giao_dich(self, index, so_tien, danh_muc, ngay):
        self.giao_dich[index] = {'so_tien': so_tien, 'danh_muc': danh_muc, 'ngay': ngay}
        self.luu_du_lieu()

    def xoa_giao_dich(self, index):
        del self.giao_dich[index]
        self.luu_du_lieu()

    def lay_du_lieu_tu_api(self):
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            data = response.json()
            self.luu_du_lieu_tu_api(data)
            return data
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu từ API: {e}")
            return None

    def luu_du_lieu_tu_api(self, data):
        if 'rates' in data:
            for currency, rate in data['rates'].items():
                self.them_giao_dich(rate, currency, datetime.now().strftime('%Y-%m-%d'))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Tài Chính")
        self.user_manager = UserManager()
        self.manager = QuanLyTaiChinh()
        self.current_user = None
        self.user_role = None

        self.login_window()

    def login_window(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack()

        tk.Label(self.login_frame, text="Username").grid(row=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password").grid(row=1)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.login_frame, text="Đăng Nhập", command=self.dang_nhap).grid(row=2, column=0, sticky=tk.W, pady=4)
        tk.Button(self.login_frame, text="Đăng Ký", command=self.dang_ky).grid(row=2, column=1, sticky=tk.W, pady=4)

    def dang_nhap(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, role = self.user_manager.dang_nhap(username, password)
        if success:
            self.current_user = username
            self.user_role = role  # Lưu vai trò của người dùng
            self.login_frame.pack_forget()
            self.main_window()
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng.")

    def dang_ky(self):
        username = simpledialog.askstring("Đăng Ký", "Nhập tên người dùng:")
        password = simpledialog.askstring("Đăng Ký", "Nhập mật khẩu:", show='*')
        is_admin = simpledialog.askstring("Đăng Ký", "Bạn có muốn làm quản trị viên? (yes/no):")
        role = 'admin' if is_admin.lower() == 'yes' else 'user'
        if self.user_manager.tao_tai_khoan(username, password, role):
            messagebox.showinfo("Thành công", "Tài khoản đã được tạo.")
        else:
            messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại.")

    def main_window(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        self.listbox = Listbox(self.main_frame)
        self.listbox.pack()

        self.scrollbar = Scrollbar(self.main_frame)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        if self.user_role == 'admin':
            tk.Button(self.main_frame, text="Thêm Giao Dịch", command=self.them_giao_dich).pack()
            tk.Button(self.main_frame, text="Cập Nhật Giao Dịch", command=self.cap_nhat_giao_dich).pack()
            tk.Button(self.main_frame, text="Xóa Giao Dịch", command=self.xoa_giao_dich).pack()

        tk.Button(self.main_frame, text="Đọc Dữ Liệu", command=self.hien_thi_giao_dich).pack()
        tk.Button(self.main_frame, text="Lấy Dữ Liệu Từ API", command=self.lay_du_lieu_tu_api).pack()

        self.hien_thi_giao_dich()

    def hien_thi_giao_dich(self):
        self.manager.nhap_du_lieu()
        self.listbox.delete(0, tk.END)
        for gd in self.manager.giao_dich:
            self.listbox.insert(tk.END, f"{gd['ngay']}: {gd['danh_muc']} - {gd['so_tien']}")

    def them_giao_dich(self):
        so_tien = simpledialog.askfloat("Nhập số tiền", "Số tiền:")
        danh_muc = simpledialog.askstring("Nhập danh mục", "Danh mục:")
        if so_tien and danh_muc:
            self.manager.them_giao_dich(so_tien, danh_muc)
            self.hien_thi_giao_dich()

    def cap_nhat_giao_dich(self):
        index = self.listbox.curselection()
        if index:
            index = index[0]
            so_tien = simpledialog.askfloat("Nhập số tiền", "Số tiền:", initialvalue=self.manager.giao_dich[index]['so_tien'])
            danh_muc = simpledialog.askstring("Nhập danh mục", "Danh mục:", initialvalue=self.manager.giao_dich[index]['danh_muc'])
            if so_tien and danh_muc:
                self.manager.cap_nhat_giao_dich(index, so_tien, danh_muc, self.manager.giao_dich[index]['ngay'])
                self.hien_thi_giao_dich()

    def xoa_giao_dich(self):
        index = self.listbox.curselection()
        if index:
            self.manager.xoa_giao_dich(index[0])
            self.hien_thi_giao_dich()

    def lay_du_lieu_tu_api(self):
        data = self.manager.lay_du_lieu_tu_api()
        if data:
            messagebox.showinfo("Thông Tin API", f"Dữ liệu lấy được: {data}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()