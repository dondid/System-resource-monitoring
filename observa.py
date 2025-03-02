import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque

# Definirea clasei pentru monitorizarea sistemului
class SystemMonitor:
    def __init__(self):
        # Coada pentru a gestiona datele monitorizate
        self.data_queue = queue.Queue()
        self.is_running = True  # Flag pentru a controla execuția monitorizării
        self.history_length = 60  # Păstrăm datele pentru ultimele 60 de secunde

        # Inițializare istorice pentru grafice
        self.cpu_history = deque(maxlen=self.history_length)
        self.memory_history = deque(maxlen=self.history_length)
        self.disk_io_history = deque(maxlen=self.history_length)
        self.network_history = deque(maxlen=self.history_length)

        # Timpul inițial pentru măsurători
        self.last_disk_io = psutil.disk_io_counters()
        self.last_network_io = psutil.net_io_counters()
        self.last_time = time.time()

    # Funcția pentru monitorizarea utilizării CPU
    def monitor_cpu(self):
        while self.is_running:
            cpu_percent = psutil.cpu_percent(interval=1)  # Calculare procentaj utilizare CPU
            print(f"Monitor CPU: {cpu_percent}%")  # Afișare în consolă pentru testare
            self.cpu_history.append(cpu_percent)  # Salvare istoric utilizare CPU
            self.data_queue.put(('cpu', cpu_percent))  # Trimitere date către coadă
            time.sleep(1)

    # Funcția pentru monitorizarea memoriei și I/O pe disc
    def monitor_memory_disk(self):
        while self.is_running:
            memory = psutil.virtual_memory()  # Obținerea datelor despre memorie
            memory_percent = memory.percent
            print(f"Monitor Memorie: {memory_percent}%")
            self.memory_history.append(memory_percent)
            self.data_queue.put(('memory', memory_percent))

            # Calculul vitezei de citire și scriere pe disc
            current_disk_io = psutil.disk_io_counters()
            current_time = time.time()
            time_delta = current_time - self.last_time  # Calculul intervalului de timp

            # Calculul vitezei de citire și scriere pe disc în MB/s
            read_speed = (current_disk_io.read_bytes - self.last_disk_io.read_bytes) / (1024 * 1024 * time_delta)
            write_speed = (current_disk_io.write_bytes - self.last_disk_io.write_bytes) / (1024 * 1024 * time_delta)

            self.disk_io_history.append((read_speed, write_speed))
            print(f"Monitor Disk I/O: Read {read_speed} MB/s, Write {write_speed} MB/s")
            self.data_queue.put(('disk', (read_speed, write_speed)))

            # Actualizarea valorilor anterioare
            self.last_disk_io = current_disk_io
            self.last_time = current_time
            time.sleep(1)

    # Funcția pentru monitorizarea traficului de rețea
    def monitor_network(self):
        while self.is_running:
            current_network = psutil.net_io_counters()
            current_time = time.time()
            time_delta = current_time - self.last_time

            # Calculul vitezei de upload și download în MB/s
            upload_speed = (current_network.bytes_sent - self.last_network_io.bytes_sent) / (1024 * 1024 * time_delta)
            download_speed = (current_network.bytes_recv - self.last_network_io.bytes_recv) / (1024 * 1024 * time_delta)

            self.network_history.append((upload_speed, download_speed))
            print(f"Monitor Network: Upload {upload_speed} MB/s, Download {download_speed} MB/s")
            self.data_queue.put(('network', (upload_speed, download_speed)))

            # Actualizarea valorilor anterioare
            self.last_network_io = current_network
            self.last_time = current_time
            time.sleep(1)

    # Funcție pentru oprirea monitorizării
    def stop_monitoring(self):
        self.is_running = False

