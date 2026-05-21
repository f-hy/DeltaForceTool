import tkinter as tk
from datetime import datetime, timezone, timedelta
def update_time():
  # 设置时区为北京时间 (UTC+8)
  tz_bj = timezone(timedelta(hours=8))
  now = datetime.now(tz_bj)

  # 格式化时间为 24h制 HH:MM:SS.ms (不带单位)
  time_str = now.strftime("%H:%M:%S.") + f"{now.microsecond // 1000:03d}"
  label.config(text=time_str)

  # 每 10 毫秒刷新一次
  root.after(10, update_time)
# --- 拖动逻辑 ---
def start_move(event):
  root.x = event.x
  root.y = event.y
def stop_move(event):
  root.x = None
  root.y = None
def do_move(event):
  deltax = event.x - root.x
  deltay = event.y - root.y
  x = root.winfo_x() + deltax
  y = root.winfo_y() + deltay
  root.geometry(f"+{x}+{y}")
# --- 菜单逻辑 ---
def show_menu(event):
  # 在鼠标当前所在的屏幕坐标处弹出菜单
  menu.post(event.x_root, event.y_root)
# --- 主程序 UI 初始化 ---
root = tk.Tk()
root.overrideredirect(True) # 去除窗口边框和顶部栏
root.attributes("-topmost", True) # 窗口置顶显示

# 设置透明背景 (注意：此特性主要在 Windows 系统下完美生效)
# 选取一个不常用的颜色作为“抠像色” (纯黑可能会和某些字体边缘冲突，所以选一个特定的深色)
transparent_color = '#010203'
root.configure(bg=transparent_color)
root.attributes("-transparentcolor", transparent_color)

# 创建时间显示的标签
label = tk.Label(
  root,
  text="",
  font=("Consolas", 32, "bold"),
  fg="#00ff00", # 字体颜色
  bg=transparent_color # 标签背景色必须和窗口透明色一致，才能被完全“抠”掉
)
label.pack(padx=15, pady=10)

# --- 创建右键菜单 ---
menu = tk.Menu(root, tearoff=0) # tearoff=0 去除菜单默认的虚线可分离特性
menu.add_command(label="关闭程序", command=root.destroy)
# 如果以后需要，可以在这里继续添加菜单项，例如：
# menu.add_separator()
# menu.add_command(label="设置", command=some_function)

# 绑定鼠标事件
root.bind("<ButtonPress-1>", start_move) # 左键按下：准备拖动
root.bind("<ButtonRelease-1>", stop_move) # 左键释放：结束拖动
root.bind("<B1-Motion>", do_move) # 左键按住移动：拖动窗口
root.bind("<Button-3>", show_menu) # 右键点击：呼出菜单

update_time()
root.mainloop()
