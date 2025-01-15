import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import csv
import matplotlib.pyplot as plt

class DayBook:
    def __init__(self, root):
        self.root = root
        self.root.title("Day Book")

        # Main frame
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky="NSEW")

        # Variables
        self.date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.description_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Income")

        # Widgets
        ttk.Label(self.frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="E")
        self.date_entry = ttk.Entry(self.frame, textvariable=self.date_var, width=30)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky="E")
        self.description_entry = ttk.Entry(self.frame, textvariable=self.description_var, width=30)
        self.description_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="Amount (INR):").grid(row=2, column=0, padx=5, pady=5, sticky="E")
        self.amount_entry = ttk.Entry(self.frame, textvariable=self.amount_var, width=30)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="Type:").grid(row=3, column=0, padx=5, pady=5, sticky="E")
        self.type_combo = ttk.Combobox(self.frame, textvariable=self.type_var, values=["Income", "Expense", "Contra"], state="readonly", width=28)
        self.type_combo.grid(row=3, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(self.frame, text="Add Entry", command=self.add_entry)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.view_chart_button = ttk.Button(self.frame, text="View Charts", command=self.view_charts)
        self.view_chart_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.frame, columns=("Date", "Description", "Amount", "Type"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount (INR)")
        self.tree.heading("Type", text="Type")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Description", width=200)
        self.tree.column("Amount", width=100, anchor="center")
        self.tree.column("Type", width=100, anchor="center")
        self.tree.grid(row=6, column=0, columnspan=2, pady=10, sticky="NSEW")

        self.total_label = ttk.Label(self.frame, text="Total Income: 0 INR | Total Expense: 0 INR", font=("Arial", 12, "bold"))
        self.total_label.grid(row=7, column=0, columnspan=2, pady=10)

        # Adjust row/column weights
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(6, weight=1)

        # Initialize day book data
        self.entries = []
        self.csv_file = "day_book.csv"
        self.initialize_csv()
        self.load_entries()

    def initialize_csv(self):
        try:
            with open(self.csv_file, "x", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Description", "Amount", "Type"])
        except FileExistsError:
            pass

    def load_entries(self):
        """Load existing entries from the CSV file into the treeview and calculate totals."""
        self.entries = []
        try:
            with open(self.csv_file, newline="") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    date, description, amount, entry_type = row
                    amount = float(amount)
                    self.entries.append((date, description, amount, entry_type))
                    self.tree.insert("", tk.END, values=(date, description, f"{amount:.2f}", entry_type))
            self.update_totals()
        except FileNotFoundError:
            pass

    def add_entry(self):
        date = self.date_var.get().strip()
        description = self.description_var.get().strip()
        entry_type = self.type_var.get()

        try:
            amount = float(self.amount_var.get().strip())
            if not description or amount <= 0:
                raise ValueError
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid data.")
            return

        entry = (date, description, amount, entry_type)
        self.entries.append(entry)
        self.tree.insert("", tk.END, values=(date, description, f"{amount:.2f}", entry_type))
        self.update_totals()
        self.save_to_csv(entry)

        self.description_var.set("")
        self.amount_var.set("")

    def save_to_csv(self, entry):
        with open(self.csv_file, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(entry)

    def update_totals(self):
        total_income = sum(amount for _, _, amount, t in self.entries if t == "Income")
        total_expense = sum(amount for _, _, amount, t in self.entries if t == "Expense")
        self.total_label.config(text=f"Total Income: {total_income:.2f} INR | Total Expense: {total_expense:.2f} INR")

    def view_charts(self):
        income = sum(amount for _, _, amount, t in self.entries if t == "Income")
        expense = sum(amount for _, _, amount, t in self.entries if t == "Expense")
        contra = sum(amount for _, _, amount, t in self.entries if t == "Contra")

        labels = ["Income", "Expense", "Contra"]
        values = [income, expense, contra]

        plt.figure(figsize=(6, 6))
        plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, colors=["green", "red", "blue"])
        plt.title("Day Book Summary")
        plt.axis("equal")
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = DayBook(root)
    root.mainloop()
