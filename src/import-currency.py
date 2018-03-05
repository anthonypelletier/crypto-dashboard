# coding: utf-8
import json
import os
from datetime import datetime
import django
import requests
from download_icon import download_icon
from dashboard import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'dashboard.settings'
django.setup(settings)

from portfolio.models import CryptoCurrency, Price

euro_currency = None
if CryptoCurrency.objects.filter(id='eur').count() == 0:
    euro_currency = CryptoCurrency(id='eur', name='Euro', symbol='EUR')
    euro_currency.save()
    print('{} added !'.format(euro_currency))
else:
    euro_currency = CryptoCurrency.objects.get(id='eur')

eur_usd = json.loads(requests.get(url='https://api.fixer.io/latest', params=dict(symbols='USD')).text)
date = eur_usd['date']
price = eur_usd['rates']['USD']

if Price.objects.filter(currency=euro_currency, date=date).count() == 0:
    price = Price(
        currency=euro_currency,
        date=date,
        price=price,
        rank=0,
        change1h=0,
        change24h=0,
        change7d=0
    )
    price.save()
    euro_currency.last_price_id = price.id
    euro_currency.save()
    print('{} refreshed !'.format(price))

objs = requests.get(url="https://api.coinmarketcap.com/v1/ticker", params=dict(limit=10000)).json()
for obj in objs:
    id = obj['id']
    name = obj['name']
    symbol = obj['symbol']
    if CryptoCurrency.objects.filter(id=id).count() == 0:
        if CryptoCurrency.objects.filter(symbol=symbol).count() != 0:
            continue
        crypto_currency = CryptoCurrency(id=id, name=name, symbol=symbol, last_price=None)
        crypto_currency.save()
        print('{} added !'.format(crypto_currency))
        download_icon(crypto_currency)
    else:
        crypto_currency = CryptoCurrency.objects.get(id=id)

    if obj['last_updated'] is not None and obj['price_usd'] is not None:
        date = datetime.fromtimestamp(int(obj['last_updated']))
        price_usd = float(obj['price_usd'])
        rank = int(obj['rank'])
        change1h = 0
        change24h = 0
        change7d = 0
        if obj['percent_change_1h'] is not None:
            change1h = float(obj['percent_change_1h'])
        if obj['percent_change_24h'] is not None:
            change24h = float(obj['percent_change_24h'])
        if obj['percent_change_7d'] is not None:
            change7d = float(obj['percent_change_7d'])

        if Price.objects.filter(currency=crypto_currency, date=date).count() == 0:
            price = Price(
                currency=crypto_currency,
                date=date,
                price=price_usd,
                rank=rank,
                change1h=change1h,
                change24h=change24h,
                change7d=change7d
            )
            price.save()
            crypto_currency.last_price_id = price.id
            crypto_currency.save()
            print('{} refreshed !'.format(price))
