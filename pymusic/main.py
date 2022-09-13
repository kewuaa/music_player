from functools import partial
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import importlib
import platform
import asyncio
import logging
import os

from pygubu.widgets.simpletooltip import create
from aiohttp import request
from PIL import ImageTk
from PIL import Image

from pymusic.sources.model import SourceModel
from pymusic.sources.model import SongInfo
from pymusic.ui.playerapp import PlayerApp
from pymusic.lib.plist import PlayList
from pymusic.lib import asynctk
from pymusic.lib import aiofile


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
current_path = Path(__file__).parent
data_path = Path(os.environ['Appdata']) / '^3^' / 'data'
if not data_path.exists():
    data_path.mkdir(parents=True)


async def download(url: str, name: str) -> None:
    """下载.

    :param url: 资源链接
    :param name: 资源名称
    :returns: None
    """

    path = data_path / name
    if path.exists():
        logger.info(f'{name} already exists')
        return
    async with request('GET', url) as res:
        async with aiofile.async_open(path, 'wb') as f:
            await f.write(await res.read())


class App(PlayerApp):
    """App."""

    SOURCE_OPTIONS = {
        'kg': '酷狗',
        'kw': '酷我',
        'mg': '咪咕',
        'qq': 'QQ',
        'qqjt': '千千静听',
        'wyy': '网易云',
    }

    def __init__(self) -> None:
        super().__init__()
        asynctk.add_done_before_exit(self.quit)
        self.mainwindow.after(300, self.__init_after)

    def __init_after(self) -> None:
        """初始化."""

        self.__init_attr()
        self.__init_ui()
        self.__init_bind()
        asynctk.create_task(self.__init_icon())

    def __init_attr(self) -> None:
        """init attributes."""

        self.__vlc_path = './vlc-3.0.17.4'
        self.__loop: asyncio.base_events.BaseEventLoop = asynctk._callback_loop
        self.__source_dict = {}
        self.__icons = {}
        self.__tooltips = {}
        self.__vlc = None
        self.__source_url = None
        self.__if_mute: bool = False
        self.__previous_search: str = None
        self.__previous_source: str = None
        self.__lists = {
            'play': PlayList(listvar=self._play_list),
            'download': PlayList(listvar=self._download_list),
        }
        self.__current_list: PlayList = None

    def __init_ui(self) -> None:
        """init ui."""

        def toggle_fullscreen(event) -> None:
            """全屏切换."""

            nonlocal if_fullscreen
            if_fullscreen = not if_fullscreen
            self.mainwindow.attributes('-fullscreen', if_fullscreen)

        if_fullscreen = False
        self.mainwindow.bind('<F11>', toggle_fullscreen)

        def right_button_event(event, type_: str) -> None:
            listbox: tk.Listbox = self.__getattribute__(f'{type_}_listbox')
            if listbox.size() == 0:
                return
            index = listbox.nearest(event.y)
            if index >= 0:
                listbox.activate(index)
                listbox.selection_clear(0, 'end')
                listbox.selection_set(index)
            menubar.delete(0, 'end')
            menubar.add_command(
                label='移除',
                command=partial(self._remove_from_list, index, type_))
            menubar.add_command(
                label='下载',
                command=lambda: asynctk.create_task(
                    self.__download_one(self.__lists[type_][index]),
                ).add_done_callback(
                    lambda fut: self.__lists[type_].remove(
                        fut.result(),
                    ) if type_ == 'download' else None,
                ))
            menubar.post(event.x_root, event.y_root)

        def double_click_event(event, type_: str) -> None:
            listbox: tk.Listbox = self.__getattribute__(f'{type_}_listbox')
            if listbox.size() == 0:
                return
            for widget in [self.previous_button, self.next_button]:
                widget.configure(state='normal')
            index = listbox.nearest(event.y)
            self.__current_list = list_ = self.__lists[type_]
            list_.set_index(index)
            self._play(list_[index])

        menubar = tk.Menu(master=self.mainwindow, tearoff=False)
        self.play_listbox.bind(
            '<Button-3>',
            partial(right_button_event, type_='play'))
        self.download_listbox.bind(
            '<Button-3>',
            partial(right_button_event, type_='download'))
        self.play_listbox.bind(
            '<Double-Button-1>',
            partial(double_click_event, type_='play'))
        self.download_listbox.bind(
            '<Double-Button-1>',
            partial(double_click_event, type_='download'))

        options = list(self.SOURCE_OPTIONS.keys())
        self.sources_combobox.configure(
            values=zip(options, self.SOURCE_OPTIONS.values()))
        self.sources_combobox.set(options[0])

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
        self.search_entry.bind('<Return>', lambda event: self._search())

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
            manager = self.__vlc.event_manager()
            manager.event_attach(
                vlc.EventType.MediaPlayerTimeChanged,
                on_time_changed,
            )
            manager.event_attach(
                vlc.EventType.MediaPlayerPlaying,
                on_play,
            )
            manager.event_attach(
                vlc.EventType.MediaPlayerPaused,
                on_pause,
            )
            manager.event_attach(
                vlc.EventType.MediaPlayerStopped,
                on_stop,
            )
            manager.event_attach(
                vlc.EventType.MediaPlayerLengthChanged,
                on_length_changed,
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

        def right_button_event(event, item: SongInfo) -> None:
            menubar.delete(0, 'end')
            menubar.add_command(
                label='添加至播放列表',
                command=lambda: self._add_to_list(item, 'play'))
            menubar.add_command(
                label='添加至下载列表',
                command=lambda: self._add_to_list(item, 'download'))
            menubar.add_command(
                label='下载',
                command=lambda: asynctk.create_task(self.__download_one(item)))
            menubar.post(event.x_root, event.y_root)

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

        path = data_path / '.'.join([
            item.summary.replace(' -> ', '-'),
            item.type_,
        ])
        if path.exists():
            self.__source_url = str(path)
        else:
            source: SourceModel = self.__source_dict[item.from_]
            self.__source_url = await source._get_source(item.id_)
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
        index = self.__current_list.get_index()
        if self.__current_list is self.__lists['play']:
            self.play_listbox.activate(index)
            self.play_listbox.selection_clear(0, 'end')
            self.play_listbox.selection_set(index)
        else:
            self.download_listbox.activate(index)
            self.download_listbox.selection_clear(0, 'end')
            self.download_listbox.selection_set(index)
        asynctk.create_task(self._play_source(item))

    def _next_song(self) -> None:
        """下一曲."""

        self.__switch_song(next_=True)

    def _previous_song(self) -> None:
        """上一曲."""

        self.__switch_song(next_=False)

    def _add_to_list(self, item: SongInfo, type_: str) -> None:
        """向列表中添加条目.

        :param item: 需要添加的条目
        :param type_: 列表类型
        :returns: None
        """

        list_ = self.__lists[type_]
        if item in list_:
            tk.messagebox.showinfo('info', 'the song is already in')
            return
        list_.append(item)

    def _remove_from_list(self, index: int, type_: str) -> None:
        """从列表中移除.

        :param index: 需要移除项目的索引
        :param type_: 列表类型
        :returns: None
        """

        list_ = self.__lists[type_]
        list_.pop(index)

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

    async def __download_one(self, item: SongInfo) -> SongInfo:
        """下载单曲."""

        source: SourceModel = self.__source_dict[item.from_]
        url = await source._get_source(item.id_)
        name = '.'.join([item.summary.replace(' -> ', '-'), item.type_])
        await download(url, name)
        return item

    def _download(self) -> None:
        """下载."""

        async def download_start():
            tasks = []
            for item in list_:
                task = self.__loop.create_task(self.__download_one(item))
                task.add_done_callback(lambda fut: list_.remove(fut.result()))
                tasks.append(task)
            for task in tasks:
                await task
            self.__log('下载完成', time=1000)

        list_ = self.__lists['download']
        if not list_:
            tk.messagebox.showinfo('info', 'no song in download list')
            return
        asynctk.create_task(download_start())

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
