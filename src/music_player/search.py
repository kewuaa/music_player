from typing import Optional

from music_api import Template
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from .lib.qt_components import SongLable
from .ui.search_ui import Ui_Form


class SearchWidget(QWidget, Ui_Form):
    """ frame of search."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def clear(self) -> None:
        """ clear search results."""

        item_count = self.result_verticalLayout.count()
        items = [self.result_verticalLayout.itemAt(i) for i in range(item_count)]
        for item in items:
            if item.widget():
                item.widget().deleteLater()
            self.result_verticalLayout.removeItem(item)

    def show_items(self, items: list[Template.SongInfo]) -> None:
        """ show list of items."""

        for item in items:
            widget = QWidget()
            button = QCheckBox("")
            label = SongLable(item)
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
