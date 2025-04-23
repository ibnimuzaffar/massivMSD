import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from main import msd_radix_sort


class ArraySorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MSD Radix Sort - GUI")
        self.root.geometry("900x650")  # Увеличим размер окна

        # Подключение к БД
        self.conn = sqlite3.connect('arrays.db')
        self.create_table()

        # Создание интерфейса
        self.create_widgets()

    def create_table(self):
        """Создание таблицы в БД с полем для отсортированного массива"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arrays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                array_data TEXT NOT NULL,
                sorted_array_data TEXT,
                is_sorted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основные фреймы
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="Ввод/Редактирование массива", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        db_frame = ttk.LabelFrame(main_frame, text="База данных", padding="10")
        db_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Элементы ввода
        ttk.Label(input_frame, text="Элементы массива (через пробел):").grid(row=0, column=0, sticky=tk.W)
        self.array_entry = ttk.Entry(input_frame, width=50)
        self.array_entry.grid(row=0, column=1, padx=5)

        ttk.Button(input_frame, text="Сортировать", command=self.sort_array).grid(row=1, column=0, pady=5, sticky=tk.W)
        ttk.Button(input_frame, text="Сохранить в БД", command=self.save_to_db).grid(row=1, column=1, pady=5,
                                                                                     sticky=tk.E)

        # Элементы работы с БД
        columns = ("id", "array_data", "sorted_array_data", "is_sorted", "created_at")
        self.tree = ttk.Treeview(db_frame, columns=columns, show="headings")

        # Настройка заголовков и ширины столбцов
        self.tree.heading("id", text="ID")
        self.tree.heading("array_data", text="Исходный массив")
        self.tree.heading("sorted_array_data", text="Отсортированный массив")
        self.tree.heading("is_sorted", text="Отсортирован?")
        self.tree.heading("created_at", text="Дата создания")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("array_data", width=200)
        self.tree.column("sorted_array_data", width=200)
        self.tree.column("is_sorted", width=100, anchor=tk.CENTER)
        self.tree.column("created_at", width=150, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Добавим вертикальную прокрутку
        scrollbar = ttk.Scrollbar(db_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(db_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Загрузить из БД", command=self.load_from_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить список", command=self.refresh_db_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить выбранное", command=self.delete_from_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Справка", command=self.show_help).pack(side=tk.RIGHT, padx=5)

        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM,
                                                                                                fill=tk.X)

        # Инициализация отображения данных
        self.refresh_db_view()

    def sort_array(self):
        """Сортировка введенного массива"""
        try:
            arr = list(map(int, self.array_entry.get().split()))
            sorted_arr = msd_radix_sort(arr)
            self.array_entry.delete(0, tk.END)
            self.array_entry.insert(0, ' '.join(map(str, sorted_arr)))
            self.status_var.set("Массив успешно отсортирован")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите только целые числа, разделенные пробелами!")
            self.status_var.set("Ошибка ввода данных")

    def save_to_db(self):
        """Сохранение массива в БД с автоматической сортировкой"""
        array_data = self.array_entry.get()
        if not array_data:
            messagebox.showwarning("Предупреждение", "Введите массив для сохранения!")
            return

        try:
            # Преобразуем в массив чисел
            arr = list(map(int, array_data.split()))

            # Сортируем массив
            sorted_arr = msd_radix_sort(arr)
            sorted_data = ' '.join(map(str, sorted_arr))

            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO arrays (array_data, sorted_array_data, is_sorted) VALUES (?, ?, ?)",
                (array_data, sorted_data, 1)  # Устанавливаем флаг is_sorted в 1
            )
            self.conn.commit()
            self.status_var.set(f"Массив сохранен в БД. ID: {cursor.lastrowid}")
            self.refresh_db_view()
        except ValueError:
            messagebox.showerror("Ошибка", "Массив должен содержать только целые числа!")
            self.status_var.set("Ошибка: неверный формат массива")

    def load_from_db(self):
        """Загрузка массива из БД в поле ввода"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите массив из списка!")
            return

        item = self.tree.item(selected_item[0])
        array_data = item['values'][1]  # Берем исходный массив
        self.array_entry.delete(0, tk.END)
        self.array_entry.insert(0, array_data)
        self.status_var.set(f"Массив ID {item['values'][0]} загружен")

    def edit_selected(self):
        """Редактирование выбранного массива"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите массив для редактирования!")
            return

        # Получаем текущие данные
        item = self.tree.item(selected_item[0])
        array_id = item['values'][0]
        current_data = self.array_entry.get()

        if not current_data:
            messagebox.showwarning("Предупреждение", "Введите новые данные массива!")
            return

        try:
            # Проверяем корректность ввода
            arr = list(map(int, current_data.split()))

            # Сортируем новый массив
            sorted_arr = msd_radix_sort(arr)
            sorted_data = ' '.join(map(str, sorted_arr))

            # Обновляем запись в БД
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE arrays SET array_data = ?, sorted_array_data = ?, is_sorted = 1 WHERE id = ?",
                (current_data, sorted_data, array_id)
            )
            self.conn.commit()

            self.status_var.set(f"Массив ID {array_id} успешно обновлен")
            self.refresh_db_view()

            # Очищаем поле ввода
            self.array_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Ошибка", "Массив должен содержать только целые числа!")
            self.status_var.set("Ошибка: неверный формат массива")

    def delete_from_db(self):
        """Удаление массива из БД"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите массив для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный массив из БД?"):
            item = self.tree.item(selected_item[0])
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM arrays WHERE id = ?", (item['values'][0],))
            self.conn.commit()
            self.status_var.set(f"Массив ID {item['values'][0]} удален")
            self.refresh_db_view()

    def refresh_db_view(self):
        """Обновление отображения данных из БД"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, array_data, sorted_array_data, is_sorted, created_at FROM arrays ORDER BY created_at DESC")

        for row in cursor.fetchall():
            # Форматируем данные для отображения
            original_data = row[1] if len(row[1]) <= 20 else row[1][:17] + "..."
            sorted_data = row[2] if row[2] and len(row[2]) <= 20 else (row[2][:17] + "..." if row[2] else "")
            is_sorted = "Да" if row[3] else "Нет"
            created_at = row[4].split('.')[0]  # Убираем миллисекунды

            self.tree.insert("", tk.END, values=(row[0], original_data, sorted_data, is_sorted, created_at))

    def show_help(self):
        """Отображение справки"""
        help_text = """MSD Radix Sort - GUI\n
        Инструкция:
        1. Введите массив целых чисел в поле ввода (через пробел)
        2. Нажмите 'Сортировать' для сортировки массива
        3. Нажмите 'Сохранить в БД' для сохранения текущего массива
           (массив будет автоматически отсортирован)
        4. Выберите массив из списка:
           - Нажмите 'Загрузить из БД' для редактирования
           - Нажмите 'Редактировать' для обновления выбранного массива
           - Нажмите 'Удалить выбранное' для удаления
        5. Используйте 'Обновить список' для актуализации данных

        В таблице отображаются:
        - Исходный массив
        - Отсортированный массив
        - Статус сортировки
        - Дата создания

        Статус операций отображается в нижней части окна."""
        messagebox.showinfo("Справка", help_text)

    def __del__(self):
        """Закрытие соединения с БД при завершении"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ArraySorterApp(root)
    root.mainloop()