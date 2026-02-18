import telebot
from telebot import types
from datetime import datetime, timedelta
import uuid

# Konfiguratsiya va ma'lumotlar
from config import *
from database import *
from utils import *
from keyboards import *
from admin_handlers import user_states, start_add_admin, add_admin_callback, start_delete_admin, delete_admin_callback, show_admins_list, show_pending_channels
from admin_settings_handlers import show_settings_panel, start_edit_instagram, edit_instagram_callback, start_edit_card_number, edit_card_number_callback, start_edit_card_owner, edit_card_owner_callback, start_edit_base_channel, edit_base_channel_callback
from premium_handlers import show_premium_users, remove_premium_user, start_manual_premium_add, manual_premium_user_id_callback, manual_premium_days_callback
from channel_handlers import start_add_channel, add_channel_link_callback, add_channel_name_callback, start_delete_channel, show_channels_list
from movie_handlers import start_upload_movie, get_movie_code_callback, get_movie_file_callback, get_movie_description_callback, send_movie_to_user, start_delete_movie, delete_movie_callback, start_add_movie_to_channel, add_movie_to_channel_callback, send_movie_to_channel_callback, show_movies_list
from broadcast_handlers import start_send_broadcast, handle_broadcast_message
from movie_handlers import start_upload_movie, get_movie_code_callback, get_movie_file_callback, get_movie_description_callback, send_movie_to_user, start_delete_movie, delete_movie_callback, start_add_movie_to_channel, add_movie_to_channel_callback, send_movie_to_channel_callback, show_movies_list

# Bot yaratish
bot = telebot.TeleBot(BOT_TOKEN)

# ==================== CONTENT PROTECTION ====================
@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'voice', 'video_note'], 
                     func=lambda message: message.forward_from or message.forward_from_chat)
def protect_content(message):
    """Forward himoyasi"""
    if not is_admin(message.from_user.id):
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(
            message.chat.id,
            "⚠️ Botdan kontent forward qilish taqiqlanğan!"
        )
        return

# ==================== START COMMAND ====================
@bot.message_handler(commands=['start'])
def start(message):
    """Bot ishga tushirish"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    save_user(user_id, username, first_name)
    
    # Inline mode orqali kelgan bo'lsa (ulashish)
    args = message.text.split()
    if len(args) > 1:
        movie_code = args[1].strip()
        if movie_code.isdigit():
            try:
                movies_db = load_data(MOVIES_FILE)
                movie_found = False
                if movies_db and isinstance(movies_db, list):
                    movie_found = any(m.get("code") == movie_code or str(m.get("code")) == movie_code for m in movies_db)
                
                if movie_found:
                    # Obuna tekshirish - MAJBURIY
                    if not is_admin(user_id) and not check_premium(user_id):
                        not_subscribed = check_subscription(user_id, bot)
                        if not_subscribed:
                            bot.send_message(
                                message.chat.id,
                                "<b>🔒 Kanallarga Obuna Bo'lish Majburiy!</b>\n\n"
                                "Kinoni ko'rish uchun avval quyidagi kanallarga obuna bo'ling:",
                                parse_mode="HTML",
                                reply_markup=subscription_keyboard(not_subscribed, bot)
                            )
                            return
                    
                    # Kinoni yuborish
                    send_movie_to_user(message.chat.id, movie_code, user_id, bot)
                    return
            except Exception as e:
                print(f"[ERROR] Start shaklida kino jo'natishda xatolik: {str(e)}")
    
    # Admin ekanligini tekshirish
    if is_admin(user_id):
        bot.send_message(
            message.chat.id,
            f"<b>Assalomu alaykum, {first_name}!</b>\n\n"
            f"🎬 Admin paneliga xush kelibsiz!\n\n"
            f"Kerakli amallarni tanlang:",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    # Premium tekshirish
    is_premium_user = check_premium(user_id)
    
    if is_premium_user:
        premium_db = load_data(PREMIUM_FILE)
        if str(user_id) in premium_db:
            try:
                expire_date = datetime.fromisoformat(premium_db[str(user_id)]['expire_date'])
                days_left = (expire_date - datetime.now()).days
                bot.send_message(
                    message.chat.id,
                    f"<b>Assalomu alaykum, {first_name}! ⭐️</b>\n\n"
                    f"🎬 <b>Premium foydalanuvchi sifatida xush kelibsiz!</b>\n\n"
                    f"📅 <b>Premium amal qiladi:</b> {expire_date.strftime('%d.%m.%Y')}\n"
                    f"⏳ <b>Qolgan kunlar:</b> {days_left} kun\n\n"
                    f"Kerakli kinoning kodini yozing.\n"
                    f"<b>Masalan: 54</b>",
                    parse_mode="HTML",
                    reply_markup=user_keyboard(is_premium=True)
                )
            except Exception as e:
                print(f"[ERROR] Premium tafsili yozishda xatolik: {str(e)}")
                bot.send_message(
                    message.chat.id,
                    f"<b>Assalomu alaykum, {first_name}! ⭐️</b>\n\n"
                    f"🎬 <b>Premium foydalanuvchi sifatida xush kelibsiz!</b>",
                    parse_mode="HTML",
                    reply_markup=user_keyboard(is_premium=True)
                )
        return
    
    # Obuna tekshirish - MAJBURIY hamma azo bo'lmasalar uchun
    not_subscribed = check_subscription(user_id, bot)
    
    if not_subscribed:
        bot.send_message(
            message.chat.id,
            f"<b>Assalomu alaykum, {first_name}!</b>\n\n"
            f"<b>🔒 Kanallarga Obuna Bo'lish Majburiy!</b>\n\n"
            f"Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling yoki ⭐️ Premium sotib oling:",
            parse_mode="HTML",
            reply_markup=subscription_keyboard(not_subscribed, bot)
        )
    else:
        bot.send_message(
            message.chat.id,
            f"<b>Assalomu alaykum, {first_name}!</b>\n\n"
            f"🎬 <b>Xush kelibsiz! Kerakli kinoning kodini yozing.</b>\n\n"
            f"<b>Masalan: 54</b>",
            parse_mode="HTML",
            reply_markup=user_keyboard()
        )

# ==================== INSTAGRAM ====================
@bot.message_handler(func=lambda message: message.text == "📱 Instagram")
def instagram_redirect(message):
    """Instagram'ga yo'naltirish"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="📱 Instagram'da biz",
        url=get_setting("instagram_url", INSTAGRAM_URL)
    ))
    bot.send_message(
        message.chat.id,
        "📱 Bizning Instagram sahifamiz:\n\n"
        "Yangiliklar, kinolar va ko'p narsalar!",
        reply_markup=markup
    )

