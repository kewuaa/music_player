# coding=gbk
from pymusic.lib.asynctk import AsyncTk
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.combobox import Combobox
from pygubu.widgets.scrolledframe import ScrolledFrame


class PlayerApp:
    def __init__(self, master=None):
        # build ui
        self.toplevel = AsyncTk()
        self.panedwindow2 = ttk.Panedwindow(self.toplevel, orient="horizontal")
        self.notebook1 = ttk.Notebook(self.panedwindow2)
        self.frame2 = ttk.Frame(self.notebook1)
        self.play_listbox = tk.Listbox(self.frame2)
        self.play_listbox.pack(expand="true", fill="both", padx=6, pady=6, side="top")
        self.frame2.configure(height=200, width=200)
        self.frame2.pack(side="top")
        self.notebook1.add(self.frame2, text="播放列表")
        self.frame3 = ttk.Frame(self.notebook1)
        self.download_listbox = tk.Listbox(self.frame3)
        self.download_listbox.pack(
            expand="true", fill="both", padx=6, pady=6, side="top"
        )
        self.frame3.configure(height=200, width=200)
        self.frame3.pack(side="top")
        self.notebook1.add(self.frame3, text="下载列表")
        self.notebook1.configure(height=400, width=150)
        self.notebook1.pack(expand="true", fill="both", side="left")
        self.panedwindow2.add(self.notebook1, weight="1")
        self.frame10 = ttk.Frame(self.panedwindow2)
        self.frame11 = ttk.Frame(self.frame10)
        self.sources_combobox = Combobox(self.frame11)
        self._current_source = tk.StringVar(value="")
        self.sources_combobox.configure(keyvariable=self._current_source, width=6)
        self.sources_combobox.pack(side="left")
        self.search_entry = ttk.Entry(self.frame11)
        self.search_entry.configure(width=49)
        self.search_entry.pack(expand="true", fill="x", padx=9, side="left")
        self.search_button = ttk.Button(self.frame11)
        self.search_button.configure(width=3)
        self.search_button.pack(side="left")
        self.search_button.configure(command=self._search)
        self.frame11.configure(height=200)
        self.frame11.pack(pady=36, side="top")
        self.frame12 = ttk.Frame(self.frame10)
        self.scrolledframe = ScrolledFrame(self.frame12, scrolltype="both")
        self.scrolledframe.innerframe.configure(relief="groove")
        self.scrolledframe.configure(usemousewheel=True)
        self.scrolledframe.pack(expand="true", fill="both", side="top")
        self.frame12.configure(height=200, width=200)
        self.frame12.pack(expand="true", fill="both", padx=30, side="top")
        self.audio_canvas = tk.Canvas(self.frame10)
        self.audio_canvas.configure(height=60, state="disabled")
        self.audio_canvas.pack(fill="x", padx=30, pady=20, side="top")
        self.frame13 = ttk.Frame(self.frame10)
        self.frame14 = ttk.Frame(self.frame13)
        self.progress_bar = ttk.Scale(self.frame14)
        self._current_pos = tk.IntVar(value="")
        self.progress_bar.configure(
            from_=0, orient="horizontal", state="disabled", variable=self._current_pos
        )
        self.progress_bar.pack(expand="true", fill="x", padx=30, pady=9, side="left")
        self.progress_bar.configure(command=self._do_pos_changed)
        self.progress_label1 = ttk.Label(self.frame14)
        self._current_length = tk.StringVar(value="--")
        self.progress_label1.configure(text="--", textvariable=self._current_length)
        self.progress_label1.pack(side="left")
        self.label1 = ttk.Label(self.frame14)
        self.label1.configure(text="/")
        self.label1.pack(padx=6, side="left")
        self.process_label2 = ttk.Label(self.frame14)
        self._total_length = tk.StringVar(value="--")
        self.process_label2.configure(text="--", textvariable=self._total_length)
        self.process_label2.pack(side="left")
        self.frame14.configure(height=200, width=200)
        self.frame14.pack(expand="true", fill="x", side="top")
        self.frame15 = ttk.Frame(self.frame13)
        self.volume_button = ttk.Button(self.frame15)
        self.volume_button.configure(width=3)
        self.volume_button.pack(padx=9, side="left")
        self.volume_button.configure(command=self._toggle_mute)
        self.volume_scale = ttk.Scale(self.frame15)
        self._current_volume = tk.IntVar(value="33")
        self.volume_scale.configure(from_=0, orient="horizontal", to=100, value=33)
        self.volume_scale.configure(variable=self._current_volume)
        self.volume_scale.pack(padx=9, side="left")
        self.volume_scale.configure(command=self._do_volume_changed)
        self.previous_button = ttk.Button(self.frame15)
        self.previous_button.configure(state="disabled", width=3)
        self.previous_button.pack(padx=8, side="left")
        self.previous_button.configure(command=self._previous_song)
        self.play_button = ttk.Button(self.frame15)
        self.play_button.configure(state="disabled", width=3)
        self.play_button.pack(padx=8, side="left")
        self.play_button.configure(command=self._toggle_play)
        self.stop_button = ttk.Button(self.frame15)
        self.stop_button.configure(state="disabled", width=3)
        self.stop_button.pack(padx=8, side="left")
        self.stop_button.configure(command=self._stop)
        self.login_button = ttk.Button(self.frame15)
        self.login_button.configure(width=3)
        self.login_button.pack(padx=9, side="right")
        self.login_button.configure(command=self._login)
        self.download_button = ttk.Button(self.frame15)
        self.download_button.configure(width=3)
        self.download_button.pack(padx=9, side="right")
        self.download_button.configure(command=self._download)
        self.next_button = ttk.Button(self.frame15)
        self.next_button.configure(state="disabled", width=3)
        self.next_button.pack(padx=8, side="left")
        self.next_button.configure(command=self._next)
        self.frame15.configure(height=200, width=800)
        self.frame15.pack(expand="true", fill="x", side="top")
        self.frame13.configure(height=200, relief="groove", width=200)
        self.frame13.pack(fill="x", padx=30, pady=9, side="top")
        self.frame10.configure(height=200, relief="groove", width=800)
        self.frame10.pack(expand="true", fill="both", padx=9, pady=9, side="top")
        self.panedwindow2.add(self.frame10, weight="9")
        self.panedwindow2.configure(height=600, width=800)
        self.panedwindow2.pack(expand="true", fill="both", side="top")
        self.menu1 = tk.Menu(self.toplevel)
        self.submenu1 = tk.Menu(self.menu1, tearoff="false")
        self.menu1.add(tk.CASCADE, menu=self.submenu1, label="设置")
        self.mi_command1 = 0
        self.submenu1.add("command", label="导出")
        self.toplevel.configure(menu=self.menu1)
        self.toplevel.configure(height=200, width=200)
        self.toplevel.title("^3^")

        # Main widget
        self.mainwindow = self.toplevel

    def run(self):
        self.mainwindow.mainloop()

    def _search(self):
        pass

    def _do_pos_changed(self, scale_value):
        pass

    def _toggle_mute(self):
        pass

    def _do_volume_changed(self, scale_value):
        pass

    def _previous_song(self):
        pass

    def _toggle_play(self):
        pass

    def _stop(self):
        pass

    def _login(self):
        pass

    def _download(self):
        pass

    def _next(self):
        pass


if __name__ == "__main__":
    app = PlayerApp()
    app.run()
