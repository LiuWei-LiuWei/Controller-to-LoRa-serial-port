import serial
import serial.tools.list_ports
import pygame
import time
import tkinter as tk
from tkinter import ttk, messagebox

# 初始化全局变量
serial_port = None
baud_rate = 115200
joystick_connected = False
ser = None

# 初始化 Pygame
pygame.init()
pygame.joystick.init()

# 检查手柄是否连接
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joystick_connected = True
    print(f"已连接手柄: {joystick.get_name()}")
else:
    print("没有检测到手柄。")

# 定义一个主窗体
root = tk.Tk()
root.title("手柄与串口控制面板")
root.geometry("600x600")  # 设置窗体大小

# 自动检测可用串口
def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# 创建顶部串口设置区域
def setup_serial():
    global serial_port, baud_rate, ser
    try:
        serial_port = port_combobox.get()
        baud_rate = int(baud_combobox.get())
        ser = serial.Serial(serial_port, baud_rate, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
        if ser.is_open:
            messagebox.showinfo("连接成功", f"成功连接到 {serial_port} @ {baud_rate} 波特率")
            serial_status_label.config(text=f"串口已连接: {serial_port} @ {baud_rate} 波特率", fg="green")
        else:
            raise Exception("串口未打开")
    except Exception as e:
        messagebox.showerror("连接失败", f"无法连接到串口: {e}")
        serial_status_label.config(text="串口连接失败", fg="red")

# 创建断开连接按钮
def disconnect_serial():
    global ser
    try:
        if ser and ser.is_open:
            ser.close()
            serial_status_label.config(text="串口已断开", fg="red")
            messagebox.showinfo("断开成功", "串口连接已成功断开")
        else:
            messagebox.showwarning("警告", "串口尚未连接")
    except Exception as e:
        messagebox.showerror("断开失败", f"无法断开串口: {e}")

top_frame = tk.Frame(root, height=100, relief=tk.RIDGE, bd=2)
top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

tk.Label(top_frame, text="选择LoRa串口:").pack(side=tk.LEFT, padx=5)
port_combobox = ttk.Combobox(top_frame, values=get_available_ports(), width=10)
port_combobox.pack(side=tk.LEFT, padx=5)

# 默认选择第一个可用端口（如果有）
available_ports = get_available_ports()
if available_ports:
    port_combobox.set(available_ports[0])
else:
    port_combobox.set("无可用端口")

tk.Label(top_frame, text="波特率:").pack(side=tk.LEFT, padx=5)
baud_combobox = ttk.Combobox(top_frame, values=["9600", "19200", "38400", "57600", "115200", "230400", "460800"], width=10)
baud_combobox.pack(side=tk.LEFT, padx=5)
baud_combobox.set("115200")

connect_button = tk.Button(top_frame, text="连接", command=setup_serial)
connect_button.pack(side=tk.LEFT, padx=10)

disconnect_button = tk.Button(top_frame, text="断开连接", command=disconnect_serial)
disconnect_button.pack(side=tk.LEFT, padx=10)

serial_status_label = tk.Label(top_frame, text="串口未连接", fg="red")
serial_status_label.pack(side=tk.LEFT, padx=10)

# 创建中间摇杆位置显示区域
middle_frame = tk.Frame(root, height=400, relief=tk.RIDGE, bd=2, bg="white")
middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

# 初始化 Pygame 绘制区域
canvas = tk.Canvas(middle_frame, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

# 创建底部手柄状态显示区域
bottom_frame = tk.Frame(root, height=100, relief=tk.RIDGE, bd=2)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

joystick_status_label = tk.Label(bottom_frame, text="手柄未连接", fg="red")
joystick_status_label.pack(side=tk.LEFT, padx=10)

# 绘制摇杆位置
def update_joystick():
    global joystick_connected

    canvas.delete("all")  # 清空画布

    # 获取画布的宽高
    width, height = canvas.winfo_width(), canvas.winfo_height()

    # 绘制中心点和参考线
    canvas.create_line(width // 2, 0, width // 2, height, fill="gray", dash=(4, 4))
    canvas.create_line(0, height // 2, width, height // 2, fill="gray", dash=(4, 4))

    if joystick_connected:
        joystick_status_label.config(text=f"手柄已连接: {joystick.get_name()}", fg="green")

        # 获取摇杆的x和y轴值，并将其映射到 -100 到 100
        axis_x = joystick.get_axis(0) * 100  # 摇杆的x轴映射
        axis_y = joystick.get_axis(1) * 100  # 摇杆的y轴映射

        # 映射摇杆位置到画布中心（确保位置映射是对称的）
        display_x = int(((axis_x + 100) / 200) * width)  # 映射后的位置
        display_y = int(((axis_y + 100) / 200) * height)

        # 绘制摇杆位置
        canvas.create_oval(
            display_x - 10, display_y - 10,
            display_x + 10, display_y + 10,
            fill="red"
        )

        # 如果串口已连接，发送数据
        if ser and ser.is_open:
            data_str = f"x: {int(axis_x)} y: {int(axis_y)}\n"  # 发送整数数据
            ser.write(data_str.encode('utf-8'))

    else:
        joystick_status_label.config(text="手柄未连接", fg="red")

    # 递归调用更新摇杆位置
    root.after(50, update_joystick)


# 启动摇杆更新
update_joystick()

# 创建重新连接手柄的功能
def reconnect_joystick():
    global joystick, joystick_connected
    pygame.joystick.quit()
    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        joystick_connected = True
        joystick_status_label.config(text=f"手柄已连接: {joystick.get_name()}", fg="green")
        messagebox.showinfo("连接成功", f"已连接手柄: {joystick.get_name()}")
    else:
        joystick_connected = False
        joystick_status_label.config(text="手柄未连接", fg="red")
        messagebox.showwarning("连接失败", "未检测到手柄，请确保手柄已连接并重试。")

# 添加重新连接手柄按钮
reconnect_button = tk.Button(bottom_frame, text="重新连接手柄", command=reconnect_joystick)
reconnect_button.pack(side=tk.LEFT, padx=10)


# 主循环
try:
    root.mainloop()
except KeyboardInterrupt:
    print("\n退出程序。")
finally:
    if ser and ser.is_open:
        ser.close()