# ==================== PREMIUM ====================
@bot.callback_query_handler(func=lambda call: call.data == "premium_info")
def premium_info(call):
    """Premium tariflar"""
    bot.edit_message_text(
        "⭐️ <b>Premium obuna</b>\n\n"
        "Premium a'zo bo'lsangiz:\n"
        "✅ Kanallarga obuna bo'lmasdan foydalanish\n"
        "✅ Cheklovsiz kino ko'rish\n"
        "✅ Tezkor xizmat\n\n"
        "💳 <b>Tariflar:</b>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=premium_tariffs_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff:"))
def select_tariff(call):
    """Tarif tanlash"""
    data = call.data.split(":")
    months = int(data[1])
    price = int(data[2])
    user_id = call.from_user.id
    
    user_states[user_id] = {
        "action": "waiting_payment",
        "months": months,
        "price": price
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text="✅ To'lov qildim",
            callback_data="payment_done"
        ),
        types.InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data="premium_info"
        )
    )
    
    bot.edit_message_text(
        f"💳 <b>To'lov ma'lumotlari</b>\n\n"
        f"📦 Tarif: {months} oy\n"
        f"💰 Narxi: {price:,} so'm\n\n"
        f"💳 Karta raqami:\n"
        f"<code>{get_setting('card_number', CARD_NUMBER)}</code>\n\n"
        f"👤 Karta egasi: {get_setting('card_owner', CARD_OWNER)}\n\n"
        f"⚠️ To'lovni amalga oshirgach, pastdagi tugmani bosing!",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "payment_done")
def payment_done(call):
    """To'lov tasdiqlanishi"""
    user_id = call.from_user.id
    
    if user_id not in user_states or user_states[user_id].get("action") != "waiting_payment":
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi!", show_alert=True)
        return
    
    user_states[user_id]["action"] = "waiting_screenshot"
    
    bot.edit_message_text(
        "📸 To'lov skrinshotini yuboring:\n\n"
        "⚠️ Skrinshotda:\n"
        "• To'lov summasi\n"
        "• Sana va vaqt\n"
        "• Karta raqami\n"
        "ko'rinishi shart!",
        call.message.chat.id,
        call.message.message_id
    )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    """Asosiy menyuga qaytish"""
    user_id = call.from_user.id
    not_subscribed = check_subscription(user_id, bot)
    
    if not_subscribed:
        bot.edit_message_text(
            "❗️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling yoki Premium sotib oling:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=subscription_keyboard(not_subscribed, bot)
        )
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['photo'], func=lambda message: 
                     message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "waiting_screenshot")
