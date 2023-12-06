import time 
import logging
import os
import  dotenv
import datetime
import asyncio
import pandas


from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageIsTooLong


from messages import START_MESSAGE, RANGE_OF_SEARCH, SEARCH_OF_START_PUMP, START_SEARCHING
from async_script_fsm_implement import set_starting_data, subscribe, string_handling, \
                                 subscribe_1, check_actual_price_mov_data, \
                                 check_actual_alt_state, check_actual_btc_history,\
                                 check_historical_pure_price_mov_data, clearning_str, handler_history_data,\
                                 get_choose_token, get_list_percentage_change, get_list_tokens_data,\
                                 get_coin_price_percentage_change, set_time_range, get_time_range,\
                                 get_pumping_tokens
                                 

from keyboards import keyb_client, keyb_client_1, keyb_client_2, keyb_client_3, keyb_client_4
from models import SymbolCoinError


load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
sin_bot = Bot(TOKEN)
my_storage = MemoryStorage()
sin_disp = Dispatcher(sin_bot, storage=my_storage,)

class Testing_state(StatesGroup):
    get_btc_historical_data = State()
    request_period_btc_async = State()
    request_search_range = State()
    get_search_alt_for_trading = State()
    request_search_point_pump = State()
    get_alt_historical_data = State()
    get_pure_alt_move = State()
    request_subscribe = State()
    subscribing = State()
    

@sin_disp.message_handler(commands=['start'], state='*')
async def start_handler (message: types.Message, state:FSMContext):
    user_id = message.from_id
    user_name = message.from_user.full_name
    logging.info(f'{time.asctime()}: start work whith user {user_id} {user_name}')
#Formation of Memory Storage structure for new user:
    async with state.proxy() as data:
        data['price']= {  
        'bitcoin_history':[],
        }   
        data['active_coin'] = None
        await sin_bot.send_message(user_id, START_MESSAGE.format(user_name), reply_markup=keyb_client)



@sin_disp.message_handler(commands=["history"], state="*")
async def history_handler(message, state:FSMContext):
    """
    Custom button processing "Histoty". 
    We get data about price movements of the bitcoin for the last week
    """
    try:
        user_id = message.from_id
        user_name = message.from_user.full_name
        logging.info(f'{time.asctime()}: start work whith user {user_id} {user_name}')
        await check_actual_btc_history(state)
        async with state.proxy() as data:
            key_for_last_btc_price = (datetime.datetime.fromtimestamp(time.time()-84600).date()).strftime('%d-%m-%Y')
            last_btc_price = data['price']['bitcoin_history'][-1][key_for_last_btc_price]
            await check_actual_alt_state('bitcoin', state, last_btc_price)
            crud_data = data['price']['bitcoin_history']
            clear_data = handler_history_data(crud_data)
            await sin_bot.send_message(user_id, '<b>Bitcoin history:</b>', parse_mode='HTML')
            await sin_bot.send_message(user_id, clear_data)
            await sin_bot.send_message (user_id, "Specify the name of the coin for which you want to get information")
    # Caching Bitcoin Data to Retrieve History from Memory Storage if Repeated Requests:
            await Testing_state.get_btc_historical_data.set()
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")

@sin_disp.message_handler(commands=["search"], state="*")
async def search_begining_handler(message, state:FSMContext):
    """
    Start the mode of searching for promising alts on the basis of missynchronization
    with the bitcoin movement. Initially it is necessary to choose a time period of search.
    """
    user_id = message.from_id
    await sin_bot.send_message(user_id, 
                               START_SEARCHING,
                                reply_markup=keyb_client_4)
    await Testing_state.request_period_btc_async.set()





@sin_disp.message_handler(commands=["24h"], state=Testing_state.request_period_btc_async)
async def start_search_24h_handler(message:types.bot_command, state:FSMContext):
    """
    At this stage it is necessary to determine the field of search of 
    alts within their rating by market capitalization.  
 
    """
    user_id = message.from_id
    user_name = message.from_user.full_name
    
    await set_time_range(state,message.text) #save the selected time period in MemoryStorage
    await sin_bot.send_message(user_id, RANGE_OF_SEARCH.format(user_name), reply_markup=keyb_client_2)
    await Testing_state.request_search_range.set()

