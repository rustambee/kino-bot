# Bot Tuzilishi

Kino rejissorni bot modular tuzilmaga ajratilgan. Quyida har bir faylning maqsadi ko'rsatilgan:

## 📁 Fayllar Tuzilmasi

### 1. **config.py** - Konfiguratsiya
- Bot tokenini va konstantalarni o'z ichiga oladi
- Instagram havolasi, admin ID, karta raqami va boshqalar
- Ma'lumotlar bazasi fayllarining nomlarini belgilaydi

### 2. **database.py** - Ma'lumotlar bazasi operatsiyalari
- JSON fayllardan ma'lumot yuklash va saqlash
- Tasdiqlanmagan kanallar bilan ishlash
- Kanalni tasdiqlash va rad etish funksiyalari

### 3. **utils.py** - Vositachi funksiyalar
- Admin tekshirish
- Premium statusni tekshirish
- Obuna statusni tekshirish
- Likes/Ko'rishlar soni bilan ishlash

### 4. **keyboards.py** - Tugmalar va menyular
- Kinoni ko'rsatish tugmalari (like, ulashish)
- Obuna bo'lish tugmalari
- Premium tariflar tugmalari
- Admin va oddiy foydalanuvchi menyulari

### 5. **admin_handlers.py** - Admin funksiyalari
- Admin qo'shish va o'chirish
- Tasdiqlanmagan kanallar ro'yxati
- Adminlar ro'yxatini ko'rsatish

### 6. **channel_handlers.py** - Kanal boshqaruvi
- Ochiq va mahfiy kanallarni qo'shish
- Kanallarni o'chirish
- Kanal tasdiqlanmagan so'rovlarini yuborish adminlarga

### 7. **movie_handlers.py** - Kino boshqaruvi
- Kino yuklash (kod va fayl)
- Kino tavsifini qabul qilish
- Kino o'chirish

### 8. **main.py** - Asosiy bot fayli
- Barcha handlerlari ro'yxatiga olish
- Callback funksiyalarini joylashtirish
- Bot ishga tushirish

## 🎯 Kanal Tasdiqlanmasi Tizimi

### Mahfiy kanallar qo'shish:
1. Admin "➕ Kanal qo'shish" tugmasini bosadi
2. Admin mahfiy kanal linkini yubor adi (masalan: `https://t.me/+xxxxx`)
3. Kanal nomini kiritadi
4. So'rov tasdiqlanmasi uchun boshqa adminlarga yuboriladi
5. Admin ✅ yoki ❌ tugmasini bosadi
6. Tasdiqlansa, kanal majburiy obuna ro'yxatiga qo'shiladi

### Qayta tashkilantirilgan kanal talabi tizimi:
- Foydalanuvchi "➕ Kanal qo'shish" yoki obuna bo'lish paytida kanalga qoshilish so'rovini yuboradi
- Admin soʻrovni tasdiqlasa, foydalanuvchi subscribed deb hisoblanadi
- Agar foydalanuvchi so'rovni qabul qilsa (inline tugmasini bosasa), to'liq subscribe bo'lgan bo'ladi

## 📊 Ma'lumotlar Bazasi Fayllari

- `movies.json` - Kinolar ma'lumotlari
- `users.json` - Foydalanuvchilar ma'lumotlari
- `channels.json` - Tasdiqlangan kanallar
- `pending_channels.json` - Tasdiqlanmagan kanallar
- `premium.json` - Premium a'zolar
- `admins.json` - Adminlar
- `views.json` - Ko'rishlar soni
- `likes.json` - Likelar

## 🚀 Ishga tushirish

```bash
python main.py
```

## ✨ Yangi Xususiyatlar

✅ Modular kod tuzilmasi  
✅ Mahfiy kanal qo'shish bilan admin tasdiqlanmasi  
✅ Kanal so'rovi tizimi  
✅ Xavfsiz kino uzatishi  
✅ Broadcast xabar yuborish  
✅ Premium obuna tizimi
