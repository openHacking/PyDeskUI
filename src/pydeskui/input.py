# Program to make a simple
# login screen

# https://www.geeksforgeeks.org/python-tkinter-entry-widget/

import tkinter as tk
import tkinter.ttk as ttk


# reference: https://stackoverflow.com/a/66090998
class DeskInput(ttk.Entry):
    def __init__(self, root, *args, **kwargs):

        style = ttk.Style(root)

        # padding = (padx left, pady up,padx right,pady down)
        style.configure('DeskUI.TEntry', padding=(11, 4, 11, 4))

        # declaring string variable
        self.name_var = tk.StringVar()

        # creating a entry for input
        ttk.Entry.__init__(self)

        self.config(
            textvariable=self.name_var,
            style='DeskUI.TEntry'
        )

    # defining a function that will
    # get the name and password and
    # print them on the screen
    def input(self, event):

        name = self.name_var.get()

        print("The name is : " + name)

        self.name_var.set("")
