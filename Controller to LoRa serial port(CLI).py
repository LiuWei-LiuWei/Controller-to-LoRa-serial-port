import serial
import pygame
import time

# 初始化 Pygame
pygame.init()
pygame.joystick.init()

# 检查是否连接了手柄
if pygame.joystick.get_count() == 0:
    print("没有检测到手柄，请检查连接。")
    exit()

# 选择第一个连接的手柄
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"已连接手柄: {joystick.get_name()}")

# 串口设置
serial_port = 'COM8'  # 请根据实际串口号修改
baud_rate = 115200

# 打开串口
ser = serial.Serial(serial_port, baud_rate, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
if not ser.is_open:
    print(f"无法打开串口: {serial_port}")
    exit()

# 主循环
try:
    while True:
        pygame.event.pump()  # 更新事件队列

        # 获取左摇杆的 X 和 Y 值
        axis_x = joystick.get_axis(0)
        axis_y = joystick.get_axis(1)

        # 打印原始摇杆值（调试用）
        print(f"原始左摇杆: X={axis_x}, Y={axis_y}")

        # 将摇杆值从 [-1, 1] 映射到 [-100, 100]
        axis_x = axis_x * 100  # 手动映射
        axis_y = axis_y * 100

        # 打印最终映射的值
        print(f"映射后的左摇杆: X={axis_x}, Y={axis_y}")

        # 将 X 和 Y 值转为字符串格式
        data_str = f"x: {axis_x:.0f} y: {axis_y:.0f}\n"

        # 打印将要发送的数据
        print(f"发送的字符串数据: {data_str.strip()}")

        # 通过串口发送数据
        ser.write(data_str.encode('utf-8'))

        # 增加适当的延时
        time.sleep(0.1)  # 每0.1秒发送一次数据

except KeyboardInterrupt:
    print("\n退出程序。")

finally:
    joystick.quit()
    pygame.quit()
    ser.close()  # 关闭串口连接
