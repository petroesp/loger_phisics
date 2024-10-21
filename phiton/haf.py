import serial
import matplotlib.pyplot as plt
import csv
from time import strftime, localtime
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SensorDataApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Sensor Data Logger")

        # Настройки COM порта
        self.serial_port = '/dev/ttyUSB1'  # Укажите ваш COM-порт
        self.baud_rate = 115200
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)

        # Имена датчиков
        self.sensor_names = {
            '28C49A5C0000009D': 'Sensor 1',
            '28FD486000000061': 'Sensor 2',
            '281B176000000000': 'Sensor 3'
        }

        # Списки для хранения данных
        self.time_data = []
        self.sensor_data = {name: [] for name in self.sensor_names}

        # Имя CSV файла
        self.csv_filename = 'sensor_data.csv'
        self.file = open(self.csv_filename, mode='w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Timestamp'] + list(self.sensor_names.values()))

        # UI
        self.setup_ui()
        self.update_data()

    def setup_ui(self):
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.tree_frame = tk.Frame(self.master)
        self.tree_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_frame, columns=['Timestamp'] + list(self.sensor_names.values()), show='headings')
        self.tree.heading('Timestamp', text='Timestamp')
        for sensor_name in self.sensor_names.values():
            self.tree.heading(sensor_name, text=sensor_name)

        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def update_data(self):
        try:
            line = self.ser.readline().decode('utf-8').strip()
            if line:
                parts = line.split(';')
                if len(parts) < 4:  # Проверяем, достаточно ли данных
                    print(f"Ignored line due to insufficient parts: {line}")
                    return

                try:
                    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime(int(parts[0])))
                except ValueError:
                    print(f"Invalid timestamp: {parts[0]}")
                    return
                
                self.time_data.append(timestamp)

                # Обрабатываем данные для каждого датчика
                for i in range(1, len(parts)):
                    address_temp = parts[i].split(',')
                    if len(address_temp) == 2:
                        address = address_temp[0]
                        temperature = address_temp[1]

                        # Сохраняем температуру
                        if address in self.sensor_names:
                            try:
                                temp_value = float(temperature)
                                self.sensor_data[address].append(temp_value)

                                # Записываем данные в CSV
                                self.writer.writerow([timestamp] + [self.sensor_data[name][-1] for name in self.sensor_names])

                                # Добавляем данные в таблицу
                                self.tree.insert('', 'end', values=[timestamp] + [self.sensor_data[name][-1] for name in self.sensor_names])
                                self.tree.yview_moveto(1)

                            except ValueError:
                                print(f"Invalid temperature value: {temperature}")

                self.update_graph()

        except Exception as e:
            print(f"Error reading serial data: {e}")

        # Повторяем обновление данных
        self.master.after(1000, self.update_data)

    def update_graph(self):
        self.ax.clear()
        for sensor_name in self.sensor_names:
            if self.sensor_data[sensor_name]:  # Проверяем, есть ли данные
                self.ax.plot(self.time_data, self.sensor_data[sensor_name], label=self.sensor_names[sensor_name])
        
        self.ax.set_xlabel('Timestamp')
        self.ax.set_ylabel('Sensor Value')
        self.ax.set_title('Real-time Sensor Data')
        if any(self.sensor_data.values()):  # Проверяем, есть ли данные для легенды
            self.ax.legend(loc='upper left')
        self.ax.grid(True)
        self.canvas.draw()

    def close(self):
        self.file.close()
        self.ser.close()
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorDataApp(root)
    try:
        root.protocol("WM_DELETE_WINDOW", app.close)  # Закрытие файла и порта при выходе
        root.mainloop()
    except KeyboardInterrupt:
        app.close()

