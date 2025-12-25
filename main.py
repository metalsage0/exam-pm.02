import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "med_dispatch.db"


def init_db():
    """Инициализация базы данных и создание таблиц, если они не существуют."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT NOT NULL UNIQUE,
            car_class TEXT NOT NULL,
            is_busy INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            condition TEXT NOT NULL,
            addr_from TEXT NOT NULL,
            addr_to TEXT NOT NULL,
            vehicle_id INTEGER,
            status TEXT DEFAULT 'Новая',
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
        )
    """)

    conn.commit()
    conn.close()


class MedDispatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("МедДиспетчер v0.1")
        self.root.geometry("1000x600")

        init_db()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        self.tab_dispatch = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dispatch, text="Диспетчерская")

        self.tab_create = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_create, text="Создать заявку")

        self.tab_fleet = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_fleet, text="Управление автопарком")

        self.setup_create_tab()
        self.setup_fleet_tab()
        self.setup_dispatch_tab()

        self.refresh_all_data()

    def setup_create_tab(self):
        frame = ttk.Frame(self.tab_create, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Регистрация вызова", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10
        )

        ttk.Label(frame, text="ФИО Пациента:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_name = ttk.Entry(frame, width=40)
        self.entry_name.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Состояние:").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_condition = ttk.Combobox(
            frame,
            values=["Стабильное", "Средней тяжести", "Критическое"],
            state="readonly",
        )
        self.combo_condition.current(0)
        self.combo_condition.grid(row=2, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="Адрес подачи (Откуда):").grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.entry_from = ttk.Entry(frame, width=40)
        self.entry_from.grid(row=3, column=1, pady=5)

        ttk.Label(frame, text="Адрес назначения (Куда):").grid(
            row=4, column=0, sticky="w", pady=5
        )
        self.entry_to = ttk.Entry(frame, width=40)
        self.entry_to.grid(row=4, column=1, pady=5)

        btn_create = ttk.Button(
            frame, text="Создать заявку", command=self.create_request
        )
        btn_create.grid(row=5, column=0, columnspan=2, pady=20)

    def create_request(self):
        name = self.entry_name.get()
        condition = self.combo_condition.get()
        addr_from = self.entry_from.get()
        addr_to = self.entry_to.get()

        if not name or not addr_from or not addr_to:
            messagebox.showerror("Ошибка", "Заполните обязательные поля (ФИО, Адреса)!")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO requests (patient_name, condition, addr_from, addr_to, status)
            VALUES (?, ?, ?, ?, 'Новая')
        """,
            (name, condition, addr_from, addr_to),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Заявка успешно создана!")

        self.entry_name.delete(0, tk.END)
        self.entry_from.delete(0, tk.END)
        self.entry_to.delete(0, tk.END)

        self.refresh_all_data()

    def setup_fleet_tab(self):
        left_frame = ttk.Frame(self.tab_fleet, padding=10)
        left_frame.pack(side="left", fill="y")

        ttk.Label(left_frame, text="Добавить ТС", font=("Arial", 12, "bold")).pack(
            pady=10
        )

        ttk.Label(left_frame, text="Госномер:").pack(anchor="w")
        self.entry_plate = ttk.Entry(left_frame)
        self.entry_plate.pack(fill="x", pady=5)

        ttk.Label(left_frame, text="Класс:").pack(anchor="w")
        self.combo_class = ttk.Combobox(
            left_frame,
            values=["А (Линейная)", "B (Фельдшерская)", "C (Реанимобиль)"],
            state="readonly",
        )
        self.combo_class.current(0)
        self.combo_class.pack(fill="x", pady=5)

        ttk.Button(left_frame, text="Добавить машину", command=self.add_vehicle).pack(
            pady=20
        )

        right_frame = ttk.Frame(self.tab_fleet, padding=10)
        right_frame.pack(side="right", fill="both", expand=True)

        columns = ("id", "plate", "class", "status")
        self.tree_fleet = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.tree_fleet.heading("id", text="ID")
        self.tree_fleet.heading("plate", text="Госномер")
        self.tree_fleet.heading("class", text="Класс")
        self.tree_fleet.heading("status", text="Состояние")

        self.tree_fleet.column("id", width=30)
        self.tree_fleet.column("plate", width=100)
        self.tree_fleet.column("status", width=80)

        self.tree_fleet.pack(fill="both", expand=True)

    def add_vehicle(self):
        plate = self.entry_plate.get()
        car_class = self.combo_class.get()

        if not plate:
            messagebox.showerror("Ошибка", "Введите госномер!")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO vehicles (plate, car_class) VALUES (?, ?)",
                (plate, car_class),
            )
            conn.commit()
            messagebox.showinfo("Успех", f"Машина {plate} добавлена.")
            self.entry_plate.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Машина с таким номером уже существует!")
        finally:
            conn.close()
            self.refresh_all_data()

    def setup_dispatch_tab(self):
        top_frame = ttk.LabelFrame(
            self.tab_dispatch, text="Активные заявки (Ожидают или В пути)", padding=10
        )
        top_frame.pack(fill="both", expand=True, padx=10, pady=5)

        req_cols = ("id", "patient", "condition", "from", "to", "vehicle", "status")
        self.tree_requests = ttk.Treeview(
            top_frame, columns=req_cols, show="headings", height=8
        )
        self.tree_requests.heading("id", text="ID")
        self.tree_requests.heading("patient", text="Пациент")
        self.tree_requests.heading("condition", text="Состояние")
        self.tree_requests.heading("from", text="Откуда")
        self.tree_requests.heading("to", text="Куда")
        self.tree_requests.heading("vehicle", text="Назначено ТС (ID)")
        self.tree_requests.heading("status", text="Статус")

        self.tree_requests.column("id", width=30)
        self.tree_requests.column("vehicle", width=100)
        self.tree_requests.column("status", width=80)

        self.tree_requests.pack(side="left", fill="both", expand=True)

        scrollbar_req = ttk.Scrollbar(
            top_frame, orient="vertical", command=self.tree_requests.yview
        )
        scrollbar_req.pack(side="right", fill="y")
        self.tree_requests.configure(yscrollcommand=scrollbar_req.set)

        control_frame = ttk.Frame(self.tab_dispatch, padding=10)
        control_frame.pack(fill="x")

        ttk.Label(
            control_frame, text="Действия диспетчера:", font=("Arial", 10, "bold")
        ).pack(anchor="w")

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(
            btn_frame,
            text="НАЗНАЧИТЬ МАШИНУ (Выбрать заявку и свободное ТС ниже)",
            command=self.assign_vehicle,
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="ЗАВЕРШИТЬ РЕЙС (Выбрать заявку 'В пути')",
            command=self.finish_trip,
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame, text="Обновить таблицы", command=self.refresh_all_data
        ).pack(side="right", padx=5)

        bottom_frame = ttk.LabelFrame(
            self.tab_dispatch, text="Доступные машины (Свободные)", padding=10
        )
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)

        free_cols = ("id", "plate", "class", "status")
        self.tree_free_cars = ttk.Treeview(
            bottom_frame, columns=free_cols, show="headings", height=6
        )
        self.tree_free_cars.heading("id", text="ID")
        self.tree_free_cars.heading("plate", text="Госномер")
        self.tree_free_cars.heading("class", text="Класс")
        self.tree_free_cars.heading("status", text="Состояние")

        self.tree_free_cars.pack(side="left", fill="both", expand=True)

    def refresh_all_data(self):
        """Обновление данных во всех таблицах из БД"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        for row in self.tree_fleet.get_children():
            self.tree_fleet.delete(row)

        cursor.execute("SELECT id, plate, car_class, is_busy FROM vehicles")
        for row in cursor.fetchall():
            status_text = "ЗАНЯТА" if row[3] else "СВОБОДНА"
            self.tree_fleet.insert(
                "", "end", values=(row[0], row[1], row[2], status_text)
            )

        for row in self.tree_requests.get_children():
            self.tree_requests.delete(row)

        cursor.execute("""
            SELECT id, patient_name, condition, addr_from, addr_to, vehicle_id, status 
            FROM requests 
            WHERE status != 'Завершена'
        """)
        for row in cursor.fetchall():
            vh_id = row[5] if row[5] else "---"
            self.tree_requests.insert(
                "",
                "end",
                values=(row[0], row[1], row[2], row[3], row[4], vh_id, row[6]),
            )

        for row in self.tree_free_cars.get_children():
            self.tree_free_cars.delete(row)

        cursor.execute("SELECT id, plate, car_class FROM vehicles WHERE is_busy = 0")
        for row in cursor.fetchall():
            self.tree_free_cars.insert(
                "", "end", values=(row[0], row[1], row[2], "СВОБОДНА")
            )

        conn.close()

    def assign_vehicle(self):
        selected_req = self.tree_requests.selection()
        if not selected_req:
            messagebox.showwarning("Внимание", "Выберите заявку из списка!")
            return

        req_item = self.tree_requests.item(selected_req)
        req_id = req_item["values"][0]
        req_status = req_item["values"][6]

        if req_status != "Новая":
            messagebox.showerror(
                "Ошибка", "Машину можно назначить только на заявку со статусом 'Новая'."
            )
            return

        selected_car = self.tree_free_cars.selection()
        if not selected_car:
            messagebox.showwarning(
                "Внимание", "Выберите свободную машину из нижнего списка!"
            )
            return

        car_item = self.tree_free_cars.item(selected_car)
        car_id = car_item["values"][0]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE vehicles SET is_busy = 1 WHERE id = ?", (car_id,))
            cursor.execute(
                "UPDATE requests SET vehicle_id = ?, status = 'В пути' WHERE id = ?",
                (car_id, req_id),
            )
            conn.commit()
            messagebox.showinfo(
                "Назначение", f"Машина ID {car_id} назначена на заявку ID {req_id}."
            )
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            conn.close()
            self.refresh_all_data()

    def finish_trip(self):
        selected_req = self.tree_requests.selection()
        if not selected_req:
            messagebox.showwarning("Внимание", "Выберите заявку для завершения!")
            return

        req_item = self.tree_requests.item(selected_req)
        req_id = req_item["values"][0]
        req_status = req_item["values"][6]
        car_id_str = req_item["values"][5]

        if req_status != "В пути":
            messagebox.showerror(
                "Ошибка", "Завершить можно только заявку, которая находится 'В пути'."
            )
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE requests SET status = 'Завершена' WHERE id = ?", (req_id,)
            )

            if car_id_str != "---":
                cursor.execute(
                    "UPDATE vehicles SET is_busy = 0 WHERE id = ?", (car_id_str,)
                )

            conn.commit()
            messagebox.showinfo(
                "Завершение", f"Рейс по заявке ID {req_id} завершен. Машина свободна."
            )
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            conn.close()
            self.refresh_all_data()


if __name__ == "__main__":
    root = tk.Tk()
    app = MedDispatchApp(root)
    root.mainloop()
