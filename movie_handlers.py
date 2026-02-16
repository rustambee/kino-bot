# Kino operatsiyalari

from telebot import types
from database import load_data, save_data
from admin_handlers import user_states

def start_upload_movie(user_id, bot):
    """Kino yuklashni boshlash"""
    user_states[user_id] = {"action": "waiting_code"}
    from keyboards import admin_keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        "❌ Bekor qilish"
    )
    bot.send_message(
        user_id,
        "📝 <b>Yangi kino qo'shish</b>\n\n"
        "Kino kodini kiriting (faqat raqam):\n\n"
        "Masalan: 54",
        parse_mode="HTML",
        reply_markup=markup
    )

def get_movie_code_callback(user_id, code_text, bot):
    """Kino kodini qabul qilish"""
    from keyboards import admin_keyboard
    from config import MOVIES_FILE
    
    # Bekor qilish tekshiruvi
    if code_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    # Raqamli kod tekshiruvi
    if not code_text.isdigit():
        bot.send_message(
            user_id,
            "❗️ <b>Faqat raqam kiriting!</b>",
            parse_mode="HTML"
        )
        return
    
    code = code_text.strip()
    
    try:
        # Kinolar bazasini yuklash va kod tekshirish
        movies_db = load_data(MOVIES_FILE)
        
        # Agar movies_db dict bo'lsa (eski format), uni list'ga o'zgartirish
        if isinstance(movies_db, dict):
            movies_db = list(movies_db.values())
        elif not isinstance(movies_db, list):
            movies_db = []
        
        # Kod allaqachon mavjud bo'lsa, xatolik
        if any(isinstance(m, dict) and m.get("code") == code for m in movies_db):
            bot.send_message(
                user_id,
                f"⚠️ <b>Xatolik!</b>\n\n"
                f"Kod <code>{code}</code> allaqachon mavjud!\n\n"
                f"Boshqa kod kiriting yoki ❌ Bekor qilish bosing.",
                parse_mode="HTML"
            )
            return
        
        # State o'rnatish va keyingi qadam
        user_states[user_id] = {
            "action": "waiting_movie",
            "code": code
        }
        
        bot.send_message(
            user_id,
            f"✅ <b>Kod qabul qilindi!</b>\n\n"
            f"Kod: <code>{code}</code>\n\n"
            f"📹 Endi kinoni yuboring (video fayli):",
            parse_mode="HTML"
        )
        
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik yuz berdi!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Kod tekshirishda xatolik: {str(e)}")

