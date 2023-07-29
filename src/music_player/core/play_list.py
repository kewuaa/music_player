import asyncio
from functools import partial
from typing import Callable, Optional

from music_api import Template
from PySide6.QtCore import Slot
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from ..lib.media_player import Player
from ..lib.qt_components import SongLabel as _SongLabel
from ..ui.play_list_ui import Ui_Form


class SongLabel(_SongLabel):
    def __init__(
        self,
        song: Template.Song,
        cal_index: Callable[[], int],
        parent: Optional[QWidget] = None,
        loop: Optional[asyncio.base_events.BaseEventLoop] = None
    ) -> None:
        self._cal_index = cal_index
        super().__init__(song, parent, loop)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        index = self._cal_index()
        self._player.play_media_at(index)
        return super().mouseDoubleClickEvent(event)


class PlayListWidget(QWidget, Ui_Form):
    """ play list widget."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """ initialize.

        :param parent: parent of the widget
        """

        super().__init__(parent)
        self.setupUi(self)

    def _create_item(self, item: Template.Song) -> None:
        """ create item from Song

        :param item: Song
        """

        widget = QWidget()
        button = QCheckBox("")
        label = SongLabel(item, partial(self.list_verticalLayout.indexOf, widget))
        hbox = QHBoxLayout(widget)
        hbox.addWidget(button)
        hbox.addWidget(label)
        hbox.addSpacerItem(QSpacerItem(
            40,
            20,
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        ))
        self.list_verticalLayout.addWidget(widget)


    def connect_to_player(self, player: Player) -> None:
        self._player = player
        player.listAdd.connect(self.add)
        player.listRemove.connect(self.remove)

    def clear(self) -> None:
        """ clear list."""

        item_count = self.verticalLayout.count()
        for i in range(item_count - 1, -1, -1):
            item = self.verticalLayout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.verticalLayout.removeItem(item)

    def add(self, items: tuple[Template.Song]) -> None:
        """ add items.

        :param items: tuple of Song
        """

        for item in items:
            self._create_item(item)

    def remove(self, index: tuple[int]) -> None:
        """ remove list of items.

        :param index: tuple of index of item to be removed
        """

        for i in sorted(index, reverse=True):
            item = self.verticalLayout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.verticalLayout.removeItem(item)

    def refresh(self) -> None:
        """ refresh list."""

        if not hasattr(self, "_player"):
            raise RuntimeError("not connect to player yet")
        self.clear()
        for song in self._player:
            self._create_item(song)

    @Slot()
    def on_remove_pushButton_clicked(self) -> None:
        QMessageBox.information(self, "info", "Not implement")

    @Slot()
    def on_download_pushButton_clicked(self) -> None:
        QMessageBox.information(self, "info", "Not implement")
