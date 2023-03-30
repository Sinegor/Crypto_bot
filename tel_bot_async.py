import time 
import logging
import os
import dotenv
import datetime
import asyncio



from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from messages import START_MESSAGE
from async_script import set_starting_data, subscribe, string_handling, get_previous_week_btc_data_price_1
from models import today_pure_price_mov, global_pure_price_mov, price
from keyboards import keyb_client


load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
sin_bot = Bot(TOKEN)
sin_disp = Dispatcher(sin_bot)



@sin_disp.message_handler(commands=['start'])
async def start_handler (message: types.Message):
    user_id = message.from_id
    user_name = message.from_user.full_name
    logging.info(f'{time.asctime()}: start work whith user {user_id} {user_name}')
    await message.reply(START_MESSAGE.format(user_name), reply_markup=keyb_client)

# Получаем данные о ценовых движениях битка за прошедшую неделю:
@sin_disp.message_handler(commands=["history"])
async def history_handler(message):
    user_id = message.from_id
    user_name = message.from_user.full_name
    logging.info(f'{time.asctime()}: start work whith user {user_id} {user_name}')
    responce_data = await get_previous_week_btc_data_price_1()
    await sin_bot.send_message(user_id, responce_data)


# Получаем следующие данные: 1. Информацию о чистом ценовом активе за прошедшую неделю. 2. Подписку на отслеживание цены данного актива
# и вычисление чистого движения. 3. По истечению суток мониторинга добавление новых данных в глобальные недельные сведения.
@sin_disp.message_handler()
async def st_handler_1 (message: types.Message):
    global price, today_pure_price_mov, global_pure_price_mov
    user_id = message.from_id
    current_date = datetime.datetime.now().date()
    coin = string_handling(message.text)
    try:
        await message.reply(f'Last week data on net percentage movement of {coin} asset compared to bitcoin movement: {await set_starting_data(coin)}')
        i =1
        while i<20:
            subscribe_response = await subscribe(coin, current_date)
            await message.reply(subscribe_response)
            i+=1
            await asyncio.sleep(90)
    except KeyError as e:
        await message.reply('Error, no such coin. Check spelling correctly.')
        print(e)
   
   
if __name__ == '__main__':
    executor.start_polling(sin_disp,timeout=200)
    
   