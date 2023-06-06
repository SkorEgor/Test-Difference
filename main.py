from data_and_processing import DataAndProcessing
from data_for_verification import TrueData
import pandas as pd


# Входной список, парсит по столбцам
def parser_all_data(string_list):
    frequency_list = list()
    gamma_list = list()

    skipping_first_line = True  # Пропускаем первую строку?

    for line in string_list:
        # Пропуск первой строки
        if skipping_first_line:
            skipping_first_line = False
            continue

        # Если звездочки, конец файла
        if line[0] == "*":
            break

        # Разделяем строку по пробелу в список
        row = line.split()

        frequency_list.append(float(row[1]))
        gamma_list.append(float(row[4]))

    return frequency_list, gamma_list


def read_and_parse(name_file):
    # Чтение данных
    with open(name_file) as f:
        lines_file_without_gas = f.readlines()  # Читаем по строчно, в список

    # Парс данных
    return parser_all_data(lines_file_without_gas)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # ПАРАМЕТРЫ ПРОГРАММЫ
    # Путь к файлу без газа
    file_name_without_gas = "../Detector - Difference/25empty.csv"
    # Путь к файлу с газом
    file_name_with_gas = "../Detector - Difference/25DMSO.csv"
    # Порог
    threshold_percentage = 40.

    # ПОЛЯ
    # Объект данных и обработки
    data_signals = DataAndProcessing()

    # Таблица статистики данных
    column_name = [
        "всего_верных_частот",
        "найденных_частот",
        "правильно_найденных",
        "неправильно_найденных"
    ]
    statistics_data = pd.DataFrame(columns=column_name)
    print(statistics_data)
    # АЛГОРИТМ РАБОТЫ
    # (1) ПОЛУЧЕНИЕ ДАННЫХ БЕЗ ВЕЩЕСТВА
    # (1.1) Чтение и парс данных
    frequency, gamma = read_and_parse(file_name_without_gas)
    # (1.2) Запись в класс обработки данных
    data_signals.data["frequency"] = pd.Series(frequency)
    data_signals.data["without_gas"] = pd.Series(gamma)

    # (2) ПОЛУЧЕНИЕ ДАННЫХ С ВЕЩЕСТВОМ
    # (2.1) Чтение и парс данных
    frequency, gamma = read_and_parse(file_name_with_gas)
    # (2.2) Запись в класс обработки данных
    data_signals.data["with_gas"] = pd.Series(gamma)

    for threshold in range(10, 100, 1):
        # (3) ОБРАБОТКА
        # ОБРАБОТКА
        data_signals.all_processing(
            difference_threshold=threshold
        )

        # (4) РЕЗУЛЬТАТ
        total_correct_rows = len(TrueData.data_exactly)
        total_found = 0  # всего найдено
        correct = 0  # правильные
        bad = 0  # не правильные
        disputable = 0  # спорные

        for f in data_signals.point_absorption_after_difference["frequency"]:
            if f in TrueData.data_exactly.values:
                correct += 1
            elif f in TrueData.data_disputable.values:
                disputable += 1
            else:
                bad += 1
            total_found += 1

        experiment_data = {
            "порог": threshold,
            "всего_верных_частот": total_correct_rows,
            "найденных_частот": total_found,
            "правильно_найденных": correct,
            "неправильно_найденных": bad,
            "спорные частоты": disputable,
            "прав/найден (A, %)": correct / total_found,
            "прав/всего_верных (B, %)": correct / total_correct_rows,
            "оптимум (A * B)": (correct / total_found) * (correct / total_correct_rows)
        }
        statistics_data = statistics_data._append(experiment_data, ignore_index=True)

    print(statistics_data.to_string())

    with pd.ExcelWriter('out_statistics/statistics_data.xlsx', mode='w') as writer:
        statistics_data.to_excel(writer, sheet_name='sheetName')
        header = statistics_data.columns.values.tolist()
        for index in range(0, len(header)):
            writer.sheets['sheetName'].set_column(index + 1, index + 1, len(header[index]) + 2)
