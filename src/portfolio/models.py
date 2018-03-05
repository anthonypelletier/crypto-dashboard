from django.contrib.auth.models import User
from django.db import models


class CryptoCurrency(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=64)
    symbol = models.CharField(max_length=16, unique=True)
    last_price = models.OneToOneField(to='price', to_field='id', on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return "{} crypto-currency".format(self.name)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Crypto-currency'
        verbose_name_plural = 'Crypto-currencies'


class Price(models.Model):
    currency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    date = models.DateTimeField()
    price = models.FloatField()
    rank = models.IntegerField()
    change1h = models.FloatField()
    change24h = models.FloatField()
    change7d = models.FloatField()

    def __str__(self):
        return "{} price".format(self.currency)

    class Meta:
        verbose_name = 'Price'
        verbose_name_plural = 'Prices'


class Exchange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.CharField(max_length=16, choices=(
        ('BITFINEX', 'Bitfinex'),
        ('BITTREX', 'Bittrex'),
        ('BINANCE', 'Binance'),
        ('KUCOIN', 'KuCoin'),
        ('KRAKEN', 'Kraken'),
        ('NICEHASH', 'NiceHash'),
    ))
    key = models.CharField(max_length=128)
    secret = models.CharField(max_length=128)

    def __str__(self):
        return "{}'s {} API key".format(self.user, self.get_exchange_display())

    class Meta:
        verbose_name = 'Exchange'
        verbose_name_plural = 'Exchanges'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    address = models.CharField(max_length=128)

    def __str__(self):
        return "{}'s {} address".format(self.user, self.currency.name)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'


class Balance(models.Model):
    amount = models.FloatField()
    date = models.DateTimeField()


class ExchangeBalance(Balance):
    currency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)

    def __str__(self):
        return "{}'s {} exchange balance".format(self.exchange.user, self.currency.name)

    class Meta:
        verbose_name = 'Exchange Balance'
        verbose_name_plural = 'Exchanges Balances'


class AddressBalance(Balance):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    def __str__(self):
        return "{}'s {} address balance".format(self.address.user, self.address.currency.name)

    class Meta:
        verbose_name = 'Address Balance'
        verbose_name_plural = 'Addresses Balances'


class TokenBalance(Balance):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    currency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)

    def __str__(self):
        return "{}'s {} token balance".format(self.address.user, self.address.currency.name)

    class Meta:
        verbose_name = 'Token Balance'
        verbose_name_plural = 'Tokens Balances'
