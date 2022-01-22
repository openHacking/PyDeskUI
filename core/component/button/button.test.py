from tkinter import *
from tkinter import ttk
from button import TxRectButton,TxRoundedButton,TxCanvas

class Win:
    def __init__(self,root):
        # set title
        root.title("test button")

        # screen width
        sw = root.winfo_screenwidth()
        # screen height
        sh = root.winfo_screenheight()
        # frame width
        ww = 380
        # frame height
        wh = 280
        x = (sw-ww) / 2
        y = (sh-wh) / 2 - 20

        root.geometry("%dx%d+%d+%d" %(ww,wh,x,y))
        root.resizable(False, False)
        root.config(background="white")
        
        # create content frame
        mainFrame = ttk.Frame(root,padding='20 20 20 20')
        mainFrame.grid(column=0,row=0,sticky=(N,W,E,S))
        # The columnconfigure/rowconfigure bits tell Tk that the frame should expand to fill any extra space if the window is resized.
        root.columnconfigure(0,weight=1)
        root.rowconfigure(0,weight=1)

        # # default button style
        # defaultButton = CustomButton(root, text="button one",handleClick=self.useClassic)
        # defaultButton.grid(column=0, row=0, columnspan=2, sticky=(N, W), padx=5,pady=20)

        # # custom button style
        # customButton = CustomButton(root, text="button two",foreground='#1a1a1a',hoverBackground="#ede9e5",background='#fcfbfa',handleClick=self.useDefault)
        # customButton.grid(column=0, row=1, columnspan=2, sticky=(N, W), padx=5,pady=20)

        defaultButton = TxRectButton(root)
        defaultButton.grid(column=0, row=0, columnspan=2, sticky=(N, W),padx=5,pady=20)

        self.start_btn = TxRoundedButton(
        root, border_radius=3, padding=8, color="#16A765", text='Start Camera')
        self.start_btn.grid(column=0, row=1, columnspan=2, sticky=(N, W), padx=5,pady=20)
        
        self.end_btn = TxCanvas(
        root)
        self.end_btn.grid(column=0, row=2, columnspan=2, sticky=(N, W), padx=5,pady=20)
        
    # exec bat
    def useClassic(self,*args):

        print('click one')

    def useDefault(self,*args):

        print('click two')

# sets up the main application window
root = Tk()
# init function
Win(root)
# necessary for everything to appear onscreen and allow users to interact with it.
root.mainloop()
