from functools import partial
from typing import Optional

from music_api import Template
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from ..lib.media_player import Player
from ..lib.qt_components import SongLabel
from ..ui.search_ui import Ui_Form


class SearchWidget(QWidget, Ui_Form):
    """ frame of search."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._choosed: list[Optional[Template.Song]] = [None] * 15
        self._player = Player()
        self.setupUi(self)

    def clear(self) -> None:
        """ clear search results."""

        item_count = self.result_verticalLayout.count()
        for i in range(item_count - 1, -1, -1):
            item = self.result_verticalLayout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.result_verticalLayout.removeItem(item)

    def show_items(self, items: list[Template.Song]) -> None:
        """ show list of items."""

        def toggle(state, item: Template.Song, index: int) -> None:
            if state == Qt.CheckState.Checked.value:
                self._choosed[index] = item
            else:
                self._choosed[index] = None
        for i, item in enumerate(items):
            widget = QWidget()
            button = QCheckBox("")
            button.stateChanged.connect(partial(toggle, item=item, index=i))
            label = SongLabel(item)
            hbox = QHBoxLayout(widget)
            hbox.addWidget(button)
            hbox.addWidget(label)
            hbox.addSpacerItem(QSpacerItem(
                40,
                20,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            ))
            self.result_verticalLayout.addWidget(widget)

    @Slot()
    def on_add_pushButton_clicked(self) -> None:
        self._player.extend_play_list(
            *[song for song in self._choosed if song is not None]
        )

    @Slot()
    def on_download_pushButton_clicked(self) -> None:
        QMessageBox.information(self, "info", "Not implement")
