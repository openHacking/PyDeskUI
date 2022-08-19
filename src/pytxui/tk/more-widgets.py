# Basic Widgets,reference https://tkdocs.com/tutorial/morewidgets.html

from tkinter import *
from tkinter import ttk

root = Tk()

root.title("More Widgets")

# create content frame
mainFrame = ttk.Frame(root,padding='3 3 12 12')
mainFrame.grid(column=0,row=0,sticky=(N,W,E,S))

# The columnconfigure/rowconfigure bits tell Tk that the frame should expand to fill any extra space if the window is resized.
root.columnconfigure(0,weight=1)
root.rowconfigure(0,weight=1)


################################################ Simple Listbox

choices = ["apple", "orange", "banana"]
choicesvar = StringVar(value=choices)
l = Listbox(mainFrame, listvariable=choicesvar)

# add more item
choices.append("peach")
choicesvar.set(choices)

def getActiveItem(s):
    print('select',l.get(s))

l.bind("<<ListboxSelect>>", lambda e: getActiveItem(l.curselection()))

# place to grid
l.grid(column=0,row=0,sticky=(W,E))


################################################ Scrollbar

lb = Listbox(mainFrame, height=5)
lb.grid(column=0, row=1, sticky=(N,W,E,S))
s = ttk.Scrollbar(mainFrame, orient=VERTICAL, command=lb.yview)
s.grid(column=1, row=1, sticky=(N,S))
lb['yscrollcommand'] = s.set
ttk.Label(mainFrame, text="Status message here", anchor=(W)).grid(column=0, columnspan=2, row=2, sticky=(W,E))
for i in range(1,101):
    lb.insert('end', 'Line %d of 100' % i)

################################################ Text
t = Text(mainFrame, width=40, height=10)
t.insert(INSERT,'It is Text')
t.grid(column=0,row=3,sticky=(W,E))

################################################ Scale
# label tied to the same variable as the scale, so auto-updates
num = StringVar()
ttk.Label(root, textvariable=num).grid(column=0, row=4, sticky='we')

# label that we'll manually update via the scale's command callback
manual = ttk.Label(root)
manual.grid(column=0, row=5, sticky='we')

def update_lbl(val):
   manual['text'] = "Scale at " + val

scale = ttk.Scale(root, orient='horizontal', length=200, from_=1.0, to=100.0, variable=num, command=update_lbl)
scale.grid(column=0, row=6, sticky='we')
scale.set(20)

################################################ Spinbox

spinval = StringVar()
spin = ttk.Spinbox(mainFrame, from_=1.0, to=100.0, textvariable=spinval)
spin.grid(column=2,row=0,sticky=(W,E))


################################################ Progressbar

p = ttk.Progressbar(mainFrame,value=20, orient=HORIZONTAL, length=200, mode='determinate')
p.grid(column=2,row=1)

root.mainloop()


