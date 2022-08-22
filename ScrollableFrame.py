# Credits to https://python.tutorialink.com/scrollable-frame-class-in-tkinter/

import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True, side="left")
        self.scroll = tk.Scrollbar(self, command=self.canvas.yview)
        self.scroll.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=self.scroll.set)
        self.content = tk.Frame(self.canvas)
        self.contentWindow = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Enter>", self.enable_scroll_canvas)
        self.content.bind("<Leave>", self.disable_scroll_canvas)
        self.bind("<Configure>", self.resize_canvas)

    def scroll_canvas(self, event=None):
        if event is None:
            return self.canvas.yview_moveto(1.0)
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def enable_scroll_canvas(self, event):
        self.canvas.bind_all("<MouseWheel>", self.scroll_canvas)

    def disable_scroll_canvas(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def resize_canvas(self, event):
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.contentWindow, width=self.canvas.winfo_width())


if __name__ == "__main__":
    root = tk.Tk()
    exampleFrame = ScrollableFrame(root, border=1, relief="sunken")
    exampleFrame.place(x=0, y=0, relheight=1, relwidth=1)
    for i in range(100):
        text = tk.Text(exampleFrame.content, height=1, width=20)
        text.insert(tk.END, "item " + str(i))
        text.pack(anchor=tk.W if i % 2 == 0 else tk.E)
    root.mainloop()
