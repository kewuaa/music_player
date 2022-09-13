from tkinter import StringVar


class PlayList(list):

    def __init__(self, *args, listvar: StringVar, **kwargs) -> None:
        """初始化."""

        super().__init__(*args, **kwargs)
        self.__index: int = None
        self.__listvar: StringVar = listvar

    def __update_listvar(self) -> None:
        self.__listvar.set(tuple(item.summary for item in self))

    def append(self, object):
        result = super().append(object)
        self.__update_listvar()
        return result

    def insert(self, index, object):
        result = super().insert(index, object)
        self.__update_listvar()
        return result

    def pop(self, index):
        result = super().pop(index)
        self.__update_listvar()
        return result

    def remove(self, value):
        result = super().remove(value)
        self.__update_listvar()
        return result

    def check_index(self) -> bool:
        """检查是否设置索引."""

        return self.__index is not None

    def set_index(self, index: int) -> None:
        """设置当前索引.

        :param index: 索引
        :returns: None
        """

        assert type(index) is int
        self.__index = index

    def get_index(self) -> int:
        """返回当前索引."""

        return self.__index

    def next(self):
        """返回下一个."""

        self.__index += 1
        if self.__index >= self.__len__():
            return
        v = self[self.__index]
        return v

    def previous(self):
        """返回上一个."""

        self.__index -= 1
        if self.__index < 0:
            return
        v = self[self.__index]
        return v
