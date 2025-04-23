def msd_radix_sort(arr, radix=10):
    """
    Поразрядная сортировка (MSD - Most Significant Digit)
    :param arr: список элементов для сортировки
    :param radix: основание системы счисления (по умолчанию 10)
    :return: отсортированный список
    """
    if len(arr) <= 1:
        return arr

    # Находим максимальное число для определения количества разрядов
    max_val = max(arr)
    digit = 1
    while max_val // digit > 0:
        digit *= radix
    digit //= radix  # Возвращаемся к старшему разряду

    return _msd_radix_sort(arr, digit, radix)


def _msd_radix_sort(arr, digit, radix):
    if len(arr) <= 1 or digit == 0:
        return arr

    # Создаем корзины для каждой цифры
    buckets = [[] for _ in range(radix)]

    # Распределяем числа по корзинам в соответствии с текущим разрядом
    for num in arr:
        current_digit = (num // digit) % radix
        buckets[current_digit].append(num)

    # Рекурсивно сортируем каждую корзину со следующим разрядом
    result = []
    for bucket in buckets:
        if len(bucket) > 0:
            sorted_bucket = _msd_radix_sort(bucket, digit // radix, radix)
            result.extend(sorted_bucket)

    return result


def input_array():
    """
    Функция для ввода массива с клавиатуры
    :return: список чисел
    """
    print("Введите элементы массива через пробел:")
    try:
        arr = list(map(int, input().split()))
        return arr
    except ValueError:
        print("Ошибка: введите только целые числа!")
        return input_array()


def generate_random_array(size=10, min_val=0, max_val=100):
    """
    Генерация случайного массива
    :param size: размер массива
    :param min_val: минимальное значение
    :param max_val: максимальное значение
    :return: случайный массив
    """
    import random
    return [random.randint(min_val, max_val) for _ in range(size)]


def save_to_file(arr, filename="output.txt"):
    """
    Сохранение массива в файл
    :param arr: массив для сохранения
    :param filename: имя файла
    """
    with open(filename, 'w') as f:
        f.write(' '.join(map(str, arr)))
    print(f"Массив сохранен в файл {filename}")


def load_from_file(filename="input.txt"):
    """
    Загрузка массива из файла
    :param filename: имя файла
    :return: загруженный массив
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
            arr = list(map(int, content.split()))
            print(f"Массив загружен из файла {filename}")
            return arr
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
        return []
    except ValueError:
        print("Ошибка: файл должен содержать только целые числа!")
        return []


def main():
    print("Программа для поразрядной сортировки (MSD Radix Sort)")
    print("Выберите способ ввода данных:")
    print("1 - Ввод с клавиатуры")
    print("2 - Загрузка из файла")
    print("3 - Генерация случайного массива")
    print("4 - Завершение работы программы")

    choice = input("Ваш выбор (1/2/3/4): ")

    while choice != "4":
        if choice == '1':
            arr = input_array()
        elif choice == '2':
            filename = input("Введите имя файла (по умолчанию input.txt): ") or "input.txt"
            arr = load_from_file(filename)
            if not arr:
                return
        elif choice == '3':
            size = int(input("Введите размер массива (по умолчанию 10): ") or 10)
            min_val = int(input("Введите минимальное значение (по умолчанию 0): ") or 0)
            max_val = int(input("Введите максимальное значение (по умолчанию 100): ") or 100)
            arr = generate_random_array(size, min_val, max_val)
        else:
            print("Неверный выбор!")

        print("\nИсходный массив:")
        print(arr)

        # Сортируем массив
        sorted_arr = msd_radix_sort(arr)

        print("\nОтсортированный массив:")
        print(sorted_arr)

        # Сохранение результата
        save_choice = input("Хотите сохранить результат? (y/n): ").lower()
        if save_choice == 'y':
            filename = input("Введите имя файла (по умолчанию output.txt): ") or "output.txt"
            save_to_file(sorted_arr, filename)

        print("Выберите способ ввода данных:")
        print("1 - Ввод с клавиатуры")
        print("2 - Загрузка из файла")
        print("3 - Генерация случайного массива")
        print("4 - Завершение работы программы")

        choice = input("Ваш выбор (1/2/3/4): ")


if __name__ == "__main__":
    main()