from tkinter import *
from tkinter import ttk
from button import DeskButton, TxRoundedButton
from input import DeskInput


class Win:
    def __init__(self, root):
        # set title
        root.title("test button")

        # screen width
        sw = root.winfo_screenwidth()
        # screen height
        sh = root.winfo_screenheight()
        # frame width
        ww = 600
        # # frame height
        wh = 600
        x = (sw-ww) / 2
        y = (sh-wh) / 2 - 20

        root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
        root.resizable(False, False)
        root.config(background="white")

        # create content frame
        # mainFrame = ttk.Frame(root,padding='20 20 20 20')
        # mainFrame.grid(column=0,row=0,sticky=(N,W,E,S))
        # The columnconfigure/rowconfigure bits tell Tk that the frame should expand to fill any extra space if the window is resized.
        # root.columnconfigure(0,weight=1)
        # root.rowconfigure(0,weight=1)

        defaultButton = DeskButton(root, command=self.useClassic)
        defaultButton.place(x=50, y=50)

        primaryButton = DeskButton(root, type='primary', size='large')
        primaryButton.place(x=150, y=50)

        textButton = DeskButton(root, type='text', size='small')
        textButton.place(x=250, y=50)

        linkButton = DeskButton(root, type='link')
        linkButton.place(x=350, y=50)

        input = DeskInput(root)
        input.place(x=50, y=100)

        cb = Checkbutton(root)
        cb.place(x=100, y=100)

        def metricChanged():
            print('checkbutton', measureSystem.get())

        measureSystem = StringVar()
        check = ttk.Checkbutton(root, text='Use Metric',
                                command=metricChanged, variable=measureSystem,
                                onvalue='metric', offvalue='imperial')

        check.place(x=130, y=100)

        self.start_btn = TxRoundedButton(
            root, border_radius=3, padding=8, color="#16A765", text='Start Camera')
        self.start_btn.place(x=50, y=200)

    # click event listener callback
    def useClassic(self, *args):

        print('click one')

    def useDefault(self, *args):

        print('click two')


# sets up the main application window
root = Tk()
# init function
Win(root)
# necessary for everything to appear onscreen and allow users to interact with it.
root.mainloop()
