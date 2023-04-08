import time
import requests
import pandas as pd
import os

symbol = 'ETH'

# Список для хранения цен на ETH
prices = []
price = 0

# Необходимо заменить pathto/btcusdt.csv на путь до файла, где хранится истр.данные по BTCUSDT за тот же временной период.
btcusdt_path = 'path/to/btcusdt.csv'


# Функция для получения цены на ETH и добавления ее в список
def get_cryptocompare_price():
    response = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT')
    price = float(response.json()['USDT'])
    prices.append(price)
    print(f'Current ETHUSDT price: {price}')

# Функция для определения собственных движений цены ETH
def analyze_prices():
    # Создаем DataFrame с ценами на ETHUSDT
    dafr = pd.DataFrame(prices, columns=['ETHUSDT'])
    # Получаем цены на BTCUSDT с тем же временным интервалом
    if os.path.exists(btcusdt_path):
        dafr_btcusdt = pd.read_csv(btcusdt_path)
        dafr['BTCUSDT'] = dafr_btcusdt['close'].astype(float)[-len(prices):]
    else:
        print(f'Файл {btcusdt_path} для расчета корреляции не найден')
    # Рассчитываем корреляцию между ценами на ETHUSDT и BTCUSDT
    corr = dafr.corr()['ETHUSDT']['BTCUSDT']
    print(f'Корреляция между ETHUSDT и BTCUSDT: {corr}')
    # Исключаем влияние цены BTCUSDT на основе регрессионного анализа
    slope, intercept = pd.np.polyfit(dafr['BTCUSDT'], dafr['ETHUSDT'], 1)
    residual = dafr['ETHUSDT'] - (slope*dafr['BTCUSDT'] + intercept)
    # Определяем движение цены ETH
    std = residual[-30:].std()
    if std >= 0.01 * price:
        print(f'ETH собственное движение: {std}')
    else:
        print('Не хватает данных для анализа')

# Цикл получает с задержкой в секунду цены, а после каждые 60 минут оценивает разницу и выводит данные.
while True:
    get_cryptocompare_price()
    time.sleep(1)
    if len(prices) >= 30:
        analyze_prices()
    time.sleep(3600)
