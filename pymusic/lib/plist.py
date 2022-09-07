class PlayList:

    def __init__(self) -> None:
        """初始化."""

        self.__list: list = []
        self.__index: int = -1

    def reset(self, new_list: list) -> None:
        """重置."""

        self.__list = new_list

