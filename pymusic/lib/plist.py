from tkinter import StringVar
import tkinter as tk


class PlayList:
    def __init__(self, listbox: tk.Listbox) -> None:
        self.__box = listbox
        self.__var = StringVar(value="")
        self.__list = []
        self.__index: int = None
        listbox.configure(listvariable=self.__var)

    def __iter__(self):
        return iter(self.__list)

    def __getitem__(self, index: int):
        assert type(index) is int
        return self.__list[index]

    def __setitem__(self, index: int, value):
        assert type(index) is int
        self.__list[index] = value

    def __update(self) -> None:
        self.__var.set(tuple(item.summary for item in self.__list))

    def __activate(self, index: int = None) -> None:
        index = index or self.__index
        self.__box.activate(index)
        self.__box.selection_clear(0, 'end')
        self.__box.selection_set(index)

    def empty(self) -> bool:
        return bool(not self.__list)

    def response(self, event: tk.Event) -> int:
        if not self.__list:
            return
        index = self.__box.nearest(event.y)
        x, y, w, h = self.__box.bbox(index)
        if event.y > y + h:
            return
        self.__box.activate(index)
        return index

    def check_index(self) -> bool:
        return self.__index is not None

    def get_index(self) -> int:
        if self.__index is None:
            raise RuntimeError('index not set yet')
        return self.__index

    def set_index(self, index: int) -> None:
        assert type(index) is int
        if not 0 <= index < len(self.__list):
            raise RuntimeError('index out of range')
        self.__index = index
        self.__activate(index)

    def append(self, item) -> None:
        self.__list.append(item)
        self.__update()

    def pop(self, index: int):
        result = self.__list.pop(index)
        self.__update()
        return result

    def remove(self, value) -> None:
        self.__list.remove(value)
        self.__update()

    def next(self):
        self.__index += 1
        if self.__index >= len(self.__list):
            return
        self.__activate()
        return self.__list[self.__index]

    def previous(self):
        self.__index -= 1
        if self.__index < 0:
            return
        self.__activate()
        return self.__list[self.__index]
