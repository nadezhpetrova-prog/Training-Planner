import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "workouts.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("750x550")

        # Данные
        self.workouts = []
        self.load_data()

        # Виджеты ввода
        self.create_input_frame()

        # Таблица
        self.create_table()

        # Фильтры
        self.create_filter_frame()

        # Кнопки управления
        self.create_control_buttons()

        # Обновить таблицу
        self.refresh_table()

    def create_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Добавить тренировку", padx=10, pady=10)
        frame.pack(pady=10, padx=10, fill="x")

        # Дата
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w")
        self.date_entry = tk.Entry(frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Тип тренировки
        tk.Label(frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var, width=15,
                                       values=["Бег", "Плавание", "Велоспорт", "Силовая", "Йога"])
        self.type_combo.grid(row=0, column=3, padx=5)
        self.type_combo.set("Бег")

        # Длительность
        tk.Label(frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w", padx=(10,0))
        self.duration_entry = tk.Entry(frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5)

        # Кнопка добавить
        self.add_btn = tk.Button(frame, text="➕ Добавить тренировку", command=self.add_workout,
                                 bg="lightgreen")
        self.add_btn.grid(row=0, column=6, padx=10)

    def create_table(self):
        frame = tk.LabelFrame(self.root, text="Список тренировок", padx=10, pady=10)
        frame.pack(pady=5, padx=10, fill="both", expand=True)

        columns = ("id", "date", "type", "duration")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("type", width=150, anchor="center")
        self.tree.column("duration", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_filter_frame(self):
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        frame.pack(pady=5, padx=10, fill="x")

        tk.Label(frame, text="Фильтр по типу:").grid(row=0, column=0, sticky="w")
        self.filter_type_var = tk.StringVar(value="Все")
        self.filter_type_combo = ttk.Combobox(frame, textvariable=self.filter_type_var,
                                              values=["Все", "Бег", "Плавание", "Велоспорт", "Силовая", "Йога"],
                                              width=12)
        self.filter_type_combo.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.filter_date_entry = tk.Entry(frame, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5)

        self.apply_filter_btn = tk.Button(frame, text="🔍 Применить фильтр", command=self.refresh_table)
        self.apply_filter_btn.grid(row=0, column=4, padx=10)

        self.reset_filter_btn = tk.Button(frame, text="❌ Сбросить фильтры", command=self.reset_filters)
        self.reset_filter_btn.grid(row=0, column=5)

    def create_control_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        self.save_btn = tk.Button(frame, text="💾 Сохранить в JSON", command=self.save_data, bg="lightblue", width=15)
        self.save_btn.pack(side="left", padx=5)

        self.load_btn = tk.Button(frame, text="📂 Загрузить из JSON", command=self.load_data, bg="lightyellow", width=15)
        self.load_btn.pack(side="left", padx=5)

        self.delete_btn = tk.Button(frame, text="🗑 Удалить выбранное", command=self.delete_selected, bg="salmon", width=15)
        self.delete_btn.pack(side="left", padx=5)

    # ------------- Валидация -------------
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_str):
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False

    # ------------- Добавление -------------
    def add_workout(self):
        date = self.date_entry.get().strip()
        workout_type = self.type_var.get()
        duration = self.duration_entry.get().strip()

        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return

        duration_num = float(duration)
        new_id = max([w["id"] for w in self.workouts], default=0) + 1

        workout = {
            "id": new_id,
            "date": date,
            "type": workout_type,
            "duration": duration_num
        }
        self.workouts.append(workout)
        self.save_data()  # автосохранение
        self.refresh_table()

        # Очистка поля длительности
        self.duration_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Тренировка добавлена!")

    # ------------- Фильтрация и отображение -------------
    def refresh_table(self):
        # Очистить таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получить фильтры
        filter_type = self.filter_type_var.get()
        filter_date = self.filter_date_entry.get().strip()

        filtered = self.workouts[:]

        if filter_type != "Все":
            filtered = [w for w in filtered if w["type"] == filter_type]

        if filter_date:
            if self.validate_date(filter_date):
                filtered = [w for w in filtered if w["date"] == filter_date]
            else:
                if filter_date:
                    messagebox.showwarning("Предупреждение", "Неверный формат даты фильтра. Фильтр по дате не применён.")

        # Сортировка по дате
        filtered.sort(key=lambda x: x["date"])

        for w in filtered:
            self.tree.insert("", "end", values=(w["id"], w["date"], w["type"], w["duration"]))

    def reset_filters(self):
        self.filter_type_var.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.refresh_table()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите тренировку для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную тренировку?"):
            item = self.tree.item(selected[0])
            workout_id = item["values"][0]
            self.workouts = [w for w in self.workouts if w["id"] != workout_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Тренировка удалена!")

    # ------------- Работа с JSON -------------
    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.workouts, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.workouts = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.workouts = []
        else:
            self.workouts = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()