from functools import partial
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import platform
import asyncio
import os

from pygubu.widgets.simpletooltip import create
from PIL import ImageTk
from PIL import Image

from pymusic import sources
from pymusic.sources.model import SourceModel
from pymusic.sources.model import SongInfo
from pymusic.ui import PlayerApp
from pymusic.lib.plist import PlayList
from pymusic.lib.logger import logger
from pymusic.lib import asynctk
from .login import LoginDialog


current_path = Path(__file__).parent


class App(PlayerApp):
    """App."""

    def __init__(self) -> None:
        root = asynctk.AsyncTk()
        super().__init__(root)
        assert self.mainwindow is root
        asynctk.add_done_before_exit(self.quit)
        self.mainwindow.after(300, self.__init_after)
        sources.set_stdout(partial(tk.messagebox.showinfo, 'info'))

    def run(self) -> None:
        logger.info('App launched successfully')
        super().run()

    def __init_after(self) -> None:
        """初始化."""

        logger.info('init attributes')
        self.__init_attr()
        logger.info('init ui')
        self.__init_ui()
        logger.info('binding callback function')
        self.__init_bind()
        logger.info('rendering icons')
        asynctk.create_task(self.__init_icon())

    def __init_attr(self) -> None:
        """init attributes."""

        self.__vlc_path = './vlc-3.0.17.4'
        self.__loop: asyncio.base_events.BaseEventLoop = asynctk._callback_loop
        self.__icons = {}
        self.__tooltips = {}
        self.__vlc = None
        self.__source_url = None
        self.__if_mute: bool = False
        self.__previous_search: str = None
        self.__previous_source: str = None
        self.__play_list = PlayList(listbox=self.play_listbox)
        self.__download_list = PlayList(listbox=self.download_listbox)
        self.__current_list: PlayList = None

    def __init_ui(self) -> None:
        """init ui."""

        self.__login_dialog = LoginDialog(self.mainwindow)

        style = tk.ttk.Style(self.mainwindow)
        for style_name in style.theme_names():
            self.style_submenu.add_command(
                label=style_name,
                command=partial(style.theme_use, style_name),
            )
        style.theme_use('xpnative')
        self.style_submenu.add('separator')

        options = list(sources.SOURCE_OPTIONS.keys())
        self.sources_combobox.configure(
            values=zip(options, sources.SOURCE_OPTIONS.values()))
        self.sources_combobox.set(options[2])

        create(self.sources_combobox, '选择歌曲来源')
        create(self.search_button, '点击进行搜索')
        self.__tooltips['volume_button'] = create(self.volume_button, '静音')
        self.__tooltips['volume_scale'] = create(
            self.volume_scale, str(self._current_volume.get()))
        create(self.previous_button, '上一曲')
        self.__tooltips['play'] = create(self.play_button, '播放')
        create(self.stop_button, '停止')
        create(self.next_button, '下一曲')
        create(self.download_button, '点击下载列表内的歌曲')
        create(self.login_button, '点击登录')

        self.search_entry.focus_set()

    def __init_bind(self) -> None:
        """ init binds """

        # 添加ttkthemes的主题样式
        def add_additional_styles():
            def try_init():
                try:
                    import ttkthemes
                except ImportError:
                    self.mainwindow.after(
                        0,
                        tk.messagebox.showinfo,
                        'info',
                        'ttkthemes is needed\nuse pip to install it',
                    )
                else:
                    self.style_submenu.delete('load more')
                    self.mainwindow.after(100, init, ttkthemes)

            def init(ttkthemes):
                style = ttkthemes.ThemedStyle(self.mainwindow)
                for style_name in ttkthemes.THEMES:
                    self.style_submenu.add_command(
                        label=style_name,
                        command=partial(style.set_theme, style_name),
                    )

            self.__loop.call_soon_threadsafe(
                self.__loop.run_in_executor,
                None,
                try_init,
            )

        def toggle_fullscreen(event) -> None:
            """全屏切换."""

            nonlocal if_fullscreen
            if_fullscreen = not if_fullscreen
            self.mainwindow.attributes('-fullscreen', if_fullscreen)

        if_fullscreen = False
        self.mainwindow.bind_all('<F11>', toggle_fullscreen)

        self.style_submenu.add_command(
            label='load more',
            command=add_additional_styles,
        )

        def forward(event) -> None:
            if self.__vlc is not None:
                pos = self.__vlc.get_time()
                self.__vlc.set_time(pos + 1000)

        def backward(event) -> None:
            if self.__vlc is not None:
                pos = self.__vlc.get_time()
                if pos > 1000:
                    self.__vlc.set_time(pos - 1000)

        self.mainwindow.bind('<Right>', forward)
        self.mainwindow.bind('<Left>', backward)

        def right_button_event(event, list_: PlayList) -> None:
            index = list_.response(event)
            if index is None:
                return
            menubar.delete(0, 'end')
            menubar.add_command(
                label='移除',
                command=partial(list_.pop, index))
            menubar.add_command(
                label='下载',
                command=lambda: asynctk.create_task(
                    list_[index].download(),
                ).add_done_callback(
                    lambda fut: list_.remove(fut.result())
                    if list_ is self.__download_list else None,
                )
            )
            menubar.post(event.x_root, event.y_root)

        def double_click_event(event, list_: PlayList) -> None:
            index = list_.response(event)
            if index is None:
                return
            for widget in [self.previous_button, self.next_button]:
                widget.configure(state='normal')
            self.__current_list = list_
            list_.set_index(index)
            self._play(list_[index])

        menubar = tk.Menu(master=self.mainwindow, tearoff=False)
        self.play_listbox.bind(
            '<Button-3>',
            partial(right_button_event, list_=self.__play_list))
        self.download_listbox.bind(
            '<Button-3>',
            partial(right_button_event, list_=self.__download_list))
        self.play_listbox.bind(
            '<Double-Button-1>',
            partial(double_click_event, list_=self.__play_list))
        self.download_listbox.bind(
            '<Double-Button-1>',
            partial(double_click_event, list_=self.__download_list))

        self.search_entry.bind('<Return>', lambda event: self._search())

    async def __init_icon(self) -> None:
        """init icons."""

        async def fit_widget(
                widget: tk.Widget, imname: str, render: bool = True) -> None:
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
            if render:
                widget.configure(image=img)

        icons_path = current_path / '../icons'
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

    def __init_vlc(self) -> asyncio.futures.Future:
        """初始化vlc播放器."""

        def check_path() -> bool:
            return not (Path(self.__vlc_path) / 'libvlc.dll').exists()

        while check_path():
            tk.messagebox.showwarning(
                title='warning',
                message='vlc not found, please choose one existed vlc path')
            self._set_vlc_path()
        os.environ['PYTHON_VLC_MODULE_PATH'] = self.__vlc_path
        import vlc
        global State
        State = vlc.State

        def init_vlc() -> asyncio.futures.Future:
            def init():
                return vlc.Instance(
                    "--audio-visual=visual",
                    "--effect-list=spectrum",
                    "--effect-fft-window=flattop").media_player_new()

            def callback():
                loop = asyncio.events.get_running_loop()
                fut = loop.run_in_executor(None, init)
                asyncio.futures._chain_future(fut, future)

            self.__loop.call_soon_threadsafe(callback)

        def init_callback(future: asyncio.futures.Future) -> None:
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
                self.__tooltips['play'].text = '暂停'

            def on_pause(event) -> None:
                self.play_button.configure(image=play_icon)
                self.__tooltips['play'].text = '播放'

            def on_stop(event) -> None:
                self.play_button.configure(image=play_icon)
                self.__tooltips['play'].text = '播放'
                self._current_pos.set(0)
                self._current_length.set('--')
                self._total_length.set('--')
                self.progress_bar.configure(state='disabled')
                if self.__vlc.get_state() == State.Ended:
                    self.__switch_song(next_=True)

            def on_time_changed(event) -> None:
                pos = self.__vlc.get_time()
                self._current_pos.set(pos)
                self._current_length.set(format_time(pos))

            def on_length_changed(event) -> None:
                length = self.__vlc.get_length()
                self._total_length.set(format_time(length))
                self.progress_bar.configure(to=str(length))

            self.__vlc = future.result()
            wm_id = self.audio_canvas.winfo_id()
            if platform.system() == 'Windows':
                self.__vlc.set_hwnd(wm_id)
            else:
                self.__vlc.set_xwindow(wm_id)
            self.__vlc.audio_set_volume(
                0 if self.__if_mute else self._current_volume.get())
            events = [
                vlc.EventType.MediaPlayerTimeChanged,
                vlc.EventType.MediaPlayerPlaying,
                vlc.EventType.MediaPlayerPaused,
                vlc.EventType.MediaPlayerStopped,
                vlc.EventType.MediaPlayerLengthChanged,
            ]
            callbacks = [
                on_time_changed,
                on_play,
                on_pause,
                on_stop,
                on_length_changed,
            ]
            manager = self.__vlc.event_manager()
            for event, callback in zip(events, callbacks):
                manager.event_attach(
                    event,
                    callback,
                )

        future = self.__loop.create_future()
        future.add_done_callback(init_callback)
        self.__log('init vlc, please wait for a minute')
        future.add_done_callback(
            lambda future: self.__log('', time=1000))
        init_vlc()
        return future

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
        menubar = tk.Menu(master=self.mainwindow, tearoff=False)

        def right_button_event(event: tk.Event, item: SongInfo) -> None:
            menubar.delete(0, 'end')
            menubar.add_command(
                label='添加至播放列表',
                command=lambda: self.__play_list.append(item)
                if item not in self.__play_list
                else tk.messagebox.showinfo('info', 'the song is already in'),
            )
            menubar.add_command(
                label='添加至下载列表',
                command=lambda: self.__download_list.append(item)
                if item not in self.__download_list
                else tk.messagebox.showinfo('info', 'the song is already in'),
            )
            menubar.add_command(
                label='下载',
                command=lambda: asynctk.create_task(item.download()),
            )
            menubar.post(event.x_root, event.y_root)

        async def show_search_result() -> None:
            """获取搜索结果并展示."""

            source = sources.get(source_name)
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
            item_button.bind(
                '<Button-3>', partial(right_button_event, item=item))
            frame.pack(side='top', expand=True, fill='both', pady=6, padx=3)
            item_button.pack(side='left', expand=True, fill='x')

        self.__previous_search = name
        self.__previous_source = source_name
        old_items = self.scrolledframe.innerframe.winfo_children()
        asynctk.create_task(show_search_result())
        # 清空之前的结果
        for item in old_items:
            item.destroy()

    async def _play_source(self, item: SongInfo) -> None:
        """播放资源.

        :param item: 歌曲信息
        :returns: None
        """

        path = item.check_download()
        if path is not None:
            self.__source_url = str(path)
        else:
            url = await item.url()
            if url is None:
                return
            self.__source_url = url
        self.__vlc.set_mrl(self.__source_url)
        self.__vlc.play()

    def _play(self, item: SongInfo) -> None:
        """播放歌曲.

        :param item: 选中的歌曲
        :returns: None
        """

        if self.__vlc is None:
            def callback(fut):
                asynctk.create_task(self._play_source(item))
                for widget in [self.stop_button, self.play_button]:
                    widget.configure(state='normal')

            self.__init_vlc().add_done_callback(callback)
        else:
            asynctk.create_task(self._play_source(item))

    def __switch_song(self, next_: bool) -> None:
        if self.__current_list is None\
                or not self.__current_list.check_index():
            return
        item: SongInfo = \
            self.__current_list.next() if next_ \
            else self.__current_list.previous()
        if item is None:
            i = 0 if next_ else -1
            item = self.__current_list[i]
            self.__current_list.set_index(i)
        asynctk.create_task(self._play_source(item))

    def _next_song(self) -> None:
        """下一曲."""

        self.__switch_song(next_=True)

    def _previous_song(self) -> None:
        """上一曲."""

        self.__switch_song(next_=False)

    def _toggle_mute(self) -> None:
        """音量按钮事件."""

        if self.__if_mute:
            self.volume_scale.configure(state='normal')
            self.volume_button.configure(image=self.__icons['sound_on'])
            self.__tooltips['volume_button'].text = '静音'
            if self.__vlc is not None:
                self.__vlc.audio_set_volume(self._current_volume.get())
        else:
            self.volume_scale.configure(state='disabled')
            self.volume_button.configure(image=self.__icons['sound_off'])
            self.__tooltips['volume_button'].text = '恢复音量'
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
        elif state == State.Stopped:
            self.__vlc.play()
        elif state == State.Ended:
            self.__vlc.set_mrl(self.__source_url)
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
        self.__tooltips['volume_scale'].text = str(volume)
        if self.__vlc is not None:
            self.__vlc.audio_set_volume(volume)

    def _set_vlc_path(self) -> None:
        """ 设置vlc路径. """

        res = filedialog.askdirectory(title='choose vlc path')
        if res:
            self.__vlc_path = res
            if self.__vlc is not None:
                self.__vlc.release()
                self.__vlc = None

    def _download(self) -> None:
        """下载."""

        async def download_start():
            tasks = []
            for item in list_:
                task = self.__loop.create_task(item.download())
                task.add_done_callback(
                    lambda fut: list_.remove(fut.result())
                    if fut.exception() is None else None
                )
                tasks.append(task)
            for task in tasks:
                await task
            self.__log('下载完成', time=1000)

        list_ = self.__download_list
        if list_.empty():
            tk.messagebox.showinfo('info', 'no song in download list')
            return
        asynctk.create_task(download_start())

    def _login(self) -> None:
        """登录."""

        dialog = self.__login_dialog
        source_name = self._current_source.get()
        source: SourceModel = sources.get(source_name)
        login_config = source.check_login()
        if not login_config.enabled:
            tk.messagebox.showinfo(
                'info',
                login_config.message,
            )
            return
        dialog.reset(login_config)
        dialog.show()
        asynctk.create_task(source.check_settings()).add_done_callback(
            lambda fut: dialog.update_login_info(fut.result())
            if fut.result() is not None else None
        )

    def __log(self, msg: str, time: int = -1) -> None:
        """打印状态栏消息.

        :param msg: 需要打印的信息
        :param time: 打印后多久消失
        :returns: None
        """

        self.status_line.configure(text=msg)
        if time > 0:
            self.mainwindow.after(
                time,
                lambda: self.status_line.configure(text=''),
            )

    async def quit(self) -> None:
        """退出App."""

        if self.__vlc is not None:
            if self.__vlc.is_playing():
                self.__vlc.stop()
            self.__vlc.release()
        self.__login_dialog.destroy()
