import logging
from traceback import format_stack
import aiogram.utils.markdown as md
import datetime
from datetime import datetime, timedelta
import psycopg2
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton



logging.basicConfig(level=logging.INFO)
# Replace YOUR_TOKEN_HERE with your actual bot token
bot = Bot(token='6284191295:AAE1ufNMdFkuYWrydmJluY4lQNftrUxAdyk')
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    fullname = State()
    phone = State()
    location = State()
    region = State()
    books = State()
    price = State()
    comment = State()
    fromwhere = State()
    confirmation=State(0)

stats = {
    "form_filled": {},
    "locations": {},
    "books": {},
    "total_price": 0,
    "fromwhere": {}
}
REGIONS = {
    "Toshkent shahri": ["Bektemir", "Chilonzor", "Mirzo-Ulug'bek", "Mirobod", "Olmazor", "Sergeli", "Shayxontohur", "Uchtepa", "Yakkasaray", "Yashnobod", "Chilanzar","Yunusobod"],
    "Toshkent viloyati": ["Angren shahri","Bekobod shahri","Buka tumani","Bo'ztonliq tumani","Ohangaron tumani","Chinaz tumani","Yangiyo'l tumani","Zangiota tumani","Qibray tumani","Parkent tumani","Pskent tumani","Chirchiq shahri","Quyi chirchiq","O'rtachirchiq tumani","Yuqori chirchiq","Yangi yo'l tumani","Olmaliq shahri","Oqqo'rg'on tumani"],
    "Andijon": ["Andijon shahri", "Andijon tumani", "Asaka tumani", "Balikchi tumani", "Baliqchi shahri", "Boz tumani", "Buloqboshi tumani", "Izboskan tumani", "Jalaquduq tumani", "Marhamat tumani", "Oltinko'l tumani","Paxtaobod tumani","Qorasuv shahri", "Qo'rg'on tumani", "Shahrixon tumani", "Ulugnor tumani", "Xo'jaobod tumani","Xonobod shahri"],
    "Buxoro": ["Buxoro shahri", "Buxoro tumani", "G'ijduvon tumani", "Jondor tumani", "Kogon shahri", "Kogon tumani", "Olot tumani", "Peshku tumani", "Qorako'l tumani", "Qorovulbozor tumani", "Romitan tumani", "Shofirkon tumani", "Vobkent tumani"],
    "Farg'ona": ["Beshariq tumani", "Bog'dod tumani","Buvayda","Farg'ona shahri", "Farg'ona tumani", "Furqat tumani","Qo'qon shahri","Qo'shtepa tumani","Quva shahri", "Quva tumani", "Marg'ilon shahri", "Oltiariq tumani", "Rishton shahri", "So'x tumani", "Toshloq tumani", "Uchko'prik tumani","Uzbekiston tumani", "Yozyovon tumani"],
    "Jizzax": ["Arnasoy tumani", "Baxmal tumani", "Do'stlik tumani", "Forish tumani", "G'allaorol tumani", "Jizzax shahri", "Jizzax tumani", "Mirzachul tumani", "Paxtakor tumani", "Yangiobod tumani", "Zafarobod tumani", "Zarbdor tumani","Zaraband","Zomin tumani"],
    "Namangan": ["Chust shahri", "Chust tumani","Chortoq", "Kosonsoy tumani", "Mingbuloq tumani", "Namangan shahri", "Namangan tumani", "Norin tumani", "Pop tumani", "To'rakurgon tumani", "Uchqo'rg'on shahri", "Uychi tumani","Yangi qo'rg'on"],
    "Navoiy": ["Karmana tumani", "Konimex tumani", "Navbahor tumani", "Navoiy shahri", "Navoiy tumani","Nurota tumani","Qiziltepa tumani", "Tomdi tumani", "Uchquduq tumani","Xatirchi tumani","Zarafshon shahri"],
    "Qashqadaryo": ["Chiroqchi shahri", "Dehqonobod tumani", "G'uzor tumani", "Kasbi tumani", "Kitob tumani","Koson tumani", "Mirishkor tumani", "Muborak shahri", "Muborak tumani", "Nishon tumani", "Qamashi tumani", "Qarshi shahri", "Qarshi tumani", "Shahrisabz shahri", "Yakkabog' tumani"],
    "Samarqand": ["Samarqand shahri","Samarqand tumani", "Bulung'ur", "Ishtixon", "Jomboy", "Kattaqo'rg'on", "Narpay", "Nurobod", "Oqdaryo", "Pastdarg'om","Paxtachi", "Payariq", "Qo'shrabot", "Toyloq","Urgut"],
    "Sirdaryo": ["Guliston", "Bo`ston","Boyovut", "Sardoba", "Sayhunobod", "Shirin", "Sirdaryo tumani","Xovos","Yangiyer"],
    "Surxondaryo": ["Termiz", "Angor", "Boysun","Bandixon", "Denov", "Jarqo`rg`on","Muzrobot","Oltinsoy", "Qiziriq", "Sherobod", "Sho`rchi", "Sariosiyo", "Uzun", "Qumqo'rg'on"],
    "Xorazm": ["Urganch shahri", "Yangiariq", "Urganch tumani", "Bogot tumani", "Gurlan tumani", "Shovot tumani", "Xonqa tumani","Qo'shko'pir","Xazorasp","Xiva","Yangibozor"],
    "Qoraqalpog'iston":["Amudaryo", "Beruniy","Chimboy","Ellikqala", "Kegeyli", "Moynaq", "Nukus", "Qonliko'l", "Qo'ng'irot", "Qorao'zak", "Shumanay", "Taxiatosh","Taxtako'pir","To'rtko'l","Xo'jayli"]
}