def receive_payment_screenshot(message):
    """To'lov skrinshotini qabul qilish"""
    user_id = message.from_user.id
    state = user_states[user_id]
    months = state["months"]
    price = state["price"]
    
    users_db = load_data(USERS_FILE)
    user_info = users_db.get(str(user_id), {}) if isinstance(users_db, dict) else {}
    username = user_info.get("username", "Yo'q")
    first_name = user_info.get("first_name", "Noma'lum")
    
    caption = (
        f"💳 <b>Yangi to'lov so'rovi</b>\n\n"
        f"👤 Ism: {first_name}\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"📱 Username: @{username if username != 'Yo\'q' else 'Yo\'q'}\n\n"
        f"📦 Tarif: {months} oy\n"
        f"💰 Summa: {price:,} so'm\n\n"
        f"📅 Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(
            text=f"✅ 1 oy",
            callback_data=f"approve:{user_id}:1"
        ),
        types.InlineKeyboardButton(
            text=f"✅ 3 oy",
            callback_data=f"approve:{user_id}:3"
        ),
        types.InlineKeyboardButton(
            text=f"✅ 12 oy",
            callback_data=f"approve:{user_id}:12"
        ),
        types.InlineKeyboardButton(
            text="❌ Rad etish",
            callback_data=f"reject:{user_id}"
        )
    )
    
    admins_db = load_data(ADMINS_FILE)
    for admin_id in admins_db:
        try:
            bot.send_photo(
                int(admin_id),
                message.photo[-1].file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=markup
            )
        except:
            pass
    
    bot.send_message(
        message.chat.id,
        "✅ To'lov skrinshotingiz qabul qilindi!\n\n"
        "⏳ Admin ko'rib chiqib, tez orada tasdiqlab beradi.\n\n"
        "📬 Javob kelishi bilan xabar beramiz."
    )
    
    user_states.pop(user_id, None)

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve:"))
def approve_premium(call):
    """Premium tasdiqlash"""
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!", show_alert=True)
        return
    
    data = call.data.split(":")
    user_id = int(data[1])
    months = int(data[2])
    
    expire_date = datetime.now() + timedelta(days=30 * months)
    
    premium_db = load_data(PREMIUM_FILE)
    premium_db[str(user_id)] = {
        "expire_date": expire_date.isoformat(),
        "months": months,
        "activated_by": call.from_user.id,
        "activated_at": datetime.now().isoformat()
    }
    save_data(PREMIUM_FILE, premium_db)
    
    try:
        bot.send_message(
            user_id,
            f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            f"⭐️ Premium faollashtirildi!\n"
            f"📦 Tarif: {months} oy\n"
            f"📅 Amal qiladi: {expire_date.strftime('%d.%m.%Y')}\n\n"
            f"🎬 Endi siz kanallarga obuna bo'lmasdan botdan foydalanishingiz mumkin!",
            parse_mode="HTML",
            reply_markup=user_keyboard(is_premium=True)
        )
    except:
        pass
    
    bot.edit_message_caption(
        caption=call.message.caption + f"\n\n✅ <b>Tasdiqlandi ({months} oy)</b>\n"
                f"👤 Admin: {call.from_user.first_name}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="HTML"
    )
    
    bot.answer_callback_query(call.id, f"✅ Premium faollashtirildi ({months} oy)!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject:"))
def reject_premium(call):
    """To'lovni rad etish"""
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!", show_alert=True)
        return
    
    user_id = int(call.data.split(":")[1])
    
    try:
        bot.send_message(
            user_id,
            "❌ <b>To'lovingiz rad etildi!</b>\n\n"
            "Iltimos, to'lov ma'lumotlarini tekshiring va qayta urinib ko'ring.\n\n"
            "Savol bo'lsa, admin bilan bog'laning.",
            parse_mode="HTML"
        )
    except:
        pass
    
    bot.edit_message_caption(
        caption=call.message.caption + f"\n\n❌ <b>Rad etildi</b>\n"
                f"👤 Admin: {call.from_user.first_name}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="HTML"
    )
    
    bot.answer_callback_query(call.id, "❌ Rad etildi!")

@bot.message_handler(func=lambda message: message.text == "⭐️ Premium status")
def premium_status(message):
    """Premium statusni ko'rsatish"""
    user_id = message.from_user.id
    
    if not check_premium(user_id):
        bot.send_message(
            message.chat.id,
            "❌ Sizda faol Premium obuna yo'q!",
            reply_markup=user_keyboard()
        )
        return
    
    premium_db = load_data(PREMIUM_FILE)
    if str(user_id) in premium_db:
        try:
            expire_date = datetime.fromisoformat(premium_db[str(user_id)]['expire_date'])
            days_left = (expire_date - datetime.now()).days
            
            bot.send_message(
                message.chat.id,
                f"⭐️ <b>Premium status</b>\n\n"
                f"✅ Faol\n"
                f"📅 Amal qiladi: {expire_date.strftime('%d.%m.%Y')}\n"
                f"⏳ Qolgan kunlar: {days_left} kun",
                parse_mode="HTML",
                reply_markup=user_keyboard(is_premium=True)
            )
        except:
            bot.send_message(
                message.chat.id,
                "❌ Premium haqida ma'lumot olishda xatolik!",
                reply_markup=user_keyboard()
            )

# ==================== ADMIN PANEL ====================
@bot.message_handler(func=lambda message: message.text == "⭐️ Premium a'zolar" and is_admin(message.from_user.id))
def premium_list(message):
    """Premium a'zolar ro'yxati"""
    show_premium_users(message.from_user.id, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_premium:"))
def remove_premium_callback(call):
    """Premium o'chirish callback"""
    premium_user_id = call.data.split(":")[1]
    remove_premium_user(call.from_user.id, premium_user_id, bot)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "close_premium_users")
def close_premium_users(call):
    """Premium panelini yopish"""
    from keyboards import admin_keyboard
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.from_user.id,
        "✅ <b>Premium panel yopildi</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "manual_premium_user_id")
def manual_premium_user_id(message):
    """Premium qo'shish - user ID qabul qilish"""
    manual_premium_user_id_callback(message.from_user.id, message.text, bot)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "manual_premium_days")
