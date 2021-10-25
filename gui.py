import tkinter as tk
from tkinter import ttk
from functools import partial

from PIL import Image, ImageTk

from frfr import reduce, T, apply


def add_transformation(transformation):
    all_trans_widget.insert(tk.END, transformation.name)

    all_trans_sequence = tuple(T[name] for name in all_trans.get())
    updated_reduced_trans_sequence = tuple(op.name for op in reduce(all_trans_sequence))

    updated_reduced_trans = tk.Variable(value=updated_reduced_trans_sequence)
    reduced_trans_widget[
        "listvariable"
    ] = reduced_trans_widget.listvariable = updated_reduced_trans

    apply_transformations(all_trans, all_image_widget)
    apply_transformations(updated_reduced_trans, reduced_image_widget)


def reset_transformations(keypress=None):
    all_trans_widget.delete(0, tk.END)
    reduced_trans_widget.delete(0, tk.END)
    all_image_widget["image"] = original_photo_image
    reduced_image_widget["image"] = original_photo_image


def apply_transformations(trans, image_widget):
    trans_sequence = [T[name] for name in trans.get()]
    transformed_image = apply(trans_sequence, original_image)
    transformed_photo_image = ImageTk.PhotoImage(transformed_image)
    image_widget["image"] = image_widget.image = transformed_photo_image


root = tk.Tk()
root.title("~")
root.resizable(width=False, height=False)

mainframe = ttk.Frame(root, padding="5 10 5 10")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

ttk.Button(
    mainframe,
    text="Rotate Left",
    command=partial(add_transformation, T.ROTATE_LEFT),
).grid(column=1, row=1, sticky=tk.E)
ttk.Button(
    mainframe,
    text="Rotate Right",
    command=partial(add_transformation, T.ROTATE_RIGHT),
).grid(column=2, row=1, sticky=tk.W)

ttk.Button(
    mainframe,
    text="Flip Top Bottom",
    command=partial(add_transformation, T.FLIP_TOP_BOTTOM),
).grid(column=1, row=2, sticky=tk.E)
ttk.Button(
    mainframe,
    text="Flip Left Right",
    command=partial(add_transformation, T.FLIP_LEFT_RIGHT),
).grid(column=2, row=2, sticky=tk.W)

ttk.Label(mainframe, text="All transformations").grid(column=1, row=3)
ttk.Label(mainframe, text="Reduced transformations").grid(column=2, row=3)

all_trans = tk.Variable(value=())
all_trans_widget = tk.Listbox(mainframe, listvariable=all_trans, height=10)
all_trans_widget.grid(column=1, row=4, sticky=tk.W)
reduced_trans = tk.Variable(value=())
reduced_trans_widget = tk.Listbox(mainframe, listvariable=reduced_trans, height=4)
reduced_trans_widget.grid(column=2, row=4, sticky=(tk.N, tk.E))

original_image = Image.open("ylde.png").resize((126, 126))
original_photo_image = ImageTk.PhotoImage(original_image)
all_image_widget = tk.Label(mainframe, image=original_photo_image)
all_image_widget.grid(column=1, row=5)
reduced_image_widget = tk.Label(mainframe, image=original_photo_image)
reduced_image_widget.grid(column=2, row=5)

reset_button = ttk.Button(mainframe, text="Reset", command=reset_transformations)
reset_button.grid(column=2, row=6)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
reset_button.focus()
root.bind("<Escape>", reset_transformations)
root.mainloop()
