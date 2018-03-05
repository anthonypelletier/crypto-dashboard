# coding: utf-8
import os
import django
import requests
import json
from datetime import datetime
from bitex import Bitfinex
from bitex.api.REST import BittrexREST, KrakenREST, BinanceREST
from kucoin.client import Client as KuCoin
from dashboard import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'dashboard.settings'
django.setup(settings)

from django.contrib.auth.models import User
from portfolio.models import Exchange, CryptoCurrency, ExchangeBalance, Address, AddressBalance, TokenBalance

bitfinex_symbols = {
    'USD': 'USDT',
    'DAT': 'DATA',
    'IOT': 'MIOTA',
    'DSH': 'DASH',
    'QTM': 'QTUM',
    'YYW': 'YOYOW',
    'QSH': 'QASH',

}

bittrex_symbols = {}

binance_symbols = {
    'YOYO': 'YOYOW',
    'BQX': 'ETHOS',
    'IOTA': 'MIOTA',
    'BCC': 'BCH'
}

kucoin_symbols = {}

kraken_symbols = {
    'ZEUR': 'EUR',
    'XXBT': 'BTC',
    'XXRP': 'XRP',
    'XETH': 'ETH',
    'XETC': 'ETC',
    'XXMR': 'XMR',
    'XZEC': 'ZEC'
}

token_symbols = {
    'ERC20': 'ERC20'
}

