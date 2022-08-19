# reference: https://stackoverflow.com/a/65725414
# https://www.tcl.tk/man/tcl8.4/TkCmd/cursors.html

import tkinter as tk

root = tk.Tk()

frame = tk.Frame(root)
frame.pack(expand=True, fill=tk.BOTH)

cursors = """
X_cursor
arrow
based_arrow_down
based_arrow_up
boat
bogosity
bottom_left_corner
bottom_right_corner
bottom_side
bottom_tee
box_spiral
center_ptr
circle
clock
coffee_mug
cross
cross_reverse
crosshair
diamond_cross
dot
dotbox
double_arrow
draft_large
draft_small
draped_box
exchange
fleur
gobbler
gumby
hand1
hand2
heart
icon
iron_cross
left_ptr
left_side
left_tee
leftbutton
ll_angle
lr_angle
man
middlebutton
mouse
pencil
pirate
plus
question_arrow
right_ptr
right_side
right_tee
rightbutton
rtl_logo
sailboat
sb_down_arrow
sb_h_double_arrow
sb_left_arrow
sb_right_arrow
sb_up_arrow
sb_v_double_arrow
shuttle
sizing
spider
spraycan
star
target
tcross
top_left_arrow
top_left_corner
top_right_corner
top_side
top_tee
trek
ul_angle
umbrella
ur_angle
watch
xterm
copyarrow
aliasarrow
contextualmenuarrow
text
cross-hair
closedhand
openhand
pointinghand
resizeleft
resizeright
resizeleftright
resizeup
resizedown
resizeupdown
none
notallowed
poof
countinguphand
countingdownhand
countingupanddownhand
spinning""".split()

i = 0
j = 0
for cur in cursors:
    if i == 20:
        i = 0
        j += 1
    tk.Button(frame, text=cur, height=2, width=15, cursor=cur).grid(row=i, column=j)
    i += 1

tk.mainloop()