@sin_disp.message_handler(commands=["week"], state=Testing_state.request_period_btc_async)
async def start_search_1d_handler(message:types.bot_command, state:FSMContext):
    """
    At this stage it is necessary to determine the field of search of 
    alts within their rating by market capitalization.  
 
    """
    user_id = message.from_id
    user_name = message.from_user.full_name
    
    await set_time_range(state,message.text) #save the selected time period in MemoryStorage
    await sin_bot.send_message(user_id, RANGE_OF_SEARCH.format(user_name), reply_markup=keyb_client_2)
    await Testing_state.request_search_range.set()

@sin_disp.message_handler(commands=["1h"], state=Testing_state.request_period_btc_async)
async def start_search_1h_handler(message:types.bot_command, state:FSMContext):
    """
    At this stage it is necessary to determine the field of search of 
    alts within their rating by market capitalization.  
 
    """
    user_id = message.from_id
    user_name = message.from_user.full_name
    
    await set_time_range(state,message.text) #save the selected time period in MemoryStorage
    await sin_bot.send_message(user_id, RANGE_OF_SEARCH.format(user_name), reply_markup=keyb_client_2)
    await Testing_state.request_search_range.set()

@sin_disp.message_handler(commands=["pump"], state=Testing_state.request_period_btc_async)
async def start_pump_search_handler(message:types.message, state:FSMContext):
    user_id = message.from_id
    user_name = message.from_user.full_name
    
    # await set_time_range(state,message.text) #save the selected time period in MemoryStorage
    await sin_bot.send_message(user_id, SEARCH_OF_START_PUMP.format(user_name), reply_markup=keyb_client_2)
    await Testing_state.request_search_point_pump.set()


@sin_disp.message_handler(commands=["cancel"], state=Testing_state.request_period_btc_async)
async def handler_cancel_5 (message: types.Message, state:FSMContext):
    """
    State of Memory Storage reset to None
    """
    user_id = message.from_id
    await Testing_state.first()
    await sin_bot.send_message(user_id, text='Вы вернулись на первоначальный экран', reply_markup=keyb_client)


@sin_disp.message_handler(commands=["cancel"], state=Testing_state.request_search_range)
async def handler_cancel_5 (message: types.Message, state:FSMContext):
    """
    State of Memory Storage reset to None
    """
    user_id = message.from_id
    await Testing_state.first()
    await sin_bot.send_message(user_id, text='Вы вернулись на первоначальный экран', reply_markup=keyb_client)


@sin_disp.message_handler(commands=["cancel"], state=Testing_state.request_search_point_pump)
async def handler_cancel_5 (message: types.Message, state:FSMContext):
    """
    State of Memory Storage reset to None
    """
    user_id = message.from_id
    await Testing_state.first()
    await sin_bot.send_message(user_id, text='Вы вернулись на первоначальный экран', reply_markup=keyb_client)


@sin_disp.message_handler(state=Testing_state.request_search_point_pump)
async def search_pump_point(message:types.message, state:FSMContext):
    user_id = message.from_id
    user_name = message.from_user.full_name
    #logging.info(f'{time.asctime()}: start work whith user {user_id} {user_name}')
    range_alt = message.text    
    SEARCH_PERIOD = '1h,24h,7d'
    try:
        bitcoin_price_mov = await get_coin_price_percentage_change('bitcoin', SEARCH_PERIOD)
        tokens_list = await get_list_tokens_data(250, range_alt, SEARCH_PERIOD)
        crud_data = get_pumping_tokens(tokens_list, bitcoin_price_mov)
        if type(crud_data)==list:
            result_data = handler_history_data(crud_data)
        else:
            result_data = crud_data
        await sin_bot.send_message(user_id, result_data, parse_mode='HTML', reply_markup=keyb_client)
        await Testing_state.finish()
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")




