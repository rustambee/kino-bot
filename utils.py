# Vositachi funksiyalar

from datetime import datetime, timedelta
from database import load_data, save_data
from config import (
    USERS_FILE, PREMIUM_FILE, VIEWS_FILE, LIKES_FILE, 
    ADMINS_FILE, CHANNELS_FILE
)

def is_admin(user_id):
    """Admin ekanligini tekshirish"""
    try:
        admins_list = load_data(ADMINS_FILE)
        if isinstance(admins_list, list):
            return user_id in admins_list
        return False
    except:
        return False

def save_user(user_id, username, first_name):
    """Foydalanuvchini saqlash (dict format)"""
    try:
        users_db = load_data(USERS_FILE)
        # Dict bo'lmasa, dict'ga o'zgartirish
        if not isinstance(users_db, dict):
            users_db = {}
        
        # Foydalanuvchini saqlash
        users_db[str(user_id)] = {
            "id": user_id,
            "username": username,
            "first_name": first_name
        }
        save_data(USERS_FILE, users_db)
    except Exception as e:
        print(f"[ERROR] Foydalanuvchi saqlashda xatolik: {str(e)}")

def check_premium(user_id):
    """Premium statusni tekshirish"""
    try:
        premium_db = load_data(PREMIUM_FILE)
        user_id_str = str(user_id)
        
        if user_id_str in premium_db:
            expire_date = datetime.fromisoformat(premium_db[user_id_str]['expire_date'])
            if datetime.now() < expire_date:
                return True
            else:
                # Muddati o'tgan premium'ni o'chirish
                del premium_db[user_id_str]
                save_data(PREMIUM_FILE, premium_db)
        return False
    except Exception as e:
        print(f"[ERROR] Premium tekshirishda xatolik: {str(e)}")
        return False

def check_subscription(user_id, bot):
    """Obuna statusni tekshirish - FAQAT OCHIQ KANALLAR majburiy"""
    try:
        # Admin yoki premium bo'lsa - obuna kerak emas
        if is_admin(user_id) or check_premium(user_id):
            return []
        
        channels_db = load_data(CHANNELS_FILE)
        not_subscribed = []
        
        # Agar channels bazasi bo'sh yoki tuzilishi noto'g'ri bo'lsa
        if not channels_db or not isinstance(channels_db, dict):
            return not_subscribed
        
        # Agar channels bo'sh bo'lsa hech qanday kanal majurmis emas
        if len(channels_db) == 0:
            return not_subscribed
        
        # Har bir kanalni tekshirish - FAQAT OCHIQ KANALLAR MAJBURIY
        for channel_id, channel_data in channels_db.items():
            if not isinstance(channel_data, dict):
                continue
            
            is_private = channel_data.get("is_private", False)
            
            # Mahfiy kanallarni o'tkazib yuborish - IXTIYORIY
            if is_private:
                continue
                
            invite_link = channel_data.get("invite_link")
            channel_name = channel_data.get("name", "Kanal")
            chat_id = channel_data.get("chat_id")
            
            if not chat_id or not invite_link:
                continue
            
            try:
                # Foydalanuvchining ochiq kanal a'zosimami tekshirish
                status = bot.get_chat_member(chat_id, user_id).status
                # Agar member yoki member emasalar (administrator, creator) bo'lsa ok
                if status in ['left', 'kicked']:
                    not_subscribed.append({
                        "chat_id": chat_id,
                        "name": channel_name,
                        "invite_link": invite_link,
                        "is_private": False
                    })
            except Exception as member_error:
                # Agar bot foydalanuvchini tekshira olmasa, uni obunamasiz deb hisobla (xavfsizlik)
                not_subscribed.append({
                    "chat_id": chat_id,
                    "name": channel_name,
                    "invite_link": invite_link,
                    "is_private": False
                })
        
        return not_subscribed
    except Exception as e:
        print(f"[ERROR] Obuna tekshirishda xatolik: {str(e)}")
        return []


def get_all_channels_for_display(bot):
    """Barcha kanallarni olinadi (majburiy va ixtiyoriy) - Ko'rsatish uchun"""
    try:
        channels_db = load_data(CHANNELS_FILE)
        if not channels_db or not isinstance(channels_db, dict):
            return []
        
        channels_list = []
        for channel_id, channel_data in channels_db.items():
            if not isinstance(channel_data, dict):
                continue
            
            channel_info = {
                "chat_id": channel_data.get("chat_id", channel_id),
                "name": channel_data.get("name", "Kanal"),
                "invite_link": channel_data.get("invite_link", ""),
                "is_private": channel_data.get("is_private", False)
            }
            
            if channel_info["invite_link"]:
                channels_list.append(channel_info)
        
        return channels_list
    except Exception as e:
        print(f"[ERROR] Kanallarni olishda xatolik: {str(e)}")
        return []

def increment_views(movie_code):
    """Ko'rishlar sonini oshirish"""
    try:
        views_db = load_data(VIEWS_FILE)
        if not isinstance(views_db, dict):
            views_db = {}
        
        if movie_code not in views_db:
            views_db[movie_code] = 0
        views_db[movie_code] += 1
        save_data(VIEWS_FILE, views_db)
        return views_db[movie_code]
    except Exception as e:
        print(f"[ERROR] Ko'rishlar soni oshirishda xatolik: {str(e)}")
        return 0

def toggle_like(movie_code, user_id):
    """Like/unlike"""
    try:
        likes_db = load_data(LIKES_FILE)
        if not isinstance(likes_db, dict):
            likes_db = {}
        
        if movie_code not in likes_db:
            likes_db[movie_code] = []
        
        # likes_db[movie_code] bir roʻyxat boʻlsa:
        if isinstance(likes_db[movie_code], list):
            if user_id in likes_db[movie_code]:
                likes_db[movie_code].remove(user_id)
                liked = False
            else:
                likes_db[movie_code].append(user_id)
                liked = True
        else:
            # Agar roʻyxat boʻlmasa, uni yaratish
            likes_db[movie_code] = [user_id]
            liked = True
        
        save_data(LIKES_FILE, likes_db)
        likes_count = len(likes_db[movie_code]) if isinstance(likes_db[movie_code], list) else 0
        return liked, likes_count
    except Exception as e:
        print(f"[ERROR] Like bo'lishda xatolik: {str(e)}")
        return False, 0
