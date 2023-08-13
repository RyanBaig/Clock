import tkinter as tk
from tkinter import ttk
import datetime
import platform
import threading
import winsound
import os
import requests
from dateutil import parser

class ModernClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Clock")
        self.root.geometry('800x600')

        self.tabs_control = ttk.Notebook(self.root)
        self.clock_tab = ttk.Frame(self.tabs_control)
        self.alarm_tab = ttk.Frame(self.tabs_control)
        self.stopwatch_tab = ttk.Frame(self.tabs_control)
        self.timer_tab = ttk.Frame(self.tabs_control)
        self.tabs_control.add(self.clock_tab, text="Clock")
        self.tabs_control.add(self.alarm_tab, text="Alarm")
        self.tabs_control.add(self.stopwatch_tab, text='Stopwatch')
        self.tabs_control.add(self.timer_tab, text='Timer')
        self.tabs_control.pack(expand=1, fill="both")

        self.time_label = ttk.Label(self.clock_tab, font='Helvetica 40 bold')
        self.time_label.pack(anchor='center')
        self.date_label = ttk.Label(self.clock_tab, font='Helvetica 20 bold')
        self.date_label.pack(anchor='s')

        self.alarm_time_entry = ttk.Entry(self.alarm_tab, font='Helvetica 15 bold')
        self.alarm_time_entry.pack(anchor='center')
        self.alarm_instructions_label = ttk.Label(self.alarm_tab, font='Helvetica 10 bold',
                                                  text="Enter Alarm Time. Eg -> 01:30 PM")
        self.alarm_instructions_label.pack(anchor='s')
        self.set_alarm_button = ttk.Button(self.alarm_tab, text="Set Alarm", command=self.set_alarm)
        self.set_alarm_button.pack(anchor='s')
        self.alarm_status_label = ttk.Label(self.alarm_tab, font='Helvetica 15 bold')
        self.alarm_status_label.pack(anchor='s')

        self.stopwatch_label = ttk.Label(self.stopwatch_tab, font='Helvetica 40 bold', text='Stopwatch')
        self.stopwatch_label.pack(anchor='center')
        self.stopwatch_start = ttk.Button(self.stopwatch_tab, text='Start', command=self.start_stopwatch)
        self.stopwatch_start.pack(anchor='center')
        self.stopwatch_stop = ttk.Button(self.stopwatch_tab, text='Stop', state='disabled', command=self.stop_stopwatch)
        self.stopwatch_stop.pack(anchor='center')
        self.stopwatch_reset = ttk.Button(self.stopwatch_tab, text='Reset', state='disabled', command=self.reset_stopwatch)
        self.stopwatch_reset.pack(anchor='center')
        self.stopwatch_running = False
        self.stopwatch_counter_num = 0

        self.timer_time_entry = ttk.Entry(self.timer_tab, font='Helvetica 15 bold')
        self.timer_time_entry.pack(anchor='center')
        self.timer_instructions_label = ttk.Label(self.timer_tab, font='Helvetica 10 bold',
                                                  text="Enter Timer Time. Eg -> 01:30:30")
        self.timer_instructions_label.pack(anchor='s')
        self.timer_label = ttk.Label(self.timer_tab, font='Helvetica 40 bold', text='Timer')
        self.timer_label.pack(anchor='center')
        self.timer_start = ttk.Button(self.timer_tab, text='Start', command=self.start_timer)
        self.timer_start.pack(anchor='center')
        self.timer_stop = ttk.Button(self.timer_tab, text='Stop', state='disabled', command=self.stop_timer)
        self.timer_stop.pack(anchor='center')
        self.timer_reset = ttk.Button(self.timer_tab, text='Reset', state='disabled', command=self.reset_timer)
        self.timer_reset.pack(anchor='center')
        self.timer_running = False
        self.timer_counter_num = 0

        self.clock_update_thread = threading.Thread(target=self.update_clock, daemon=True)
        self.clock_update_thread.start()

    def update_clock(self):
        while True:
            try:
                response = requests.get("http://worldclockapi.com/api/json/utc/now")
                data = response.json()
                current_utc_time = data["currentDateTime"]

                utc_time = parser.parse(current_utc_time)
                gmt5_time = utc_time + datetime.timedelta(hours=5)
                gmt5_time_str = gmt5_time.strftime("""
%d %B, %Y
%I:%M:%S %p
""")

                self.time_label.config(text=gmt5_time_str)
            except Exception as e:
                print("Error fetching time:", e)

            self.root.update()
            self.root.after(1000)

    def set_alarm(self):
        alarm_time = self.alarm_time_entry.get()
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        if alarm_time == current_time:
            self.alarm_status_label.config(text='Time Is Up')
            self.play_alarm_sound()

    def play_alarm_sound(self):
        if platform.system() == 'Windows':
            winsound.Beep(5000, 1000)
        elif platform.system() == 'Darwin':
            os.system('say Time is Up')
        elif platform.system() == 'Linux':
            os.system('beep -f 5000')

    def start_stopwatch(self):
        self.stopwatch_running = True
        self.stopwatch_start.config(state='disabled')
        self.stopwatch_stop.config(state='enabled')
        self.stopwatch_reset.config(state='enabled')
        self.update_stopwatch()

    def stop_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_start.config(state='enabled')
        self.stopwatch_stop.config(state='disabled')

    def reset_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_counter_num = 0
        self.stopwatch_label.config(text='Stopwatch')
        self.stopwatch_start.config(state='enabled')
        self.stopwatch_stop.config(state='disabled')
        self.stopwatch_reset.config(state='disabled')

    def update_stopwatch(self):
        if self.stopwatch_running:
            self.stopwatch_counter_num += 1
            time_str = str(datetime.timedelta(seconds=self.stopwatch_counter_num))
            self.stopwatch_label.config(text=time_str)
            self.root.after(1000, self.update_stopwatch)

    def start_timer(self):
        self.timer_running = True
        self.timer_start.config(state='disabled')
        self.timer_stop.config(state='enabled')
        self.timer_reset.config(state='enabled')
        timer_time_str = self.timer_time_entry.get()
        hours, minutes, seconds = map(int, timer_time_str.split(':'))
        self.timer_counter_num = hours * 3600 + minutes * 60 + seconds
        self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        self.timer_start.config(state='enabled')
        self.timer_stop.config(state='disabled')

    def reset_timer(self):
        self.timer_running = False
        self.timer_counter_num = 0
        self.timer_label.config(text='Timer')
        self.timer_start.config(state='enabled')
        self.timer_stop.config(state='disabled')
        self.timer_reset.config(state='disabled')
        self.timer_time_entry.config(state='enabled')

    def update_timer(self):
        if self.timer_running and self.timer_counter_num > 0:
            self.timer_counter_num -= 1
            time_str = str(datetime.timedelta(seconds=self.timer_counter_num))
            self.timer_label.config(text=time_str)
            self.root.after(1000, self.update_timer)

def main():
    root = tk.Tk()
    app = ModernClockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
