from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from portfolio.models import Exchange, ExchangeBalance, Address, CryptoCurrency, Price


def __calculate_diff(value, change):
    return value - (value / (1 + change / 100))


@login_required
def portfolio(request):
    query = "SELECT " \
            "  portfolio_cryptocurrency.id, " \
            "  portfolio_cryptocurrency.name, " \
            "  (e.amount * portfolio_price.price) AS value " \
            "FROM ( " \
            "  SELECT d.id, SUM(d.amount) AS amount FROM ( " \
            "    ( " \
            "      SELECT " \
            "        portfolio_cryptocurrency.id AS id, " \
            "        SUM(portfolio_balance.amount) AS amount " \
            "      FROM portfolio_cryptocurrency " \
            "      LEFT JOIN portfolio_exchangebalance ON portfolio_exchangebalance.currency_id = portfolio_cryptocurrency.id " \
            "      LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_exchangebalance.balance_ptr_id " \
            "      LEFT JOIN portfolio_exchange ON portfolio_exchange.id = portfolio_exchangebalance.exchange_id " \
            "      JOIN ( " \
            "        SELECT portfolio_exchange.id, max(portfolio_balance.date) AS last_check FROM portfolio_exchange " \
            "        LEFT JOIN portfolio_exchangebalance ON portfolio_exchangebalance.exchange_id = portfolio_exchange.id " \
            "        LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_exchangebalance.balance_ptr_id " \
            "        WHERE portfolio_exchange.user_id = %s AND portfolio_balance.date NOTNULL " \
            "        GROUP BY portfolio_exchange.id " \
            "      ) AS a ON a.id = portfolio_exchange.id AND a.last_check = portfolio_balance.date " \
            "      WHERE portfolio_balance.amount > 0 " \
            "      GROUP BY portfolio_cryptocurrency.id " \
            "    ) " \
            "    UNION ( " \
            "      SELECT " \
            "        portfolio_cryptocurrency.id AS id, " \
            "        SUM(portfolio_balance.amount) AS amount " \
            "      FROM portfolio_cryptocurrency " \
            "      LEFT JOIN portfolio_address ON portfolio_address.currency_id = portfolio_cryptocurrency.id " \
            "      LEFT JOIN portfolio_addressbalance ON portfolio_addressbalance.address_id = portfolio_address.id " \
            "      LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_addressbalance.balance_ptr_id " \
            "      JOIN ( " \
            "        SELECT portfolio_address.id AS id, max(portfolio_balance.date) AS last_check FROM portfolio_address " \
            "        LEFT JOIN portfolio_addressbalance ON portfolio_addressbalance.address_id = portfolio_address.id " \
            "        LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_addressbalance.balance_ptr_id " \
            "        WHERE portfolio_address.user_id = %s " \
            "        GROUP BY portfolio_address.id " \
            "      ) AS b ON b.id = portfolio_address.id AND b.last_check = portfolio_balance.date " \
            "      WHERE portfolio_balance.amount > 0 " \
            "      GROUP BY portfolio_cryptocurrency.id " \
            "    ) " \
            "    UNION ( " \
            "      SELECT portfolio_cryptocurrency.id AS id, SUM(portfolio_balance.amount) AS amount " \
            "      FROM portfolio_cryptocurrency " \
            "      LEFT JOIN portfolio_tokenbalance ON portfolio_tokenbalance.currency_id = portfolio_cryptocurrency.id " \
            "      LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_tokenbalance.balance_ptr_id " \
            "      LEFT JOIN portfolio_address ON portfolio_address.id = portfolio_tokenbalance.address_id " \
            "      JOIN ( " \
            "        SELECT portfolio_address.id AS id, max(portfolio_balance.date) AS last_check FROM portfolio_tokenbalance " \
            "        LEFT JOIN portfolio_address ON portfolio_address.id = portfolio_tokenbalance.address_id " \
            "        LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_tokenbalance.balance_ptr_id " \
            "        WHERE portfolio_address.user_id = %s " \
            "        GROUP BY portfolio_address.id " \
            "      ) AS c ON c.id = portfolio_address.id AND c.last_check = portfolio_balance.date " \
            "      WHERE portfolio_balance.amount > 0 " \
            "      GROUP BY portfolio_cryptocurrency.id " \
            "    ) " \
            "  ) d " \
            "  GROUP BY d.id " \
            ") e " \
            "LEFT JOIN portfolio_cryptocurrency ON portfolio_cryptocurrency.id = e.id " \
            "LEFT JOIN portfolio_price ON portfolio_price.id = portfolio_cryptocurrency.last_price_id " \
            "ORDER BY (e.amount * portfolio_price.price) DESC"

    currencies = list()
    for currency in CryptoCurrency.objects.raw(query, params=[request.user.id, request.user.id, request.user.id]):
        currencies.append([currency.name, currency.value])
    return JsonResponse(currencies, safe=False)