def manual_premium_days(message):
    """Premium qo'shish - kunlar sonini qabul qilish"""
    manual_premium_days_callback(message.from_user.id, message.text, bot)

@bot.message_handler(func=lambda message: message.text == "👤 Admin qo'shish" and is_admin(message.from_user.id))
def add_admin_start(message):
    """Admin qo'shishni boshlash"""
    start_add_admin(message.from_user.id, bot)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "adding_admin")
def add_admin_id(message):
    """Admin ID-ni qabul qilish"""
    add_admin_callback(message.from_user.id, message.text, bot)

@bot.message_handler(func=lambda message: message.text == "🗑 Admin o'chirish" and is_admin(message.from_user.id))
def delete_admin_start(message):
    """Admin o'chirishni boshlash"""
    start_delete_admin(message.from_user.id, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_admin:"))
def delete_admin_callback_handler(call):
    """Adminni o'chirish callback"""
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!", show_alert=True)
        return
    
    admin_id = int(call.data.split(":")[1])
    result = delete_admin_callback(admin_id, call.from_user.id, bot)
    
    if result:
        users_db = load_data(USERS_FILE)
        user_info = users_db.get(str(admin_id), {}) if isinstance(users_db, dict) else {}
        first_name = user_info.get("first_name", "Noma'lum")
        
        bot.edit_message_text(
            f"✅ Admin o'chirildi!\n\n"
            f"👤 {first_name} (ID: {admin_id})",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id, "✅ Admin o'chirildi!")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_delete_admin")
def cancel_delete_admin(call):
    """Admin o'chirishni bekor qilish"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")

@bot.message_handler(func=lambda message: message.text == "👥 Adminlar ro'yxati" and is_admin(message.from_user.id))
def admins_list_view(message):
    """Adminlar ro'yxati"""
    show_admins_list(message.from_user.id, bot)

# ==================== SETTINGS MANAGEMENT ====================
@bot.message_handler(func=lambda message: message.text == "⚙️ Sozlamalar" and is_admin(message.from_user.id))
def settings_panel(message):
    """Sozlamalar panelini ko'rsatish"""
    show_settings_panel(message.from_user.id, bot)

@bot.callback_query_handler(func=lambda call: call.data == "edit_instagram")
def edit_instagram(call):
    """Instagram URL tahrirlashni boshlash"""
    start_edit_instagram(call.from_user.id, bot)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "editing_instagram")
def edit_instagram_text(message):
    """Instagram URL tahrirlashni tasdiqlash"""
    edit_instagram_callback(message.from_user.id, message.text, bot)

@bot.callback_query_handler(func=lambda call: call.data == "edit_card_number")
def edit_card_number(call):
    """Karta raqami tahrirlashni boshlash"""
    start_edit_card_number(call.from_user.id, bot)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "editing_card_number")
def edit_card_number_text(message):
    """Karta raqami tahrirlashni tasdiqlash"""
    edit_card_number_callback(message.from_user.id, message.text, bot)

@bot.callback_query_handler(func=lambda call: call.data == "edit_card_owner")
def edit_card_owner(call):
    """Karta egasi tahrirlashni boshlash"""
    start_edit_card_owner(call.from_user.id, bot)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "editing_card_owner")
def edit_card_owner_text(message):
    """Karta egasi tahrirlashni tasdiqlash"""
    edit_card_owner_callback(message.from_user.id, message.text, bot)

@bot.callback_query_handler(func=lambda call: call.data == "edit_base_channel")
def edit_base_channel_callback_handler(call):
    """Baza kanal tahrirlashni boshlash"""
    start_edit_base_channel(call.from_user.id, bot)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "editing_base_channel")
def edit_base_channel_text(message):
    """Baza kanal tahrirlashni tasdiqlash"""
    edit_base_channel_callback(message.from_user.id, message.text, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_movie_channel:"))
def add_movie_channel_callback_handler(call):
    """Kanalga kino qo'shishda kanal tanlash"""
    channel_id = call.data.split(":")[1]
    add_movie_to_channel_callback(call.from_user.id, channel_id, bot)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_add_movie_channel")
def cancel_add_movie_channel(call):
    """Kino kanalga qo'shimni bekor qilish"""
    from keyboards import admin_keyboard
    user_states.pop(call.from_user.id, None)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.from_user.id,
        "❌ <b>Amal bekor qilindi</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "close_settings")
def close_settings(call):
    """Sozlamalar panelini yopish"""
    from keyboards import admin_keyboard
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.from_user.id,
        "✅ <b>Sozlamalar paneli yopildi</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )

# ==================== CHANNEL MANAGEMENT ====================
@bot.message_handler(func=lambda message: message.text == "➕ Kanal qo'shish" and is_admin(message.from_user.id))
def add_channel_start(message):
    """Kanal qo'shishni boshlash"""
    start_add_channel(message.from_user.id, bot)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "adding_channel_link")
def add_channel_link(message):
    """Kanal silkasini qabul qilish"""
    add_channel_link_callback(message.from_user.id, message.text, bot)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "adding_public_channel_name")