@sin_disp.message_handler(state=Testing_state.request_search_range)
async def search_handler(message:types.message, state:FSMContext):
    """
    Will search by simultaneous from selected time intervals
    """
    user_id = message.from_id
    user_name = message.from_user.full_name
    #logging.info(f'{time.asctime()}: start work whith user {user_id} {user_name}')
    amount_alts, range_alt = message.text.split(' ')
    cur_period = await get_time_range(state)    
    try:
        bitcoin_price_mov = await get_coin_price_percentage_change('bitcoin', cur_period)
        tokens_list = await get_list_tokens_data(amount_alts, range_alt, cur_period)
        crud_data = get_choose_token(tokens_list, bitcoin_price_mov,cur_period)
        if type(crud_data)== list:
            result_data = handler_history_data(crud_data)
        else:
            result_data = crud_data
        await sin_bot.send_message(user_id, result_data, parse_mode='HTML', reply_markup=keyb_client)
        await Testing_state.finish()
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")
    except MessageIsTooLong as e:
        await sin_bot.send_message(user_id, f"Итоговый результат слишком объёмный, сократите зону поиска",reply_markup=keyb_client)
        #await Testing_state.finish()





@sin_disp.message_handler(commands=['alt_subscribe'], state=Testing_state.get_pure_alt_move)
async def handler_request_subscribe (message: types.Message, state:FSMContext):
    """
    Handler "custom keyboard button "alt_subscribe", suggests to specify the interval 
    through which the user will receive new data
    """
    user_id = message.from_id
    await sin_bot.send_message(user_id, "Укажите c какой переиодичностью вы хотели бы получать информацию. От 30 до 300 минут", reply_markup=keyb_client_2)
    await Testing_state.request_subscribe.set()


@sin_disp.message_handler(commands=['home'], state=Testing_state.get_pure_alt_move)
async def handler_cancel_1 (message: types.Message, state:FSMContext):
    """
    State of Memory Storage reset to 'get_btc_historical_data'
    """
    user_id = message.from_id
    await Testing_state.get_btc_historical_data.set()
    await sin_bot.send_message(user_id, text='Вы вернулись на первоначальный экран', reply_markup=keyb_client)


@sin_disp.message_handler(commands=['alt_history'], state=Testing_state.get_pure_alt_move)
async def st_handler_1 (message: types.Message, state:FSMContext):
    """
    Handler "custom keyboard button "alt_history". We receive data for a week on net price movement altcoin. 
    In the event that coin lags far behind Bitcoin or is far ahead of it, emojis are added. 
    """
    try:
        user_id = message.from_id
        await check_actual_btc_history(state)
        async with state.proxy() as data:
            coin = data['active_coin']
        result = await check_historical_pure_price_mov_data(coin, state)
        async with state.proxy() as data:
            if result == False:
                crud_data = data['price'][coin]['clean_price_movement']['history']
                clear_data = handler_history_data(crud_data)
                last_data:str = crud_data[-1][f'{datetime.datetime.fromtimestamp(time.time()-86400).strftime("%d-%m-%Y")}']
                data_float = float(last_data[0:-1])
                await sin_bot.send_message(user_id, f'<b>Pure price movement history of {coin}:</b>', parse_mode='HTML')
                await sin_bot.send_message(user_id, text=clear_data)
                if data_float >3:
                   await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqItkQYwRYaRvKyla92ymdZWPCaJEhAAC3AsAAt8K6Uo-ZVuZEObjpC8E')
                elif data_float <-3:
                    await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqH1kQYuBMBnCMxkG3TbC9gdz9mADGAACKwADspiaDvxK5u_xtoLRLwQ')
            else:
                [data['price'][coin]['clean_price_movement']['history'].append(value) for value in result]
                crud_data = data['price'][coin]['clean_price_movement']['history']
                clear_data = handler_history_data(crud_data)
                last_data:str = crud_data[-1][f'{datetime.datetime.fromtimestamp(time.time()-86400).strftime("%d-%m-%Y")}']
                data_float = float(last_data[0:-1])
                await sin_bot.send_message(user_id, f'<b>Pure price movement history of {coin}:</b>', parse_mode='HTML')
                await sin_bot.send_message(user_id, clear_data)
                if data_float >3:
                   await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqItkQYwRYaRvKyla92ymdZWPCaJEhAAC3AsAAt8K6Uo-ZVuZEObjpC8E')
                elif data_float <-3:
                    await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqH1kQYuBMBnCMxkG3TbC9gdz9mADGAACKwADspiaDvxK5u_xtoLRLwQ')
    except KeyError as e:
        await message.reply("Такая монета не поддерживается, проверьте правильность написания", reply_markup=keyb_client)
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")
    except SymbolCoinError as e:
        my_message = f' Попробуйте следующее название/ия:\n<b>{e}</b>'
        await sin_bot.send_message(user_id, my_message, reply_markup=keyb_client, parse_mode='HTML')


