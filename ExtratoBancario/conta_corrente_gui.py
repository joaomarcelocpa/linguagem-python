import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Label, Button
from PIL import Image, ImageTk
from main import update_sheet, initialize_sheet, get_current_balance, get_credentials
from googleapiclient.discovery import build
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ContaCorrenteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Livro de Conta Corrente - Fabiana Móveis")
        self.root.geometry("570x550")
        self.root.configure(bg="#ADD8E6")

        self.create_widgets()
        initialize_sheet()
        self.update_current_balance()

    def create_widgets(self):
        self.logo_image = Image.open(resource_path("logofabianamoveis.png"))
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = Label(self.root, image=self.logo_photo, bg="#ADD8E6")
        self.logo_label.grid(row=0, column=0, columnspan=2, pady=12)

        tk.Label(self.root, text="Data (dia/mês)", font=("Helvetica", 14, "bold"), bg="#ADD8E6").grid(row=1, column=0, padx=10, pady=10)
        self.entry_date = tk.Entry(self.root, font=("Helvetica", 14), width=20)
        self.entry_date.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Tipo da Transação", font=("Helvetica", 14, "bold"), bg="#ADD8E6").grid(row=2, column=0, padx=10, pady=10)
        self.combo_type = ttk.Combobox(self.root,
                                       values=["PIX", "Pagamento", "Cheque", "Stone", "Depósito", "Serviços"],
                                       font=("Helvetica", 14), state="readonly", width=18)
        self.combo_type.grid(row=2, column=1, padx=10, pady=10)
        self.combo_type.bind("<<ComboboxSelected>>", self.update_description_label)

        self.label_description = tk.Label(self.root, text="Descrição", font=("Helvetica", 14, "bold"), bg="#ADD8E6")
        self.label_description.grid(row=3, column=0, padx=10, pady=10)
        self.entry_description = tk.Entry(self.root, font=("Helvetica", 14), width=20)
        self.entry_description.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Valor (R$)", font=("Helvetica", 14, "bold"), bg="#ADD8E6").grid(row=4, column=0, padx=10, pady=10)
        self.entry_value = tk.Entry(self.root, font=("Helvetica", 14), width=20)
        self.entry_value.grid(row=4, column=1, padx=10, pady=10)

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 14, "bold"), padding=10)

        ttk.Button(self.root, text="Limpar", command=self.clear_entries, style="TButton").grid(row=5, column=0, pady=20)
        ttk.Button(self.root, text="Salvar", command=self.submit_data, style="TButton").grid(row=5, column=1, pady=20)

        self.label_balance = tk.Label(self.root, text="Saldo Atual: R$0,00", font=("Helvetica", 14, "bold"), bg="#ADD8E6")
        self.label_balance.grid(row=6, column=0, columnspan=2, pady=10)

    def update_description_label(self, event):
        tipo = self.combo_type.get()
        if tipo == "PIX":
            self.label_description.config(text="Filial")
        elif tipo == "Pagamento":
            self.label_description.config(text="Empresa")
        elif tipo == "Cheque":
            self.label_description.config(text="Número do Cheque")
        else:
            self.label_description.config(text="Descrição")

    def update_current_balance(self):
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)
        current_balance = get_current_balance(service)
        formatted_balance = f"R$ {current_balance:.2f}".replace(".", ",")
        self.label_balance.config(text=f"Saldo Atual: {formatted_balance}")

    def submit_data(self):
        valor_str = self.entry_value.get().replace(",", ".")
        data = {
            "Data": self.entry_date.get(),
            "Tipo": self.combo_type.get(),
            "Detalhes": self.entry_description.get(),
            "Valor": float(valor_str)
        }
        self.confirm_submission(data)

    def confirm_submission(self, data):
        confirm_window = Toplevel(self.root)
        confirm_window.title("Confirmação de Dados")
        confirm_window.geometry("400x300")
        confirm_window.configure(bg="#ADD8E6")

        Label(confirm_window, text="Confirme os dados inseridos:", font=("Helvetica", 14, "bold"), bg="#ADD8E6").pack(
            pady=10)
        Label(confirm_window, text=f"Data: {data['Data']}", font=("Helvetica", 12, "bold"), bg="#ADD8E6").pack(pady=5)
        Label(confirm_window, text=f"Tipo: {data['Tipo']}", font=("Helvetica", 12, "bold"), bg="#ADD8E6").pack(pady=5)
        Label(confirm_window, text=f"Descrição: {data['Detalhes']}", font=("Helvetica", 12, "bold"), bg="#ADD8E6").pack(
            pady=5)
        Label(confirm_window, text=f"Valor: R${data['Valor']:.2f}".replace(".", ","), font=("Helvetica", 12, "bold"),
              bg="#ADD8E6").pack(pady=5)

        ttk.Button(confirm_window, text="Confirmar", command=lambda: self.finalize_submission(data, confirm_window),
                   style="TButton").pack(side="left", padx=20, pady=20)
        ttk.Button(confirm_window, text="Cancelar", command=confirm_window.destroy, style="TButton").pack(side="right",
                                                                                                          padx=20,
                                                                                                          pady=20)
    def finalize_submission(self, data, confirm_window):
        update_sheet(data)
        self.update_current_balance()
        confirm_window.destroy()

    def clear_entries(self):
        self.entry_date.delete(0, tk.END)
        self.combo_type.set("")
        self.entry_description.delete(0, tk.END)
        self.entry_value.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ContaCorrenteGUI(root)
    root.mainloop()