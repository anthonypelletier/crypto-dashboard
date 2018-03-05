from django.contrib import admin
from portfolio.models import Exchange, CryptoCurrency, Address, ExchangeBalance, AddressBalance, TokenBalance, Price


class CryptoCurrencyAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']


class AddressAdmin(admin.ModelAdmin):
    autocomplete_fields = ['currency']

admin.site.register(Exchange)
admin.site.register(CryptoCurrency, CryptoCurrencyAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(ExchangeBalance)
admin.site.register(AddressBalance)
admin.site.register(TokenBalance)
admin.site.register(Price)