# Definirea clasei pentru interfața grafică
class SystemMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Resurse Sistem")
        self.root.geometry("1200x800")

        # Praguri de alertă pentru diferite resurse
        self.alert_thresholds = {
            'cpu': 80,
            'memory': 90,
            'disk': 50,
            'network': 20
        }

        self.system_monitor = SystemMonitor()  # Inițializare instanță de monitorizare
        self.setup_gui()
        self.start_monitoring()

    # Configurarea interfeței grafice (GUI)
    def setup_gui(self):
        canvas = tk.Canvas(self.root)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        self.main_frame = ttk.Frame(canvas)
        self.main_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.setup_graphs(self.main_frame)  # Configurare secțiune pentru grafice
        self.setup_stats_panel(self.main_frame)  # Configurare secțiune pentru statistici
        self.setup_alerts_panel(self.main_frame)  # Configurare secțiune pentru alerte

    # Configurarea graficelor pentru resurse
    def setup_graphs(self, parent):
        graphs_frame = ttk.LabelFrame(parent, text="Grafice", padding="5")
        graphs_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.fig = Figure(figsize=(12, 8), dpi=100)  # Crearea unei figuri pentru grafice
        self.cpu_plot = self.fig.add_subplot(221)
        self.memory_plot = self.fig.add_subplot(222)
        self.disk_plot = self.fig.add_subplot(223)
        self.network_plot = self.fig.add_subplot(224)

        self.fig.tight_layout(pad=3.0)  # Ajustare margini între grafice
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Configurarea panoului de statistici în timp real
    def setup_stats_panel(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="Statistici în timp real", padding="5")
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Etichete pentru afișarea utilizării CPU, memoriei, I/O pe disc și traficului de rețea
        self.cpu_label = ttk.Label(stats_frame, text="CPU: 0%")
        self.cpu_label.grid(row=0, column=0, padx=5, pady=2)

        self.memory_label = ttk.Label(stats_frame, text="Memorie: 0%")
        self.memory_label.grid(row=1, column=0, padx=5, pady=2)

        self.disk_label = ttk.Label(stats_frame, text="Disk I/O: 0 MB/s")
        self.disk_label.grid(row=2, column=0, padx=5, pady=2)

        self.network_label = ttk.Label(stats_frame, text="Rețea: 0 MB/s")
        self.network_label.grid(row=3, column=0, padx=5, pady=2)

    # Configurarea panoului pentru setarea alertelor
    def setup_alerts_panel(self, parent):
        alerts_frame = ttk.LabelFrame(parent, text="Configurare Alerte", padding="5")
        alerts_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Setarea pragurilor pentru CPU și memorie
        ttk.Label(alerts_frame, text="CPU Threshold (%):").grid(row=0, column=0, padx=5, pady=2)
        self.cpu_threshold = ttk.Spinbox(alerts_frame, from_=0, to=100, width=5)
        self.cpu_threshold.set(self.alert_thresholds['cpu'])
        self.cpu_threshold.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(alerts_frame, text="Memory Threshold (%):").grid(row=1, column=0, padx=5, pady=2)
        self.memory_threshold = ttk.Spinbox(alerts_frame, from_=0, to=100, width=5)
        self.memory_threshold.set(self.alert_thresholds['memory'])
        self.memory_threshold.grid(row=1, column=1, padx=5, pady=2)

    # Pornirea monitorizării într-un thread separat
    def start_monitoring(self):
        self.cpu_thread = threading.Thread(target=self.system_monitor.monitor_cpu, daemon=True)
        self.memory_disk_thread = threading.Thread(target=self.system_monitor.monitor_memory_disk, daemon=True)
        self.network_thread = threading.Thread(target=self.system_monitor.monitor_network, daemon=True)

        self.cpu_thread.start()
        self.memory_disk_thread.start()
        self.network_thread.start()

        self.update_gui()

    # Actualizarea interfeței GUI în mod recurent
    def update_gui(self):
        try:
            while True:
                try:
                    data_type, value = self.system_monitor.data_queue.get_nowait()
                    self.update_stats(data_type, value)
                    self.check_alerts(data_type, value)
                except queue.Empty:
                    break

            self.update_plots()
            self.root.after(1000, self.update_gui)
        except Exception as e:
            print(f"Eroare la actualizarea GUI: {e}")

    # Actualizarea etichetelor pentru statistici în funcție de tipul de date
    def update_stats(self, data_type, value):
        if data_type == 'cpu':
            self.cpu_label.config(text=f"CPU: {value:.1f}%")
        elif data_type == 'memory':
            self.memory_label.config(text=f"Memorie: {value:.1f}%")
        elif data_type == 'disk':
            read_speed, write_speed = value
            self.disk_label.config(text=f"Disk I/O: R: {read_speed:.1f} MB/s, W: {write_speed:.1f} MB/s")
        elif data_type == 'network':
            upload_speed, download_speed = value
            self.network_label.config(text=f"Rețea: ↑{upload_speed:.1f} MB/s, ↓{download_speed:.1f} MB/s")

    # Actualizarea graficelor cu date noi
    def update_plots(self):
        self.cpu_plot.clear()
        self.cpu_plot.plot(self.system_monitor.cpu_history, label='CPU %')
        self.cpu_plot.set_title('CPU Utilizare')

        self.memory_plot.clear()
        self.memory_plot.plot(self.system_monitor.memory_history, label='Memorie %')
        self.memory_plot.set_title('Memorie Utilizare')

        self.disk_plot.clear()
        read_speeds = [x[0] for x in self.system_monitor.disk_io_history]
        write_speeds = [x[1] for x in self.system_monitor.disk_io_history]
        self.disk_plot.plot(read_speeds, label='Citire (MB/s)')
        self.disk_plot.plot(write_speeds, label='Scriere (MB/s)')
        self.disk_plot.set_title('Disk I/O')

        self.network_plot.clear()
        upload_speeds = [x[0] for x in self.system_monitor.network_history]
        download_speeds = [x[1] for x in self.system_monitor.network_history]
        self.network_plot.plot(upload_speeds, label='Upload (MB/s)')
        self.network_plot.plot(download_speeds, label='Download (MB/s)')
        self.network_plot.set_title('Rețea I/O')

        self.canvas.draw()

    # Verificarea alertelor pe baza pragurilor definite
    def check_alerts(self, data_type, value):
        if data_type == 'cpu' and value > float(self.cpu_threshold.get()):
            print("Avertizare: CPU peste prag!")
        elif data_type == 'memory' and value > float(self.memory_threshold.get()):
            print("Avertizare: Memorie peste prag!")

# Funcția principală pentru inițierea interfeței grafice
def main():
    root = tk.Tk()
    app = SystemMonitorGUI(root)
    root.mainloop()

# Verificarea dacă scriptul este rulat direct
if __name__ == "__main__":
    main()