@sin_disp.message_handler(state=None)
async def handler_get_alt_data_1 (message: types.Message, state:FSMContext):
    """
    Request a pure price movement aitcoin for last day from the state "None". Primary.
    """
    user_id = message.from_id
    coin = string_handling(message.text)
    try:
        yesterday_data = await set_starting_data(coin)
        await check_actual_alt_state(coin, state, yesterday_data['alt'])
        await check_actual_alt_state('bitcoin', state, yesterday_data['btc'])
        crud_subscribe_response = await subscribe(coin, state)
        subscribe_response = clearning_str(crud_subscribe_response.create_basic_responce())
        await sin_bot.send_message(user_id, subscribe_response, parse_mode="HTML", reply_markup=keyb_client_1)
        await Testing_state.get_pure_alt_move.set()
        if crud_subscribe_response.current_move_price_data['Pure price movement data']>3:
            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqItkQYwRYaRvKyla92ymdZWPCaJEhAAC3AsAAt8K6Uo-ZVuZEObjpC8E')
        elif crud_subscribe_response.current_move_price_data['Pure price movement data']<-3:
            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqH1kQYuBMBnCMxkG3TbC9gdz9mADGAACKwADspiaDvxK5u_xtoLRLwQ')
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")
    except SymbolCoinError as e:
        my_message = f' Попробуйте следующее название/ия:\n<b>{e}</b>'
        await sin_bot.send_message(user_id, my_message, reply_markup=keyb_client, parse_mode='HTML')
    except KeyError as e:
        await sin_bot.send_message(user_id, "Такая монета не поддерживается, проверьте правильность написания", 
                                   reply_markup=keyb_client)
    

@sin_disp.message_handler(state=Testing_state.get_btc_historical_data)
async def handler_get_alt_data_2 (message: types.Message, state:FSMContext):
    """
    Request a pure price movement aitcoin for last day from the state "get_btc_historical_data".
    """
    user_id = message.from_id
    coin = string_handling(message.text)
    try:
        await check_actual_alt_state(coin, state)
        crud_subscribe_response = await subscribe(coin, state)
        subscribe_response = clearning_str(crud_subscribe_response.create_basic_responce())
        await sin_bot.send_message(user_id, subscribe_response, parse_mode="HTML", reply_markup=keyb_client_1)
        await Testing_state.get_pure_alt_move.set()
        if crud_subscribe_response.current_move_price_data['Pure price movement data']>3:
            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqItkQYwRYaRvKyla92ymdZWPCaJEhAAC3AsAAt8K6Uo-ZVuZEObjpC8E')
        elif crud_subscribe_response.current_move_price_data['Pure price movement data']<-3:
            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqH1kQYuBMBnCMxkG3TbC9gdz9mADGAACKwADspiaDvxK5u_xtoLRLwQ')
    except KeyError as e:
        await message.reply("Такая монета не поддерживается, проверьте правильность написания", reply_markup=keyb_client)
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")
    except SymbolCoinError as e:
        my_message = f' Попробуйте следующее название/ия:\n<b>{e}</b>'
        await sin_bot.send_message(user_id, my_message, reply_markup=keyb_client, parse_mode='HTML')
 


@sin_disp.message_handler(state=Testing_state.get_pure_alt_move)
async def handler_get_alt_data_3 (message: types.Message, state:FSMContext):
    """
    Request a pure price movement aitcoin for last day from the state "get_pure_alt_move"
    """
    try:
        user_id = message.from_id
        coin = string_handling(message.text)
        await check_actual_alt_state(coin, state)
        crud_subscribe_response = await subscribe(coin, state)
        subscribe_response = clearning_str(crud_subscribe_response.create_basic_responce())
        await sin_bot.send_message(user_id, subscribe_response, parse_mode="HTML", reply_markup=keyb_client_1)
        await Testing_state.get_pure_alt_move.set()
        if crud_subscribe_response.current_move_price_data['Pure price movement data']>3:
            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqItkQYwRYaRvKyla92ymdZWPCaJEhAAC3AsAAt8K6Uo-ZVuZEObjpC8E')
        elif crud_subscribe_response.current_move_price_data['Pure price movement data']<-3:
            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqH1kQYuBMBnCMxkG3TbC9gdz9mADGAACKwADspiaDvxK5u_xtoLRLwQ')
    except KeyError as e:
        await message.reply("Такая монета не поддерживается, проверьте правильность написания", keyb_client)
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")
    except SymbolCoinError as e:
        my_message = f' Попробуйте следующее название/ия:\n<b>{e}</b>'
        await sin_bot.send_message(user_id, my_message, reply_markup=keyb_client, parse_mode='HTML')
 
   