users = User.objects.all()
for user in users:
    addresses = Address.objects.filter(user=user)
    date = datetime.now()
    for address in addresses:
        amount = None
        if address.currency.id == 'bitcoin':
            amount = float(int(requests.get(
                url="https://blockchain.info/fr/q/addressbalance/{}".format(address.address)
            ).text) / 10 ** 8)
        elif address.currency.id == 'ethereum':
            amount = float(requests.get(url="https://api.etherscan.io/api", params=dict(
                module='account',
                action='balance',
                address=address.address
            )).json()['result']) / 10 ** 18
        elif address.currency.id == 'ripple':
            amount = 0
            for balance in requests.get(
                url="https://data.ripple.com/v2/accounts/{}/balances".format(address.address)
            ).json()['balances']:
                amount += float(balance['value'])
        if amount >= 0:
            address_balance = AddressBalance(
                address=address,
                amount=amount,
                date=date,
            )
            address_balance.save()
            print('{} refreshed !'.format(address_balance))

        if address.currency.id == 'ethereum':
            result = json.loads(requests.get(
                url="https://api.ethplorer.io/getAddressInfo/{}?apiKey=freekey".format(address.address)
            ).text)
            if 'tokens' in result:
                for token in result['tokens']:
                    symbol = token['tokenInfo']['symbol']
                    name = token['tokenInfo']['name']
                    if name in token_symbols.keys():
                        symbol = token_symbols[name]
                    if CryptoCurrency.objects.filter(symbol=symbol).count() == 0:
                        print('Symbol {} not found !'.format(symbol))
                        continue
                    currency = CryptoCurrency.objects.get(symbol=symbol)
                    amount = token['balance'] / pow(10, int(token['tokenInfo']['decimals']))
                    token_balance = TokenBalance(
                        address=address,
                        currency=currency,
                        amount=amount,
                        date=date,
                    )
                    token_balance.save()
                    print('{} refreshed !'.format(token_balance))

    exchanges = Exchange.objects.filter(user=user)
    for exchange in exchanges:
        if exchange.exchange == 'BITFINEX':
            api = Bitfinex(key=exchange.key, secret=exchange.secret)
            date = datetime.now()
            for obj in api.balances().json():
                if obj['type'] != 'exchange':
                    continue
                symbol = obj['currency'].upper()
                if symbol in bitfinex_symbols.keys():
                    symbol = bitfinex_symbols[symbol]
                if CryptoCurrency.objects.filter(symbol=symbol).count() == 0:
                    print('Symbol {} not found !'.format(symbol))
                    continue
                currency = CryptoCurrency.objects.get(symbol=symbol)
                amount = float(obj['amount'])
                exchange_balance = ExchangeBalance(
                    exchange=exchange,
                    currency=currency,
                    amount=amount,
                    date=date,
                )
                exchange_balance.save()
                print('{} refreshed !'.format(exchange_balance))
        elif exchange.exchange == 'BITTREX':
            api = BittrexREST(key=exchange.key, secret=exchange.secret)
            date = datetime.now()
            for obj in api.private_query('GET', 'account/getbalances').json()['result']:
                symbol = obj['Currency']
                if symbol in bittrex_symbols.keys():
                    symbol = bittrex_symbols[symbol]
                if CryptoCurrency.objects.filter(symbol=symbol).count() == 0:
                    print('Symbol {} not found !'.format(symbol))
                    continue
                currency = CryptoCurrency.objects.get(symbol=symbol)
                amount = float(obj['Balance'])
                exchange_balance = ExchangeBalance(
                    exchange=exchange,
                    currency=currency,
                    amount=amount,
                    date=date,
                )
                exchange_balance.save()
                print('{} refreshed !'.format(exchange_balance))
        elif exchange.exchange == 'BINANCE':
            api = BinanceREST(key=exchange.key, secret=exchange.secret)
            date = datetime.now()
            for obj in api.private_query('GET', 'v3/account').json()['balances']:
                symbol = obj['asset'].upper()
                if symbol in binance_symbols.keys():
                    symbol = binance_symbols[symbol]
                if CryptoCurrency.objects.filter(symbol=symbol).count() == 0:
                    print('Symbol {} not found !'.format(symbol))
                    continue
                currency = CryptoCurrency.objects.get(symbol=symbol)
                amount = float(obj['free'])
                exchange_balance = ExchangeBalance(
                    exchange=exchange,
                    currency=currency,
                    amount=amount,
                    date=date,
                )
                exchange_balance.save()
                print('{} refreshed !'.format(exchange_balance))
        elif exchange.exchange == 'KUCOIN':
            api = KuCoin(api_key=exchange.key, api_secret=exchange.secret)
            date = datetime.now()
            for obj in api.get_all_balances():
                symbol = obj['coinType']
                if symbol in kucoin_symbols.keys():
                    symbol = kucoin_symbols[symbol]
                if CryptoCurrency.objects.filter(symbol=symbol).count() == 0:
                    print('Symbol {} not found !'.format(symbol))
                    continue
                currency = CryptoCurrency.objects.get(symbol=symbol)
                amount = float(obj['balance'])
                exchange_balance = ExchangeBalance(
                    exchange=exchange,
                    currency=currency,
                    amount=amount,
                    date=date,
                )
                exchange_balance.save()
                print('{} refreshed !'.format(exchange_balance))
        elif exchange.exchange == 'KRAKEN':
            api = KrakenREST(key=exchange.key, secret=exchange.secret)
            date = datetime.now()
            wallet = api.private_query('POST', 'private/Balance').json()['result']
            for obj in wallet:
                symbol = obj
                if symbol in kraken_symbols.keys():
                    symbol = kraken_symbols[symbol]
                if CryptoCurrency.objects.filter(symbol=symbol).count() == 0:
                    print('Symbol {} not found !'.format(symbol))
                    continue
                currency = CryptoCurrency.objects.get(symbol=symbol)
                amount = wallet[obj]
                exchange_balance = ExchangeBalance(
                    exchange=exchange,
                    currency=currency,
                    amount=amount,
                    date=date,
                )
                exchange_balance.save()
                print('{} refreshed !'.format(exchange_balance))
        elif exchange.exchange == 'NICEHASH':
            r = requests.get(
                url="https://api.nicehash.com/api?method=balance&id={}&key={}".format(exchange.key, exchange.secret)
            )
            if r.status_code == 200:
                amount = json.loads(r.text)['result']['balance_confirmed']
                currency = CryptoCurrency.objects.get(symbol='BTC')
                exchange_balance = ExchangeBalance(
                    exchange=exchange,
                    currency=currency,
                    amount=amount,
                    date=date,
                )
                exchange_balance.save()
                print('{} refreshed !'.format(exchange_balance))