def get_db_conn():
    conn = psycopg2.connect(
        host="ec2-34-202-127-5.compute-1.amazonaws.com",
        database="ds9imtqqar70k",
        user="nfulnnpqksrohq",
        password="2e0471893ef613645d40742ee7e709e2f2d6a01a43f3f9de33b7b98fae9eb6c4"
    )
    return conn

counter = 0
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    await message.reply("🙋‍♂️ Assalomu alaykum! Iltimos, quyidagi savollarga javob bering:\n\n"
                          "👥Mijozning Ism va familiyasi?")
    await Form.fullname.set()
    await state.update_data(user_id=user_id)

@dp.message_handler(state=Form.fullname)
async def process_fullname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fullname'] = message.text

    await message.reply("📱 Telefon raqami:")
    await Form.phone.set()

@dp.message_handler(state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text

    # Create an inline keyboard with regions and districts
    region_keyboard = InlineKeyboardMarkup(row_width=1)
    for region in REGIONS:
        region_keyboard.add(InlineKeyboardButton(region, callback_data=f"region:{region}"))

    await message.reply("🗺️ Mijozning manzili:", reply_markup=region_keyboard)
    await Form.location.set()

@dp.callback_query_handler(lambda c: c.data.startswith("region:"), state=Form.location)
async def process_region(callback_query: types.CallbackQuery, state: FSMContext):
    region = callback_query.data.split(":")[1]
    district_keyboard = InlineKeyboardMarkup(row_width=1)
    for district in REGIONS[region]:
        district_keyboard.add(InlineKeyboardButton(district, callback_data=f"district:{district}"))
    async with state.proxy() as data:
        data['region'] = region
    await bot.send_message(callback_query.message.chat.id, "🗺️ Qaysi tuman:", reply_markup=district_keyboard)
    await Form.region.set()  # Change this line
    
@dp.callback_query_handler(lambda c: c.data.startswith("district:"), state=Form.region)
async def process_district(callback_query: types.CallbackQuery, state: FSMContext):
    district = callback_query.data.split(":")[1]
    async with state.proxy() as data:
        data['location'] = f"{data['region']}, {district}"
    stats['locations'][data['location']] = stats['locations'].get(data['location'], 0) + 1

    keyboard = InlineKeyboardMarkup(row_width=1)
    for book_name in ["Tizimlashtirish", "150 uslub", "440 amaliy keys", "Buyuk menejer","Savdogar ustozi","Good to great"]:
        button_text = f"{book_name} {'☑️' if book_name in data.get('books', []) else ' '}"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"books:{book_name}"))

    await bot.send_message(callback_query.message.chat.id, "📖 Kitoblarni tanlang:", reply_markup=keyboard)
    await Form.books.set()

