# RASA Proxy Server

Этот сервер работает как **посредник между RASA и пользовательскими клиентами**. Он позволяет:

- Регистрировать клиентов и их `client_url`
- Принимать сообщения от RASA
- Перенаправлять сообщения на URL, связанный с `user_id`

---

##  Запуск

### 1. Установка зависимостей

```bash
pip install fastapi uvicorn aiohttp sqlalchemy
```
2. Запуск сервера
```bash
uvicorn main:app --reload
```
После запуска сервер будет доступен по адресу:
```
http://127.0.0.1:8000
```
---  

### Структура проекта
```bash

rasa_proxy/
│
├── main.py           # Основная логика FastAPI
├── models.py         # Pydantic-схемы для валидации
├── database.py       # Настройки и модель базы данных
└── README.md         # Документация
```
---
### Основные переменные
|Переменная |	Где используется |	Описание |
|-----------|--------------------|-----------|
|user_id |	во всех моделях и БД |	Уникальный ID пользователя |
|client_url |	в регистрации и отправке |	URL, куда перенаправляется сообщение |
|message |	во входящих запросах |	Само сообщение, отправляемое пользователю |

---
### Эндпоинты

#### ``` POST /register ```

Регистрирует или обновляет клиента (user_id → client_url).

Вход (JSON):

```json
{
  "user_id": "123",
  "client_url": "https://user-app.com/webhook"
}
```
Ответ:

```json
{
  "status": "registered"
}
```

#### ```POST /rasa-webhook```

Принимает сообщение от RASA и перенаправляет его пользователю.

Вход (JSON):

```json
{
  "user_id": "123",
  "message": "Hello"
}
```
Поле client_url опционально:

Если указано — будет использовано напрямую

Если не указано — сервер найдёт его по user_id в базе

Выход:

```json
{
  "status": "delivered"
}
```
---
### База данных
Используется SQLite (clients.db) и SQLAlchemy ORM.

Таблица: clients
|Поле |	Тип |	Описание |
|-----|-----|---------|
|user_id |	TEXT |	Первичный ключ |
|client_url |	TEXT |	URL для перенаправления |

### Аутентификация / Ошибки

Аутентификация не используется
Ошибки доставки (повторы, очереди) не обрабатываются
Если user_id не найден в базе — возвращается 404

---
### Пример использования
Клиент регистрируется:

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "client_url": "http://localhost:9000/client-webhook"}'
RASA отправляет сообщение:
```

```bash
curl -X POST http://localhost:8000/rasa-webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "message": "Hi!"}'
```

Сообщение доставляется на client_url в виде:
```json
{
  "user_id": "123",
  "message": "Hi!"
}
```