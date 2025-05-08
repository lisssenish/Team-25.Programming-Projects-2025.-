import telebot
from telebot import types
import pandas as pd
from io import BytesIO
import os
import re

# Загрузка данных из файла при запуске
if os.path.exists('users.csv'):
    names = pd.read_csv('users.csv')
else:
    names = pd.DataFrame(columns=['id', 'role', 'name', 'number'])

names=pd.DataFrame(columns=['id','role','name','number'])#создание DataFrame для хранения id
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
Команды:
/get_names- посмотреть список всех пользователей
/add_user - добавить пользователя
/remove_user - удалить пользователя
        """
        bot.send_message(message.chat.id, users_text)
    else:
        bot.send_message(message.chat.id, "⛔ Доступ запрещён! Требуются права администратора")

user_data = {}
def create_and_add_id(role, name):
    roles_index = {'Developer': 'T', 'Administrator': 'A', 'Manager': 'M', 'Shop': 'S'}  # Заглавные буквы
    k = roles_index[role]

    existing = names[names['role'] == role]
    if existing.empty:
        n = 1
    else:
        n = existing['number'].max() + 1

    numeric_part = str(n).zfill(5)
    new_id = f"{k}{numeric_part}"  # Теперь ID с заглавной буквы
    names.loc[len(names)] = [new_id, role, name, n]
    names.to_csv('users.csv', index=False)
    return new_id
def clean_user_data(chat_id):
    """Удаляем временные данные пользователя"""
    if chat_id in user_data:
        del user_data[chat_id]
@bot.message_handler(commands=['add_user'])
def handle_add_user(message):
    if user_roles.get(message.chat.id) == 'admin':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
        markup.add('Shop', 'Administrator', 'Manager')

        bot.send_message(message.chat.id, "🔽 Выберите роль из кнопок ниже:", reply_markup=markup)
        bot.register_next_step_handler(message, process_role_step)
    else:
        bot.send_message(message.chat.id, "⛔ Доступ запрещён! Требуются права администратора")


def process_role_step(message):
    chat_id = message.chat.id
    try:
        if message.content_type != 'text':
            raise ValueError("Некорректный тип сообщения")

        role_mapping = {
            'shop': 'Shop',
            'administrator': 'Administrator',
            'manager': 'Manager'
        }
        input_role = message.text.strip().lower()
        role_name = role_mapping.get(input_role)

        if not role_name:
            raise ValueError("Некорректная роль")

        user_data[chat_id] = {'role': role_name}
        bot.send_message(chat_id, "✏️ Введите название точки:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_location_step)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        clean_user_data(chat_id)  # Очистка только при ошибке
def process_location_step(message):
    chat_id = message.chat.id
    try:
        if message.content_type != 'text':
            raise ValueError("Название точки должно быть текстом")

        location = message.text.strip()
        if len(location) < 2:
            raise ValueError("Слишком короткое название точки")

        role_data = user_data.get(chat_id, {})
        role_name = role_data.get('role')

        unique_id = create_and_add_id(role_name, location)
        bot.send_message(chat_id, f"✅ Успешное создание!\n🏷 ID: {unique_id}\n📍 Точка: {location}")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
    finally:
        clean_user_data(chat_id)  # Всегда очищаем после обработки


@bot.message_handler(commands=['get_names'])
def send_names_excel(message):
    try:
        if user_roles.get(message.chat.id) != 'admin':
            bot.reply_to(message, "⛔ Требуются права администратора!")
            return

        if names.empty:
            bot.reply_to(message, "📭 База данных пуста")
            return

        output = BytesIO()

        # Используем правильный параметр sheet_name
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            names.to_excel(
                excel_writer=writer,
                sheet_name='Users',  # Правильное написание
                index=False
            )

        output.seek(0)
        bot.send_document(
            chat_id=message.chat.id,
            document=output,
            caption='📊 Полная база данных пользователей',
            visible_file_name='users_database.xlsx'
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при генерации файла: {str(e)}")
    finally:
        output.close() if 'output' in locals() else None


@bot.message_handler(commands=['remove_user'])
def handle_remove_user(message):
    if user_roles.get(message.chat.id) == 'admin':
        bot.send_message(
            message.chat.id,
            "✏️ Введите ID пользователя для удаления:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, process_remove_user)
    else:
        bot.send_message(message.chat.id, "⛔ Требуются права администратора!")


def process_remove_user(message):
    try:
        chat_id = message.chat.id
        raw_input = message.text.strip()
        user_id_to_remove = raw_input[0].upper() + raw_input[1:].lower()

        if not re.match(r'^[A-Za-z]\d{5}$', user_id_to_remove):
            raise ValueError("Неверный формат ID. Пример: A12345")

        # Поиск без учета регистра
        mask = names['id'].str.upper() == user_id_to_remove.upper()

        if not mask.any():
            raise ValueError("Пользователь с таким ID не найден")

        # Получаем ID перед удалением
        found_id = names.loc[mask, 'id'].values[0]

        # Удаляем запись
        names.drop(names[mask].index, inplace=True)
        names.to_csv('users.csv', index=False)

        # Используем сохраненный ID
        bot.send_message(chat_id, f"✅ Пользователь {found_id} удалён")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
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