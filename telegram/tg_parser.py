from dotenv import load_dotenv
import asyncio
import re
import pandas as pd
import os 
import datetime as dt
from datetime import timedelta
from collections import defaultdict

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)
 
# time format = '%Y-%m-%d %H:%M'

def remove_emoji(text):
    regrex_pattern = re.compile(pattern="["
                                        u"\U00000000-\U00000009"
                                        u"\U0000000B-\U0000001F"
                                        u"\U00000080-\U00000400"
                                        u"\U00000402-\U0000040F"
                                        u"\U00000450-\U00000450"
                                        u"\U00000452-\U0010FFFF"
                                        "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


async def parse_filter_news(channels: dict, KEYWORDS: list | tuple, filename: str, days_back: int, phone: str, api_id: str, api_hash: str):
    client = TelegramClient(phone, api_id, api_hash, )
    await client.start()
    if client.is_user_authorized() == False:
        await client.send_code_request(phone)
        await client.sign_in(phone, input('Enter the code: '))
    all_messages = defaultdict(list)
    for input_channel_id in channels.values():        

        offset_id = 0
        limit = 100
        
        history = await client(GetHistoryRequest(
            peer=input_channel_id,
            offset_id=offset_id,
            offset_date=dt.datetime.now() - timedelta(days=days_back),
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        messages = history.messages
        for message in messages:
            if message.message is not None:
                for j in KEYWORDS:
                    if j in message.message.lower():
                        all_messages['news'].append(remove_emoji(message.message).lower().replace('\n', ' '))
                        all_messages['time'].append(message.date.strftime('%Y-%m-%d %H:%M'))
        offset_id = messages[len(messages) - 1].id
        print(input_channel_id, 'success')
    all_messages = pd.DataFrame(all_messages)
    all_messages.to_csv('IMOEX_news.csv')
    print('data is saved')
    return all_messages
        
        
def main():
    load_dotenv()
    api_id, api_hash = os.getenv('tg_api_id'), os.getenv('tg_api_hash')
    username, phone = os.getenv('username'), os.getenv('phone')
    print(api_hash, api_id)
    """KEYWORDS = ('актив', 'акци', 'валют', 'волантильн', 'инвест', 'инструмент', 'компани', 'кризис', 'крипто',
                'ликвидн', 'облигаци', 'пассив', 'рынок', 'рыноч', 'торг', 'трейд', 'тренд', 'фонд')"""
                
    KEYWORDS = ('цб ', "фнс ", "фас ", "минюст ", "набиуллин", "ключевая ставка ", "мвф ",
                'мосбиржа', "бирж", "индекс мос", "imoex", "moex" )
    channels = {
        'РБК': -1001099860397,
        'суверенная Экономика': -1001551891830,
        'РБК_Инвест': -1001498653424,
        'Хулиномика': -1001380524958,
        'ПростаяЭкономика': -1001903548131,
        'InvestingCom': -1001369248634,
        'CBofRussia': -1001680634724,
        'ФАС России': -1001063810192,
        'Банкста': -1001136626166,
        "Газпромбанк Инвестиции": -1001056908994,
        "Сигналы РЦБ": -1001197210433,
        "Сам ты инвестор": -1001498653424,
        "Финансы | экономика": -1001985006088,
        "Дилер": -1001411960688,
        "Alex Butmanov": -1001068371661,
        "РИА Новости": -1001101170442,
        "ТАСС": -1001050820672,
        "Раньше всех. Ну почти": -1001394050290,
        "Илья Петров | Инвестиции": -1001469685510,
        'shitty': -1001154838044,
        'a': -1001441563903,
        'b': -1001203560567,
        'c': -1001364672287,
        'd': -1001140930248,
        'f': -1001107922757,
        'g': -1001308785417,
        'h': -1001043793945,
        'i': -1001486790946,
        'j': -1001197296889,
        'k': -1001344086554,
        'l': -1001199979298,
        'm': -1001321187596, 
        'n': -1001344892461,
        'o': -1001366670815,
        'p': -1001650095675,
        'q': -1001521490869,
        'r': -1001446666131,
        's': -1001231489696,
        't': -1001163804330,
        'u': -1001686704553,
        'v': -1001116202842,
        'w': -1001511455705,
        'x': -1001637846600,
        'y': -1002060032686,
    }
    
    news = asyncio.run(parse_filter_news(channels=channels,
                                  KEYWORDS=KEYWORDS,
                                  filename='IMOEX_news',
                                  days_back=120,
                                  phone=phone,
                                  api_hash=api_hash,
                                  api_id=api_id))
    
    print('data successfully saved')
    
if __name__ == '__main__':
    main()