def add_public_channel_name(message):
    """Ochiq kanal nomini qabul qilish"""
    add_channel_name_callback(message.from_user.id, message.text, bot, is_private=False)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "adding_private_channel")
def add_private_channel_name(message):
    """Mahfiy kanal nomini qabul qilish"""
    add_channel_name_callback(message.from_user.id, message.text, bot, is_private=True)

@bot.message_handler(func=lambda message: message.text == "➖ Kanal o'chirish" and is_admin(message.from_user.id))
def delete_channel_start(message):
    """Kanal o'chirishni boshlash"""
    start_delete_channel(message.from_user.id, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_channel:"))
def delete_channel_callback_handler(call):
    """Kanalni o'chirish"""
    from channel_handlers import delete_channel_callback as delete_handler
    channel_id = call.data.split(":")[1]
    channel_data = delete_handler(channel_id, bot)
    
    if channel_data:
        bot.edit_message_text(
            f"✅ {channel_data['name']} ({channel_data.get('title', 'Mahfiy')}) kanali o'chirildi!",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id, "✅ Kanal o'chirildi!")
    else:
        bot.answer_callback_query(call.id, "❌ Kanal topilmadi!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_delete_channel")
def cancel_delete_channel(call):
    """Kanal o'chirishni bekor qilish"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")

@bot.message_handler(func=lambda message: message.text == "📋 Kanallar ro'yxati" and is_admin(message.from_user.id))
def channels_list(message):
    """Kanallar ro'yxati"""
    show_channels_list(message.from_user.id, bot)

@bot.message_handler(func=lambda message: message.text == "🎞️ Kinolar ro'yxati" and is_admin(message.from_user.id))
def movies_list(message):
    """Kinolar ro'yxati"""
    show_movies_list(message.from_user.id, bot)

# Kanal tasdiqlash callbacklari
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_channel:"))
def approve_channel_callback(call):
    """Kanalni tasdiqlash"""
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Faqat adminlar qila oladi!", show_alert=True)
        return
    
    request_id = call.data.split(":")[1]
    channel_data = get_pending_channel(request_id)
    
    if channel_data:
        # Kanalni tasdiqlash (approve_pending_channel hamma narsani o'z ichiga oladi)
        result = approve_pending_channel(request_id)
        
        if result:
            try:
                requesting_user_id = channel_data.get("requested_by")
                bot.send_message(
                    requesting_user_id,
                    f"✅ <b>Kanal tasdiqlandi!</b>\n\n"
                    f"📝 <b>Kanal nomi:</b> {channel_data['name']}\n"
                    f"🔗 <b>Link:</b> {channel_data['invite_link']}\n\n"
                    f"🎉 Kanal majburiy obuna ro'yxatiga muvaffaqiyatli qo'shildi!",
                    parse_mode="HTML"
                )
            except Exception as msg_error:
                print(f"[WARNING] Foydalanuvchiga xabar yuborishda xatolik: {str(msg_error)}")
            
            bot.edit_message_text(
                f"✅ <b>KANAL TASDIQLANDI!</b>\n\n"
                f"📝 <b>Nomi:</b> {channel_data['name']}\n"
                f"🔗 <b>Link:</b> {channel_data['invite_link']}\n"
                f"🔒 <b>Tur:</b> {'Mahfiy' if channel_data.get('is_private') else 'Ochiq'}\n\n"
                f"👤 <b>Tasdiqladi:</b> {call.from_user.first_name}",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
            
            bot.answer_callback_query(call.id, "✅ Kanal muvaffaqiyatli tasdiqlandi!")
            print(f"[OK] Kanal tasdiqlandi: {request_id}")
        else:
            bot.answer_callback_query(call.id, "❌ Tasdiqlashda xatolik yuz berdi!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ Kanal topilmadi!", show_alert=True)
        print(f"[ERROR] Kanal topilmadi: {request_id}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_channel:"))
def reject_channel_callback(call):
    """Kanalni rad etish"""
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Faqat adminlar qila oladi!", show_alert=True)
        return
    
    request_id = call.data.split(":")[1]
    channel_data = get_pending_channel(request_id)
    
    if channel_data:
        # Kanalni rad etish
        result = reject_pending_channel(request_id)
        
        if result:
            try:
                requesting_user_id = channel_data.get("requested_by")
                bot.send_message(
                    requesting_user_id,
                    f"❌ <b>Kanal so'rovi rad etildi!</b>\n\n"
                    f"📝 <b>Kanal nomi:</b> {channel_data['name']}\n"
                    f"🔗 <b>Link:</b> {channel_data['invite_link']}\n\n"
                    f"⚠️ Iltimos, keyin qayta urinib ko'ring yoki admin bilan bog'laning.",
                    parse_mode="HTML"
                )
            except Exception as msg_error:
                print(f"[WARNING] Foydalanuvchiga xabar yuborishda xatolik: {str(msg_error)}")
            
            bot.edit_message_text(
                f"❌ <b>KANAL RAD ETILDI!</b>\n\n"
                f"📝 <b>Nomi:</b> {channel_data['name']}\n"
                f"🔗 <b>Link:</b> {channel_data['invite_link']}\n"
                f"🔒 <b>Tur:</b> {'Mahfiy' if channel_data.get('is_private') else 'Ochiq'}\n\n"
                f"👤 <b>Rad etdi:</b> {call.from_user.first_name}",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
            
            bot.answer_callback_query(call.id, "❌ Kanal rad etildi!")
            print(f"[OK] Kanal rad etildi: {request_id}")
        else:
            bot.answer_callback_query(call.id, "❌ Radda xatolik yuz berdi!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ Kanal topilmadi!", show_alert=True)
        print(f"[ERROR] Kanal topilmadi: {request_id}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_pending:"))
def view_pending_channel(call):
    """Tasdiqlanmagan kanalni ko'rish"""
    request_id = call.data.split(":")[1]
    channel_data = get_pending_channel(request_id)
    
    if channel_data:
        users_db = load_data(USERS_FILE)
        requesting_user_id = channel_data.get("requested_by")
        requesting_user = users_db.get(str(requesting_user_id), {}) if isinstance(users_db, dict) else {}
        first_name = requesting_user.get("first_name", "Noma'lum")
        
        text = (
            f"📝 <b>Kanal tafsili</b>\n\n"
            f"📝 Nomi: {channel_data['name']}\n"
            f"🔗 Link: {channel_data['invite_link']}\n"
            f"🔒 Tur: Mahfiy kanal\n\n"
            f"👤 So'rov yuborgan: {first_name}\n"
            f"📅 Vaqti: {channel_data.get('requested_at', 'Noma\'lum')}"
        )
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"approve_channel:{request_id}"
            ),
            types.InlineKeyboardButton(
                text="❌ Rad etish",
                callback_data=f"reject_channel:{request_id}"
            )
        )
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=markup
        )

