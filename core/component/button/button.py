# reference https://stackoverflow.com/a/34466743
class CustomButton(Label):

    def __init__(self, *args, **kwargs):
        # TODO: Create a Frame for border https://www.geeksforgeeks.org/how-to-change-border-color-in-tkinter-widget/
        Label.__init__(self)
        self.bind("<Enter>", self.changeBGEnter)
        self.bind("<Leave>", self.changeBGLeave)
        self.bind("<Button-1>",kwargs.get('handleClick',self.handleClickDefault) )

        self.background = kwargs.get('background',"#1890ff")
        self.hoverBackground = kwargs.get('hoverBackground',"#40a9ff")
        self.foreground = kwargs.get('foreground',"#fff")
        self.fontsize = kwargs.get('fontsize',14) 
        self.fontfamily = kwargs.get('fontfamily',"微软雅黑") 
        self.text = kwargs.get('text',"Button") 
        self.width = kwargs.get('width',30) 
        self.padx = kwargs.get('padx',10) 
        self.pady = kwargs.get('pady',10) 
        self.relief = kwargs.get('relief','solid') 
        self.borderwidth = kwargs.get('borderwidth',1) 
        self.anchor = kwargs.get('anchor','center') 
        self.justify = kwargs.get('justify','center') 

        self.config(
            anchor=self.anchor,  # Where to anchor the text in the widget
            justify=self.justify,
            background=self.background,
            foreground=self.foreground,
            font=(self.fontfamily, self.fontsize),
            text=self.text,
            relief=self.relief,
            width=self.width,
            padx=self.padx,
            pady=self.pady,
            borderwidth=self.borderwidth
        )

    def changeBGEnter(self,event):
        self.config(background=self.hoverBackground,foreground=self.foreground)

    def changeBGLeave(self, event):
        self.config(background=self.background,foreground=self.foreground)
    
    def handleClickDefault(self, event):
        print('click')