def get_movie_file_callback(user_id, message, bot, BASE_CHANNEL):
    """Kino faylini qabul qilish va base kanalga yuborish"""
    from keyboards import admin_keyboard
    
    if user_id not in user_states or user_states.get(user_id, {}).get("action") != "waiting_movie":
        bot.send_message(message.chat.id, "❌ Xatolik! Kino kodini qayta kiriting.", reply_markup=admin_keyboard())
        return
    
    code = user_states[user_id]["code"]
    
    try:
        # Foydalanuvchi yuborgan video fayli
        if not message.video:
            bot.send_message(
                message.chat.id,
                "❌ <b>Video fayl emas!</b>\n\nIltimos, video fayl yuboring.",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            user_states.pop(user_id, None)
            return
        
        # Video haqida ma'lumot
        video_file_id = message.video.file_id
        video_file_size = message.video.file_size if message.video.file_size else 0
        
        # Base kanalga yuborish
        try:
            sent_message = bot.forward_message(
                BASE_CHANNEL,
                message.chat.id,
                message.message_id
            )
            saved_file_id = sent_message.video.file_id
            
            print(f"[OK] Video base kanalga yuborildi: Kod={code}, File_ID={saved_file_id[:20]}..., Hajmi={video_file_size}")
        except Exception as forward_error:
            # Agar forward bo'lmasa, original file_id dan foydalanish
            print(f"[WARNING] Forward xatoligi, original file_id dan foydalanilmoqda: {str(forward_error)}")
            saved_file_id = video_file_id
        
        user_states[user_id] = {
            "action": "waiting_description",
            "code": code,
            "file_id": saved_file_id,
            "video_size": video_file_size
        }
        
        size_text = f"{video_file_size / (1024*1024):.1f} MB" if video_file_size else "Noma'lum"
        
        bot.send_message(
            message.chat.id,
            f"✅ <b>Video qabul qilindi!</b>\n\n"
            f"📹 <b>Hajm:</b> {size_text}\n\n"
            f"📝 Endi kino haqida ma'lumot yuboring:\n\n"
            f"<b>Masalan:</b>\n"
            f"Avatar (2009)\n"
            f"Janr: Fantastika, Sarguzasht\n"
            f"Yilda: 2009\n"
            f"Reyting: 8.5/10",
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("❌ Bekor qilish")
        )
    except Exception as e:
        print(f"[ERROR] Video qabul qilishda xatolik (Kod={code}): {str(e)}")
        bot.send_message(
            message.chat.id,
            f"❌ <b>Xatolik yuz berdi!</b>\n\n"
            f"<b>Sabab:</b> {str(e)[:100]}\n\n"
            f"Iltimos, video yuborishni qayta urinib ko'ring yoki boshqa video tanlang.",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        user_states.pop(user_id, None)

def get_movie_description_callback(user_id, description_text, bot):
    """Kino tavsifini qabul qilish va saqlash"""
    from keyboards import admin_keyboard
    from database import load_data, save_data
    from config import MOVIES_FILE, VIEWS_FILE, LIKES_FILE
    
    # Bekor qilish tugmasi tekshiruvi
    if description_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    # State tekshiruvi
    if user_id not in user_states or user_states.get(user_id, {}).get("action") != "waiting_description":
        bot.send_message(
            user_id,
            "❌ <b>Xatolik!</b> Boshidan boshlang.",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        state = user_states[user_id]
        code = state.get("code")
        file_id = state.get("file_id")
        description = description_text
        
        if not code or not file_id:
            raise ValueError("Kod yoki file_id topilmadi!")
        
        # Databases ni yuklash
        movies_db = load_data(MOVIES_FILE)
        views_db = load_data(VIEWS_FILE)
        likes_db = load_data(LIKES_FILE)
        
        # Agar movies_db dict bo'lsa (eski format), uni list'ga o'zgartirish
        if isinstance(movies_db, dict):
            movies_db = list(movies_db.values())
        elif not isinstance(movies_db, list):
            movies_db = []
        
        # Faqat dict bo'lganlari saqla
        movies_db = [m for m in movies_db if isinstance(m, dict)]
        
        # views_db va likes_db ni dict sifatida tekshir
        if not isinstance(views_db, dict):
            views_db = {}
        if not isinstance(likes_db, dict):
            likes_db = {}
        
        # Kod allaqachon mavjud bo'lsa, xatolik
        if any(m.get("code") == code for m in movies_db):
            bot.send_message(
                user_id,
                f"❌ <b>Xatolik!</b>\n\n"
                f"Kod <code>{code}</code> allaqachon mavjud!\n"
                f"Boshqa kod tanlang.",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            user_states.pop(user_id, None)
            return
        
        # Yangi kinoni qo'shish
        movies_db.append({
            "code": code,
            "file_id": file_id,
            "description": description,
            "uploaded_by": user_id,
            "uploaded_at": str(__import__('datetime').datetime.now())
        })
        
        save_data(MOVIES_FILE, movies_db)
        
        # Ko'rishlar va bekorlar uchun 0 ni o'rnatish
        views_db[code] = 0
        likes_db[code] = 0
        save_data(VIEWS_FILE, views_db)
        save_data(LIKES_FILE, likes_db)
        
        bot.send_message(
            user_id,
            f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n\n"
            f"📌 Kod: <code>{code}</code>\n"
            f"📝 Tavsif: {description}\n\n"
            f"👥 Foydalanuvchilarga qidiruv orqali taqdim etiladi.",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        
        # Tadbir logga yozish
        print(f"[OK] Kino qo'shildi: Code={code}, User={user_id}")
        
    except ValueError as ve:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik!</b>\n\n{str(ve)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Kino state xatoligi: {str(ve)}")
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Saqlashda xatolik yuz berdi!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Kino saqlashda xatolik: {str(e)}")
    
    finally:
        user_states.pop(user_id, None)


def start_add_movie_to_channel(user_id, bot):
    """Kinoni kanalga qo'shimni boshlash"""
    from database import load_data
    from config import CHANNELS_FILE, MOVIES_FILE
    
    # Kanallar ro'yxatini yuklash
    channels_db = load_data(CHANNELS_FILE)
    
    if not channels_db or isinstance(channels_db, list):
        from keyboards import admin_keyboard
        bot.send_message(
            user_id,
            "❌ <b>Hozircha kanallar mavjud emas!</b>\n\n"
            "Avval kanal qo'shish kerak.",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    # Kinolar ro'yxatini yuklash
    movies_db = load_data(MOVIES_FILE)
    if not isinstance(movies_db, list) or not movies_db:
        from keyboards import admin_keyboard
        bot.send_message(
            user_id,
            "❌ <b>Hozircha kinolar mavjud emas!</b>\n\n"
            "Avval kino yuklash kerak.",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    # Kanal tanlash uchun tugmalar
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for channel_id, channel_info in channels_db.items():
        if isinstance(channel_info, dict):
            channel_name = channel_info.get('name', f'Kanal {channel_id}')
            markup.add(types.InlineKeyboardButton(
                text=f"📢 {channel_name}",
                callback_data=f"add_movie_channel:{channel_id}"
            ))
    
    markup.add(types.InlineKeyboardButton(
        text="❌ Bekor qilish",
        callback_data="cancel_add_movie_channel"
    ))
    
    bot.send_message(
        user_id,
        "<b>🎬 Kinoni kanalga qo'shish</b>\n\n"
        "Kinoni qaysi kanalga qo'shmoqchisiz?\n\n"
        "Kanal tanlang:",
        parse_mode="HTML",
        reply_markup=markup
    )


def add_movie_to_channel_callback(user_id, channel_id, bot):
    """Kanal tanlangandan so'ng kino kodini so'rash"""
    from keyboards import admin_keyboard
    
    user_states[user_id] = {
        "action": "selecting_movie_for_channel",
        "channel_id": channel_id
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("❌ Bekor qilish")
    
    bot.send_message(
        user_id,
        f"<b>Kino kodini kiriting</b>\n\n"
        f"📢 Kanal ID: <code>{channel_id}</code>\n\n"
        f"Kinoni qaysi kod bilan qo'shimni xohlaysiz?",
        parse_mode="HTML",
        reply_markup=markup
    )


def send_movie_to_channel_callback(user_id, code_text, bot):
    """Kinoni tanlangan kanalga yuborish"""
    from keyboards import admin_keyboard
    from database import load_data
    from config import MOVIES_FILE, CHANNELS_FILE
    
    # Bekor qilish tekshiruvi
    if code_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        code = code_text.strip()
        channel_id = user_states[user_id].get("channel_id")
        
        # Kino'ni topish
        movies_db = load_data(MOVIES_FILE)
        if not isinstance(movies_db, list):
            movies_db = []
        
        movie = None
        for m in movies_db:
            if isinstance(m, dict) and (m.get("code") == code or str(m.get("code")) == code):
                movie = m
                break
        
        if not movie:
            bot.send_message(
                user_id,
                f"❌ <b>Topilmadi!</b>\n\n"
                f"Kod <code>{code}</code> bilan kino topilmadi!",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            user_states.pop(user_id, None)
            return
        
        # Kanal ma'lumotlarini yuklash
        channels_db = load_data(CHANNELS_FILE)
        if not isinstance(channels_db, dict):
            channels_db = {}
        
        channel_info = channels_db.get(channel_id, {})
        if not channel_info:
            bot.send_message(
                user_id,
                f"❌ <b>Kanal topilmadi!</b>",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            user_states.pop(user_id, None)
            return
        
        # Video'ni kanalga yuborish
        try:
            file_id = movie.get('file_id')
            description = movie.get('description', 'Tavsif mavjud emas')
            caption = f"<b>{description}</b>\n📌 Kod: <code>{code}</code>"
            
            # Actual channel ID'sini olish (agar 'id' field bo'lsa)
            target_channel_id = channel_info.get('id', channel_id)
            
            bot.send_video(
                target_channel_id,
                file_id,
                caption=caption,
                parse_mode="HTML"
            )
            
            bot.send_message(
                user_id,
                f"✅ <b>Kino muvaffaqiyatli yuborildi!</b>\n\n"
                f"📢 Kanal: {channel_info.get('name', 'Noma\'lum')}\n"
                f"📌 Kod: <code>{code}</code>\n"
                f"📝 Tavsif: {description}",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            
            print(f"[OK] Kino kanalga yuborildi: Code={code}, Channel={target_channel_id}, User={user_id}")
            
        except Exception as send_err:
            bot.send_message(
                user_id,
                f"❌ <b>Yuborishda xatolik!</b>\n\n"
                f"Xatolik: {str(send_err)[:100]}\n\n"
                f"Kanal ID'sining to'g'ri ekanligini tekshiring.",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            print(f"[ERROR] Kino kanalga yuborishda xatolik: {str(send_err)}")
        
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik yuz berdi!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Kino kanal yuborishda xatolik: {str(e)}")
    
    finally:
        user_states.pop(user_id, None)

def send_movie_to_user(chat_id, movie_code, user_id, bot):
    """Kinoni foydalanuvchiga yuborish (obuna tekshirishi bilan)"""
    from database import load_data, save_data
    from keyboards import movie_keyboard
    from utils import increment_views, is_admin, check_premium, check_subscription
    from config import MOVIES_FILE
    
    try:
        # Admin yoki premium bo'lmasalar uchun obuna tekshirish (xavfsizlik)
        if not is_admin(user_id) and not check_premium(user_id):
            not_subscribed = check_subscription(user_id, bot)
            if not_subscribed:
                from keyboards import subscription_keyboard
                bot.send_message(
                    chat_id,
                    "❗️ <b>Kinoni ko'rish uchun avval kanallarga obuna bo'lish majburiy!</b>\n\n"
                    "Quyidagi kanallarga obuna bo'ling:",
                    parse_mode="HTML",
                    reply_markup=subscription_keyboard(not_subscribed, bot)
                )
                return
        
        # Kinolar ma'lumotlarini yuklash
        movies_db = load_data(MOVIES_FILE)
        
        if not movies_db or not isinstance(movies_db, list):
            bot.send_message(
                chat_id,
                "❌ <b>Xatolik!</b>\n\n"
                "Hozircha kinolar mavjud emas.",
                parse_mode="HTML"
            )
            return
        
        # Faqat dict bo'lganlari olib qolish
        movies_db = [m for m in movies_db if isinstance(m, dict)]
        
        # Kino ma'lumotlarini qidiruv (string va int ikkala formatda)
        movie = None
        for m in movies_db:
            if m.get("code") == movie_code or str(m.get("code")) == movie_code:
                movie = m
                break
        
        if not movie:
            bot.send_message(
                chat_id,
                f"❌ <b>Topilmadi!</b>\n\n"
                f"Kod <code>{movie_code}</code> bilan kino topilmadi.\n\n"
                f"Iltimos kod to'g'riligini tekshiring.",
                parse_mode="HTML"
            )
            return
        
        # Kinoni yuborish oldin validatsiya qilish
        file_id = movie.get('file_id')
        if not file_id:
            bot.send_message(
                chat_id,
                f"❌ <b>Xatolik!</b>\n\n"
                f"Kod <code>{movie_code}</code> kinosi buzilgan. Admin bilan bog'laning.",
                parse_mode="HTML"
            )
            return
        
        # Ko'rishlar sonini oshirish
        views_count = increment_views(movie_code)
        
        # Caption yaratish
        description = movie.get('description', 'Tavsif mavjud emas')
        caption = (
            f"<b>{description}</b>\n\n"
            f"👁 <b>Ko'rishlar:</b> {views_count}\n"
            f"📊 <b>Kod:</b> <code>{movie_code}</code>\n\n"
            f"❤️ Like bosib qo'ying!"
        )
        
        # Video yuborish
        if is_admin(user_id):
            # Adminlar uchun himoya yo'q
            bot.send_video(
                chat_id,
                file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=movie_keyboard(movie_code, user_id)
            )
        else:
            # Oddiy foydalanuvchilar uchun himoya bilan
            bot.send_video(
                chat_id,
                file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=movie_keyboard(movie_code, user_id),
                protect_content=True  # Screenshot va forward himoyasi
            )
            
    except Exception as e:
        bot.send_message(
            chat_id,
            f"❌ <b>Kinoni yuborishda xatolik!</b>\n\n"
            f"Xatolik: {str(e)[:100]}\n\n"
            f"Admin bilan bog'laning.",
            parse_mode="HTML"
        )
        print(f"[ERROR] Kino yuborishda xatolik: {str(e)}")

def start_delete_movie(user_id, bot):
    """Kino o'chirishni boshlash"""
    user_states[user_id] = {"action": "deleting_movie"}
    from keyboards import admin_keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("❌ Bekor qilish")
    bot.send_message(
        user_id,
        "🗑 <b>Kino o'chirish</b>\n\n"
        "O'chirmoqchi bo'lgan kino kodini kiriting:",
        parse_mode="HTML",
        reply_markup=markup
    )

def delete_movie_callback(user_id, code_text, bot):
    """Kinoni o'chirish"""
    from keyboards import admin_keyboard
    from database import load_data, save_data
    from config import MOVIES_FILE, VIEWS_FILE, LIKES_FILE
    
    # Bekor qilish tekshiruvi
    if code_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(
            user_id,
            "❌ <b>Amal bekor qilindi</b>",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        return
    
    try:
        code = code_text.strip()
        
        # Databases ni yuklash
        movies_db = load_data(MOVIES_FILE)
        views_db = load_data(VIEWS_FILE)
        likes_db = load_data(LIKES_FILE)
        
        # Agar movies_db dict bo'lsa (eski format), uni list'ga o'zgartirish
        if isinstance(movies_db, dict):
            movies_db = list(movies_db.values())
        
        # Agar movies_db list bo'lmasa, xatolik
        if not isinstance(movies_db, list):
            raise ValueError("Kinolar bazasi noto'g'ri formatda")
        
        # Kino topish va o'chirish
        original_count = len(movies_db)
        # Faqat dicts'ni filterlash
        movies_db = [m for m in movies_db if isinstance(m, dict) and m.get("code") != code]
        
        if original_count > len(movies_db):
            # Kino topildi va o'chirildi
            save_data(MOVIES_FILE, movies_db)
            
            # Ko'rishlar va likelarni ham o'chirish
            if isinstance(views_db, dict):
                views_db = {k: v for k, v in views_db.items() if k != code}
                save_data(VIEWS_FILE, views_db)
            
            if isinstance(likes_db, dict):
                likes_db = {k: v for k, v in likes_db.items() if k != code}
                save_data(LIKES_FILE, likes_db)
            
            bot.send_message(
                user_id,
                f"✅ <b>Kino o'chirildi!</b>\n\n"
                f"Kod: <code>{code}</code>\n"
                f"Ko'rishlar va likelar ham o'chirildi.",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            
            print(f"[OK] Kino o'chirildi: Code={code}, User={user_id}")
        else:
            bot.send_message(
                user_id,
                f"❌ <b>Xatolik!</b>\n\n"
                f"Kod <code>{code}</code> kodli kino topilmadi!",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>O'chirishda xatolik yuz berdi!</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Kino o'chirishda xatolik: {str(e)}")
    
    finally:
        user_states.pop(user_id, None)

def show_movies_list(user_id, bot):
    """Barcha kinolarning ro'yxatini ko'rsatish"""
    from database import load_data
    from config import MOVIES_FILE, VIEWS_FILE, LIKES_FILE
    from keyboards import admin_keyboard
    
    try:
        # Barcha bazalarni yuklash
        movies_db = load_data(MOVIES_FILE)
        views_db = load_data(VIEWS_FILE)
        likes_db = load_data(LIKES_FILE)
        
        # Data format tekshiruvi
        if isinstance(movies_db, dict):
            movies_db = list(movies_db.values())
        elif not isinstance(movies_db, list):
            movies_db = []
        
        # Faqat dicts
        movies_db = [m for m in movies_db if isinstance(m, dict)]
        
        if not isinstance(views_db, dict):
            views_db = {}
        if not isinstance(likes_db, dict):
            likes_db = {}
        
        # Kinolar mavjud emasligini tekshirish
        if not movies_db:
            bot.send_message(
                user_id,
                "📭 <b>Kinolar ro'yxati bo'sh!</b>\n\n"
                "Hozircha hech qanday kino qo'shilmagan.",
                parse_mode="HTML",
                reply_markup=admin_keyboard()
            )
            return
        
        # Ro'yxatni tayyorlash
        message_text = "🎬 <b>KINOLAR RO'YXATI</b>\n\n"
        message_text += f"📊 Jami kinolar: <b>{len(movies_db)}</b>\n\n"
        message_text += "─" * 50 + "\n\n"
        
        for idx, movie in enumerate(movies_db, 1):
            code = movie.get("code", "N/A")
            description = movie.get("description", "Tavsif yo'q")
            uploaded_at = movie.get("uploaded_at", "Noma'lum")
            uploaded_by = movie.get("uploaded_by", "Noma'lum")
            
            # Ko'rishlar va likelarni olish
            views_count = views_db.get(code, 0) if isinstance(views_db, dict) else 0
            likes_data = likes_db.get(code, []) if isinstance(likes_db, dict) else []
            likes_count = len(likes_data) if isinstance(likes_data, list) else 0
            
            # Yuklanish vaqtini formatlash
            try:
                if "(" in str(uploaded_at):
                    # datetime format
                    from datetime import datetime
                    dt = datetime.fromisoformat(str(uploaded_at).split('.')[0])
                    uploaded_at = dt.strftime("%d.%m.%Y %H:%M")
            except:
                uploaded_at = str(uploaded_at)[:20]
            
            # Har bir kino uchun ma'lumot
            message_text += f"<b>{idx}. Kod:</b> <code>{code}</code>\n"
            message_text += f"   <b>Nomi:</b> {description}\n"
            message_text += f"   👁 <b>Ko'rishlar:</b> {views_count}\n"
            message_text += f"   ❤️ <b>Likelar:</b> {likes_count}\n"
            message_text += f"   📅 <b>Yuklangan:</b> {uploaded_at}\n"
            message_text += f"   👤 <b>Admin:</b> {uploaded_by}\n"
            message_text += "\n"
            
            # Telegram mesaj uzunligini tekshirish (4096 belgidan ko'p bo'lmasligini tekshir)
            if len(message_text) > 3500:
                # Agar ko'p bo'lsa, hozirgi qismini yuborish
                bot.send_message(
                    user_id,
                    message_text,
                    parse_mode="HTML"
                )
                message_text = "<b>KINOLAR RO'YXATI (DAVOMI)</b>\n\n"
        
        # So'ngi qismni yuborish
        message_text += "─" * 50 + "\n"
        message_text += f"✅ Jami: <b>{len(movies_db)}</b> ta kino\n"
        
        bot.send_message(
            user_id,
            message_text,
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        
        print(f"[OK] Kinolar ro'yxati ko'rsatildi: Jami={len(movies_db)}, Admin={user_id}")
        
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ <b>Xatolik yuz berdi!</b>\n\n{str(e)[:100]}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
        print(f"[ERROR] Kinolar ro'yxatini ko'rsatishda xatolik: {str(e)}")