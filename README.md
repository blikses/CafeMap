CafeMap
=

### Авторы проекта: 

#### Федченко Мария Дмитриевна,

#### Семидьянова Ксения Сергеевна

> **Краткий функционал:**
> 
> Удобный и быстрый сервис для поиска эстетичных локаций, который экономит время пользователей и предоставляет актуальную информацию.

**Причины выбора темы:**

В наше время ежедневно возникает вопрос «Куда пойдем погулять?» Особенно важно, чтобы место было не только интересным, но и эстетически привлекательным. Обычно поиск таких мест занимает много времени: пользователи просматривают Instagram, Telegram или TikTok, затем проверяют расположение в картах. Это может занять от 30 минут до 1,5 часов. Наш сайт поможет сократить время поиска, предоставляя удобный каталог локаций с фильтрами по местоположению, типу места и другим параметрам.

**Основные функции сайта:**

1. Каталог локаций с фотографиями, названиями, адресами, ближайшими станциями метро, координатами на картах, типом места (улица, кофейня и др.) и описанием.

2. Поиск и фильтрация по параметрам:

- Ближайшее метро

- Тип локации (платная/бесплатная, улица, кафе и т.п.)

- Популярность

3. Интеграция с картами (Yandex Maps) для быстрого просмотра местоположения.

4. Добавление новых локаций пользователями (после модерации).

5. Промокоды для сотрудничающих заведений.

6. Личный кабинет пользователя для сохранения избранных мест.

**Дополнительные возможности:**

- Удобный и современный интерфейс с адаптивным дизайном.

- Уведомления о новых местах или акциях.

**Предполагаемые технологии:**

- Язык программирования: Python

- Фреймворк: Flask

- База данных: SQL, SQLite3

- API: REST для взаимодействия с фронтендом

- Yandex Maps API

- ORM: SQLAlchemy
  
- Хостинг

*Интерфейс:*

- Bootstrap для адаптивного дизайна

- Jinja2 для HTML-шаблонизации


**База данных:**

Будет включать несколько таблиц. Предположительно:

1. Локации (название, описание, адрес, метро, координаты, тип, фото и т.д.)
2. Пользователи (логин, почта, пароль, роль)
3. Промокоды и акции (если предусмотрены)

**Этапы разработки:**
1. Проектирование структуры БД и API.
2. Разработка сайта.
3. Создание frontend-интерфейса (шаблоны, адаптивность).
4. Интеграция с картами.
5. Развертывание на хостинге.
   
**Целевая аудитория:**
- Люди, ищущие красивые места для фотосессий и прогулок.
- Посетители кафе и заведений, желающие найти уютные места.
- Владельцы заведений, заинтересованные в продвижении.
