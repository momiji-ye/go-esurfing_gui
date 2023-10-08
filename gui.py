import json
import os
from tkinter import messagebox as msgbox
from tkinter import simpledialog
import ttkbootstrap as ttk
import threading
import esurfing
import multiprocessing
import pystray
from PIL import Image
import sys

DEFAULT_CONF_FILE = "./ESurfingPy-CLI.json"


class Gui:
    def __init__(self, hide_console: bool = False):
        """init"""

        data = self.read_conf()
        self.login_thread = None  # 添加一个属性用于保存登录线程
        self.toplevel = ttk.Window(themename="lumen")
        self.toplevel.configure(width=600)
        self.toplevel.resizable(False, False)

        self.frame1 = ttk.Frame(self.toplevel)
        self.frame1.configure(padding=10)
        self.frame2 = ttk.Frame(self.frame1)
        self.frame2.configure(height=10)

        self.label_c = ttk.Label(self.frame2)
        self.label_c.configure(text='认证服务器 IP')
        self.label_c.grid(column=0, row=1)
        self.entry_c = ttk.Entry(self.frame2)
        self.entry_c.insert("0", data.get("wlanacip", ""))
        self.entry_c.grid(column=1, padx=5, pady=2, row=1)

        self.label_r = ttk.Label(self.frame2)
        self.label_r.configure(text='登录设备 MAC')
        self.label_r.grid(column=0, row=2, sticky="e")
        self.entry_r = ttk.Entry(self.frame2)
        self.entry_r.insert("0", data.get("wlanusermac", ""))
        self.entry_r.grid(column=1, padx=5, pady=2, row=2)

        self.label_a = ttk.Label(self.frame2)
        self.label_a.configure(text='账号')
        self.label_a.grid(column=0, row=3, sticky="e")
        self.entry_a = ttk.Entry(self.frame2)
        self.entry_a.insert("0", data.get("account", ""))
        self.entry_a.grid(column=1, padx=5, pady=2, row=3)

        self.label_p = ttk.Label(self.frame2)
        self.label_p.configure(text='密码')
        self.label_p.grid(column=0, row=4, sticky="e")
        self.entry_p = ttk.Entry(self.frame2)
        self.entry_p.configure(show="•")
        self.entry_p.insert("0", data.get("password", ""))
        self.entry_p.grid(column=1, padx=5, pady=2, row=4)

        self.var_save = ttk.BooleanVar(value=True)
        self.checkbutton_save = ttk.Checkbutton(self.frame2, variable=self.var_save)
        self.checkbutton_save.configure(text='保存信息')
        self.checkbutton_save.grid(column=1, row=5, pady=10)

        self.frame2.pack(side="top")
        self.frame3 = ttk.Frame(self.frame1)

        self.button_login = ttk.Button(self.frame3)
        self.button_login.configure(text='登录')
        self.button_login.pack(padx=5, side="left")
        self.button_login.configure(command=self.login)

        self.frame3.pack(side="top")
        self.separator = ttk.Separator(self.frame1)
        self.separator.configure(orient="horizontal")
        self.separator.pack(expand=True, fill="both", pady=8)
        self.frame4 = ttk.Frame(self.frame1)

        self.frame4.pack(side="top")
        self.frame1.pack(side="top")

        self.window = self.toplevel
        self.window.title("24岁,事校园认证")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # 设置关闭按钮的行为

        # 设置窗口居中
        self.window.geometry("+0+0")
        self.window.update_idletasks()

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.iconbitmap(default='114514.ico')

    def run(self):
        self.window.mainloop()

    @staticmethod
    def read_conf() -> dict:
        """读取配置"""
        if os.path.isfile(DEFAULT_CONF_FILE):
            try:
                with open(DEFAULT_CONF_FILE, encoding="utf-8") as f:
                    return json.loads(f.read())
            except json.JSONDecodeError:
                pass
        return {}

    def save_conf(self) -> bool:
        """保存配置"""
        try:
            with open(DEFAULT_CONF_FILE, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "wlanacip": self.entry_c.get(),
                    "wlanusermac": self.entry_r.get(),
                    "account": self.entry_a.get(),
                    "password": self.entry_p.get()
                }, indent=4))
                return True
        except PermissionError:
            msgbox.showwarning(
                title="警告",
                message="保存信息失败，可能的原因："
                        "\n1. 程序权限不足"
                        "\n2. 文件已被占用"
            )
        except Exception as exc:
            msgbox.showwarning(
                title="警告",
                message=f"保存信息失败，原因："
                        f"\n{exc}"
            )
        return False

    def on_close(self):
        """点击关闭按钮时的处理"""
        # 停止之前的登录线程
        if self.login_thread and self.login_thread.is_alive():
            self.login_thread.join()

        # 弹出选择框
        response = msgbox.askyesno("选择操作", "你想要退出程序吗？\n是 - 退出程序\n否 - 最小化到托盘")

        if response:
            self.window.destroy()
        else:
            def on_end():
                try:
                    # 停止之前的登录线程
                    if self.login_thread and self.login_thread.is_alive():
                        self.login_thread.join()
                finally:
                    tray_icon.stop()
                    self.window.destroy()

            def on_recover():
                tray_icon.stop()
                self.window.deiconify()  # 确保在托盘图标运行后才将窗口恢复
                self.window.focus_force()

            self.window.withdraw()
            # 最小化到托盘
            image = Image.open("114514.ico")
            menu = (
                pystray.MenuItem('恢复窗口', on_recover),
                pystray.MenuItem('退出程序', on_end)
            )
            tray_icon = pystray.Icon("name", image, "title", menu)
            tray_icon.run()

    def login(self):
        """登录"""

        def login_thread():
            if self.var_save.get():
                self.save_conf()
            success = esurfing.login(
                account=self.entry_a.get(),
                password=self.entry_p.get(),
                wlanacip=self.entry_c.get(),
                wlanusermac=self.entry_r.get()
            )

            # 获取当前进程数量
            process_count = len(multiprocessing.active_children())
            msgbox.showinfo("登入信息", success + '\n' + f"当前进程数量：{process_count}")
            self.window.after(0)  # 使用 after 方法确保在主线程中执行登录尝试

        # 停止之前的登录线程
        if self.login_thread and self.login_thread.is_alive():
            self.login_thread.join()

        # 创建一个线程来执行登录操作
        login_thread = threading.Thread(target=login_thread)
        login_thread.start()


if __name__ == "__main__":
    Gui().run()
