# coding: utf-8
import os
import django
from lxml import html
import requests
import shutil
from dashboard import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'dashboard.settings'
django.setup(settings)

from portfolio.models import CryptoCurrency


def download_icon(currency):
    path = os.path.join(os.getcwd(), 'static', 'img')
    if not os.path.exists(path):
        os.makedirs(path)
    img_filename = currency.id + '.png'
    if os.path.isfile(os.path.join(path, img_filename)):
        return

    req = requests.get(url="https://coinmarketcap.com/currencies/{}".format(currency.id))
    content = html.fromstring(req.content)
    url = content.xpath("string(//img[@class='currency-logo-32x32']/@src)")
    if len(url) == 0:
        print('Error: Can\'t get icon url from {} :('.format(currency))
        return

    response = requests.get(url, stream=True)
    with open(os.path.join(os.getcwd(), 'static', 'img', currency.id + '.png'), 'wb') as img_file:
        shutil.copyfileobj(response.raw, img_file)
    print('Icon from {} downloaded !'.format(currency))


def download_all_icons():
    currencies = CryptoCurrency.objects.all()
    for currency in currencies:
        download_icon(currency)

download_all_icons()
