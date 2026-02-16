# Habar yuborish (broadcast) operatsiyalari

from telebot import types
from database import load_data
from admin_handlers import user_states

def start_send_broadcast(user_id, bot):
    """Habar yuborishni boshlash"""
    user_states[user_id] = {"action": "waiting_broadcast_content"}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        "❌ Bekor qilish"
    )
    
    bot.send_message(
        user_id,
        "📢 <b>Habar yuborish</b>\n\n"
        "Foydalanuvchilarga yuboradigan habarni kiriting:\n\n"
        "<b>Qabul qilinadi:</b>\n"
        "✅ Matn xabar\n"
        "✅ Rasmli (JPG, PNG)\n"
        "✅ Video\n"
        "✅ GIF/Animation\n"
        "✅ PDF fayl\n"
        "✅ APK fayl\n"
        "✅ Audio fayl\n"
        "✅ Ovozli xabar\n"
        "✅ Sticker\n"
        "✅ Boshqa hujjatlar\n\n"
        "<b>💡 Maslahat:</b> Faqat 1 ta fayl/habar yuboring. Captions/izohlar ham qo'shishingiz mumkin.\n\n"
        "Habarni yuboring:",
        parse_mode="HTML",
        reply_markup=markup
    )

def handle_broadcast_message(user_id, message, bot):
    """Habarni qabul qilish va yuborish"""
    from keyboards import admin_keyboard
    from config import USERS_FILE
    
    # Bekor qilish tekshiruvi
    if message.text and message.text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        # Foydalanuvchilar ro'yxatini yuklash
        users_db = load_data(USERS_FILE)
        if not isinstance(users_db, dict):
            users_db = {}
        
        user_ids = list(users_db.keys())
        
        print(f"\n{'='*60}")
        print(f"[BROADCAST] Boshlandi!")
        print(f"[BROADCAST] Admin ID: {user_id}")
        print(f"[BROADCAST] Foydalanuvchilar fayli: {USERS_FILE}")
        print(f"[BROADCAST] Jami foydalanuvchilar: {len(user_ids)}")
        if user_ids:
            print(f"[BROADCAST] User ID misollari: {user_ids[:3]}...")
            # Birinchi foydalanuvchining ma'lumotini ko'rsat
            first_user_key = user_ids[0]
            print(f"[BROADCAST] Birinchi user ma'lumoti: {users_db.get(first_user_key, {})}")
        print(f"{'='*60}\n")
        
        if not user_ids:
            bot.send_message(
                user_id,
                "❌ <b>Habar yuborib bo'lmadi!</b>\n\n"
                "Hozircha foydalanuvchilar ro'yxati bo'sh.\n"
                "🔍 Debug: birinchi habar yuboradigan foydalanuvchi yo'q.",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            user_states.pop(user_id, None)
            return
        
        # Habarni tayyorlash
        status_msg = bot.send_message(
            user_id,
            "⏳ <b>Habar yuborilmoqda...</b>\n\n"
            f"📊 Jami: {len(user_ids)} ta foydalanuvchi",
            parse_mode="HTML"
        )
        
        sent_count = 0
        failed_count = 0
        
        # Har bir foydalanuvchiga habar yuborish
        for recipient_user_id in user_ids:
            try:
                # String dan int'ga o'girish
                recipient_user_id_int = int(recipient_user_id)
                
                # Yuboruvchiga o'zini habar yubormaslik
                if recipient_user_id_int == user_id:
                    sent_count += 1
                    continue
                
                # Habar turini aniqlash va yuborish
                message_sent = False
                message_type = "Unknown"
                
                try:
                    if message.text and message.text.strip():
                        # Matn xabari
                        message_type = "Text"
                        bot.send_message(
                            recipient_user_id_int,
                            message.text,
                            parse_mode="HTML"
                        )
                        message_sent = True
                    
                    elif message.photo:
                        # Rasm
                        message_type = "Photo"
                        caption = message.caption if message.caption else ""
                        bot.send_photo(
                            recipient_user_id_int,
                            message.photo[-1].file_id,
                            caption=caption,
                            parse_mode="HTML" if caption else None
                        )
                        message_sent = True
                    
                    elif message.video:
                        # Video
                        message_type = "Video"
                        caption = message.caption if message.caption else ""
                        bot.send_video(
                            recipient_user_id_int,
                            message.video.file_id,
                            caption=caption,
                            parse_mode="HTML" if caption else None
                        )
                        message_sent = True
                    
                    elif message.document:
                        # Hujjat (PDF, APK, va hakazo)
                        message_type = "Document"
                        caption = message.caption if message.caption else ""
                        bot.send_document(
                            recipient_user_id_int,
                            message.document.file_id,
                            caption=caption,
                            parse_mode="HTML" if caption else None
                        )
                        message_sent = True
                    
                    elif message.audio:
                        # Audio
                        message_type = "Audio"
                        caption = message.caption if message.caption else ""
                        bot.send_audio(
                            recipient_user_id_int,
                            message.audio.file_id,
                            caption=caption,
                            parse_mode="HTML" if caption else None
                        )
                        message_sent = True
                    
                    elif message.voice:
                        # Ovozli xabar
                        message_type = "Voice"
                        caption = message.caption if message.caption else ""
                        bot.send_voice(
                            recipient_user_id_int,
                            message.voice.file_id,
                            caption=caption,
                            parse_mode="HTML" if caption else None
                        )
                        message_sent = True
                    
                    elif message.animation:
                        # GIF/Animation
                        message_type = "Animation"
                        caption = message.caption if message.caption else ""
                        bot.send_animation(
                            recipient_user_id_int,
                            message.animation.file_id,
                            caption=caption,
                            parse_mode="HTML" if caption else None
                        )
                        message_sent = True
                    
                    elif message.sticker:
                        # Sticker
                        message_type = "Sticker"
                        bot.send_sticker(
                            recipient_user_id_int,
                            message.sticker.file_id
                        )
                        message_sent = True
                    
                except Exception as send_err:
                    print(f"[ERROR] {message_type} yuborishda xatolik (User={recipient_user_id_int}): {str(send_err)}")
                    message_sent = False
                
                if message_sent:
                    sent_count += 1
                    print(f"[OK] {message_type} yuborildi (User={recipient_user_id_int})")
                else:
                    # Agar hech narsa yuborilmasa, xatolik
                    failed_count += 1
                    print(f"[WARNING] Habar yuborilmadi - tur aniqllab bo'lmadi (User={recipient_user_id_int})")
                    print(f"[DEBUG] Message attributes: text={bool(message.text)}, photo={bool(message.photo)}, video={bool(message.video)}, document={bool(message.document)}, audio={bool(message.audio)}, voice={bool(message.voice)}, animation={bool(message.animation)}, sticker={bool(message.sticker)}")
                    
            except Exception as send_err:
                failed_count += 1
                print(f"[ERROR] User {recipient_user_id}'ga habar yuborishda xatolik: {str(send_err)}")
        
        # Natijani ko'rsatish
        bot.edit_message_text(
            f"✅ <b>Habar muvaffaqiyatli yuborildi!</b>\n\n"
            f"📊 Muvaffaqiyatli: <b>{sent_count}</b>\n"
            f"❌ Xatolik: <b>{failed_count}</b>\n"
            f"📈 Jami: <b>{len(user_ids)}</b>\n\n"
            f"💡 <b>DEBUG INFO:</b>\n"
            f"Bazada: {len(user_ids)} foydalanuvchi saqlangan\n"
            f"Yuborildi: {sent_count} ta\n"
            f"Xatolik: {failed_count} ta",
            user_id,
            status_msg.message_id,
            parse_mode="HTML"
        )
        
        bot.send_message(
            user_id,
            "✅ <b>Habar yuborish tugallandi!</b>\n\n"
            f"✅ Muvaffaqiyatli: {sent_count}\n"
            f"❌ Xatolik: {failed_count}\n"
            f"📊 Jami: {len(user_ids)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        
        print(f"\n{'='*60}")
        print(f"[BROADCAST] YAKUNLANDI!")
        print(f"[BROADCAST] Muvaffaqiyatli: {sent_count}")
        print(f"[BROADCAST] Xatolik: {failed_count}")
        print(f"[BROADCAST] Jami bazada: {len(user_ids)}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik yuz berdi!</b>\n\n{str(e)[:100]}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Habar yuborishda xatolik: {str(e)}")
    
    finally:
        user_states.pop(user_id, None)