# ==================== MOVIE MANAGEMENT ====================
@bot.message_handler(func=lambda message: message.text == "🎬 Kino yuklash" and is_admin(message.from_user.id))
def upload_movie_start(message):
    """Kino yuklashni boshlash"""
    start_upload_movie(message.from_user.id, bot)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "waiting_code")
def get_movie_code(message):
    """Kino kodini qabul qilish"""
    get_movie_code_callback(message.from_user.id, message.text, bot)

@bot.message_handler(content_types=['video'], func=lambda message: 
                     message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "waiting_movie")
def get_movie_file(message):
    """Kino videosini qabul qilish"""
    from config import get_base_channel
    get_movie_file_callback(message.from_user.id, message, bot, get_base_channel())

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "waiting_description")
def get_movie_description(message):
    """Kino tavsifini qabul qilish"""
    get_movie_description_callback(message.from_user.id, message.text, bot)

@bot.message_handler(func=lambda message: message.text == "🗑 Kinoni o'chirish" and is_admin(message.from_user.id))
def delete_movie_start(message):
    """Kino o'chirishni boshlash"""
    start_delete_movie(message.from_user.id, bot)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "deleting_movie")
def delete_movie(message):
    """Kinoni o'chirish"""
    delete_movie_callback(message.from_user.id, message.text, bot)

@bot.message_handler(func=lambda message: message.text == "🎬➡️ Kinoni kanalga" and is_admin(message.from_user.id))
def add_movie_to_channel_start(message):
    """Kinoni kanalga qo'shimni boshlash"""
    start_add_movie_to_channel(message.from_user.id, bot)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "selecting_movie_for_channel")
def send_movie_to_channel(message):
    """Kinoni kanalga yuborish"""
    send_movie_to_channel_callback(message.from_user.id, message.text, bot)

# ==================== LIKE SYSTEM ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("like:"))
def like_callback(call):
    """Like callback"""
    movie_code = call.data.split(":")[1]
    user_id = call.from_user.id
    
    liked, likes_count = toggle_like(movie_code, user_id)
    
    # Tugmalarni yangilash
    try:
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=movie_keyboard(movie_code, user_id)
        )
    except:
        pass
    
    if liked:
        bot.answer_callback_query(call.id, "❤️ Yoqdi!")
    else:
        bot.answer_callback_query(call.id, "Yoqmadi")

