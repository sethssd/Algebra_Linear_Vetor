import tkinter as tk
from tkinter import ttk
from ui.theme import PALETTE as T

class VertexCountDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Nova Figura Personalizada")
        self.geometry("340x180")
        self.resizable(False, False)
        self.configure(bg=T["bg"])
        
        # Center the dialog on parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (340 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (180 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self._build_ui()

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=T["bg"], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        lbl = tk.Label(
            main_frame, text="Quantos vértices a sua figura vai ter?",
            font=("Segoe UI", 11), bg=T["bg"], fg=T["text"]
        )
        lbl.pack(pady=(0, 15))

        # Spinbox minimalista
        vcmd = (self.register(self._validate_input), '%P')
        self.spin = tk.Spinbox(
            main_frame, from_=1, to=100, width=10,
            font=("Segoe UI", 12), validate="key", validatecommand=vcmd,
            bg=T["card"], fg=T["text"], insertbackground=T["text"],
            buttonbackground=T["card_alt"], bd=1, relief="solid"
        )
        self.spin.pack(pady=(0, 20))
        
        # Botões
        btn_frame = tk.Frame(main_frame, bg=T["bg"])
        btn_frame.pack(fill=tk.X)
        
        btn_cancel = tk.Button(
            btn_frame, text="Cancelar", font=("Segoe UI", 9),
            bg=T["card"], fg=T["text"], activebackground=T["card_alt"],
            activeforeground=T["text"], relief="flat", padx=10, pady=5,
            command=self.destroy
        )
        btn_cancel.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        btn_ok = tk.Button(
            btn_frame, text="Continuar", font=("Segoe UI", 9, "bold"),
            bg=T["accent"], fg=T["bg"], activebackground="#ff66b8",
            activeforeground=T["bg"], relief="flat", padx=10, pady=5,
            command=self._on_ok
        )
        btn_ok.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Hover effects
        btn_cancel.bind("<Enter>", lambda e: btn_cancel.config(bg=T["card_alt"]))
        btn_cancel.bind("<Leave>", lambda e: btn_cancel.config(bg=T["card"]))
        btn_ok.bind("<Enter>", lambda e: btn_ok.config(bg="#ff66b8"))
        btn_ok.bind("<Leave>", lambda e: btn_ok.config(bg=T["accent"]))

    def _validate_input(self, value):
        if value == "":
            return True
        if value.isdigit() and int(value) > 0:
            return True
        return False

    def _on_ok(self):
        val = self.spin.get()
        if val.isdigit() and int(val) > 0:
            self.result = int(val)
            self.destroy()
