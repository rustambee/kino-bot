# Admin handlerlar

from telebot import types
from datetime import datetime, timedelta
from database import (
    admins_list, users_db, premium_db, channels_db, 
    movies_db, views_db, likes_db, pending_channels_db,
    save_list, save_data, approve_pending_channel, reject_pending_channel,
    ADMINS_FILE, USERS_FILE, PREMIUM_FILE, CHANNELS_FILE,
    MOVIES_FILE, VIEWS_FILE, LIKES_FILE, PENDING_CHANNELS_FILE
)
from utils import is_admin, save_user
from keyboards import admin_keyboard
from config import SUPER_ADMIN

user_states = {}  # Foydalanuvchi holatlari

def start_add_admin(user_id, bot):
    """Admin qo'shishni boshlash"""
    user_states[user_id] = {"action": "adding_admin"}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Bekor qilish")
    bot.send_message(
        user_id,
        "👤 Yangi admin ID sini kiriting:\n\n"
        "ID ni olish uchun @userinfobot dan foydalaning",
        reply_markup=markup
    )

def add_admin_callback(user_id, admin_text, bot):
    """Admin ID-ni qabul qilish"""
    if admin_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(user_id, "❌ Bekor qilindi", reply_markup=admin_keyboard())
        return
    
    if not admin_text.isdigit():
        bot.send_message(user_id, "❌ Faqat raqam kiriting!")
        return
    
    new_admin_id = int(admin_text)
    
    if new_admin_id in admins_list:
        bot.send_message(
            user_id,
            "⚠️ Bu foydalanuvchi allaqachon admin!",
            reply_markup=admin_keyboard()
        )
        user_states.pop(user_id, None)
        return
    
    admins_list.append(new_admin_id)
    save_list(ADMINS_FILE, admins_list)
    
    try:
        from database import load_data, USERS_FILE
        
        users_data = load_data(USERS_FILE)
        if not isinstance(users_data, dict):
            users_data = {}
        
        user_info = users_data.get(str(new_admin_id), {})
        first_name = user_info.get("first_name", "")
        
        bot.send_message(
            new_admin_id,
            f"🎉 Tabriklaymiz!\n\n"
            f"Siz bot admini sifatida qo'shildingiz!\n\n"
            f"Admin paneliga kirish uchun /start ni bosing.",
            reply_markup=admin_keyboard()
        )
        
        bot.send_message(
            user_id,
            f"✅ Yangi admin qo'shildi!\n\n"
            f"👤 ID: {new_admin_id}\n"
            f"📝 Ism: {first_name if first_name else 'Noma\'lum'}",
            reply_markup=admin_keyboard()
        )
    except:
        bot.send_message(
            user_id,
            f"✅ Admin qo'shildi!\n\n"
            f"👤 ID: {new_admin_id}\n\n"
            f"⚠️ Foydalanuvchi hali botni ishga tushirmagan.",
            reply_markup=admin_keyboard()
        )
    
    user_states.pop(user_id, None)

def start_delete_admin(user_id, bot):
    """Admin o'chirishni boshlash"""
    if len(admins_list) <= 1:
        bot.send_message(
            user_id,
            "❌ Kamida bitta admin bo'lishi kerak!",
            reply_markup=admin_keyboard()
        )
        return
    
    from database import load_data, USERS_FILE
    
    users_data = load_data(USERS_FILE)
    if not isinstance(users_data, dict):
        users_data = {}
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for admin_id in admins_list:
        if admin_id == SUPER_ADMIN:
            continue
        
        user_info = users_data.get(str(admin_id), {})
        first_name = user_info.get("first_name", "Noma'lum")
        username = user_info.get("username", "Yo'q")
        
        button_text = f"🗑 {first_name}"
        if username != "Yo'q":
            button_text += f" (@{username})"
        button_text += f" - {admin_id}"
        
        markup.add(types.InlineKeyboardButton(
            text=button_text,
            callback_data=f"delete_admin:{admin_id}"
        ))
    
    markup.add(types.InlineKeyboardButton(
        text="❌ Bekor qilish",
        callback_data="cancel_delete_admin"
    ))
    
    bot.send_message(
        user_id,
        "🗑 O'chirmoqchi bo'lgan adminni tanlang:",
        reply_markup=markup
    )

def delete_admin_callback(admin_id, user_id, bot):
    """Adminni o'chirish"""
    if admin_id == SUPER_ADMIN:
        bot.answer_callback_query(user_id, "❌ Asosiy adminni o'chirish mumkin emas!", show_alert=True)
        return False
    
    if admin_id in admins_list:
        admins_list.remove(admin_id)
        save_list(ADMINS_FILE, admins_list)
        
        try:
            bot.send_message(
                admin_id,
                "❌ Siz adminlikdan olib tashlangiz.\n\n"
                "Botdan oddiy foydalanuvchi sifatida foydalanishingiz mumkin."
            )
        except:
            pass
        
        return True
    return False

def show_admins_list(user_id, bot):
    """Adminlar ro'yxatini ko'rsatish"""
    from database import load_data, USERS_FILE
    
    users_data = load_data(USERS_FILE)
    if not isinstance(users_data, dict):
        users_data = {}
    
    text = "👥 <b>Bot adminlari:</b>\n\n"
    
    for i, admin_id in enumerate(admins_list, 1):
        user_info = users_data.get(str(admin_id), {})
        first_name = user_info.get("first_name", "Noma'lum")
        username = user_info.get("username", "Yo'q")
        
        text += f"{i}. {first_name}"
        if username != "Yo'q":
            text += f" (@{username})"
        text += f"\n   🆔 <code>{admin_id}</code>"
        if admin_id == SUPER_ADMIN:
            text += " ⭐️ (Asosiy admin)"
        text += "\n\n"
    
    bot.send_message(
        user_id,
        text,
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )

def show_pending_channels(user_id, bot):
    """Tasdiqlanmagan kanallar"""
    if not pending_channels_db:
        bot.send_message(
            user_id,
            "📋 Tasdiqlanmaydigan kanallar yo'q!",
            reply_markup=admin_keyboard()
        )
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for request_id, channel_data in pending_channels_db.items():
        markup.add(
            types.InlineKeyboardButton(
                text=f"📢 {channel_data['name']} - {channel_data['title']}",
                callback_data=f"view_pending:{request_id}"
            )
        )
    
    bot.send_message(
        user_id,
        "📋 <b>Tasdiqlanmaydigan kanallar:</b>",
        parse_mode="HTML",
        reply_markup=markup
    )
