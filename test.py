import tkinter as tk
import numpy as np

root = tk.Tk()

im_blck = tk.PhotoImage(file='~/go/black.gif') 
im_wht = tk.PhotoImage(file='~/go/white.gif') 

def on_click(i, j, e, label_arr): 
	print(i)
	this_label = label_arr[i,j]
	
	im_blck = tk.PhotoImage(file='~/go/black.gif') 
	this_label.configure(image = im_blck)
	this_label.image = im_blck
	print(label_arr)

sz = 4
label_arr = np.ndarray(shape=(sz,sz), dtype=object)
label_arr[0,0] = 1
print(label_arr)

for i in range(sz):
	for j in range(sz):
		if i % 2 == 0:
			label = tk.Label(root, image = im_blck)
			label.image = im_blck
			print("new label created")
		else:
			label = tk.Label(root, image = im_wht)
			label.image = im_wht
			print("new label created")
	
		label_arr[i,j] = label
		label.bind('<Button-1>',lambda e,i=i, j=j: on_click(i,j, e, label_arr))
		label.grid(row=i,column=j)

root.mainloop()


