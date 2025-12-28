import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from datetime import datetime
import requests
import re
# ==============================
# CẤU HÌNH FILE DỮ LIỆU
# ==============================
FILE_USER = "users.json"
FILE_SP   = "san_pham.json"
FILE_HD   = "hoa_don.json"
FILE_SP_BAK = "san_pham_backup.json"   # backup dùng cho nút QUAY LẠI (Undo) khi xóa kho
FILE_SP_INPUT = "san_pham_dien_tu.json"  # file người dùng cung cấp


class UngDung:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Phần Mềm Quản Lý Bán Hàng (Pro Simple)")
        self.root.geometry("1000x700")

        self.nguoi_dang_nhap = None
        self.gio_hang = []

        self.che_do_kho = ""
        self.che_do_ns = ""

        self.entry_user = self.entry_pass = self.combo_role = None

        self.tree_ban_hang = None
        self.tree_gio = None
        self.lbl_tong_tien = None

        self.tree_lich_su = None

        self.e_k_ma = self.e_k_ten = self.e_k_sl = self.e_k_gia = None
        self.tree_kho = None

        self.e_n_ma = self.e_n_user = self.e_n_pass = None
        self.e_n_ten = self.e_n_ngay = self.e_n_luong = None
        self.c_n_role = None
        self.tree_ns = None

        self.khoi_tao_du_lieu()
        self.hien_thi_manh_hinh_login()

    # ==============================
    # TIỆN ÍCH JSON
    # ==============================
    def doc_file(self, ten_file):
        if not os.path.exists(ten_file):
            return []
        try:
            with open(ten_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []

    def ghi_file(self, ten_file, du_lieu):
        with open(ten_file, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False, indent=4)

    # ==============================
    # NẠP SẢN PHẨM TỪ FILE NGƯỜI DÙNG
    # ==============================
    def nap_san_pham_tu_file_nguoi_dung(self):
        if not os.path.exists(FILE_SP_INPUT):
            return
        
        try:
            data = self.doc_file(FILE_SP_INPUT)
            chuyen_doi = []

            for sp in data:
                chuyen_doi.append({
                    "id": sp.get("ma_sp"),
                    "ten": sp.get("ten_hang"),
                    "sl": sp.get("so_luong_ton", 0),
                    "gia": sp.get("don_gia", 0)
                })

            # Chỉ nạp nếu kho đang rỗng
            ds_sp = self.doc_file(FILE_SP)
            if len(ds_sp) == 0:
                self.ghi_file(FILE_SP, chuyen_doi)

        except Exception as e:
            messagebox.showerror("Lỗi file sản phẩm đầu vào", str(e))

    # ==============================
    # KHỞI TẠO DỮ LIỆU
    # ==============================
    def khoi_tao_du_lieu(self):
        # tạo user mặc định
        if not os.path.exists(FILE_USER):
            users = [
                {"ma_nv": "NV000", "username": "admin", "password": "Ad00001@", "role": "admin",
                 "ten": "Quản Trị Viên", "ngay_vao_lam": "2020-01-01", "luong": 2000000},
                {"ma_nv": "NV001", "username": "nv1", "password": "Nv1@01234", "role": "user",
                 "ten": "Nhân Viên", "ngay_vao_lam": "2022-01-01", "luong": 1800000},
            ]
            self.ghi_file(FILE_USER, users)

        if not os.path.exists(FILE_SP):
            self.ghi_file(FILE_SP, [])

        # Nạp sản phẩm từ file bạn cung cấp
        self.nap_san_pham_tu_file_nguoi_dung()

        if not os.path.exists(FILE_HD):
            self.ghi_file(FILE_HD, [])

    # ==============================
    # ĐĂNG NHẬP
    # ==============================
    def dang_nhap(self):
        user = (self.entry_user.get() or "").strip()
        pw = (self.entry_pass.get() or "").strip()
        role = (self.combo_role.get() or "").strip()

        ds = self.doc_file(FILE_USER)
        tim = next((u for u in ds if u.get("username") == user and u.get("password") == pw), None)

        if not tim:
            messagebox.showerror("Lỗi", "Sai tài khoản / mật khẩu")
            return
        if tim.get("role") != role:
            messagebox.showerror("Lỗi", "Sai vai trò")
            return

        self.nguoi_dang_nhap = tim
        self.gio_hang = []
        self.hien_thi_manh_hinh_chinh()

    def dang_xuat(self):
        self.nguoi_dang_nhap = None
        self.gio_hang = []
        self.hien_thi_manh_hinh_login()

    # ==============================
    # UI LOGIN
    # ==============================
    def xoa_man_hinh(self):
        for w in self.root.winfo_children():
            w.destroy()

    def hien_thi_manh_hinh_login(self):
        self.xoa_man_hinh()

        f = tk.Frame(self.root)
        f.pack(pady=50)

        tk.Label(f, text="ĐĂNG NHẬP", font=("Arial", 18, "bold")).pack(pady=10)

        tk.Label(f, text="Username").pack()
        self.entry_user = tk.Entry(f)
        self.entry_user.pack()

        tk.Label(f, text="Password").pack()
        self.entry_pass = tk.Entry(f, show="*")
        self.entry_pass.pack()

        tk.Label(f, text="Vai trò").pack()
        self.combo_role = ttk.Combobox(f, values=["admin", "user"], state="readonly")
        self.combo_role.current(1)
        self.combo_role.pack(pady=5)

        tk.Button(f, text="Đăng nhập", bg="blue", fg="white", command=self.dang_nhap).pack(pady=10)

    # ==============================
    # MÀN HÌNH CHÍNH
    # ==============================
    def hien_thi_manh_hinh_chinh(self):
        self.xoa_man_hinh()

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        menu_ht = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hệ thống", menu=menu_ht)

        if self.nguoi_dang_nhap["role"] == "admin":
            menu_ht.add_command(label="Tải API Sản phẩm", command=self.nap_du_lieu_api)

        menu_ht.add_command(label="Đăng xuất", command=self.dang_xuat)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        tab_ban = tk.Frame(notebook)
        notebook.add(tab_ban, text="Bán Hàng")
        self.xay_dung_tab_ban_hang(tab_ban)

        tab_ls = tk.Frame(notebook)
        notebook.add(tab_ls, text="Lịch Sử Hóa Đơn")
        self.xay_dung_tab_lich_su(tab_ls)

        if self.nguoi_dang_nhap["role"] == "admin":
            tab_kho = tk.Frame(notebook)
            notebook.add(tab_kho, text="Quản Lý Kho")
            self.xay_dung_tab_kho(tab_kho)

            tab_ns = tk.Frame(notebook)
            notebook.add(tab_ns, text="Quản Lý Nhân Sự")
            self.xay_dung_tab_nhan_su(tab_ns)

    # ==============================
    # TAB BÁN HÀNG
    # ==============================
    def xay_dung_tab_ban_hang(self, parent):
        f_trai = tk.LabelFrame(parent, text="Sản phẩm")
        f_trai.pack(side="left", fill="both", expand=True)

        self.tree_ban_hang = ttk.Treeview(
            f_trai, columns=("id", "ten", "sl", "gia"), show="headings"
        )
        for c, t, w in [
            ("id", "Mã", 80),
            ("ten", "Tên", 200),
            ("sl", "Tồn", 80),
            ("gia", "Giá", 120),
        ]:
            self.tree_ban_hang.heading(c, text=t)
            self.tree_ban_hang.column(c, width=w)
        self.tree_ban_hang.pack(fill="both", expand=True)
        self.tree_ban_hang.bind("<Double-1>", self.them_vao_gio)

        f_phai = tk.LabelFrame(parent, text="Giỏ hàng")
        f_phai.pack(side="right", fill="both", expand=True)

        self.tree_gio = ttk.Treeview(
            f_phai, columns=("ten", "sl", "tt"), show="headings"
        )
        self.tree_gio.heading("ten", text="Tên SP")
        self.tree_gio.heading("sl", text="SL")
        self.tree_gio.heading("tt", text="Thành tiền")
        self.tree_gio.pack(fill="both", expand=True)

        self.lbl_tong_tien = tk.Label(
            f_phai, text="Tổng: 0 VNĐ", fg="red", font=("Arial", 14)
        )
        self.lbl_tong_tien.pack(pady=5)

        tk.Button(f_phai, text="Thanh toán", bg="orange", command=self.thanh_toan).pack(fill="x")
        tk.Button(f_phai, text="Xóa giỏ hàng", command=self.xoa_gio_hang).pack(fill="x")

        self.load_data_ban_hang()

    def load_data_ban_hang(self):
        if not self.tree_ban_hang:
            return
        for i in self.tree_ban_hang.get_children():
            self.tree_ban_hang.delete(i)

        ds_sp = self.doc_file(FILE_SP)
        for sp in ds_sp:
            self.tree_ban_hang.insert(
                "", "end",
                values=(sp["id"], sp["ten"], sp["sl"], f"{sp['gia']:,}")
            )

        # loại bỏ sản phẩm đã bị xóa
        id_hien_tai = {sp["id"] for sp in ds_sp}
        self.gio_hang = [g for g in self.gio_hang if g["id"] in id_hien_tai]
        self.cap_nhat_gio()

    def them_vao_gio(self, event=None):
        chon = self.tree_ban_hang.focus()
        if not chon:
            return

        id_sp, ten, sl_str, gia_str = self.tree_ban_hang.item(chon, "values")
        ton_kho = int(sl_str)
        gia = int(str(gia_str).replace(",", ""))

        top = tk.Toplevel(self.root)
        top.title("Nhập số lượng")
        tk.Label(top, text=f"Mua: {ten}").pack(padx=10, pady=5)

        e_sl = tk.Entry(top)
        e_sl.pack(pady=5)
        e_sl.focus()

        def ok():
            try:
                sl = int(e_sl.get())
                if sl <= 0:
                    messagebox.showerror("Lỗi", "SL > 0")
                    return
                if sl > ton_kho:
                    messagebox.showerror("Lỗi", "Không đủ hàng")
                    return

                for m in self.gio_hang:
                    if m["id"] == id_sp:
                        m["sl"] += sl
                        m["tt"] = m["sl"] * m["gia"]
                        break
                else:
                    self.gio_hang.append({
                        "id": id_sp,
                        "ten": ten,
                        "sl": sl,
                        "gia": gia,
                        "tt": sl * gia
                    })

                self.cap_nhat_gio()
                top.destroy()
            except:
                messagebox.showerror("Lỗi", "Sai dữ liệu")

        tk.Button(top, text="OK", command=ok).pack(pady=5)

    def cap_nhat_gio(self):
        for i in self.tree_gio.get_children():
            self.tree_gio.delete(i)

        tong = 0
        for m in self.gio_hang:
            tong += m["tt"]
            self.tree_gio.insert("", "end", values=(m["ten"], m["sl"], f"{m['tt']:,}"))

        self.lbl_tong_tien.config(text=f"Tổng: {tong:,} VNĐ")

    def xoa_gio_hang(self):
        self.gio_hang = []
        self.cap_nhat_gio()

    def thanh_toan(self):
        if not self.gio_hang:
            return

        ds_sp = self.doc_file(FILE_SP)
        map_sp = {sp["id"]: sp for sp in ds_sp}

        loi = []
        for m in self.gio_hang:
            pid = m["id"]
            if pid not in map_sp:
                loi.append(f"{m['ten']} (đã bị xóa khỏi kho)")
            elif m["sl"] > map_sp[pid]["sl"]:
                loi.append(f"{m['ten']} (không đủ tồn)")

        if loi:
            messagebox.showerror("Lỗi", "\n".join(loi))
            self.load_data_ban_hang()
            return

        # tạo hóa đơn
        ds_hd = self.doc_file(FILE_HD)
        ma = f"HD{len(ds_hd)+1:03d}"
        tong = sum(m["tt"] for m in self.gio_hang)

        hd = {
            "ma": ma,
            "nguoi": self.nguoi_dang_nhap["ten"],
            "ngay": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tong": tong,
            "chitiet": self.gio_hang
        }
        ds_hd.append(hd)
        self.ghi_file(FILE_HD, ds_hd)

        # trừ kho
        for m in self.gio_hang:
            map_sp[m["id"]]["sl"] -= m["sl"]

        self.ghi_file(FILE_SP, list(map_sp.values()))

        messagebox.showinfo("OK", "Thanh toán thành công!")
        self.xoa_gio_hang()
        self.load_data_ban_hang()
        self.load_lich_su()

    
    def xay_dung_tab_lich_su(self, parent):
        tk.Button(parent, text="Làm mới", command=self.load_lich_su).pack(pady=5)
        tk.Button(parent, text="Xem chi tiết", bg="yellow",
                  command=self.xem_chi_tiet_hoa_don).pack(pady=5)

        self.tree_lich_su = ttk.Treeview(
            parent, columns=("ma", "nguoi", "ngay", "tong"), show="headings"
        )
        for c, t, w in [
            ("ma", "Mã", 90),
            ("nguoi", "Người lập", 180),
            ("ngay", "Ngày", 160),
            ("tong", "Tổng", 120),
        ]:
            self.tree_lich_su.heading(c, text=t)
            self.tree_lich_su.column(c, width=w)
        self.tree_lich_su.pack(fill="both", expand=True)

        self.load_lich_su()

    def load_lich_su(self):
        for i in self.tree_lich_su.get_children():
            self.tree_lich_su.delete(i)

        ds = self.doc_file(FILE_HD)
        for hd in ds:
            self.tree_lich_su.insert(
                "", "end",
                values=(hd["ma"], hd["nguoi"], hd["ngay"], f"{hd['tong']:,}")
            )

    def xem_chi_tiet_hoa_don(self):
        chon = self.tree_lich_su.focus()
        if not chon:
            return
        ma = self.tree_lich_su.item(chon, "values")[0]

        ds = self.doc_file(FILE_HD)
        hd = next((x for x in ds if x["ma"] == ma), None)
        if not hd:
            return

        top = tk.Toplevel(self.root)
        top.title(f"Chi tiết {ma}")

        tk.Label(top, text=f"Hóa đơn {ma} - {hd['ngay']}").pack(pady=5)

        tv = ttk.Treeview(top, columns=("ten", "sl", "gia"), show="headings")
        tv.heading("ten", text="Tên")
        tv.heading("sl", text="SL")
        tv.heading("gia", text="Giá")
        tv.pack(fill="both", expand=True)

        for sp in hd["chitiet"]:
            tv.insert("", "end", values=(
                sp["ten"],
                sp["sl"],
                f"{sp['gia']:,}",
            ))

    
    def xay_dung_tab_kho(self, parent):
        f = tk.Frame(parent)
        f.pack(pady=5)

        tk.Label(f, text="Mã").grid(row=0, column=0)
        self.e_k_ma = tk.Entry(f); self.e_k_ma.grid(row=0, column=1)

        tk.Label(f, text="Tên").grid(row=0, column=2)
        self.e_k_ten = tk.Entry(f); self.e_k_ten.grid(row=0, column=3)

        tk.Label(f, text="SL").grid(row=0, column=4)
        self.e_k_sl = tk.Entry(f); self.e_k_sl.grid(row=0, column=5)

        tk.Label(f, text="Giá").grid(row=0, column=6)
        self.e_k_gia = tk.Entry(f); self.e_k_gia.grid(row=0, column=7)

        tk.Button(f, text="Thêm", command=self.kho_chuan_bi_them).grid(row=1, column=0, columnspan=2)
        tk.Button(f, text="Sửa", command=self.kho_chuan_bi_sua).grid(row=1, column=2, columnspan=2)
        tk.Button(f, text="Xóa", command=self.kho_xoa).grid(row=1, column=4, columnspan=2)
        tk.Button(f, text="Lưu", bg="green", fg="white", command=self.kho_luu).grid(row=1, column=6, columnspan=2)

        tk.Button(f, text="Quay lại (UNDO)", bg="orange", command=self.kho_undo).grid(row=2, column=0, columnspan=4, pady=5)
        tk.Label(f, text="Tìm kiếm(Mã/Tên):").grid(row=2, column=3, columnspan=4,padx=5)  
        self.e_tim_kho = tk.Entry(f)
        self.e_tim_kho.grid(row=2, column=5, columnspan=3, padx=10)

        tk.Button(f, text="Tìm", command=self.tim_kho).grid(
            row=2, column=7, columnspan=5, padx=10, pady=5)
        
        tk.Button(f, text="Hiển thị tất cả", command=self.hien_thi_tat_ca_kho).grid(row=2, column=8, padx=5)


        self.tree_kho = ttk.Treeview(parent, columns=("id", "ten", "sl", "gia"), show="headings")
        for c, t, w in [
            ("id", "Mã", 100),
            ("ten", "Tên", 200),
            ("sl", "SL", 80),
            ("gia", "Giá", 120),
        ]:
            self.tree_kho.heading(c, text=t)
            self.tree_kho.column(c, width=w)
        self.tree_kho.pack(fill="both", expand=True)

        self.tree_kho.bind("<<TreeviewSelect>>", self.kho_chon_dong)

        self.load_kho()

    def load_kho(self):
        for i in self.tree_kho.get_children():
            self.tree_kho.delete(i)

        ds = self.doc_file(FILE_SP)
        for sp in ds:
            self.tree_kho.insert("", "end", values=(
                sp["id"], sp["ten"], sp["sl"], f"{sp['gia']:,}"
            ))

    def kho_chon_dong(self, event=None):
        chon = self.tree_kho.focus()
        if not chon:
            return

        v = self.tree_kho.item(chon, "values")

        self.e_k_ma.config(state="normal")
        self.e_k_ma.delete(0, tk.END); self.e_k_ma.insert(0, v[0])
        self.e_k_ten.delete(0, tk.END); self.e_k_ten.insert(0, v[1])
        self.e_k_sl.delete(0, tk.END);  self.e_k_sl.insert(0, v[2])
        self.e_k_gia.delete(0, tk.END); self.e_k_gia.insert(0, str(v[3]).replace(",", ""))

    def kho_chuan_bi_them(self):
        self.che_do_kho = "them"
        self.e_k_ma.config(state="normal")
        for e in (self.e_k_ma, self.e_k_ten, self.e_k_sl, self.e_k_gia):
            e.delete(0, tk.END)
        self.e_k_ma.focus()

    def kho_chuan_bi_sua(self):
        if not self.tree_kho.selection():
            messagebox.showerror("Lỗi", "Chọn dòng để sửa")
            return
        self.che_do_kho = "sua"
        self.e_k_ma.config(state="readonly")

    def kho_xoa(self):
        if not self.tree_kho.selection():
            return

        id_xoa = self.tree_kho.item(self.tree_kho.selection()[0], "values")[0]

        if not messagebox.askyesno("Xóa", "Chắn chắn xóa?"):
            return

        ds = self.doc_file(FILE_SP)

        
        self.ghi_file(FILE_SP_BAK, ds)

        ds = [x for x in ds if x["id"] != id_xoa]
        self.ghi_file(FILE_SP, ds)

        self.load_kho()
        self.load_data_ban_hang()

    def kho_undo(self):
        if not os.path.exists(FILE_SP_BAK):
            messagebox.showerror("Lỗi", "Không có backup để phục hồi")
            return

        ds_bak = self.doc_file(FILE_SP_BAK)
        self.ghi_file(FILE_SP, ds_bak)

        messagebox.showinfo("Undo", "Đã phục hồi kho")
        self.load_kho()
        self.load_data_ban_hang()

    def kho_luu(self):
        id_sp = self.e_k_ma.get().strip()
        ten = self.e_k_ten.get().strip()

        try:
            sl = int(self.e_k_sl.get())
            gia = int(self.e_k_gia.get())
        except:
            messagebox.showerror("Lỗi", "SL và giá phải là số")
            return

        ds = self.doc_file(FILE_SP)

        if self.che_do_kho == "them":
            if any(x["id"] == id_sp for x in ds):
                messagebox.showerror("Lỗi", "Mã SP đã tồn tại")
                return
            ds.append({"id": id_sp, "ten": ten, "sl": sl, "gia": gia})

        elif self.che_do_kho == "sua":
            found = False
            for x in ds:
                if x["id"] == id_sp:
                    x["ten"] = ten
                    x["sl"] = sl
                    x["gia"] = gia
                    found = True
                    break
            if not found:
                messagebox.showerror("Lỗi", "Không tìm thấy SP")
                return

            self.e_k_ma.config(state="normal")

        else:
            messagebox.showerror("Lỗi", "Chưa chọn chế độ")
            return

        self.ghi_file(FILE_SP, ds)
        self.che_do_kho = ""
        self.load_kho()
        self.load_data_ban_hang()

    def tim_kho(self):
        tu_khoa = self.e_tim_kho.get().strip().lower()

        # Xóa dữ liệu cũ trên tree
        for i in self.tree_kho.get_children():
            self.tree_kho.delete(i)

        ds = self.doc_file(FILE_SP)

        # Nếu ô tìm rỗng → load lại toàn bộ kho
        if tu_khoa == "":
            for sp in ds:
                self.tree_kho.insert("", "end", values=(
                    sp["id"], sp["ten"], sp["sl"], f"{sp['gia']:,}"
                ))
            return

        # Lọc theo MÃ hoặc TÊN
        for sp in ds:
            if tu_khoa in sp["id"].lower() or tu_khoa in sp["ten"].lower():
                self.tree_kho.insert("", "end", values=(
                    sp["id"], sp["ten"], sp["sl"], f"{sp['gia']:,}"
                ))
    def hien_thi_tat_ca_kho(self):
   
        self.e_tim_kho.delete(0, tk.END)


        for i in self.tree_kho.get_children():
            self.tree_kho.delete(i)


        ds = self.doc_file(FILE_SP)
        for sp in ds:
            self.tree_kho.insert("", "end", values=(
                sp["id"], sp["ten"], sp["sl"], f"{sp['gia']:,}"
            ))


    def xay_dung_tab_nhan_su(self, parent):
        f = tk.Frame(parent); f.pack(pady=5)

        tk.Label(f, text="Mã").grid(row=0, column=0)
        self.e_n_ma = tk.Entry(f); self.e_n_ma.grid(row=0, column=1)

        tk.Label(f, text="User").grid(row=0, column=2)
        self.e_n_user = tk.Entry(f); self.e_n_user.grid(row=0, column=3)

        tk.Label(f, text="Pass").grid(row=0, column=4)
        self.e_n_pass = tk.Entry(f); self.e_n_pass.grid(row=0, column=5)

        tk.Label(f, text="Tên").grid(row=1, column=0)
        self.e_n_ten = tk.Entry(f); self.e_n_ten.grid(row=1, column=1)

        tk.Label(f, text="Role").grid(row=1, column=2)
        self.c_n_role = ttk.Combobox(f, values=["admin", "user"]); self.c_n_role.grid(row=1, column=3)

        tk.Label(f, text="Ngày vào").grid(row=1, column=4)
        self.e_n_ngay = tk.Entry(f); self.e_n_ngay.grid(row=1, column=5)

        tk.Label(f, text="Lương").grid(row=1, column=6)
        self.e_n_luong = tk.Entry(f); self.e_n_luong.grid(row=1, column=7)

        tk.Button(f, text="Thêm", command=self.ns_chuan_bi_them).grid(row=2, column=0, columnspan=2)
        tk.Button(f, text="Sửa", command=self.ns_chuan_bi_sua).grid(row=2, column=2, columnspan=2)
        tk.Button(f, text="Xóa", command=self.ns_xoa).grid(row=2, column=4, columnspan=2)
        tk.Button(f, text="Lưu", bg="green", fg="white", command=self.ns_luu).grid(row=2, column=6, columnspan=2)

        tk.Label(f, text="Tìm kiếm (Mã / User / Tên):").grid(row=3, column=0, columnspan=2, pady=5)

        self.e_tim_ns = tk.Entry(f)
        self.e_tim_ns.grid(row=3, column=2, columnspan=3, padx=5)

        tk.Button(f, text="Tìm", command=self.tim_nhan_su).grid(row=3, column=5, padx=5)
        tk.Button(f, text="Hiển thị tất cả", command=self.hien_thi_tat_ca_ns).grid(row=3, column=6, padx=5)


        self.tree_ns = ttk.Treeview(parent, columns=("ma","user","ten","role","luong"), show="headings")
        for c in ["ma","user","ten","role","luong"]:
            self.tree_ns.heading(c, text=c)
        self.tree_ns.pack(fill="both", expand=True)

        self.tree_ns.bind("<<TreeviewSelect>>", self.ns_chon_dong)
        self.load_ns()

    def load_ns(self):
        for i in self.tree_ns.get_children():
            self.tree_ns.delete(i)

        ds = self.doc_file(FILE_USER)
        for u in ds:
            self.tree_ns.insert("", "end", values=(
                u["ma_nv"], u["username"], u["ten"], u["role"], u["luong"]
            ))
    def tim_nhan_su(self):
        tu_khoa = self.e_tim_ns.get().strip().lower()

        # Xóa tree cũ
        for i in self.tree_ns.get_children():
            self.tree_ns.delete(i)

        ds = self.doc_file(FILE_USER)

        # Nếu không nhập gì → load lại tất cả
        if tu_khoa == "":
            for u in ds:
                self.tree_ns.insert("", "end", values=(
                    u["ma_nv"], u["username"], u["ten"], u["role"], u["luong"]
                ))
            return

        # Tìm theo mã / username / tên / role
        for u in ds:
            if (
                tu_khoa in u["ma_nv"].lower()
                or tu_khoa in u["username"].lower()
                or tu_khoa in u["ten"].lower()
                or tu_khoa in u["role"].lower()
            ):
                self.tree_ns.insert("", "end", values=(
                    u["ma_nv"], u["username"], u["ten"], u["role"], u["luong"]
                ))

    def ns_chon_dong(self, event=None):
        chon = self.tree_ns.focus()
        if not chon:
            return

        ma, user, ten, role, luong = self.tree_ns.item(chon, "values")

        ds = self.doc_file(FILE_USER)
        u = next((x for x in ds if x["ma_nv"] == ma), None)
        if not u:
            return

        self.e_n_ma.config(state="normal")
        self.e_n_ma.delete(0, tk.END); self.e_n_ma.insert(0, u["ma_nv"])
        self.e_n_user.delete(0, tk.END); self.e_n_user.insert(0, u["username"])
        self.e_n_pass.delete(0, tk.END); self.e_n_pass.insert(0, u["password"])
        self.e_n_ten.delete(0, tk.END); self.e_n_ten.insert(0, u["ten"])
        self.c_n_role.set(u["role"])
        self.e_n_ngay.delete(0, tk.END); self.e_n_ngay.insert(0, u["ngay_vao_lam"])
        self.e_n_luong.delete(0, tk.END); self.e_n_luong.insert(0, u["luong"])
    def hien_thi_tat_ca_ns(self):
        self.e_tim_ns.delete(0, tk.END)

        for i in self.tree_ns.get_children():
            self.tree_ns.delete(i)

        self.load_ns()

    def ns_chuan_bi_them(self):
        self.che_do_ns = "them"
        for e in (self.e_n_ma,self.e_n_user,self.e_n_pass,self.e_n_ten,self.e_n_ngay,self.e_n_luong):
            e.delete(0, tk.END)
        self.c_n_role.set("")
        self.e_n_ma.config(state="normal")
        self.e_n_ma.focus()

    def ns_chuan_bi_sua(self):
        if not self.tree_ns.selection():
            messagebox.showerror("Lỗi", "Chọn dòng để sửa")
            return
        self.che_do_ns = "sua"
        self.e_n_ma.config(state="readonly")

    def ns_xoa(self):
        if not self.tree_ns.selection():
            return

        ma = self.tree_ns.item(self.tree_ns.selection()[0], "values")[0]

        if not messagebox.askyesno("Xóa", "Bạn chắc chắn muốn xóa?"):
            return

        ds = [x for x in self.doc_file(FILE_USER) if x["ma_nv"] != ma]
        self.ghi_file(FILE_USER, ds)
        self.load_ns()

    def ns_luu(self):
        ma = self.e_n_ma.get().strip()
        user = self.e_n_user.get().strip()
        pw = self.e_n_pass.get().strip()
        ten = self.e_n_ten.get().strip()
        role = self.c_n_role.get().strip()
        ngay = self.e_n_ngay.get().strip()

        # ===== KIỂM TRA MẬT KHẨU MẠNH =====
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$"
        if not re.match(pattern, pw):
            messagebox.showerror(
                "Mật khẩu yếu",
                "Mật khẩu phải có:\n"
                "- Ít nhất 8 ký tự\n"
                "- 1 chữ hoa\n"
                "- 1 chữ thường\n"
                "- 1 số\n"
                "- 1 ký tự đặc biệt (@, #, !, ...)"
            )
            return
        try:
            luong = int(self.e_n_luong.get())
        except:
            messagebox.showerror("Lỗi", "Lương phải là số")
            return

        ds = self.doc_file(FILE_USER)
        nguoi = {
            "ma_nv": ma,
            "username": user,
            "password": pw,
            "role": role,
            "ten": ten,
            "ngay_vao_lam": ngay,
            "luong": luong
        }

        if self.che_do_ns == "them":
            if any(x["ma_nv"] == ma for x in ds):
                messagebox.showerror("Lỗi", "Trùng mã NV")
                return
            ds.append(nguoi)

        elif self.che_do_ns == "sua":
            found = False
            for i, x in enumerate(ds):
                if x["ma_nv"] == ma:
                    ds[i] = nguoi
                    found = True
                    break
            if not found:
                messagebox.showerror("Lỗi", "Không tìm thấy NV để sửa")
                return

            self.e_n_ma.config(state="normal")

        else:
            messagebox.showerror("Lỗi", "Chưa chọn chế độ")
            return

        self.ghi_file(FILE_USER, ds)
        self.che_do_ns = ""
        self.load_ns()
        messagebox.showinfo("OK", "Lưu nhân sự thành công")


    def nap_du_lieu_api(self):
        try:
            url = "https://api.npoint.io/881fe47e8b6245bbe49a"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data_api = resp.json()

            if isinstance(data_api, list):
                products = data_api
            else:
                products = data_api.get("products", data_api.get("items", []))

            ds = self.doc_file(FILE_SP)

            for i, sp in enumerate(products):
                id_ = str(sp.get("id") or f"API_{i}")

                # nếu đã có thì bỏ qua
                if any(x["id"] == id_ for x in ds):
                    continue

                ten = sp.get("ten") or sp.get("name") or sp.get("title") or "No Name"
                sl = int(sp.get("sl") or sp.get("stock") or 0)
                gia = int(sp.get("gia") or sp.get("price") or 0)

                ds.append({"id": id_, "ten": ten, "sl": sl, "gia": gia})

            self.ghi_file(FILE_SP, ds)

            messagebox.showinfo("API", f"Đã nhập {len(products)} sản phẩm.")
            self.load_kho()
            self.load_data_ban_hang()

        except Exception as e:
            messagebox.showerror("Lỗi API", str(e))

    # ==============================
    def chay(self):
        self.root.mainloop()


if __name__ == "__main__":
    UngDung().chay()
