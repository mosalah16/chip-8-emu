import tkinter as tk

class Gui:
    def __init__(self, root):
        self.root = root
        self.root.title("Chip 8")
        
        self.cpu_interval = tk.IntVar(value = 1 / 700)
        self.scale = tk.IntVar(value = 20)
        self.rom_path = tk.StringVar( value = "roms/tetris")

        self.widgets()
    
    def widgets(self):
        