
**sos_opros** - сайт, позволяющий создать и опубликовать опрос, а также видеть статистику по созданным опросам. Проходить опрос может любой человек, у которого есть ссылка него, создать опрос и смотреть по нему статистику может только авторизированный пользователь.

Возможные действия пользователя:
* Регистрация/авторизация (логин, пароль)
* Создание опроса авторизированным пользователем и получение ссылки на опрос
* Возможность посмотреть список созданных опросов (для авторизированных пользователей)
* Возможность посмотреть статистику по каждому опросу (для авторизированных пользователей)
* Прохождение опроса (для всех, у кого есть ссылка на опрос)

Стек технология: Python (Django, Plotly, Dash, pickle), SQLite (возможно PostgresSQL), HTML/CSS/JS 

1. **Создание опроса.** Авторизированный пользователь с помощью конструктора создает опрос. После того, как опрос создан, опрос попадает в базу данных с привязкой к id конкретного пользователя, пользователь получает ссылку на прохождение опроса. Опрос сохраняется в БД посредством сериализации или разбиением опроса на вопросов (сохраняем в таблицу вопросы с привязкой к id опроса и варианты ответов с привязкой к id вопроса).
2. **Прохождение опроса.** Пользователь проходит опрос, его результат сохраняется так же, как созданный опрос - посредством сериализации или разбивки по таблицам.
3. **Отображение статистики.** Авторизированный пользователь может посмотреть статистику ответом по каждому опросу, созданному им. Статистика отображается с использованием Plotly/Dash.

# Распределение ролей
### Инденбаум Илья
Фронтенд, создание конструктора опроса (на стороне пользователя), реализация передачи данных с бэкенда через шаблонизатор.
### Векшин Кирилл
Реализация отображения статистики по опросам с помощью Plotly/Dash, интеграция с Django.
### Либина Яна
Написание основной части сервиса на Django, развертка проекта на хостинге.
### Степин Сергей
Всё, что касается БД и хранения опросов, написание классов для опросов.

# Запуск
Из папки с manage.py
```bash
python manage.py runserver
```
