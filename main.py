# Upgraded version of Day Book app
# Features:
# - Dark/Light theme
# - SQLite backend
# - Charting & analytics
# - Recurring transactions
# - Filtering and reporting
# - Auto backup
# - Configurable settings
# - Modern UI (using ttkbootstrap)

import os
import sqlite3
import datetime
import csv
import json
from tkinter import PhotoImage
import shutil
import matplotlib.pyplot as plt
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog

CONFIG_FILE = 'config.json'
DB_FILE = 'daybook.db'
BACKUP_DIR = 'backups'

class DayBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Day Book Application by Lakshay Jindal")
        
        self.load_config()
        self.setup_db()
        base_path = os.path.dirname(os.path.abspath(__file__))
        try:
            self.root.iconbitmap(os.path.join(base_path, "assets", "logo.ico"))
        except Exception as e:
            print(f"Could not set icon: {e}")

        # Initialize input variables before UI
        self.date_var = ttkb.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.description_var = ttkb.StringVar()
        self.amount_var = ttkb.StringVar()
        self.type_var = ttkb.StringVar(value="Income")

        self.setup_ui()
        self.load_entries()
        self.check_recurring()


    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            default_config = {
                "theme": "superhero",
                "currency": "INR",
                "date_format": "%Y-%m-%d"
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=4)
        with open(CONFIG_FILE) as f:
            self.config = json.load(f)

    def setup_db(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS entries (
                            id INTEGER PRIMARY KEY,
                            date TEXT,
                            description TEXT,
                            amount REAL,
                            type TEXT
                        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS recurring (
                            id INTEGER PRIMARY KEY,
                            description TEXT,
                            amount REAL,
                            type TEXT,
                            day INTEGER
                        )''')
        self.conn.commit()

    def setup_ui(self):
        self.frame = ttkb.Frame(self.root, padding=10)
        self.frame.pack(fill=BOTH, expand=True)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(6, weight=1)

        # Input Section
        ttkb.Label(self.frame, text="Date:").grid(row=0, column=0, sticky=E, padx=5, pady=5)
        ttkb.Entry(self.frame, textvariable=self.date_var, width=20).grid(row=0, column=1, sticky=W+E, padx=5, pady=5)

        ttkb.Label(self.frame, text="Description:").grid(row=1, column=0, sticky=E, padx=5, pady=5)
        ttkb.Entry(self.frame, textvariable=self.description_var).grid(row=1, column=1, sticky=W+E, padx=5, pady=5)

        ttkb.Label(self.frame, text="Amount:").grid(row=2, column=0, sticky=E, padx=5, pady=5)
        ttkb.Entry(self.frame, textvariable=self.amount_var, width=20).grid(row=2, column=1, sticky=W+E, padx=5, pady=5)

        ttkb.Label(self.frame, text="Type:").grid(row=3, column=0, sticky=E, padx=5, pady=5)
        ttkb.Combobox(self.frame, textvariable=self.type_var, values=["Income", "Expense", "Contra"], state="readonly").grid(row=3, column=1, sticky=W+E, padx=5, pady=5)

        # Buttons
        button_frame = ttkb.Frame(self.frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)

        ttkb.Button(button_frame, text="Add Entry", command=self.add_entry, bootstyle=SUCCESS).grid(row=0, column=0, padx=5, sticky="ew")
        ttkb.Button(button_frame, text="View Chart", command=self.view_charts, bootstyle=INFO).grid(row=0, column=1, padx=5, sticky="ew")

        # Treeview Section
        self.tree = ttkb.Treeview(self.frame, columns=("Date", "Description", "Amount", "Type"), show="headings", height=10, bootstyle="primary")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(10, 5))

        # Scrollbar
        scrollbar = ttkb.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=5, column=2, sticky="ns")

        # Totals
        self.total_label = ttkb.Label(self.frame, text="Totals", font=("Segoe UI", 11, "bold"))
        self.total_label.grid(row=6, column=0, columnspan=2, pady=10)


    def add_entry(self):
        try:
            date = datetime.datetime.strptime(self.date_var.get(), self.config['date_format']).strftime('%Y-%m-%d')
            desc = self.description_var.get().strip()
            amount = float(self.amount_var.get().strip())
            entry_type = self.type_var.get()
            if not desc or amount <= 0:
                raise ValueError
            self.c.execute("INSERT INTO entries (date, description, amount, type) VALUES (?, ?, ?, ?)", (date, desc, amount, entry_type))
            self.conn.commit()
            self.load_entries()
            self.description_var.set("")
            self.amount_var.set("")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid values.")

    def load_entries(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.c.execute("SELECT date, description, amount, type FROM entries ORDER BY date DESC")
        entries = self.c.fetchall()
        for e in entries:
            self.tree.insert('', 'end', values=(e[0], e[1], f"{e[2]:.2f}", e[3]))
        self.update_totals(entries)

    def update_totals(self, entries):
        income = sum(row[2] for row in entries if row[3] == "Income")
        expense = sum(row[2] for row in entries if row[3] == "Expense")
        self.total_label.config(text=f"Total Income: {income:.2f} {self.config['currency']} | Total Expense: {expense:.2f} {self.config['currency']}")

    def view_charts(self):
        self.c.execute("SELECT amount, type FROM entries")
        data = self.c.fetchall()

        categories = {"Income": 0, "Expense": 0, "Contra": 0}
        for amount, typ in data:
            if typ in categories:
                categories[typ] += amount

        labels = []
        values = []
        colors = []
        color_map = {"Income": "green", "Expense": "red", "Contra": "blue"}

        for key, val in categories.items():
            if val > 0:
                labels.append(f"{key} ({val:.2f} {self.config['currency']})")
                values.append(val)
                colors.append(color_map[key])

        if not values:
            messagebox.showinfo("No Data", "No data available to display charts.")
            return

        plt.figure(figsize=(7, 6))
        wedges, texts, autotexts = plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops={"fontsize": 12}
        )

        plt.setp(autotexts, size=12, weight="bold", color="white")
        plt.title("Day Book Summary", fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.axis("equal")
        plt.show()


    def check_recurring(self):
        today = datetime.date.today()
        self.c.execute("SELECT description, amount, type, day FROM recurring")
        recs = self.c.fetchall()
        for desc, amt, typ, day in recs:
            if today.day == day:
                self.c.execute("SELECT COUNT(*) FROM entries WHERE date=? AND description=? AND amount=?", (today.isoformat(), desc, amt))
                if self.c.fetchone()[0] == 0:
                    self.c.execute("INSERT INTO entries (date, description, amount, type) VALUES (?, ?, ?, ?)", (today.isoformat(), desc, amt, typ))
        self.conn.commit()
        self.load_entries()

if __name__ == '__main__':
    app_win = ttkb.Window(themename="superhero")
    app = DayBookApp(app_win)
    app_win.mainloop()
