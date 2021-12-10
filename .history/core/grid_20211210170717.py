# reference: https://tkdocs.com/tutorial/grid.html
from tkinter import *
from tkinter import ttk

root = Tk()

# root.rowconfigure(0,weight=1)
# root.rowconfigure(1,weight=1)
# root.rowconfigure(2,weight=0)

root.columnconfigure(0,weight=3)
root.columnconfigure(1,weight=3)
root.columnconfigure(2,weight=3)
root.columnconfigure(3,weight=1)
root.columnconfigure(4,weight=1)

# Spanning Multiple Cells
content = ttk.Frame(root)
frame = ttk.Frame(content, borderwidth=5, relief="ridge", width=200, height=100)
# set style
namelbl = ttk.Label(content, text="Name",background='orange',relief='solid',borderwidth=2)
name = ttk.Entry(content)

onevar = BooleanVar(value=True)
twovar = BooleanVar(value=False)
threevar = BooleanVar(value=True)

one = ttk.Checkbutton(content, text="One", variable=onevar, onvalue=True)
two = ttk.Checkbutton(content, text="Two", variable=twovar, onvalue=True)
three = ttk.Checkbutton(content, text="Three", variable=threevar, onvalue=True)
ok = ttk.Button(content, text="Okay")
cancel = ttk.Button(content, text="Cancel")

content.grid(column=0, row=0)
frame.grid(column=0, row=0, columnspan=3, rowspan=2)
namelbl.grid(column=3, row=0, columnspan=2,sticky=(N,W,E,S)) # fill up the entire cell
name.grid(column=3, row=1, columnspan=2)
one.grid(column=0, row=3)
two.grid(column=1, row=3)
three.grid(column=2, row=3)
ok.grid(column=3, row=3)
cancel.grid(column=4, row=3)

root.mainloop()