@login_required
def index(request):
    total = 0
    diff_7d = 0
    diff_24h = 0
    diff_1h = 0
    refreshed_price = Price.objects.last().date

    query = "SELECT portfolio_exchange.id, max(portfolio_balance.date) AS last_check " \
            "FROM portfolio_exchange " \
            "LEFT JOIN portfolio_exchangebalance ON portfolio_exchangebalance.exchange_id = portfolio_exchange.id " \
            "LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_exchangebalance.balance_ptr_id " \
            "WHERE portfolio_exchange.user_id = %s AND portfolio_balance.date NOTNULL " \
            "GROUP BY portfolio_exchange.id"
    exchanges = list()
    for exchange in Exchange.objects.raw(query, params=[request.user.id]):
        exchange.total = 0
        query = "SELECT portfolio_exchangebalance.balance_ptr_id, " \
                "portfolio_price.rank AS rank, " \
                "portfolio_cryptocurrency.id AS id, " \
                "portfolio_cryptocurrency.name AS name, " \
                "portfolio_price.change7d AS change7d, " \
                "portfolio_price.change24h AS change24h, " \
                "portfolio_price.change1h AS change1h, " \
                "portfolio_price.price AS price, " \
                "portfolio_balance.amount AS amount, " \
                "(portfolio_price.price * portfolio_balance.amount) AS value " \
                "FROM portfolio_exchangebalance " \
                "LEFT JOIN portfolio_balance " \
                "ON portfolio_balance.id = portfolio_exchangebalance.balance_ptr_id " \
                "LEFT JOIN portfolio_cryptocurrency " \
                "ON portfolio_cryptocurrency.id = portfolio_exchangebalance.currency_id " \
                "LEFT JOIN portfolio_price " \
                "ON portfolio_price.id = portfolio_cryptocurrency.last_price_id " \
                "WHERE portfolio_exchangebalance.exchange_id = %s " \
                "AND amount > 0 AND (portfolio_price.price * portfolio_balance.amount) > 0.01 " \
                "AND portfolio_balance.date = %s " \
                "ORDER BY portfolio_price.rank ASC"
        balances = ExchangeBalance.objects.raw(query, params=[exchange.id, exchange.last_check])
        exchange.balances = list(balances)
        for balance in exchange.balances:
            exchange.total += balance.value
            balance.diff7d = __calculate_diff(balance.value, balance.change7d)
            balance.diff24h = __calculate_diff(balance.value, balance.change24h)
            balance.diff1h = __calculate_diff(balance.value, balance.change1h)
            diff_7d += balance.diff7d
            diff_24h += balance.diff24h
            diff_1h += balance.diff1h
        exchanges.append(exchange)
        total += exchange.total

    address_q = "SELECT portfolio_addressbalance.balance_ptr_id, " \
                "portfolio_price.rank AS rank, " \
                "portfolio_cryptocurrency.id AS id, " \
                "portfolio_cryptocurrency.name AS name, " \
                "portfolio_price.change7d AS change7d, " \
                "portfolio_price.change24h AS change24h, " \
                "portfolio_price.change1h AS change1h, " \
                "portfolio_price.price AS price, " \
                "portfolio_balance.amount AS amount, " \
                "(portfolio_price.price * portfolio_balance.amount) AS value, " \
                "tmp.last_check " \
                "FROM portfolio_addressbalance " \
                "LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_addressbalance.balance_ptr_id " \
                "JOIN ( " \
                "SELECT portfolio_address.id AS id, max(portfolio_balance.date) AS last_check " \
                "FROM portfolio_address " \
                "LEFT JOIN portfolio_addressbalance ON portfolio_addressbalance.address_id = portfolio_address.id " \
                "LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_addressbalance.balance_ptr_id " \
                "WHERE user_id = %s " \
                "GROUP BY portfolio_address.id) AS tmp " \
                "ON portfolio_addressbalance.address_id = tmp.id " \
                "AND portfolio_balance.date = tmp.last_check " \
                "LEFT JOIN portfolio_address " \
                "ON portfolio_address.id = portfolio_addressbalance.address_id " \
                "LEFT JOIN portfolio_cryptocurrency " \
                "ON portfolio_cryptocurrency.id = portfolio_address.currency_id " \
                "LEFT JOIN portfolio_price " \
                "ON portfolio_price.id = portfolio_cryptocurrency.last_price_id " \
                "WHERE amount > 0 AND (portfolio_price.price * portfolio_balance.amount) > 0.01 " \
                "ORDER BY portfolio_price.rank ASC"

    token_q = "SELECT portfolio_tokenbalance.balance_ptr_id, " \
              "portfolio_price.rank AS rank, " \
              "portfolio_cryptocurrency.id AS id, " \
              "portfolio_cryptocurrency.name AS name, " \
              "portfolio_price.change7d AS change7d, " \
              "portfolio_price.change24h AS change24h, " \
              "portfolio_price.change1h AS change1h, " \
              "portfolio_price.price AS price, " \
              "portfolio_balance.amount AS amount, " \
              "(portfolio_price.price * portfolio_balance.amount) AS value, " \
              "tmp.last_check " \
              "FROM portfolio_tokenbalance " \
              "LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_tokenbalance.balance_ptr_id " \
              "JOIN ( " \
              "SELECT portfolio_address.id AS id, max(portfolio_balance.date) AS last_check " \
              "FROM portfolio_address " \
              "LEFT JOIN portfolio_tokenbalance ON portfolio_tokenbalance.address_id = portfolio_address.id " \
              "LEFT JOIN portfolio_balance ON portfolio_balance.id = portfolio_tokenbalance.balance_ptr_id " \
              "WHERE user_id = %s " \
              "GROUP BY portfolio_address.id) AS tmp " \
              "ON portfolio_tokenbalance.address_id = tmp.id " \
              "AND portfolio_balance.date = tmp.last_check " \
              "LEFT JOIN portfolio_address " \
              "ON portfolio_address.id = portfolio_tokenbalance.address_id " \
              "LEFT JOIN portfolio_cryptocurrency " \
              "ON portfolio_cryptocurrency.id = portfolio_tokenbalance.currency_id " \
              "LEFT JOIN portfolio_price " \
              "ON portfolio_price.id = portfolio_cryptocurrency.last_price_id " \
              "WHERE amount > 0 AND (portfolio_price.price * portfolio_balance.amount) > 0.01 " \
              "ORDER BY portfolio_price.rank ASC"

    addresses = list()
    address_total = 0
    for address in Address.objects.raw(address_q, params=[request.user.id]):
        address_total += address.value
        address.diff7d = __calculate_diff(address.value, address.change7d)
        address.diff24h = __calculate_diff(address.value, address.change24h)
        address.diff1h = __calculate_diff(address.value, address.change1h)
        diff_7d += address.diff7d
        diff_24h += address.diff24h
        diff_1h += address.diff1h
        addresses.append(address)

    for token in Address.objects.raw(token_q, params=[request.user.id]):
        address_total += token.value
        token.diff7d = __calculate_diff(token.value, token.change7d)
        token.diff24h = __calculate_diff(token.value, token.change24h)
        token.diff1h = __calculate_diff(token.value, token.change1h)
        diff_7d += token.diff7d
        diff_24h += token.diff24h
        diff_1h += token.diff1h
        addresses.append(token)

    total += address_total

    return render(request, 'index.html', {
        'exchanges': exchanges,
        'addresses': addresses,
        'address_total': address_total,
        'refreshed_price': refreshed_price,
        'total': total,
        'diff_7d': diff_7d,
        'diff_24h': diff_24h,
        'diff_1h': diff_1h
    })
