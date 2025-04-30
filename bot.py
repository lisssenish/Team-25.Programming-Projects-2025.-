import telebot

TOKEN = '7791429879:AAEgbCL8bFjQYnb81Rf1s2Hn_F5lRbZ3eKo'
bot = telebot.TeleBot(TOKEN)

# Словари для хранения состояний и ролей пользователей
user_states = {}
user_roles = {}  # Новый словарь для хранения ролей


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
            response = "✅ Режим менеджера\nДоступные команды:\n/plan - поставить задачу"
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


if __name__ == '__main__':
    print('Бот запущен...')
    bot.infinity_polling()