@dp.callback_query_handler(lambda c: c.data.startswith("district:"), state=Form.region)
async def process_district(callback_query: types.CallbackQuery, state: FSMContext):
    district = callback_query.data.split(":")[1]
    async with state.proxy() as data:
        data['location'] = f"{data['region']}, {district}"
    stats['locations'][data['location']] = stats['locations'].get(data['location'], 0) + 1

    keyboard = InlineKeyboardMarkup(row_width=1)
    for book_name in ["Tizimlashtirish", "150 uslub", "440 amaliy keys", "Buyuk menejer","Savdogar ustozi","Good to great"]:
        button_text = f"{book_name} {'☑️' if book_name in data.get('books', []) else ' '}"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"books:{book_name}"))

    await bot.send_message(callback_query.message.chat.id, "📖 Kitoblarni tanlang:", reply_markup=keyboard)
    await Form.books.set()

@dp.callback_query_handler(lambda c: c.data.startswith("books:"), state=Form.books)
async def process_books(callback_query: types.CallbackQuery, state: FSMContext):
    book = callback_query.data.split(":")[1]
    action_text = ""

    async with state.proxy() as data:
        if "books" not in data:
            data["books"] = []

        if book == "select_all":
            data["books"] = ["Tizimlashtirish", "150 uslub", "440 amaliy keys", "Buyuk menejer","Savdogar ustozi","Good to great"]
            action_text = "✅ Barcha kitoblar tanlandi"
       
        else:
            if book in data["books"]:
                data["books"].remove(book)
                action_text = f"✅ Olib tashlandi: {book}"
            else:
                data["books"].append(book)
                action_text = f"☑️ Tanlandi: {book}"

        keyboard = InlineKeyboardMarkup(row_width=1)
        for book_name in ["Tizimlashtirish", "150 uslub", "440 amaliy keys", "Buyuk menejer", "Savdogar ustozi","Good to great"]:
            button_text = f"{book_name} {'☑️' if book_name in data['books'] else ' '}"
            keyboard.add(InlineKeyboardButton(button_text, callback_data=f"books:{book_name}"))

        # Add the "Select All" and "Deselect All" buttons
        keyboard.add(InlineKeyboardButton("Hammasi 📦", callback_data="books:select_all"))
        

        # Add the confirmation button
        keyboard.add(InlineKeyboardButton("Tasdiqlash ✅", callback_data="confirm"))

    await bot.edit_message_text(
        f"📖 Kitoblar nomlari:\n\n{action_text}",
        callback_query.message.chat.id,
        callback_query.message.message_id,
        reply_markup=keyboard,
    )

    await Form.books.set()

@dp.callback_query_handler(lambda c: c.data == "confirm", state=Form.books)
async def process_books_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        selected_books = data.get("books", [])
        for book in selected_books:
            stats["books"][book] = stats["books"].get(book, 0) + 1
    fromwhere_keyboard = InlineKeyboardMarkup(row_width=1)
    fromwhere_options = ["Telegram", "Instagram","Website","Facebook", "Boshqa"]
    for option in fromwhere_options:
        fromwhere_keyboard.add(InlineKeyboardButton(option, callback_data=option))
    await bot.send_message(callback_query.message.chat.id, "📌 Qayerdan xarid qilindi ?", reply_markup=fromwhere_keyboard)
    await Form.fromwhere.set()


@dp.callback_query_handler(lambda c: c.data in ['Telegram', 'Instagram','Website','Facebook','Boshqa'], state=Form.fromwhere)
async def process_fromwhere(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['fromwhere'] = callback_query.data
    stats['fromwhere'][callback_query.data] = stats['fromwhere'].get(callback_query.data, 0) + 1
    await bot.send_message(callback_query.message.chat.id, "💸 Narxi qancha:", reply_markup=types.ReplyKeyboardRemove())
    await Form.price.set()

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.price)
async def process_price_invalid(message: types.Message):
    await message.reply("Narxi faqat raqamdan iborat bo'lishi kerak. Iltimos, qayta urinib ko'ring.")
    return

@dp.message_handler(lambda message: message.text.isdigit(), state=Form.price)
async def process_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    stats['total_price'] += int(message.text)
    # Define inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton(text="Ha ✅", callback_data="yes")
    no_button = types.InlineKeyboardButton(text="No ❌", callback_data="no")
    keyboard.add(yes_button, no_button)
    await bot.send_message(message.chat.id, 'Kiritilgan narx: '+md.bold(data['price']+" Sum Ishonchingiz komilmi ? "), reply_markup=keyboard)
    await Form.confirmation.set()

