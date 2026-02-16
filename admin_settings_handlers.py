# Admin sozlamalari boshqarish

from telebot import types
from config import load_settings, save_settings, get_setting, set_setting
from admin_handlers import user_states


def show_settings_panel(user_id, bot):
    """Sozlamalar panelini ko'rsatish"""
    settings = load_settings()
    
    markup = types.InlineKeyboardMarkup()
    
    # Instagram URL
    instagram_text = settings.get("instagram_url", "To'ri atanmagan")[:30]
    markup.add(
        types.InlineKeyboardButton(
            f"📱 Instagram ({instagram_text}...)",
            callback_data="edit_instagram"
        )
    )
    
    # Karta raqami
    card_number = settings.get("card_number", "To'ri atanmagan")
    card_display = f"{card_number[:4]} XXXX XXXX {card_number[-4:]}"
    markup.add(
        types.InlineKeyboardButton(
            f"💳 Karta raqami ({card_display})",
            callback_data="edit_card_number"
        )
    )
    
    # Karta egasi
    card_owner = settings.get("card_owner", "To'ri atanmagan")
    markup.add(
        types.InlineKeyboardButton(
            f"👤 Karta egasi ({card_owner})",
            callback_data="edit_card_owner"
        )
    )
    
    # Baza kanal ID
    base_channel = settings.get("base_channel", "To'ri atanmagan")
    markup.add(
        types.InlineKeyboardButton(
            f"📢 Baza kanal ({base_channel})",
            callback_data="edit_base_channel"
        )
    )
    
    markup.add(
        types.InlineKeyboardButton(
            "❌ Yopish",
            callback_data="close_settings"
        )
    )
    
    bot.send_message(
        user_id,
        "⚙️ <b>Bot Sozlamalari</b>\n\n"
        "O'zgartirilgan sozlamalar avtomatik saqlanadi.",
        parse_mode="HTML",
        reply_markup=markup
    )


def start_edit_instagram(user_id, bot):
    """Instagram URL tahrirlashni boshlash"""
    user_states[user_id] = {"action": "editing_instagram"}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("❌ Bekor qilish")
    
    current_url = get_setting("instagram_url", "")
    
    bot.send_message(
        user_id,
        "📱 <b>Instagram URL'ni o'zgartirish</b>\n\n"
        f"Hozirgi:\n<code>{current_url}</code>\n\n"
        "Yangi URL'ni yuboring:",
        parse_mode="HTML",
        reply_markup=markup
    )


