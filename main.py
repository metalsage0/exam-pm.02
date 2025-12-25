import tkinter as tk
from tkinter import ttk, messagebox
import copy


class MedicalLogisticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MedLogistics")
        self.root.geometry("1000x750")
        self.root.configure(bg="#F0F2F5")

        self.setup_styles()

        header_frame = tk.Frame(root, bg="#0056b3", height=60)
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame,
            text="🏥 Система распределения медицинского транспорта",
            font=("Helvetica", 16, "bold"),
            bg="#0056b3",
            fg="white",
        ).pack(pady=15)

        settings_frame = tk.Frame(root, bg="white", bd=1, relief=tk.RIDGE)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            settings_frame,
            text="Кол-во станций (Источники):",
            bg="white",
            font=("Arial", 11),
        ).pack(side=tk.LEFT, padx=15, pady=15)
        self.spin_rows = ttk.Spinbox(
            settings_frame, from_=2, to=10, width=5, font=("Arial", 11)
        )
        self.spin_rows.set(3)
        self.spin_rows.pack(side=tk.LEFT, padx=5)

        tk.Label(
            settings_frame,
            text="Кол-во больниц (Потребители):",
            bg="white",
            font=("Arial", 11),
        ).pack(side=tk.LEFT, padx=15)
        self.spin_cols = ttk.Spinbox(
            settings_frame, from_=2, to=10, width=5, font=("Arial", 11)
        )
        self.spin_cols.set(4)
        self.spin_cols.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            settings_frame,
            text="⚡ Сгенерировать таблицу",
            style="Action.TButton",
            command=self.create_grid,
        ).pack(side=tk.LEFT, padx=30)

        self.input_container = tk.Frame(root, bg="#F0F2F5")
        self.input_container.pack(fill=tk.BOTH, expand=True, padx=20)

        self.canvas = tk.Canvas(
            self.input_container, bg="#F0F2F5", highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.input_container, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="#F0F2F5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        bottom_frame = tk.Frame(root, bg="white", height=100)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.calc_btn = tk.Button(
            bottom_frame,
            text="🚀 Рассчитать маршруты",
            font=("Arial", 12, "bold"),
            bg="#28a745",
            fg="white",
            activebackground="#218838",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED,
            command=self.calculate,
        )
        self.calc_btn.pack(pady=10)

        self.cost_entries = []
        self.supply_entries = []
        self.demand_entries = []
        self.matrix_widgets = []

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Action.TButton",
            font=("Arial", 10, "bold"),
            background="#007bff",
            foreground="white",
            borderwidth=0,
        )
        style.map("Action.TButton", background=[("active", "#0056b3")])

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            background="#dfe6e9",
            foreground="#2d3436",
        )
        style.configure("Treeview", font=("Arial", 10), rowheight=25)

    def create_grid(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.cost_entries = []
        self.supply_entries = []
        self.demand_entries = []

        try:
            rows = int(self.spin_rows.get())
            cols = int(self.spin_cols.get())
        except ValueError:
            return

        tk.Label(
            self.scrollable_frame,
            text="Откуда \\ Куда",
            bg="#F0F2F5",
            font=("Arial", 10, "bold"),
        ).grid(row=0, column=0, padx=5, pady=5)

        for c in range(cols):
            tk.Label(
                self.scrollable_frame,
                text=f"Больница {c + 1}",
                bg="#F0F2F5",
                font=("Arial", 10, "bold"),
                fg="#0056b3",
            ).grid(row=0, column=c + 1, padx=5, pady=5)

        tk.Label(
            self.scrollable_frame,
            text="ЗАПАСЫ",
            bg="#F0F2F5",
            font=("Arial", 10, "bold"),
            fg="#28a745",
        ).grid(row=0, column=cols + 1, padx=10, pady=5)

        for r in range(rows):
            tk.Label(
                self.scrollable_frame,
                text=f"Станция {r + 1}",
                bg="#F0F2F5",
                font=("Arial", 10, "bold"),
                fg="#d63031",
            ).grid(row=r + 1, column=0, padx=5, pady=5)

            current_row = []
            for c in range(cols):
                cell_frame = tk.Frame(
                    self.scrollable_frame, bg="white", bd=1, relief=tk.SOLID
                )
                cell_frame.grid(row=r + 1, column=c + 1, padx=2, pady=2, sticky="nsew")

                entry = tk.Entry(
                    cell_frame,
                    width=8,
                    justify="center",
                    font=("Arial", 11),
                    relief=tk.FLAT,
                )
                entry.pack(pady=2, padx=2)

                tk.Label(
                    cell_frame, text="тариф", bg="white", fg="gray", font=("Arial", 7)
                ).pack(side=tk.BOTTOM)

                current_row.append(entry)

            self.cost_entries.append(current_row)

            s_entry = tk.Entry(
                self.scrollable_frame,
                width=10,
                justify="center",
                font=("Arial", 11, "bold"),
                bg="#e8f5e9",
                relief=tk.GROOVE,
            )
            s_entry.grid(row=r + 1, column=cols + 1, padx=10, pady=5)
            self.supply_entries.append(s_entry)

        tk.Label(
            self.scrollable_frame,
            text="ПОТРЕБНОСТИ",
            bg="#F0F2F5",
            font=("Arial", 10, "bold"),
            fg="#d63031",
        ).grid(row=rows + 1, column=0, padx=5, pady=10)

        for c in range(cols):
            d_entry = tk.Entry(
                self.scrollable_frame,
                width=8,
                justify="center",
                font=("Arial", 11, "bold"),
                bg="#ffebee",
                relief=tk.GROOVE,
            )
            d_entry.grid(row=rows + 1, column=c + 1, padx=2, pady=10)
            self.demand_entries.append(d_entry)

        self.calc_btn.config(state=tk.NORMAL)

    def get_data(self):
        try:
            costs = [[int(e.get()) for e in row] for row in self.cost_entries]
            supply = [int(e.get()) for e in self.supply_entries]
            demand = [int(e.get()) for e in self.demand_entries]
            return costs, supply, demand
        except ValueError:
            return None, None, None

    def north_west_corner(self, supply, demand):
        rows, cols = len(supply), len(demand)
        allocation = [[0] * cols for _ in range(rows)]
        s = copy.deepcopy(supply)
        d = copy.deepcopy(demand)

        i, j = 0, 0
        while i < rows and j < cols:
            qty = min(s[i], d[j])
            allocation[i][j] = qty
            s[i] -= qty
            d[j] -= qty
            if s[i] == 0 and d[j] == 0:
                i += 1
                j += 1
            elif s[i] == 0:
                i += 1
            else:
                j += 1
        return allocation

    def calculate(self):
        costs, supply, demand = self.get_data()

        if costs is None:
            messagebox.showerror(
                "Ошибка ввода", "Пожалуйста, заполните все поля целыми числами."
            )
            return

        if sum(supply) != sum(demand):
            messagebox.showwarning(
                "Дисбаланс",
                f"Сумма запасов ({sum(supply)}) не равна сумме потребностей ({sum(demand)}). Результат может быть неточным.",
            )

        allocation = self.north_west_corner(supply, demand)

        total_cost = 0
        for r in range(len(allocation)):
            for c in range(len(allocation[0])):
                total_cost += allocation[r][c] * costs[r][c]

        self.show_results_window(allocation, costs, total_cost, supply, demand)

    def show_results_window(self, allocation, costs, total_cost, supply, demand):
        res_win = tk.Toplevel(self.root)
        res_win.title("Результаты расчета")
        res_win.geometry("800x500")
        res_win.configure(bg="white")

        tk.Label(
            res_win,
            text=f"Итоговая стоимость плана: {total_cost} у.е.",
            font=("Arial", 16, "bold"),
            fg="#28a745",
            bg="white",
        ).pack(pady=15)

        cols_header = ["Источник"] + [f"Больница {i + 1}" for i in range(len(demand))]

        tree = ttk.Treeview(res_win, columns=cols_header, show="headings", height=10)

        for col in cols_header:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        for r in range(len(allocation)):
            row_vals = [f"Станция {r + 1}"]
            for c in range(len(allocation[0])):
                val = allocation[r][c]
                if val > 0:
                    row_vals.append(f"{val} ед. (x{costs[r][c]})")
                else:
                    row_vals.append("-")
            tree.insert("", "end", values=row_vals)

        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        details_frame = tk.LabelFrame(
            res_win,
            text="Детализация маршрутов",
            bg="white",
            font=("Arial", 10, "bold"),
        )
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        txt = tk.Text(
            details_frame,
            height=8,
            font=("Courier New", 10),
            bg="#f8f9fa",
            relief=tk.FLAT,
        )
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        scr = ttk.Scrollbar(details_frame, command=txt.yview)
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        txt.config(yscrollcommand=scr.set)

        report = ""
        for r in range(len(allocation)):
            for c in range(len(allocation[0])):
                if allocation[r][c] > 0:
                    report += f"✅ Машина со [Станции {r + 1}] везет пациента в [Больницу {c + 1}]: {allocation[r][c]} ед.\n"
                    report += f"   Стоимость: {allocation[r][c]} * {costs[r][c]} = {allocation[r][c] * costs[r][c]}\n"

        txt.insert(tk.END, report)
        txt.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalLogisticsApp(root)
    root.mainloop()