@dp.callback_query_handler(lambda callback_query: callback_query.data.lower() not in ['yes', 'no'], state=Form.confirmation)
async def process_confirmation_invalid(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.message.chat.id, "Iltimos 'Ha' yoki 'Yo'q' ni tanlang")
    return

@dp.callback_query_handler(lambda callback_query: callback_query.data.lower() == 'yes', state=Form.confirmation)
async def process_confirmation_yes(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['confirmation'] = True
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.message.chat.id, "💬 Izoh qoldiring:")
    await Form.comment.set()

@dp.callback_query_handler(lambda callback_query: callback_query.data.lower() == 'no', state=Form.confirmation)
async def process_confirmation_no(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.message.chat.id, "Yangi narxi kiriting")
    await Form.price.set()


@dp.message_handler(commands=['stats'])
async def stats_command(message: types.Message):
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, phone, location, books, price, fromwhere, comment FROM stats_table"
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Calculate the statistics
        locations = [result[2].split(',')[0] for result in results]
        location_counts = {}
        for location in locations:
            if location not in location_counts:
                location_counts[location] = 0
            location_counts[location] += 1

        book_counts = {}
        for result in results:
            books = result[3].split(', ')
            for book in books:
                if book in book_counts:
                    book_counts[book] += 1
                else:
                    book_counts[book] = 1

        fromwhere_counts = {}
        for result in results:
            source = result[5]
            if source in fromwhere_counts:
                fromwhere_counts[source] += 1
            else:
                fromwhere_counts[source] = 1

        total_price = sum([result[4] for result in results])

        form_filled = {}
        for result in results:
            user_id = result[0]
            if user_id in form_filled:
                form_filled[user_id] += 1
            else:
                form_filled[user_id] = 1

        max_user_id = max(form_filled, key=form_filled.get)
        max_location = max(location_counts, key=location_counts.get)
        max_book = max(book_counts, key=book_counts.get)
        max_fromwhere = max(fromwhere_counts, key=fromwhere_counts.get)
        
        stats_text = f"📈 Statistika:\n\n🧑‍💼 Ko'p sotgan hodim: <code>{max_user_id}</code> (Zakazlari soni: <b>{form_filled[max_user_id]}</b>)\n\n" \
                     "🪪 Hodimlar ID si:\nArofat: <b>1228555019</b>, Zaxro: <b>5017822040</b>, Mohidil: <b>5860657656</b>, Maftuna: <b>5437329280</b>, Shaxzoda: <b>5828663130</b> \n\n" \
                     f"📍 Ko'p tashlangan lokatsiya: <b>{max_location}</b> \n" \
                     f"📚 Ko'p sotilgan kitob nomi: <b>{max_book}</b>\n" \
                     f"💰 Jami Narx: <b>{total_price}</b>\n" \
                     f"👥 Qaysi tarmoqdan ko'p zakaz tushgan: <b>{max_fromwhere}</b>\n\n"
        stats_text += '\n🗺️ Manzillar: \n'
        for location, count in location_counts.items():
            stats_text += f"📍{location}: <b>{count}</b> ta\n"
        stats_text += '\n📚 Kitoblar:\n'
        for book, count in book_counts.items():
            stats_text += f"📖 {book}: <b>{count}</b> ta\n"
        stats_text += '\n🌐 Tarmoqlar:\n'
        for source, count in fromwhere_counts.items():
            stats_text += f"🌎 {source}: <b>{count}</b> ta\n"
        await message.answer(stats_text, parse_mode=types.ParseMode.HTML) 

