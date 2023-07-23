from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon


def load_icon(file: str) -> QIcon:
    """ load icon from file(could be qrc file).

    :param file: file path
    ;return: QIcon object
    """

    icon = QIcon()
    icon.addFile(
        file,
        QSize(),
        QIcon.Mode.Normal,
        QIcon.State.Off,
    )
    return icon
