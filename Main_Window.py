import serial
import serial.tools.list_ports
import pygame
import time
import tkinter as tk
from tkinter import ttk, messagebox

serial_port = None
baud_rate = 115200
joystick_connected = False
ser = None

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joystick_connected = True
    print(f"Joystick connected: {joystick.get_name()}")
else:
    print("No joystick detected.")

root = tk.Tk()
root.title("Joystick and Serial Control Panel")
root.geometry("600x600") 

def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def setup_serial():
    global serial_port, baud_rate, ser
    try:
        serial_port = port_combobox.get()
        baud_rate = int(baud_combobox.get())
        ser = serial.Serial(serial_port, baud_rate, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
        if ser.is_open:
            messagebox.showinfo("Connection Successful", f"Successfully connected to {serial_port} @ {baud_rate} baud rate")
            serial_status_label.config(text=f"Serial connected: {serial_port} @ {baud_rate} baud rate", fg="green")
        else:
            raise Exception("Serial port not open")
    except Exception as e:
        messagebox.showerror("Connection Failed", f"Unable to connect to serial port: {e}")
        serial_status_label.config(text="Serial connection failed", fg="red")

def disconnect_serial():
    global ser
    try:
        if ser and ser.is_open:
            ser.close()
            serial_status_label.config(text="Serial disconnected", fg="red")
            messagebox.showinfo("Disconnection Successful", "Serial connection successfully disconnected")
        else:
            messagebox.showwarning("Warning", "Serial not connected")
    except Exception as e:
        messagebox.showerror("Disconnection Failed", f"Unable to disconnect serial port: {e}")

top_frame = tk.Frame(root, height=100, relief=tk.RIDGE, bd=2)
top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

tk.Label(top_frame, text="Select LoRa Serial Port:").pack(side=tk.LEFT, padx=5)
port_combobox = ttk.Combobox(top_frame, values=get_available_ports(), width=10)
port_combobox.pack(side=tk.LEFT, padx=5)

available_ports = get_available_ports()
if available_ports:
    port_combobox.set(available_ports[0])
else:
    port_combobox.set("No available ports")

tk.Label(top_frame, text="Baud Rate:").pack(side=tk.LEFT, padx=5)
baud_combobox = ttk.Combobox(top_frame, values=["9600", "19200", "38400", "57600", "115200", "230400", "460800"], width=10)
baud_combobox.pack(side=tk.LEFT, padx=5)
baud_combobox.set("115200")

connect_button = tk.Button(top_frame, text="Connect", command=setup_serial)
connect_button.pack(side=tk.LEFT, padx=10)

disconnect_button = tk.Button(top_frame, text="Disconnect", command=disconnect_serial)
disconnect_button.pack(side=tk.LEFT, padx=10)

serial_status_label = tk.Label(top_frame, text="Serial not connected", fg="red")
serial_status_label.pack(side=tk.LEFT, padx=10)

middle_frame = tk.Frame(root, height=400, relief=tk.RIDGE, bd=2, bg="white")
middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

canvas = tk.Canvas(middle_frame, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

bottom_frame = tk.Frame(root, height=100, relief=tk.RIDGE, bd=2)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

joystick_status_label = tk.Label(bottom_frame, text="Joystick not connected", fg="red")
joystick_status_label.pack(side=tk.LEFT, padx=10)

def update_joystick():
    global joystick_connected

    canvas.delete("all") 

    width, height = canvas.winfo_width(), canvas.winfo_height()

    canvas.create_line(width // 2, 0, width // 2, height, fill="gray", dash=(4, 4))
    canvas.create_line(0, height // 2, width, height // 2, fill="gray", dash=(4, 4))

    if joystick_connected:
        joystick_status_label.config(text=f"Joystick connected: {joystick.get_name()}", fg="green")

        axis_x = joystick.get_axis(0) * 100  
        axis_y = joystick.get_axis(1) * 100  

        display_x = int(((axis_x + 100) / 200) * width)  
        display_y = int(((axis_y + 100) / 200) * height)

        canvas.create_oval(
            display_x - 10, display_y - 10,
            display_x + 10, display_y + 10,
            fill="red"
        )

        if ser and ser.is_open:
            data_str = f"x: {int(axis_x)} y: {int(axis_y)}\n"  
            ser.write(data_str.encode('utf-8'))

    else:
        joystick_status_label.config(text="Joystick not connected", fg="red")

    root.after(50, update_joystick)

update_joystick()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    if ser and ser.is_open:
        ser.close()
