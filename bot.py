import telebot
from telebot import types
#kdkkdkd
TOKEN = '7791429879:AAEgbCL8bFjQYnb81Rf1s2Hn_F5lRbZ3eKo'
bot = telebot.TeleBot(TOKEN)

# Словари для хранения состояний и ролей пользователей
user_states = {}
user_roles = {}  # Новый словарь для хранения ролей
shop_data = {}    # Словарь для временного хранения данных магазина


@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    welcome_text = """
Добро пожаловать в бота для автоматизации отчётов!
Этот бот умеет:
- Собирать информацию с точек
- Предоставлять отчёты
- Систематизировать информацию

Введите команду /id для начала работы
    """
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=['id'])
def ask_for_id(message):
    msg = bot.send_message(message.chat.id, "Введите ваш ID:")
    user_states[message.chat.id] = 'awaiting_id'
    bot.register_next_step_handler(msg, process_id)


def process_id(message):
    try:
        user_id = message.text.strip()

        if not user_id:
            raise ValueError("ID не может быть пустым")

        first_char = user_id[0].upper()

        if first_char == 'A':
            role = 'admin'
            response = "✅ Активирован режим администрирования\nДоступные команды:\n/stats - статистика\n/users - управление пользователями"
        elif first_char == 'S':
            role = 'shop'
            response = "✅ Режим магазина\nДоступные команды:\n/report - сдать отчёт"
        elif first_char == 'M':
            role = 'manager'
            response = "✅ Режим менеджера\nДоступные команды:\n/plan - установить план\n/statm - получить статистику"
        else:
            raise ValueError("ID должен начинаться с A, S или M")

        # Сохраняем роль пользователя
        user_roles[message.chat.id] = role
        bot.send_message(message.chat.id, response)

    except Exception as e:
        error_message = f"❌ Ошибка: {str(e)}"
        bot.send_message(message.chat.id, error_message)

    user_states.pop(message.chat.id, None)


# Функции для администратора
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    if user_roles.get(message.chat.id) == 'admin':
        stats_text = """
📊 Статистика системы:
- Всего пользователей: 143
- Активных магазинов: 67
- Выполнение плана: 82%
        """
        bot.send_message(message.chat.id, stats_text)
    else:
        bot.send_message(message.chat.id, "⛔ Доступ запрещён! Требуются права администратора")


@bot.message_handler(commands=['users'])
def handle_users(message):
    if user_roles.get(message.chat.id) == 'admin':
        users_text = """
👥 Управление пользователями:
1. Иванов Иван (A-123) - Админ
2. Петров Петр (S-456) - Магазин
3. Сидорова Мария (M-789) - Менеджер

Команды:
/add_user - добавить пользователя
/remove_user - удалить пользователя
        """
        bot.send_message(message.chat.id, users_text)
    else:
        bot.send_message(message.chat.id, "⛔ Доступ запрещён! Требуются права администратора")

user_data = {}
@bot.message_handler(commands=['add_user'])
def handle_add_user(message):
    if user_roles.get(message.chat.id) == 'admin':
        # Создаем клавиатуру для выбора роли
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True,
            resize_keyboard=True,
            row_width=2
        )
        markup.add('Shop', 'Administrator', 'Manager')

        bot.send_message(
            message.chat.id,
            "🔽 Выберите роль из кнопок ниже:",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_role_step)
    else:
        bot.send_message(
            message.chat.id,
            "⛔ Доступ запрещён! Требуются права администратора"
        )