def edit_instagram_callback(user_id, url_text, bot):
    """Instagram URL tahrirlashni tasdiqlash"""
    from keyboards import admin_keyboard
    
    if url_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        url = url_text.strip()
        
        # URL validatsiyasi
        if not url.startswith(("http://", "https://")):
            bot.send_message(
                user_id,
                "❌ <b>Xatolik!</b>\n\nURL http:// yoki https:// bilan boshlashi kerak.",
                parse_mode="HTML"
            )
            return
        
        if set_setting("instagram_url", url):
            bot.send_message(
                user_id,
                f"✅ <b>Instagram URL o'zgartirildi!</b>\n\n"
                f"<code>{url}</code>",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            print(f"[OK] Instagram URL o'zgartirildi: {url}")
        else:
            raise Exception("Sagat ma'lumotlar bazasida xatolik")
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
    finally:
        user_states.pop(user_id, None)


def start_edit_card_number(user_id, bot):
    """Karta raqami tahrirlashni boshlash"""
    user_states[user_id] = {"action": "editing_card_number"}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("❌ Bekor qilish")
    
    current_card = get_setting("card_number", "")
    
    bot.send_message(
        user_id,
        "💳 <b>Karta raqamini o'zgartirish</b>\n\n"
        f"Hozirgi:\n<code>{current_card}</code>\n\n"
        "Yangi karta raqamini yuboring (16 ta raqam):",
        parse_mode="HTML",
        reply_markup=markup
    )


def edit_card_number_callback(user_id, card_text, bot):
    """Karta raqami tahrirlashni tasdiqlash"""
    from keyboards import admin_keyboard
    
    if card_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        card_number = card_text.replace(" ", "").replace("-", "")
        
        # Karta raqami validatsiyasi
        if not card_number.isdigit() or len(card_number) != 16:
            bot.send_message(
                user_id,
                "❌ <b>Xatolik!</b>\n\n"
                "Karta raqami 16 ta raqamdan iborat bo'lishi kerak.",
                parse_mode="HTML"
            )
            return
        
        # Formatlash: XXXX XXXX XXXX XXXX
        formatted_card = f"{card_number[0:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:16]}"
        
        if set_setting("card_number", formatted_card):
            bot.send_message(
                user_id,
                f"✅ <b>Karta raqami o'zgartirildi!</b>\n\n"
                f"<code>{formatted_card}</code>",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            print(f"[OK] Karta raqami o'zgartirildi: {formatted_card}")
        else:
            raise Exception("Ma'lumotlar bazasida xatolik")
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
    finally:
        user_states.pop(user_id, None)


def start_edit_base_channel(user_id, bot):
    """Baza kanal tahrirlashni boshlash"""
    user_states[user_id] = {"action": "editing_base_channel"}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("❌ Bekor qilish")
    
    current_channel = get_setting("base_channel", "noma'lum")
    
    bot.send_message(
        user_id,
        "📢 <b>Baza kanal ID'sini o'zgartirish</b>\n\n"
        f"Hozirgi:\n<code>{current_channel}</code>\n\n"
        "Yangi kanal ID'sini yuboring:\n\n"
        "Masalan: <code>-1003781268251</code>\n\n"
        "<b>⚠️ DIQQAT:</b> ID'ni to'g'ri kiriting, aks holda kinolar yuborilmaydi!",
        parse_mode="HTML",
        reply_markup=markup
    )


def edit_base_channel_callback(user_id, channel_text, bot):
    """Baza kanal tahrirlashni tasdiqlash"""
    from keyboards import admin_keyboard
    from database import load_data, save_data
    from config import MOVIES_FILE
    
    if channel_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        # ID'ni validatsiya qilish
        channel_id = int(channel_text.strip())
        
        # Yangi kanalga barcha kinolarni yuborish
        movies_db = load_data(MOVIES_FILE)
        
        if not isinstance(movies_db, list):
            movies_db = []
        
        sent_count = 0
        failed_count = 0
        
        for movie in movies_db:
            if isinstance(movie, dict) and movie.get("file_id"):
                try:
                    # Video'ni yangi kanalga yuborish
                    bot.send_video(
                        channel_id,
                        movie.get("file_id"),
                        caption=f"Kod: {movie.get('code')} | {movie.get('description', 'Tavsif yo\'q')}"[:1024]
                    )
                    sent_count += 1
                except Exception as forward_err:
                    print(f"[WARNING] Video yuborishda xatolik (Kod={movie.get('code')}): {str(forward_err)}")
                    failed_count += 1
        
        # Sozlamani saqlash
        if set_setting("base_channel", channel_id):
            # config.py'dagi BASE_CHANNEL'ni ham yangilash
            import config
            config.BASE_CHANNEL = channel_id
            
            bot.send_message(
                user_id,
                f"✅ <b>Baza kanal o'zgartirildi!</b>\n\n"
                f"📢 Kanal ID: <code>{channel_id}</code>\n"
                f"📹 Barcha kinolar yangi kanalga yuborildi:\n"
                f"   • Muvaffaqiyatli: {sent_count}\n"
                f"   • Xatolik: {failed_count}",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            print(f"[OK] Baza kanal o'zgartirildi: {channel_id} (Sent: {sent_count}, Failed: {failed_count})")
        else:
            raise Exception("Sozlamalarni saqlashda xatolik")
    except ValueError:
        bot.send_message(
            user_id,
            "❌ <b>Xatolik!</b>\n\n"
            "Kanal ID faqat raqam bo'lishi kerak.\n\n"
            "Masalan: <code>-1003781268251</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Baza kanal o'zgartirishda xatolik: {str(e)}")
    finally:
        user_states.pop(user_id, None)


def start_edit_card_owner(user_id, bot):
    """Karta egasi tahrirlashni boshlash"""
    user_states[user_id] = {"action": "editing_card_owner"}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("❌ Bekor qilish")
    
    current_owner = get_setting("card_owner", "")
    
    bot.send_message(
        user_id,
        "👤 <b>Karta egasining ismini o'zgartirish</b>\n\n"
        f"Hozirgi:\n<code>{current_owner}</code>\n\n"
        "Yangi ismni yuboring:",
        parse_mode="HTML",
        reply_markup=markup
    )


def edit_card_owner_callback(user_id, owner_text, bot):
    """Karta egasi tahrirlashni tasdiqlash"""
    from keyboards import admin_keyboard
    
    if owner_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        owner_name = owner_text.strip()
        
        # Ism validatsiyasi
        if len(owner_name) < 3 or len(owner_name) > 50:
            bot.send_message(
                user_id,
                "❌ <b>Xatolik!</b>\n\n"
                "Ism 3 ta eng kamida va 50 ta eng kop harf bo'lishi kerak.",
                parse_mode="HTML"
            )
            return
        
        if set_setting("card_owner", owner_name):
            bot.send_message(
                user_id,
                f"✅ <b>Karta egasi o'zgartirildi!</b>\n\n"
                f"<code>{owner_name}</code>",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            print(f"[OK] Karta egasi o'zgartirildi: {owner_name}")
        else:
            raise Exception("Ma'lumotlar bazasida xatolik")
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
    finally:
        user_states.pop(user_id, None)
