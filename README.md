# FireFinance

**FireFinance** — это консольное приложение для анализа банковских транзакций из Excel-файлов. Проект генерирует JSON-данные для веб-страниц, формирует отчёты, очищает и нормализует данные, предоставляет инструменты поиска, фильтрации, отчётности, API-интеграции и многое другое.

---

## Возможности

* Импорт транзакций из Excel-файла, который можно получить путём экспорта из любого онлайн-банка
* Очистка данных, удаление дублей
* Генерация JSON для передачи сайтам-клиентам
* Формирование отчётов
* Аналитика топ транзакций, статистика, отчёты по категориям
* Работа с внешними API (валюты, акции)
* Гибкая архитектура и разделение бизнес-логики
* Логирование

---

## Установка

### Требования

* Python 3.10+
* pip / poetry
* Установленные зависимости из `pyproject.toml`

### Установка через Poetry

```bash
git clone https://github.com/yourusername/firefinance.git
cd firefinance
poetry install
```

### Запуск проекта

```bash
poetry run python firefinance/main.py
```

---

## Настройка

### Переменные окружения

Проект использует внешние API (например, Apilayer). Создайте `.env` файл:

```
APILAYER_KEY=your_api_key_here
MARKETSTACK_KEY=your_api_key_here
```

---

## Примеры использования

### 1. Импорт транзакций

```python
from src.utils import import_transactions_from_file

imported_transactions = import_transactions_from_file("data/example_operations.xlsx")
print(imported_transactions.head())
```

### 2. Получение топ-N транзакций

```python
from src.utils import get_top_transactions

top = get_top_transactions(imported_transactions, top_n=5)
print(top)
```

### 3. Генерация отчёта

```python
from src.reports import spending_by_category

spending_by_category(imported_transactions, "Переводы")
```

### 4. Получение курса валют

```python
from src.utils import get_currency_rates

rates = get_currency_rates("RUB", ["USD", "EUR"])
print(rates)
```

---

## Документация и ссылки

* Репозиторий: [https://github.com/firekissss/FireFinance](https://github.com/firekissss/FireFinance)
* API Apilayer: [https://apilayer.com/marketplace](https://apilayer.com/marketplace)
* API Marketstack: [https://marketstack.com](https://marketstack.com)

---

## Лицензия

Проект распространяется под лицензией **MIT License**.

Вы можете свободно использовать, изменять и распространять проект при указании авторства.
