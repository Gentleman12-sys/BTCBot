import telebot, requests
from fake_useragent import UserAgent
import threading
from bs4 import BeautifulSoup

token = 'BotAPI'
bot = telebot.TeleBot(token=token)

headers = {
    'User-Agent': UserAgent().random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

Coins = set()
response = requests.get(f'https://www.binance.com/en/markets', params={'p': 1}, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')
for g in soup.find_all('div', class_='css-1x8dg53'):
    Coins.add(g.text)
Coins = list(Coins)


def GetCoin():
    while True:
        all_users = set()
        with open('users.txt', 'r') as file:
            for i in file.read().split('\n'):
                all_users.add(str(i))
                all_users.add('\n')
        for coin in Coins:
            ua = UserAgent()
            alls = []

            url = 'https://www.binance.com/en/markets'
            try:
                mrkt_url = 'https://api.binance.com/api/v3/ticker/price'
                response = requests.get(url=mrkt_url, headers=headers, params={'symbol': coin + 'USDT'})
                response_json = response.json()
                price = '$' + response_json['price']
                alls.append(url + ': ' + price)
            except:
                alls.append(url + ': None')

            url = 'https://www.mexc.com/ru-RU/markets'
            try:
                mrkt_url = 'http://mexc.com/open/api/v2/market/ticker'
                response = requests.get(url=mrkt_url, headers=headers, params={'symbol': coin + '_USDT'})
                response_json = response.json()
                price = '$'+response_json['data'][0]['last']
                alls.append(url + ': ' + price)
            except:
                alls.append(url + ': None')

            url = 'https://www.okx.com/ru/markets/prices'
            try:
                mrkt_url = f'https://www.okx.com/api/v5/market/ticker?instId={coin}-USDT-SWAP'
                response = requests.get(url=mrkt_url, headers=headers)
                response_json = response.json()
                price = '$' + response_json['data'][0]['last']
                alls.append(url + ': ' + price)
            except:
                alls.append(url + ': None')

            url = 'https://www.kucoin.com/ru/markets'
            try:
                mrkt_url = 'https://openapi-sandbox.kucoin.com/api/v1/market/orderbook/level1'
                response = requests.get(url=mrkt_url, headers=headers, params={'symbol': coin + '-USDT'})
                response_json = response.json()
                price = '$' + response_json['data']['sell']
                alls.append(url + ': ' + price)
            except:
                alls.append(url + ': None')


            zena = []
            for coiner in alls:
                try:
                    zena.append(float(coiner[coiner.find('$')+1:]))
                except:
                    pass
            for coiner in alls:
                try:
                    if float(coiner[coiner.find('$')+1:]) == max(zena):
                        max_zen = coiner
                    elif float(coiner[coiner.find('$')+1:]) == min(zena):
                        min_zen = coiner
                except:
                    pass


            for user in all_users:
                if user not in ['', '\n']:
                    try:
                        max_Zen = float(max_zen[max_zen.find('$')+1:])
                        min_Zen = float(min_zen[min_zen.find('$')+1:])
                        razn = max_Zen - min_Zen
                        if min_Zen/max_Zen <= 0.99:
                            razn = round(razn, 10)
                            try:
                                if max_zen[:max_zen.find('$')] != min_zen[:min_zen.find('$')]:
                                    bot.send_message(user, '\n'.join([coin, max_zen + f' +${razn}', min_zen + f' -${razn}']))
                            except:
                                pass
                    except:
                        pass

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет {0.first_name} {0.last_name}\nЯ-Бот который поможет найти более оптимальные цены на нескольких биржах'.format(message.from_user, bot.get_me()), parse_mode='html')
    with open('users.txt', 'r') as all_user:
        if str(message.chat.id) not in all_user.read():
            with open('users.txt', 'a') as file:
                file.write(str(message.chat.id) + '\n')
            bot.send_message(message.chat.id, 'Добавил вас в базу данных!')

if __name__ == '__main__':
    threading.Thread(target=GetCoin).start()
    threading.Thread(target=bot.polling).start()