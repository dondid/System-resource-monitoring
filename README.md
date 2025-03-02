# System-resource-monitoring
![Image](https://github.com/user-attachments/assets/db420316-e586-4934-aedc-44ae5bd5d905)

![Image](https://github.com/user-attachments/assets/4cb519e1-2bda-4791-88af-97a31285fc7c)

This system resource monitoring application is made in Python 🐍, using the tkinter library for the graphical interface 🎨 and psutil for performance data collection 📊. The purpose of the application is to allow the user to view real-time computer resource usage, such as CPU, memory, disk, and network, while also offering alerts when certain configurable thresholds are exceeded. The application uses threads 🧵 to collect data in parallel without affecting the performance of the graphical interface.

General Operation:
Resource Monitoring:

CPU: Monitors CPU usage percentage every second 🧠.

Memory: Monitors RAM usage percentage 🧠.

Disk I/O: Measures disk read and write speeds (in MB/s), calculating differences from previous values 💾.

Network: Monitors network upload and download speeds, using total data traffic 🌐.

Using Threads: Each monitored resource is managed by a dedicated thread 🧵 that runs a while loop to periodically collect data:

monitor_cpu: Monitors CPU 🧠.

monitor_memory_disk: Monitors memory and disk I/O 💾.

monitor_network: Monitors network activity 🌐.

These threads are set as daemon threads, which allows them to run in the background and stop automatically when the application is closed 🚪.

The data collected by the threads is added to a shared queue (queue.Queue), through which it is sent to the graphical interface 📊.

Graphical Interface:

Charts Panel: Displays CPU, memory, disk I/O, and network usage in the form of line charts 📈.

Statistics Panel: Shows the current usage of each resource in real-time ⏲️.

Alerts Panel: Allows configuring alert thresholds for CPU and memory. When resources exceed the defined thresholds, warnings appear in the console ⚠️.

Updating the GUI and Synchronizing Data: The update_gui function retrieves data from the shared queue and updates the statistic labels and charts 📊.

To keep the application interactive, the graphical interface uses after to run updates recurrently without blocking the main GUI 🕒.

Purpose of the Application:
The application provides visual information and real-time statistics about system resource usage, being useful for monitoring system status 🔍. Configurable thresholds allow users to set alerts for critical values, making it an ideal tool for diagnosing problems and managing performance 🛠️.

Benefits of Using Threads:
By using threads for parallel monitoring of each resource, the application can continuously collect data without affecting the responsiveness of the graphical interface 🧵. Thus, the GUI remains fluid, and the user receives updated data in real-time 🌟.