# ==================== CHECK SUBSCRIPTION ====================
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_sub_callback(call):
    """Obunalik tekshirish"""
    user_id = call.from_user.id
    
    try:
        is_user_admin = is_admin(user_id)
        is_user_premium = check_premium(user_id)
        
        if is_user_admin or is_user_premium:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
            if is_user_admin:
                bot.send_message(
                    call.message.chat.id,
                    f"Assalomu alaykum!\n\n🎬 Admin paneliga xush kelibsiz!",
                    reply_markup=admin_keyboard()
                )
                bot.answer_callback_query(call.id, "✅ Admin sifatida kirdingiz!")
            else:
                premium_db = load_data(PREMIUM_FILE)
                if str(user_id) in premium_db:
                    expire_date = datetime.fromisoformat(premium_db[str(user_id)]['expire_date'])
                    bot.send_message(
                        call.message.chat.id,
                        f"⭐️ <b>Premium foydalanuvchi!</b>\n\n"
                        f"📅 Amal qiladi: <b>{expire_date.strftime('%d.%m.%Y')}</b>\n\n"
                        f"🎬 Kerakli kinoning kodini yozing.\n\n"
                        f"Masalan: 54",
                        parse_mode="HTML",
                        reply_markup=user_keyboard(is_premium=True)
                    )
                    bot.answer_callback_query(call.id, "✅ Premium tasdiqlandi!")
            return
        
        # Azo bo'lmasalar uchun obuna tekshirish
        not_subscribed = check_subscription(user_id, bot)
        
        if not_subscribed:
            bot.answer_callback_query(
                call.id,
                "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!",
                show_alert=True
            )
            bot.edit_message_text(
                "<b>❗️ Kanallarga Obuna Bo'lish Majburiy!</b>\n\n"
                "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n\n"
                "🔹 Yoki ⭐️ Premium sotib oling va kanallarga obuna bo'lmasdan foydalaning!",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=subscription_keyboard(not_subscribed, bot)
            )
        else:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            first_name = call.from_user.first_name
            
            bot.send_message(
                call.message.chat.id,
                f"✅ <b>Tabriklaymanviz!</b>\n\n"
                f"Assalomu alaykum, {first_name}!\n\n"
                f"🎬 Xush kelibsiz! Kerakli kinoning kodini yozing.\n\n"
                f"Masalan: 54",
                parse_mode="HTML",
                reply_markup=user_keyboard()
            )
            bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
    except Exception as e:
        print(f"[ERROR] Obuna tekshirishda xatolik: {str(e)}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi!", show_alert=True)

# ==================== SEARCH MOVIES ====================
@bot.message_handler(func=lambda message: message.text.strip().isdigit())
def search_movie(message):
    """Kino kodini qidirish yoki yuborish"""
    user_id = message.from_user.id
    code = message.text.strip()
    
    # Har doim obunani tekshirish (admin va premium ham tekshirish uchun)
    is_user_admin = is_admin(user_id)
    is_user_premium = check_premium(user_id)
    
    # Agar admin yoki premium emas bo'lsa, obuna tekshirish majburiy
    if not is_user_admin and not is_user_premium:
        not_subscribed = check_subscription(user_id, bot)
        if not_subscribed:
            bot.send_message(
                message.chat.id,
                "❗️ <b>Kinoni ko'rish uchun avval kanallarga obuna bo'ling!</b>\n\n"
                "Yoki Premium sotib oling va kanallarga obuna bo'lmasdan foydalaning:",
                parse_mode="HTML",
                reply_markup=subscription_keyboard(not_subscribed, bot)
            )
            return
    
    # Kino kodining mavjudligini tekshirish
    try:
        movies_db = load_data(MOVIES_FILE)
        if not movies_db or not isinstance(movies_db, list):
            bot.send_message(
                message.chat.id,
                "❌ <b>Xatolik!</b>\n\n"
                "Hozircha kinolar mavjud emas. Kech orada tekshirib ko'ring.",
                parse_mode="HTML",
                reply_markup=user_keyboard(is_premium=is_user_premium)
            )
            return
        
        # Kino kodini qidiruv (string va int ikkala formatda)
        movie_found = False
        for m in movies_db:
            if m.get("code") == code or str(m.get("code")) == code:
                movie_found = True
                break
        
        if not movie_found:
            bot.send_message(
                message.chat.id,
                f"❌ <b>Topilmadi!</b>\n\n"
                f"Kod <code>{code}</code> bilan kino topilmadi.\n\n"
                f"⚠️ Kino kodini to'g'ri kiriting yoki admin bilan bog'laning.",
                parse_mode="HTML",
                reply_markup=user_keyboard(is_premium=is_user_premium)
            )
            return
        
        # Kinoni yuborish
        send_movie_to_user(message.chat.id, code, user_id, bot)
        
    except Exception as e:
        print(f"[ERROR] Kino qidirishda xatolik: {str(e)}")
        bot.send_message(
            message.chat.id,
            "❌ <b>Xatolik yuz berdi!</b>\n\n"
            "Iltimos, qayta urinib ko'ring.",
            parse_mode="HTML",
            reply_markup=user_keyboard(is_premium=is_user_premium)
        )

# ==================== INLINE MODE ====================
@bot.inline_handler(lambda query: True)
def inline_query(query):
    """Inline qidiruv"""
    try:
        results = []
        search_text = query.query.strip()
        
        if search_text.isdigit() and search_text in movies_db:
            movie = movies_db[search_text]
            views_count = views_db.get(search_text, 0)
            
            description = f"👁 Ko'rishlar: {views_count}\n{movie['description'][:100]}..."
            
            result = types.InlineQueryResultVideo(
                id=search_text,
                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                mime_type="video/mp4",
                thumb_url="https://via.placeholder.com/150",
                title=f"Kino #{search_text}",
                description=description,
                input_message_content=types.InputTextMessageContent(
                    message_text=f"🎬 Kinoni ko'rish uchun botni ishga tushiring:\n\n"
                                 f"👉 /start {search_text}\n\n"
                                 f"👁 Ko'rishlar: {views_count}"
                )
            )
            results.append(result)
        
        bot.answer_inline_query(query.id, results, cache_time=1)
    except Exception as e:
        print(f"Inline query error: {e}")

