import os

from telebot import types

# Stałe i konfiguracje
CHANNEL_USERNAME = "@podvalHimikov"
user_last_message = {}
user_subscription_status = {}
user_states = {}

def setup_handlers(bot):
    """
    Funkcja inicjalizująca handlery dla bota.
    """

    def is_subscribed(user_id):
        """Sprawdza, czy użytkownik jest subskrybentem kanału."""
        try:
            member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
            return member.status in ["member", "administrator", "creator"]
        except Exception:
            return False

    def delete_last_message(chat_id):
        """Usuwa ostatnią wiadomość wysłaną przez bota do użytkownika."""
        if chat_id in user_last_message:
            try:
                bot.delete_message(chat_id, user_last_message[chat_id])
            except Exception:
                pass

    def send_and_track_message(chat_id, text, reply_markup=None, parse_mode=None):
        """Wysyła wiadomość i zapisuje jej ID, aby później można było ją usunąć."""
        delete_last_message(chat_id)
        sent_message = bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
        user_last_message[chat_id] = sent_message.message_id

    def add_back_button(callback_data="back_to_main"):
        """Tworzy przycisk powrotu."""
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("⬅️ Назад", callback_data=callback_data)
        markup.add(back_button)
        return markup

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        """Obsługuje komendę /start."""
        if message.from_user.id in user_subscription_status and user_subscription_status[message.from_user.id]:
            show_main_menu(message)
        else:
            markup = types.InlineKeyboardMarkup()
            subscribe_button = types.InlineKeyboardButton("Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
            check_subscription_button = types.InlineKeyboardButton("Я подписался", callback_data="check_subscription")
            markup.add(subscribe_button, check_subscription_button)
            send_and_track_message(
                message.chat.id,
                "Привет дружище! Чтобы иметь доступ к тренировкам, ты должен подписаться на наших спонсоров.",
                reply_markup=markup
            )

    @bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
    def check_subscription(call):
        """Sprawdza status subskrypcji użytkownika."""
        if is_subscribed(call.from_user.id):
            user_subscription_status[call.from_user.id] = True
            bot.answer_callback_query(call.id, "Подписка подтверждена!", show_alert=True)
            show_main_menu(call.message)
        else:
            user_subscription_status[call.from_user.id] = False
            bot.answer_callback_query(call.id, "Вы еще не подписались!", show_alert=True)
            send_welcome(call.message)

    def show_main_menu(message):
        """Wyświetla menu główne."""
        if not is_subscribed(message.chat.id):
            user_subscription_status[message.chat.id] = False
            send_welcome(message)
            return

        user_subscription_status[message.chat.id] = True
        markup = types.InlineKeyboardMarkup()
        row1 = [
            types.InlineKeyboardButton("🏆️ Паурлифтинг и силовые", callback_data="Паурлифтинг и силовые")
        ]
        row2 = [
            types.InlineKeyboardButton("🎾 Рандомная тренировка", callback_data="Рандомная тренировка"),
            types.InlineKeyboardButton("🏋️‍♂️ Бодибилдинг", callback_data="Бодибилдинг")
        ]
        row3 = [
            types.InlineKeyboardButton("👤 Авторы", callback_data="Авторы"),
            types.InlineKeyboardButton("📖 Гайды", callback_data="Гайды")
        ]
        markup.row(*row1)
        markup.row(*row2)
        markup.row(*row3)
        send_and_track_message(
            message.chat.id,
            "⚡️ Добро пожаловать в бота, в котором вы можете получить тренировку для себя и не платить ни копейки!",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
    def back_to_main_menu(call):
        """Obsługuje powrót do menu głównego."""
        bot.answer_callback_query(call.id)
        show_main_menu(call.message)

    @bot.callback_query_handler(func=lambda call: call.data in [
        "Паурлифтинг и силовые", "Бодибилдинг", "Рандомная тренировка", "Авторы", "Гайды",
        "Начальный", "Средний", "Высокий", "Жимовые раскладки", "Мужчина", "Женщина",
        "Стаж_1", "Стаж_2", "Стаж_3"
    ])
    def handle_callback(call):
        """Obsługuje różne callbacki z menu."""
        if not is_subscribed(call.from_user.id):
            user_subscription_status[call.from_user.id] = False
            send_welcome(call.message)
            return

        elif call.data == "Бодибилдинг":
            bot.answer_callback_query(call.id)  # Potwierdzenie callbacka
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("👨 Мужчина", callback_data="Мужчина"),
                types.InlineKeyboardButton("👩 Женщина", callback_data="Женщина")
            )
            markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
            send_and_track_message(
                call.message.chat.id,
                "💪 Бодибилдинг\n\n[прочти инструкцию перед началом!](https://telegra.ph/Instrukciya-k-programmam-bb-11-01) — Выберите пол:",
                reply_markup=markup,
                parse_mode="Markdown"
            )

        # Obsługa wyboru płci, stażu i programu
        @bot.callback_query_handler(
            func=lambda call: call.data in ["Женщина", "Мужчина", "Стаж_1", "Стаж_2", "Стаж_3", "2x2", "3day"]
        )
        def handle_callback(call):
            user_id = call.message.chat.id
            user_states.setdefault(user_id, {})

            # Obsługa wyboru płci
            if call.data in ["Женщина", "Мужчина"]:
                user_states[user_id]["gender"] = call.data
                bot.answer_callback_query(call.id)
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("Стаж 0-6 мес", callback_data="Стаж_1"),
                    types.InlineKeyboardButton("Стаж 1-3 года", callback_data="Стаж_2"),
                    types.InlineKeyboardButton("Стаж 3+ лет", callback_data="Стаж_3")
                )
                markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
                bot.edit_message_text(
                    "Выберите ваш стаж тренировок:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )


            # Obsługa wyboru stażu
            elif call.data in ["Стаж_1", "Стаж_2", "Стаж_3"]:
                user_states[user_id]["stage"] = call.data
                bot.answer_callback_query(call.id)
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("2x2", callback_data="2x2"),
                    types.InlineKeyboardButton("3 дня", callback_data="3day"),
                )
                markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
                bot.edit_message_text(
                    "💪🏻 Бодибилдинг: \n\nВыберите график:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )


            # Obsługa wyboru programu
            elif call.data in ["2x2", "3day"]:
                user_states[user_id]["program"] = call.data
                bot.answer_callback_query(call.id)
                gender = user_states[user_id].get("gender")
                stage = user_states[user_id].get("stage")
                program = user_states[user_id].get("program")

                # Generowanie ścieżki pliku na podstawie wyborów użytkownika
                file_mapping = {
                    ("Мужчина", "Стаж_1", "2x2"): "workouts/Мужской начальный 2х2.xlsx",
                    ("Мужчина", "Стаж_1", "3day"): "workouts/Мужской начальный 3 дня.xlsx",
                    ("Женщина", "Стаж_1", "2x2"): "workouts/Женский начальный 2х2.xlsx",
                    ("Женщина", "Стаж_1", "3day"): "workouts/Женский начальный 3 дня.xlsx",

                    # Dodaj pozostałe kombinacje plików
                }

                file_path = file_mapping.get((gender, stage, program))

                if file_path:
                    with open(file_path, "rb") as file:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
                        bot.send_document(
                            call.message.chat.id,
                            file,
                            caption=f"Тренировка:\n\nПол: {gender}, Стаж: {stage}, Программа: {program}",
                            reply_markup=markup
                        )

        if call.data == "Авторы":
            bot.answer_callback_query(call.id)
            markup = types.InlineKeyboardMarkup()
            row1 = [
                types.InlineKeyboardButton("💙 Разработчик", url="https://t.me/podvalHimikov")
            ]
            row2 = [
                types.InlineKeyboardButton("💛 Владелец", url="https://t.me/podvalHimikov")
            ]
            markup.row(*row1)
            markup.row(*row2)
            markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
            send_and_track_message(
                call.message.chat.id,
                "ℹ️ Авторы \n\nВ данном разделе вы можете найти контакты тренеров, у которых можете приобрести индивидуальную программу тренеровок, а также контакт владельца бота.",
                reply_markup=markup
            )

            # Paurlifting
        elif call.data == "Паурлифтинг и силовые":
            bot.answer_callback_query(call.id)
            markup = types.InlineKeyboardMarkup()
            row1 = [
                types.InlineKeyboardButton("🟢 Начальный", callback_data="Начальный"),
                types.InlineKeyboardButton("🟡 Средний", callback_data="Средний")
            ]
            row2 = [
                types.InlineKeyboardButton("🔴 Высокий", callback_data="Высокий"),
                types.InlineKeyboardButton("📋 Жимовые раскладки", callback_data="Жимовые раскладки")
            ]
            markup.row(*row1)
            markup.row(*row2)
            markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
            send_and_track_message(
                call.message.chat.id,
                "🏋️‍♂️ Паурлифтинг и силовые\n\n— Обращаем внимание: программы начального и среднего уровня подходят для мужчин и женщин. Внутри файла каждой программы есть инструкция с уточнениями. Приятной тренировки!",
                reply_markup=markup
            )

        # Action in paurlifting
        elif call.data == "Начальный":
            with open("../workouts/Цикл начального уровня.xlsx", "rb") as file:
                markup = add_back_button()
                bot.send_document(call.message.chat.id, file, caption="Тренировка:\n\nУровень: 🟢 Начальный",
                                  reply_markup=markup)
        elif call.data == "Средний":
            with open("../workouts/Цикл на 4 дня для среднего уровня.xlsx", "rb") as file:
                markup = add_back_button()
                bot.send_document(call.message.chat.id, file, caption="Тренировка:\n\nУровень: 🟡 Средний",
                                  reply_markup=markup)
        elif call.data == "Высокий":
            with open("../workouts/Линейный цикл для продвинутых.xlsx", "rb") as file:
                markup = add_back_button()
                bot.send_document(call.message.chat.id, file, caption="Тренировка:\n\nУровень: 🔴 Высокий",
                                  reply_markup=markup)
        elif call.data == "Жимовые раскладки":
            with open("../workouts/bench_presses_article.docx", "rb") as file:
                markup = add_back_button()
                bot.send_document(call.message.chat.id, file, caption="Тренировка:\n\nУровень: Жимовые раскладки",
                                  reply_markup=markup)
        else:
            bot.send_message(
                call.message.chat.id,
                "Не удалось найти подходящую тренировку. Пожалуйста, проверьте ваш выбор."
            )

    # Obsługa przycisku "⬅️ Назад"
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
    def go_back_to_main(call):
        bot.answer_callback_query(call.id)
        bot.edit_message_text("Возвращаемся в главное меню.", call.message.chat.id, call.message.message_id)

    # Gajdy
    @bot.callback_query_handler(func=lambda call: call.data == "Гайды")
    def handle_guides(call):
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("📕 МАССОНОБОРНЫЙ ГАЙД", url="https://telegra.ph/Hh-06-01-10"))
        markup.row(
        types.InlineKeyboardButton("📗 ГАЙД НА РЕКОМПОЗИЦИЮ", url="https://telegra.ph/Rekompoziciya-sushka-12-09"))
        markup.row(types.InlineKeyboardButton("📘 ПРОГРЕСС – ЭТО НЕ СКУЧНО", url="https://telegra.ph/Progress---ehto-ne-skuchno-s-07-09"))
        markup.row(types.InlineKeyboardButton("📙 ИЗБЕГАЕМ ТРАВМЫ", url="https://telegra.ph/Testovyj-dokument-07-09"))
        markup.row(types.InlineKeyboardButton("📒 СПОРТПИТ", url="https://telegra.ph/Sport-pit-07-09"))
        markup.row(types.InlineKeyboardButton("📄 ГАЙД ПО УЛУЧШЕНИЮ ПИЩЕВАРЕНИЯ", callback_data="guide_digestion"))
        markup.row(types.InlineKeyboardButton("📓 ОБЩЕСТУПНАЯ РАЗМИНКА", callback_data="guide_warmup"))
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
        send_and_track_message(
            call.message.chat.id,
            "📚 Гайды\n\nВ данном разделе вы можете найти гайды по питанию/тренировкам и другие.",
            reply_markup=markup
        )

    # Obsługa gajdu "digestive_health_article"
    @bot.callback_query_handler(func=lambda call: call.data == "guide_digestion")
    def handle_guide_digestion(call):
        if os.path.exists("../workouts/digestive_health_article.docx"):
            with open("../workouts/digestive_health_article.docx", "rb") as file:
                markup = add_back_button()
                bot.send_document(call.message.chat.id, file, reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Plik nie został znaleziony.")

    # Obsługa gajdu "joint_warm_up"
    @bot.callback_query_handler(func=lambda call: call.data == "guide_warmup")
    def handle_guide_warmup(call):
        if os.path.exists("../workouts/joint_warm_up.mp4"):
            with open("../workouts/joint_warm_up.mp4", "rb") as file:
                markup = add_back_button()
                bot.send_document(call.message.chat.id, file, reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Plik nie został znaleziony.")

    # Random training
    @bot.callback_query_handler(func=lambda call: call.data == "Рандомная тренировка")
    def handle_random_training(call):
        bot.answer_callback_query(call.id)
        send_and_track_message(
            call.message.chat.id,
            "🎾 Soon...",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
            ),
            parse_mode="Markdown"
        )

    # Obsługa nieznanych danych
    @bot.callback_query_handler(func=lambda call: True)
    def handle_unknown_callback(call):
        print(f"Error: Unknown callback {call.data}")
