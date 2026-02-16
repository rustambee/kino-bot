# Premium boshqarish

from telebot import types
from database import load_data, save_data
from config import PREMIUM_FILE, USERS_FILE
from admin_handlers import user_states


def show_premium_users(user_id, bot):
    """Premium foydalanuvchilarni ko'rsatish"""
    try:
        premium_db = load_data(PREMIUM_FILE)
        users_db = load_data(USERS_FILE)
        
        if not premium_db:
            bot.send_message(
                user_id,
                "📭 <b>Premium foydalanuvchilar yo'q</b>",
                parse_mode="HTML"
            )
            return
        
        # Premium foydalanuvchilar ro'yxati
        message = "⭐️ <b>Premium Foydalanuvchilar</b>\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for premium_user_id, premium_data in premium_db.items():
            # Foydalanuvchi ma'lumotlarini topish
            user_info = users_db.get(str(premium_user_id), None) if isinstance(users_db, dict) else None
            username = user_info.get("username", "Noma'lum") if user_info else "Noma'lum"
            
            expiry_date = premium_data.get("expiry_date", "Cheksiz")
            status = premium_data.get("status", "aktiv")
            
            markup.add(
                types.InlineKeyboardButton(
                    f"❌ O'chirish - {username}",
                    callback_data=f"remove_premium:{premium_user_id}"
                )
            )
            
            message += f"👤 {username} (ID: {premium_user_id})\n"
            message += f"   ⏱ Tugash: {expiry_date}\n"
            message += f"   📊 Status: {status}\n\n"
        
        markup.add(
            types.InlineKeyboardButton(
                "❌ Yopish",
                callback_data="close_premium_users"
            )
        )
        
        bot.send_message(
            user_id,
            message,
            parse_mode="HTML",
            reply_markup=markup
        )
        
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik!</b>\n\n{str(e)}",
            parse_mode="HTML"
        )
        print(f"[ERROR] Premium foydalanuvchilarni ko'rsatishda xatolik: {str(e)}")


def remove_premium_user(user_id, premium_user_id, bot):
    """Premium foydalanuvchidan premium'ni olib tashlash"""
    try:
        premium_db = load_data(PREMIUM_FILE)
        users_db = load_data(USERS_FILE)
        
        # Premium ma'lumotlarini o'chirish
        if premium_user_id in premium_db:
            removed_data = premium_db.pop(premium_user_id)
            save_data(PREMIUM_FILE, premium_db)
            
            # Foydalanuvchiga xabar yuborish
            try:
                user_info = users_db.get(str(premium_user_id), None) if isinstance(users_db, dict) else None
                username = user_info.get("username", "Foydalanuvchi") if user_info else "Foydalanuvchi"
                
                bot.send_message(
                    int(premium_user_id),
                    "❌ <b>Sizning premium statusingiz bekor qilindi</b>\n\n"
                    "Boshqaruv: Administrasyon",
                    parse_mode="HTML"
                )
            except:
                pass  # Foydalanuvchiga xabar yuborishda xatolik
            
            # Admin'ga xabar yuborish
            from keyboards import admin_keyboard
            bot.send_message(
                user_id,
                f"✅ <b>Premium bekor qilindi!</b>\n\n"
                f"ID: {premium_user_id}\n"
                f"Tugash: {removed_data.get('expiry_date', 'Noma\'lum')}",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            
            print(f"[OK] Premium o'chirildi: User={premium_user_id}, Admin={user_id}")
        else:
            from keyboards import admin_keyboard
            bot.send_message(
                user_id,
                f"❌ <b>Xatolik!</b>\n\n"
                f"Foydalanuvchi premium emas.",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
    except Exception as e:
        from keyboards import admin_keyboard
        bot.send_message(
            user_id,
            f"❌ <b>O'chirishda xatolik!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Premium o'chirishda xatolik: {str(e)}")


def start_manual_premium_add(user_id, bot):
    """Manual premium qo'shishni boshlash"""
    user_states[user_id] = {"action": "manual_premium_user_id"}
    
    from keyboards import admin_keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("❌ Bekor qilish")
    
    bot.send_message(
        user_id,
        "⭐️ <b>Premium qo'shish</b>\n\n"
        "Foydalanuvchining ID'sini yuboring:",
        parse_mode="HTML",
        reply_markup=markup
    )


def manual_premium_user_id_callback(user_id, user_id_text, bot):
    """Premium qo'shish - user ID qabul qilish"""
    from keyboards import admin_keyboard
    
    if user_id_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        premium_user_id = int(user_id_text.strip())
        
        user_states[user_id] = {
            "action": "manual_premium_days",
            "premium_user_id": premium_user_id
        }
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add("❌ Bekor qilish")
        
        bot.send_message(
            user_id,
            f"📅 <b>Premium davomiyligi</b>\n\n"
            f"Kunlar sonini yuboring (masalan: 30)",
            parse_mode="HTML",
            reply_markup=markup
        )
    except ValueError:
        bot.send_message(
            user_id,
            "❌ <b>Xatolik!</b>\n\nFaqat raqam yuboring.",
            parse_mode="HTML"
        )


def manual_premium_days_callback(user_id, days_text, bot):
    """Premium qo'shish - kunlar sonini qabul qilish"""
    from keyboards import admin_keyboard
    from datetime import datetime, timedelta
    
    if days_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        days = int(days_text.strip())
        
        if days < 1 or days > 365:
            bot.send_message(
                user_id,
                "❌ <b>Xatolik!</b>\n\n"
                "Kunlar soni 1 dan 365 gacha bo'lishi kerak.",
                parse_mode="HTML"
            )
            return
        
        premium_user_id = str(user_states[user_id].get("premium_user_id"))
        
        # Premium ma'lumotlarini saqlash
        premium_db = load_data("premium.json")
        expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        
        premium_db[premium_user_id] = {
            "status": "aktiv",
            "expiry_date": expiry_date,
            "added_by": user_id,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_data("premium.json", premium_db)
        
        # Foydalanuvchiga xabar yuborish
        try:
            bot.send_message(
                int(premium_user_id),
                f"🎉 <b>Tabriklaymiz!</b>\n\n"
                f"Sizga premium status berildi!\n"
                f"⏱ Tugash: {expiry_date}",
                parse_mode="HTML"
            )
        except:
            pass
        
        bot.send_message(
            user_id,
            f"✅ <b>Premium qo'shildi!</b>\n\n"
            f"ID: {premium_user_id}\n"
            f"Kunlar: {days}\n"
            f"Tugash: {expiry_date}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        
        print(f"[OK] Premium qo'shildi: User={premium_user_id}, Days={days}, Admin={user_id}")
        
    except ValueError:
        bot.send_message(
            user_id,
            "❌ <b>Xatolik!</b>\n\nFaqat raqam yuboring.",
            parse_mode="HTML"
        )
    finally:
        user_states.pop(user_id, None)
