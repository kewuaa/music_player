from typing import Optional

from PySide6.QtWidgets import QWidget

from ..ui.home_ui import Ui_Form


class HomeWidget(QWidget, Ui_Form):
    """ home widget."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
