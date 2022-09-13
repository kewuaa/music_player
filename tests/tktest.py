from tkinter import StringVar
import tkinter as tk

root = tk.Tk()
lb = tk.Listbox(root)
var = StringVar(value=('a', 'b'))
lb.pack()
root.after(1000, lambda: lb.configure(listvariable=var))
root.after(3000, lambda: var.set('a b c d e'))
root.mainloop()
