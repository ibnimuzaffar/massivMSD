import sqlite3
import random
import time
from main import msd_radix_sort


class DatabaseTester:
    def __init__(self):
        self.conn = sqlite3.connect('arrays.db')
        self.cursor = self.conn.cursor()
        self.ensure_table_exists()

    def ensure_table_exists(self):
        """Проверяем существование таблицы и её структуру"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS arrays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                array_data TEXT NOT NULL,
                sorted_array_data TEXT,
                is_sorted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def generate_random_array(self):
        """Генерация случайного массива"""
        size = random.randint(5, 50)
        return [random.randint(0, 1000) for _ in range(size)]

    def insert_arrays(self, count):
        """Тест вставки массивов в БД"""
        start_time = time.time()
        success = True

        try:
            for _ in range(count):
                arr = self.generate_random_array()
                arr_str = ' '.join(map(str, arr))
                sorted_str = ' '.join(map(str, msd_radix_sort(arr)))

                self.cursor.execute(
                    "INSERT INTO arrays (array_data, sorted_array_data, is_sorted) VALUES (?, ?, ?)",
                    (arr_str, sorted_str, 1)
                )

            self.conn.commit()

            # Проверяем количество добавленных записей
            self.cursor.execute("SELECT COUNT(*) FROM arrays WHERE id > ?",
                                (self.get_last_id() - count,))
            actual_count = self.cursor.fetchone()[0]

            if actual_count != count:
                success = False

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            success = False
            self.conn.rollback()

        elapsed_time = time.time() - start_time
        return success, elapsed_time

    def get_last_id(self):
        """Получаем последний ID в таблице"""
        self.cursor.execute("SELECT MAX(id) FROM arrays")
        return self.cursor.fetchone()[0] or 0

    def test_insert_100(self):
        """Тест a: добавление 100 массивов"""
        print("\nТест a: Добавление 100 массивов")
        success, time_taken = self.insert_arrays(100)
        print(f"Результат: {'Успех' if success else 'Ошибка'}")
        print(f"Время выполнения: {time_taken:.4f} сек")
        return success, time_taken

    def test_insert_1000(self):
        """Тест b: добавление 1000 массивов"""
        print("\nТест b: Добавление 1000 массивов")
        success, time_taken = self.insert_arrays(1000)
        print(f"Результат: {'Успех' if success else 'Ошибка'}")
        print(f"Время выполнения: {time_taken:.4f} сек")
        return success, time_taken

    def test_insert_10000(self):
        """Тест c: добавление 10000 массивов"""
        print("\nТест c: Добавление 10000 массивов")
        success, time_taken = self.insert_arrays(10000)
        print(f"Результат: {'Успех' if success else 'Ошибка'}")
        print(f"Время выполнения: {time_taken:.4f} сек")
        return success, time_taken

    def test_load_and_sort(self, db_size=100, test_size=100):
        """Тест d: выгрузка и сортировка массивов"""
        print(f"\nТест d: Выгрузка и сортировка {test_size} массивов (БД={db_size})")

        # Подготовка тестовых данных
        self.prepare_test_data(db_size)

        start_time = time.time()
        success = True

        try:
            # Выбираем случайные ID для теста
            self.cursor.execute(f'''
                SELECT id FROM arrays 
                ORDER BY RANDOM() 
                LIMIT {test_size}
            ''')
            random_ids = [row[0] for row in self.cursor.fetchall()]

            total_time = 0
            processed = 0

            for array_id in random_ids:
                self.cursor.execute("SELECT array_data FROM arrays WHERE id = ?", (array_id,))
                arr_data = self.cursor.fetchone()[0]

                # Замер времени сортировки
                sort_start = time.time()
                arr = list(map(int, arr_data.split()))
                sorted_arr = msd_radix_sort(arr)
                sort_time = time.time() - sort_start

                total_time += sort_time
                processed += 1

                # Проверка правильности сортировки
                expected = ' '.join(map(str, sorted_arr))
                self.cursor.execute(
                    "SELECT sorted_array_data FROM arrays WHERE id = ?",
                    (array_id,)
                )
                actual = self.cursor.fetchone()[0]

                if expected != actual:
                    success = False
                    print(f"Ошибка сортировки для массива ID {array_id}")

            avg_time = total_time / processed if processed > 0 else 0
            elapsed_time = time.time() - start_time

            print(f"Результат: {'Успех' if success else 'Ошибка'}")
            print(f"Общее время: {elapsed_time:.4f} сек")
            print(f"Среднее время на массив: {avg_time:.6f} сек")

            return success, elapsed_time, avg_time

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return False, 0, 0

    def prepare_test_data(self, count):
        """Подготовка тестовых данных"""
        # Удаляем старые тестовые данные
        self.cursor.execute("DELETE FROM arrays")
        self.conn.commit()

        # Добавляем новые тестовые данные
        for _ in range(count):
            arr = self.generate_random_array()
            arr_str = ' '.join(map(str, arr))
            sorted_str = ' '.join(map(str, msd_radix_sort(arr)))

            self.cursor.execute(
                "INSERT INTO arrays (array_data, sorted_array_data, is_sorted) VALUES (?, ?, ?)",
                (arr_str, sorted_str, 1)
            )

        self.conn.commit()

    def test_clear_database(self, db_size=100):
        """Тест e: очистка базы данных"""
        print(f"\nТест e: Очистка БД ({db_size} записей)")

        # Подготовка тестовых данных
        self.prepare_test_data(db_size)

        start_time = time.time()
        success = True

        try:
            # Проверяем, что в БД есть данные
            self.cursor.execute("SELECT COUNT(*) FROM arrays")
            before_count = self.cursor.fetchone()[0]

            if before_count != db_size:
                print(f"Ошибка подготовки: ожидалось {db_size} записей, получено {before_count}")
                return False, 0

            # Очищаем БД
            self.cursor.execute("DELETE FROM arrays")
            self.conn.commit()

            # Проверяем результат
            self.cursor.execute("SELECT COUNT(*) FROM arrays")
            after_count = self.cursor.fetchone()[0]

            if after_count != 0:
                success = False

            elapsed_time = time.time() - start_time

            print(f"Результат: {'Успех' if success else 'Ошибка'}")
            print(f"Время выполнения: {elapsed_time:.4f} сек")

            return success, elapsed_time

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return False, 0

    def run_all_tests(self):
        """Запуск всех тестов"""
        print("=== Начало тестирования работы с БД ===")

        # Тесты вставки
        self.test_insert_100()
        self.test_insert_1000()
        self.test_insert_10000()

        # Тесты выгрузки и сортировки для разных размеров БД
        for size in [100, 1000, 10000]:
            self.test_load_and_sort(db_size=size, test_size=100)

        # Тесты очистки для разных размеров БД
        for size in [100, 1000, 10000]:
            self.test_clear_database(db_size=size)

        print("\n=== Тестирование завершено ===")

    def __del__(self):
        """Закрытие соединения с БД"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    tester = DatabaseTester()
    tester.run_all_tests()