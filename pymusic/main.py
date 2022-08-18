from functools import partial
from pathlib import Path
import tkinter as tk
import importlib
import platform
import asyncio
import os

from pygubu.widgets.simpletooltip import create
from PIL import ImageTk
from PIL import Image

from pymusic.sources.model import SourceModel
from pymusic.sources.model import SongInfo
from pymusic.ui.playerapp import PlayerApp
from pymusic.lib import asynctk


current_path = Path(__file__).parent
os.environ['PYTHON_VLC_MODULE_PATH'] = './vlc-3.0.17.4'


class App(PlayerApp):
    """App."""

    SOURCE_OPTIONS = {
        '酷狗': 'kg',
        '酷我': 'kw',
        '咪咕': 'mg',
        'QQ': 'qq',
        '千千静听': 'qqjt',
        '网易云': 'wyy',
    }

    def __init__(self) -> None:
        super().__init__()
        asynctk.add_done_before_exit(self.quit)
        self.mainwindow.after(300, self.__init_after)

    def __init_after(self) -> None:
        """初始化."""

        self.__init_attr()
        self.__init_ui()
        asynctk.create_task(self.__init_icon())

    def __init_attr(self) -> None:
        """init attributes."""

        self.__loop: asyncio.base_events.BaseEventLoop = asynctk._callback_loop
        self.__source_dict = {}
        self.__icons = {}
        self.__tooltips = {}
        self.__vlc = None
        self.__if_mute: bool = False
        self.__previous_search: str = None
        self.__previous_source: str = None

    def __init_vlc(self) -> None:
        """初始化vlc播放器."""

        play_icon = self.__icons['play']
        pause_icon = self.__icons['pause']

        def format_time(time: int) -> str:
            seconds = time / 1000
            minutes = int(seconds // 60)
            seconds -= minutes * 60
            return f'{minutes:02d}:{int(seconds):02d}'

        def on_play(event) -> None:
            self.play_button.configure(image=pause_icon)
            self.progress_bar.configure(state='normal')

        def on_pause(event) -> None:
            self.play_button.configure(image=play_icon)

        def on_stop(event) -> None:
            self.play_button.configure(image=play_icon)
            self._current_pos.set(0)
            self._current_length.set('--')
            self._total_length.set('--')
            self.progress_bar.configure(state='disabled')

        def on_time_changed(event) -> None:
            pos = self.__vlc.get_time()
            self._current_pos.set(pos)
            self._current_length.set(format_time(pos))

        def on_length_changed(event) -> None:
            length = self.__vlc.get_length()
            self._total_length.set(format_time(length))
            self.progress_bar.configure(to=str(length))

        import vlc
        global State
        State = vlc.State
        self.__vlc = vlc.Instance(
            "--audio-visual=visual",
            "--effect-list=spectrum",
            "--effect-fft-window=flattop").media_player_new()
        wm_id = self.audio_canvas.winfo_id()
        if platform.system() == 'Windows':
            self.__vlc.set_hwnd(wm_id)
        else:
            self.__vlc.set_xwindow(wm_id)
        self.__vlc.audio_set_volume(
            0 if self.__if_mute else self._current_volume.get())
        manager = self.__vlc.event_manager()
        manager.event_attach(
            vlc.EventType.MediaPlayerTimeChanged, on_time_changed)
        manager.event_attach(vlc.EventType.MediaPlayerPlaying, on_play)
        manager.event_attach(vlc.EventType.MediaPlayerPaused, on_pause)
        manager.event_attach(vlc.EventType.MediaPlayerStopped, on_stop)
        manager.event_attach(
            vlc.EventType.MediaPlayerLengthChanged, on_length_changed)

    def __init_ui(self) -> None:
        """init ui."""

        options = list(self.SOURCE_OPTIONS.values())
        self.sources_combobox.configure(
            values=zip(options, self.SOURCE_OPTIONS.keys()))
        self.sources_combobox.set(options[0])

        create(self.sources_combobox, '选择歌曲来源')
        create(self.search_button, '点击进行搜索')
        self.__tooltips['volume'] = create(
            self.volume_scale, str(self._current_volume.get()))
        create(self.previous_button, '上一曲')
        self.__tooltips['play'] = create(self.play_button, '播放')
        create(self.stop_button, '停止')
        create(self.next_button, '下一曲')
        create(self.download_button, '点击下载列表内的歌曲')
        create(self.login_button, '点击登录')

    async def __init_icon(self) -> None:
        """init icons."""

        async def fit_widget(
                widget: tk.Widget, imname: str, config: bool = True) -> None:
            """设置图片.

            :param widget: 控件
            :param impath: 图片路径
            :returns: None
            """

            impath = icons_path / imname
            size = int(widget.winfo_width() / 1.5), \
                int(widget.winfo_height() / 1.5)
            origin_img = await self.__loop.run_in_executor(
                None, partial(Image.open, impath))
            resize_img = origin_img.resize(size, Image.ANTIALIAS)
            img = ImageTk.PhotoImage(resize_img)
            self.__icons[impath.stem] = img
            if config:
                widget.configure(image=img)

        icons_path = current_path / './icons'
        await fit_widget(self.search_button, 'search.png')
        await fit_widget(self.volume_button, 'sound_on.png')
        await fit_widget(self.previous_button, 'previous.png')
        await fit_widget(self.play_button, 'play.png')
        await fit_widget(self.stop_button, 'stop.png')
        await fit_widget(self.next_button, 'next.png')
        await fit_widget(self.download_button, 'download.png')
        await fit_widget(self.login_button, 'login.png')
        await fit_widget(self.play_button, 'pause.png', False)
        await fit_widget(self.volume_button, 'sound_off.png', False)

    def _search(self) -> None:
        """搜索."""

        name = self.search_entry.get().strip()
        source_name = self._current_source.get()
        self.search_entry.delete(0, 'end')
        if not name:
            return
        if name == self.__previous_search and \
                source_name == self.__previous_source:
            return

        async def show_search_result() -> None:
            """获取搜索结果并展示."""

            if self.__source_dict.get(source_name) is None:
                source: SourceModel = importlib.import_module(
                    'pymusic.sources.' + source_name).Source(self.__loop)
                asynctk.add_done_before_exit(source.exit)
                self.__source_dict[source_name] = source
            else:
                source: SourceModel = self.__source_dict[source_name]
            result = await source._get_info(name)
            for item in result:
                add_result_to_frame(item)
                await asyncio.sleep(0)

        def add_result_to_frame(item: SongInfo) -> None:
            """将搜索结果显示至frame中."""

            frame = tk.ttk.Frame(
                master=self.scrolledframe.innerframe)
            item_button = tk.ttk.Button(
                master=frame, text=item.summary, style='Toolbutton',
                command=lambda: self._play(item))
            frame.pack(side='top', expand=True, fill='both', pady=6, padx=3)
            item_button.pack(side='left', expand=True, fill='x')

        self.__previous_search = name
        self.__previous_source = source_name
        old_items = self.scrolledframe.innerframe.winfo_children()
        asynctk.create_task(show_search_result())
        # 清空之前的结果
        for item in old_items:
            item.destroy()

    def _play(self, item: SongInfo) -> None:
        """播放歌曲.

        :param item: 选中的歌曲
        :returns: None
        """

        if self.__vlc is None:
            self.__init_vlc()
            for widget in [self.previous_button,
                           self.play_button,
                           self.stop_button,
                           self.next_button]:
                widget.configure(state='normal')

        async def play() -> None:
            source: SourceModel = self.__source_dict[item.from_]
            url = await source._get_source(item.id_)
            self.__vlc.set_mrl(url)
            self.__vlc.play()

        asynctk.create_task(play())

    def _toggle_mute(self) -> None:
        """音量按钮事件."""

        if self.__if_mute:
            self.volume_scale.configure(state='normal')
            self.volume_button.configure(image=self.__icons['sound_on'])
            if self.__vlc is not None:
                self.__vlc.audio_set_volume(self._current_volume.get())
        else:
            self.volume_scale.configure(state='disabled')
            self.volume_button.configure(image=self.__icons['sound_off'])
            if self.__vlc is not None:
                self.__vlc.audio_set_volume(0)
        self.__if_mute = not self.__if_mute

    def _toggle_play(self) -> None:
        """播放按钮事件"""

        state = self.__vlc.get_state()
        if state == State.Playing:
            self.__vlc.pause()
        elif state == State.Paused:
            self.__vlc.set_pause(0)
        else:
            self.__vlc.play()

    def _stop(self) -> None:
        """停止播放."""

        self.__vlc.stop()

    def _do_pos_changed(self, scale_value: str) -> None:
        """进度改变事件."""

        if self.__vlc is not None:
            self.__vlc.set_time(int(scale_value.split('.', 1)[0]))

    def _do_volume_changed(self, scale_value: str) -> None:
        """音量改变事件."""

        volume = self._current_volume.get()
        self.__tooltips['volume'].text = str(volume)
        if self.__vlc is not None:
            self.__vlc.audio_set_volume(volume)

    async def quit(self) -> None:
        """退出App."""

        if self.__vlc is not None:
            self.__vlc.release()
