from tkinter import*

window = Tk()
window.title("ksdasndsnadn")

bg_image = PhotoImage(file ="pic.gif")
x = Label (image = bg_image)
x.image = bg_image.grid(row = 0, column = 0)


window.geometry("600x300")
app = Application(window)
window.mainloop()