@sin_disp.message_handler(commands=['cancel'], state=Testing_state.subscribing)
async def handler_cancel_1 (message: types.Message, state:FSMContext):
    """
    Unsubscribe from Coin tracking
    """
    user_id = message.from_id
    async with state.proxy() as data:
        coin = data['active_coin']
        data['price'][coin]['clean_price_movement']['active'] = False
    await Testing_state.get_btc_historical_data.set()
    await sin_bot.send_message(user_id, text='Подписка отменена. \
                                       Введите название актива, по которому вы хотите получить информацию', reply_markup=keyb_client)



@sin_disp.message_handler(commands=['alt_history'], state=Testing_state.subscribing)
async def st_handler_1 (message: types.Message, state:FSMContext):
    """
    Getting information on the coin last week from the state "subscribing"
    """
    try:
        user_id = message.from_id
        await check_actual_btc_history(state)
        async with state.proxy() as data:
            coin = data['active_coin']
        result = await check_historical_pure_price_mov_data(coin, state)
        async with state.proxy() as data:
            if result == False:
                global_history =data['price'][coin]['clean_price_movement']['history']   
                today_history = data['price'][coin]['clean_price_movement'] ['today_mov']
            else:
                [data['price'][coin]['clean_price_movement']['history'].append(value) for value in result]
                global_history = data['price'][coin]['clean_price_movement']['history']
                today_history = data['price'][coin]['clean_price_movement'] ['today_mov']
            clear_data_gl_history = handler_history_data(global_history)
            clear_data_today_data = ''
            today_mov_data = [clear_data_today_data+str(data)+'\n' for data in today_history]
            today_mov_response = handler_history_data(today_mov_data)
            await sin_bot.send_message(user_id, f"Недельная история чистового ценового движения {coin}:")
            await sin_bot.send_message(user_id, clear_data_gl_history)
            await sin_bot.send_message(user_id, f"История сегодняшних изменений чистового ценового движения{coin}:")
            await sin_bot.send_message(user_id, today_mov_response)
    except KeyError as e:
        await message.reply("Такая монета не поддерживается, проверьте правильность написания", reply_markup=keyb_client)
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")
    except SymbolCoinError as e:
        my_message = f' Попробуйте следующее название/ия:\n<b>{e}</b>'
        await sin_bot.send_message(user_id, my_message, reply_markup=keyb_client, parse_mode='HTML') 
        

@sin_disp.message_handler(state=Testing_state.subscribing)
async def handler_get_alt_data_2 (message: types.Message, state:FSMContext):
    """
    Getting the coin data for the previous day from the state "subscribing"(when another coin is tracked)
    """

    try:
        user_id = message.from_id
        coin = string_handling(message.text)
        await check_actual_alt_state(coin, state)
        crud_subscribe_response = await subscribe(coin, state)
        subscribe_response = clearning_str(crud_subscribe_response.create_basic_responce())
        await Testing_state.get_pure_alt_move.set()
        await sin_bot.send_message(user_id, subscribe_response, parse_mode="HTML", reply_markup=keyb_client_1)
        if crud_subscribe_response.current_move_price_data['Pure price movement data']>3:
            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqItkQYwRYaRvKyla92ymdZWPCaJEhAAC3AsAAt8K6Uo-ZVuZEObjpC8E')
        elif crud_subscribe_response.current_move_price_data['Pure price movement data']<-3:
            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqH1kQYuBMBnCMxkG3TbC9gdz9mADGAACKwADspiaDvxK5u_xtoLRLwQ')
    except KeyError as e:
        await message.reply("Такая монета не поддерживается, проверьте правильность написания", reply_markup=keyb_client)
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")
    except SymbolCoinError as e:
        my_message = f' Попробуйте следующее название/ия:\n<b>{e}</b>'
        await sin_bot.send_message(user_id, my_message, reply_markup=keyb_client, parse_mode='HTML')
 