# ==================== STATISTICS ====================
@bot.message_handler(func=lambda message: message.text == "📊 Statistika" and is_admin(message.from_user.id))
def statistics(message):
    """Bot statistikasi"""
    users_db = load_data(USERS_FILE)
    movies_db = load_data(MOVIES_FILE)
    channels_db = load_data(CHANNELS_FILE)
    premium_db = load_data(PREMIUM_FILE)
    admins_db = load_data(ADMINS_FILE)
    views_db = load_data(VIEWS_FILE)
    
    total_users = len(users_db)
    total_movies = len(movies_db)
    total_channels = len(channels_db)
    
    # Ochiq va mahfiy kanallarni hisoblash
    public_channels = sum(1 for ch in channels_db.values() if isinstance(ch, dict) and not ch.get('is_private', False))
    private_channels = sum(1 for ch in channels_db.values() if isinstance(ch, dict) and ch.get('is_private', False))
    
    total_premium = len(premium_db)
    total_admins = len(admins_db)
    total_views = sum(views_db.values()) if isinstance(views_db, dict) else 0
    
    # Eng ko'p ko'rilgan kinolar
    top_movies = sorted(views_db.items(), key=lambda x: x[1], reverse=True)[:5] if isinstance(views_db, dict) else []
    top_text = "\n\n🏆 Top 5 kinolar:\n" if top_movies else ""
    for i, (code, views) in enumerate(top_movies, 1):
        top_text += f"{i}. Kod {code}: {views} ko'rish\n"
    
    bot.send_message(
        message.chat.id,
        f"📊 Bot statistikasi:\n\n"
        f"👥 Foydalanuvchilar: {total_users}\n"
        f"🎬 Kinolar: {total_movies}\n"
        f"👁 Jami ko'rishlar: {total_views}\n"
        f"📢 Kanallar: {total_channels} (🔓 {public_channels} ochiq | 🔒 {private_channels} mahfiy)\n"
        f"⭐️ Premium a'zolar: {total_premium}\n"
        f"👤 Adminlar: {total_admins}"
        f"{top_text}",
        reply_markup=admin_keyboard()
    )

# ==================== BROADCAST ====================
@bot.message_handler(func=lambda message: message.text == "📢 Xabar yuborish" and is_admin(message.from_user.id))
def broadcast_start(message):
    """Broadcast boshlash"""
    start_send_broadcast(message.from_user.id, bot)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and 
                     user_states[message.from_user.id].get("action") == "waiting_broadcast_content",
                     content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'animation', 'sticker'])
def broadcast_message(message):
    """Broadcast xabarini yuborish (har qanday turda)"""
    handle_broadcast_message(message.from_user.id, message, bot)

# ==================== HELP ====================
@bot.message_handler(func=lambda message: message.text in ["ℹ️ Yordam", "🎬 Kino qidirish", "/help"])
def help_command(message):
    """Yordam"""
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>Bot haqida ma'lumot:</b>\n\n"
        "🎬 <b>Kino kodini yuboring va kino oling!</b>\n\n"
        "Masalan: <code>54</code>\n\n"
        "⭐️ <b>Premium obuna</b> - Kanallarga obuna bo'lmasdan foydalanish!\n\n"
        "📱 Bizni Instagram'da kuzating!",
        parse_mode="HTML"
    )

# ==================== SAFETY HANDLER ====================
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    """Boshqa barcha xabarlarni qayta yo'naltirish"""
    user_id = message.from_user.id
    
    if is_admin(user_id):
        bot.send_message(
            message.chat.id,
            "❓ <b>Noma'lum buyruq!</b>\n\n"
            "Admin menyu orqali amalni tanlang.",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
    else:
        # Premium yoki obunashing ekanligini tekshirish
        is_premium = check_premium(user_id)
        not_subscribed = [] if is_premium else check_subscription(user_id, bot)
        
        if not_subscribed:
            bot.send_message(
                message.chat.id,
                "<b>❗️ Avval kanallarga obuna bo'lish kerak!</b>\n\n"
                "Kino kodini jo'natishdan oldin quyidagi kanallarga obuna bo'ling:",
                parse_mode="HTML",
                reply_markup=subscription_keyboard(not_subscribed, bot)
            )
        else:
            bot.send_message(
                message.chat.id,
                "<b>❓ Noto'g'ri buyruq!</b>\n\n"
                "Iltimos, <b>kino kodini</b> yuboring (faqat raqamlar).\n\n"
                "Masalan: <code>54</code>",
                parse_mode="HTML",
                reply_markup=user_keyboard(is_premium=is_premium)
            )

# ==================== BOT START ====================
if __name__ == "__main__":
    print("[*] Bot started...")
    print(f"[*] Bot username: @{bot.get_me().username}")
    print(f"[*] Bot ID: {bot.get_me().id}")
    print(f"[*] Super Admin ID: {SUPER_ADMIN}")
    print(f"[*] Instagram: {INSTAGRAM_URL}")
    print("[OK] Ready!\n")
    bot.infinity_polling()