@dp.message_handler(commands=['userstats'])
async def user_stats_command(message: types.Message):
    # Connect to the database
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # Execute an SQL query to retrieve all user IDs
    cursor.execute("SELECT DISTINCT id FROM stats_table")
    user_ids = [result[0] for result in cursor.fetchall()]
    
    # Loop through all user IDs and calculate their statistics
    for user_id in user_ids:
        # Execute an SQL query to retrieve the user's submissions
        cursor.execute(
            "SELECT books, price, location FROM stats_table WHERE id=%s",
            (user_id,)
        )
        if user_id == 1228555019:
            names = "Arofat"
        elif user_id == 5017822040:
            names = "Zaxro"
        elif user_id == 5860657656:
            names = "Mohidil"
        elif user_id == 5437329280:
            names = "Maftuna"
        elif user_id == 5828663130:
            names = "Shaxzoda"
        elif user_id == 5149129536:
            names = "Hasanboy"
        elif user_id == 526302475:
            names = "Odilbek"   
        else:
            names= "unknow"
        results = cursor.fetchall()
        
        # Calculate the statistics for this user
        book_counts = {}
        total_price = 0
        locations = []
        for result in results:
            books = result[0].split(', ')
            for book in books:
                if book in book_counts:
                    book_counts[book] += 1
                else:
                    book_counts[book] = 1
            total_price += result[1]
            locations.append(result[2])
        
        # Format the message with the statistics
        stats_text = f"📈 Statistika uchun ma'lumotlar:\n\n"
        stats_text += f"🧑‍💼 Hodim Ismi: <code>{names}</code>\n"
        stats_text += f"📚 Siz <b>{sum(book_counts.values())}</b> ta kitob sotdingiz.\n"
        stats_text += f"💰 Jami narxi: <b>{total_price}</b> so'm.\n\n"
        stats_text += "📚 Sotilgan kitoblar:\n"
        for book, count in book_counts.items():
            stats_text += f"📖 {book}: <b>{count}</b> ta\n"
        
        # Send the message back to the user
        await message.answer(stats_text, parse_mode=types.ParseMode.HTML)
    
    # Close the database connection
    cursor.close()
    conn.close()

    
@dp.message_handler(state=Form.comment)
async def process_comment(message: types.Message, state: FSMContext):
    global counter
    async with state.proxy() as data:
        data['comment'] = message.text
        selected_books = data.get("books", [])
        books_str = ", ".join(selected_books)
        user_data = await state.get_data()
        user_id = user_data.get('user_id')
        if user_id == 1228555019:
            names = "Arofat"
        elif user_id == 5017822040:
            names = "Zaxro"
        elif user_id == 5860657656:
            names = "Mohidil"
        elif user_id == 5437329280:
            names = "Maftuna"
        elif user_id == 5828663130:
            names = "Shaxzoda"
        elif user_id == 5149129536:
            names = "Hasanboy"
        elif user_id == 526302475:
            names = "Odilbek"   
        else:
            names= "unknow"
        
    stats['form_filled'][user_id] = stats['form_filled'].get(user_id, 0) + 1

    async with state.proxy() as data:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stats_table (id, fullname, phone, location, books, price, fromwhere, comment) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, data['fullname'], data['phone'], data['location'], books_str, data['price'], data['fromwhere'], data['comment'])
        )
        conn.commit()
        cursor.close()
        conn.close()
    
    async with state.proxy() as data:
        counter += 1
        today = datetime.datetime.now()
        date_str = today.strftime('%d-%m-%Y')
        message_text = md.text(
            md.text(f"Zakaz #{counter} ✅ ID: #{user_id} Ism: {names}"),'\n','\n',
            md.text('👥 Ism va familiya: '), md.bold(data['fullname']), '\n',
            md.text('📱 Telefon raqami: '), md.bold(data['phone']), '\n',
            md.text('🗺️ Yashash joyi: '), md.bold(data['location']), '\n',
            md.text('📖 Kitoblar: '), md.bold(books_str), '\n',
            md.text('💸 Xarid narxi: '), md.bold(data['price']), '\n',
            md.text('📌 Qayerdan xarid qilindi: '), md.bold(data['fromwhere']), '\n',
            md.text('Izoh: '), md.bold(data['comment']), '\n\n',
            md.text('📅 Buyurtma sanasi: '), md.bold(date_str)
        )
        # Replace YOUR_CHANNEL_ID_HERE with your actual channel ID
        await bot.send_message(chat_id='-1001919687377', text=message_text, parse_mode=ParseMode.MARKDOWN)

    await state.finish()
    await message.reply(f"Rahmat! Sizning buyurtmangiz qabul qilindi ✅ Sizning ID: #{user_id}\n\n Zakaz qo'shish uchun 👉 /start bosing")

   
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)