@sin_disp.message_handler(state=Testing_state.request_subscribe, commands=['cancel'])
async def handler_subscribe (message: types.Message,  state:FSMContext):
    """
    Reset subscription procedure from "request_subscribe" status (subscription not yet established)
    """
    user_id = message.from_id
    async with state.proxy() as data:
        coin = data['active_coin']
        data['price'][coin]['clean_price_movement']['active'] = False
    await Testing_state.get_pure_alt_move.set()
    await sin_bot.send_message(user_id, "Подписка отменена!", reply_markup=keyb_client_1)



@sin_disp.message_handler(state=Testing_state.request_subscribe)
async def handler_subscribe (message: types.Message, state:FSMContext):
    """
    Getting a subscription time interval from the user and its design
    """
    user_id = message.from_id
    current_date = datetime.datetime.now()
    try:
        value = int(message.text)
        if value > 300 or value < 30:
            await sin_bot.send_message(user_id, 'Вы ввели некорректные данные. Введите цифру от 30 до 300')
            
        else:
            async with state.proxy() as data:
                coin = data['active_coin']
                data['price'][coin]['clean_price_movement']['active'] = True
            await sin_bot.send_message(user_id,text='Подписка успешно оформлена. На данный момент вы можете запросить информацию\
                                       по иным альтам')
            await Testing_state.get_pure_alt_move.set()
            while (True):
                await asyncio.sleep(value*60)
                async with state.proxy() as data:
                    if data['price'][coin]['clean_price_movement']['active']==True:
                        data['active_coin'] = coin
                        await check_actual_price_mov_data(coin, state) 
                        
                        response_inst = await subscribe_1(coin, state)
                        crud_data_for_response = response_inst.create_basic_responce()
                        subscribe_response = clearning_str(crud_data_for_response)
                        await Testing_state.subscribing.set()
                        await sin_bot.send_message(user_id, subscribe_response, parse_mode="HTML", reply_markup=keyb_client_1)
                        if response_inst.current_move_price_data['Pure price movement data']>3:
                            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqItkQYwRYaRvKyla92ymdZWPCaJEhAAC3AsAAt8K6Uo-ZVuZEObjpC8E')
                        elif response_inst.current_move_price_data['Pure price movement data']<-3:
                            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqH1kQYuBMBnCMxkG3TbC9gdz9mADGAACKwADspiaDvxK5u_xtoLRLwQ')
                        await sin_bot.send_message (user_id, text='Если хотите отменить подписку нажмите /cancel.', reply_markup=keyb_client_3)
                    else:
                        response_inst = await subscribe_1(coin, state)
                        crud_data_for_response = response_inst.create_basic_responce()
                        subscribe_response = clearning_str(crud_data_for_response)
                        await Testing_state.get_btc_historical_data.set()        
                        await sin_bot.send_message(user_id, subscribe_response, parse_mode="HTML", reply_markup=keyb_client_1)
                        if response_inst.current_move_price_data['Pure price movement data']>3:
                            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqItkQYwRYaRvKyla92ymdZWPCaJEhAAC3AsAAt8K6Uo-ZVuZEObjpC8E')
                        elif response_inst.current_move_price_data['Pure price movement data']<-3:
                            await sin_bot.send_sticker(user_id, 'CAACAgIAAxkBAAEIqH1kQYuBMBnCMxkG3TbC9gdz9mADGAACKwADspiaDvxK5u_xtoLRLwQ')
                        await sin_bot.send_message (user_id, text='Подписка отменена', reply_markup=keyb_client_1)
                        break
    except ValueError as e:
        await sin_bot.send_message(user_id, 'Вы ввели некорректные данные. Введите цифру от 30 до 300')
    except TimeoutError as e:
        await sin_bot.send_message(user_id, f"Повторите запрос через {e.args[0]} секунд")


if __name__ == '__main__':
    executor.start_polling(sin_disp,timeout=200, skip_updates=False,)     
