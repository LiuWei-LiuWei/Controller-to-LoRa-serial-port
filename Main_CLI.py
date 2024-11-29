import serial
import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick detected, please check the connection.")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick connected: {joystick.get_name()}")

serial_port = 'COM8'  # Modify based on actual serial port
baud_rate = 115200

ser = serial.Serial(serial_port, baud_rate, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
if not ser.is_open:
    print(f"Unable to open serial port: {serial_port}")
    exit()

try:
    while True:
        pygame.event.pump()

        axis_x = joystick.get_axis(0)
        axis_y = joystick.get_axis(1)

        print(f"Raw joystick: X={axis_x}, Y={axis_y}")

        axis_x = axis_x * 100
        axis_y = axis_y * 100

        print(f"Mapped joystick: X={axis_x}, Y={axis_y}")

        data_str = f"x: {axis_x:.0f} y: {axis_y:.0f}\n"

        print(f"Data to be sent: {data_str.strip()}")

        ser.write(data_str.encode('utf-8'))

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting program.")

finally:
    joystick.quit()
    pygame.quit()
    ser.close()