def process_role_step(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Некорректный тип сообщения")

        chat_id = message.chat.id
        role = message.text.strip().lower()

        # Определяем префикс для ID
        role_prefix_mapping = {
            'shop': 's',
            'administrator': 'a',
            'manager': 'm'
        }
        role_prefix = role_prefix_mapping.get(role, 'x')

        # Сохраняем префикс
        user_data[chat_id] = {'role': role_prefix}

        # Убираем клавиатуру и запрашиваем текст
        bot.send_message(
            chat_id,
            "✏️ Введите название точки:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, process_location_step)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        clean_user_data(chat_id)


def process_location_step(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Название точки должно быть текстом")

        chat_id = message.chat.id
        location = message.text.strip()

        if len(location) < 2:
            raise ValueError("Слишком короткое название точки")

        # Получаем сохраненные данные
        role_data = user_data.get(chat_id, {})
        role_prefix = role_data.get('role', 'x')

        # Генерируем уникальный ID
        unique_id = generate_unique_id(role_prefix)

        bot.send_message(
            chat_id,
            f"✅ Успешное создание!\n"
            f"🏷 ID: {unique_id}\n"
            f"📍 Точка: {location}"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
    finally:
        clean_user_data(chat_id)


def clean_user_data(chat_id):
    if chat_id in user_data:
        del user_data[chat_id]


def generate_unique_id(prefix):
    # Генерация 4-значного числа с ведущими нулями
    random_part = f"{1111}"
    return f"{prefix}{random_part}"

#Функции менеджера
@bot.message_handler(commands=['plan'])
def handle_users(message):
    if user_roles.get(message.chat.id) == 'manager':
        users_text = """
Для того, чтобы установить план вводите размер плана
Далее, сверевшись с верностью введённых данных
Нажмите ДА✅
Иначе НЕТ⛔
Название точки прописывается автоматически
        """
        bot.send_message(message.chat.id, users_text)
    else:
        bot.send_message(message.chat.id, "⛔ Доступ запрещён! Требуются права менеджера")

@bot.message_handler(commands=['statm'])
def handle_users(message):
    if user_roles.get(message.chat.id) == 'manager':
        users_text = """
План магазина А: 87% 1009290202 из 10019189101
План магазина Б: 87% 10002 из 10019189101
        """
        bot.send_message(message.chat.id, users_text)
    else:
        bot.send_message(message.chat.id, "⛔ Доступ запрещён! Требуются права менеджера")

# Функции для магазина
@bot.message_handler(commands=['report'])
def handle_report(message):
    if user_roles.get(message.chat.id) == 'shop':
        shop_data[message.chat.id] = {
            'cash': None,
            'cashless': None,
            'collection': None,
            'balance': None
        }
        msg = bot.send_message(message.chat.id, "💰 Введите сумму прихода наличными:")
        bot.register_next_step_handler(msg, process_cash)
    else:
        bot.send_message(message.chat.id, "⛔ Эта команда доступна только для магазинов")


# Добавлены проверки на тип сообщения
def process_cash(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Некорректный формат данных")

        cash = float(message.text.strip())
        shop_data[message.chat.id]['cash'] = cash
        msg = bot.send_message(message.chat.id, "💳 Теперь введите сумму прихода безналичными:")
        bot.register_next_step_handler(msg, process_cashless)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        shop_data.pop(message.chat.id, None)


def process_cashless(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Некорректный формат данных")

        cashless = float(message.text.strip())
        shop_data[message.chat.id]['cashless'] = cashless
        msg = bot.send_message(message.chat.id, "🏦 Введите сумму инкассации:")
        bot.register_next_step_handler(msg, process_collection)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        shop_data.pop(message.chat.id, None)


def process_collection(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Некорректный формат данных")

        collection = float(message.text.strip())
        shop_data[message.chat.id]['collection'] = collection
        msg = bot.send_message(message.chat.id, "📊 Введите остаток в кассе на конец дня:")
        bot.register_next_step_handler(msg, process_balance)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        shop_data.pop(message.chat.id, None)


def process_balance(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Некорректный формат данных")

        balance = float(message.text.strip())
        shop_data[message.chat.id]['balance'] = balance

        report = f"""
📋 Отчет по магазину:

💰 Приход наличными: {shop_data[message.chat.id]['cash']} руб.
💳 Приход безналичными: {shop_data[message.chat.id]['cashless']} руб.
🏦 Инкассация: {shop_data[message.chat.id]['collection']} руб.
📊 Остаток в кассе: {shop_data[message.chat.id]['balance']} руб.

Приход: {shop_data[message.chat.id]['cash'] + shop_data[message.chat.id]['cashless']} руб.
Приход с остатком в кассе: {shop_data[message.chat.id]['cash'] + shop_data[message.chat.id]['cashless'] + shop_data[message.chat.id]['balance']} руб.
        """

        bot.send_message(message.chat.id, report)
        bot.send_message(message.chat.id, "✅ Отчет успешно сохранен!")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
    finally:
        shop_data.pop(message.chat.id, None)
if __name__ == '__main__':
    print('Бот запущен...')
    bot.infinity_polling()