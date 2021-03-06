import ccxt
import iexfinance
import structlog
import pandas as pd
import random
import requests


class ExchangeInterface:
    CRYPTO_EXCHANGES = ['binance', 'bittrex', 'poloniex']

    def __init__(self, auto_load=True):
        self.logger = structlog.get_logger()
        self.crypto_tickers = []
        self.crypto_tickers_with_exchange = []
        self.stocks = []
        if auto_load:
            self.load_symbol_data()

    def load_symbol_data(self):
        self._load_crypto_exchange_symbols()
        self._load_stock_symbols()

    @property
    def crypto_exchanges(self):
        return ExchangeInterface.CRYPTO_EXCHANGES

    @property
    def all_symbols(self):
        return self.stocks + self.crypto_tickers + self.crypto_tickers_with_exchange

    @property
    def all_crypto_symbols(self):
        return self.crypto_tickers + self.crypto_tickers_with_exchange

    @staticmethod
    def max_amount(amount):
        if amount < 9:
            return amount
        return 9

    def get_random_symbols(self, amount=None):
        if amount:
            amount = ExchangeInterface.max_amount(amount)
            return random.choices(self.all_symbols, k=amount)
        else:
            return random.choice(self.all_symbols)

    def get_random_stock(self, amount=None):
        if amount:
            amount = ExchangeInterface.max_amount(amount)
            return random.choices(self.stocks, k=amount)
        else:
            return random.choice(self.stocks)

    def get_random_crypto(self, amount=None):
        if amount:
            amount = ExchangeInterface.max_amount(amount)
            return random.choices(self.all_crypto_symbols, k=amount)
        else:
            return random.choice(self.all_crypto_symbols)

    @classmethod
    def get_stock_top_gainers(cls, amount=None):
        df = pd.DataFrame(iexfinance.get_market_gainers())
        gainers = list(df['symbol'])
        if amount:
            amount = ExchangeInterface.max_amount(amount)
            return gainers[:amount]
        else:
            return gainers[0]

    @classmethod
    def get_stock_top_losers(cls, amount=None):
        df = pd.DataFrame(iexfinance.get_market_losers())
        losers = list(df['symbol'])
        if amount:
            amount = ExchangeInterface.max_amount(amount)
            return losers[:amount]
        else:
            return losers[0]

    @classmethod
    def get_fomoddio_api_superfiltered_coins(cls, amount=None):
        url = 'https://api.fomodd.io/superfilter'
        r = requests.get(url)
        data = r.json()
        binance = data['BINANCE']['coins']
        binance = [f'BINANCE:{coin}' for coin in binance]
        bittrex = data['BITTREX']['coins']
        bittrex = [f'BITTREX:{coin}' for coin in bittrex]

        coins = binance + bittrex
        if amount:
            amoutn = ExchangeInterface.max_amount(amount)
            return coins[:amount]
        else:
            return coins[0]

    def _load_crypto_exchange_symbols(self):
        for exchange__ in self.CRYPTO_EXCHANGES:
            self.logger.info(f'Downloading {exchange__} symbols.')
            crypto_tickers__ = []
            crypto_tickers_with_exchange__ = []
            try:
                assert exchange__ in ccxt.exchanges
                exchange = getattr(ccxt, exchange__)()
                markets = exchange.load_markets()
                coins = list(markets.keys())
                coins = [coin.replace('/', '').upper() for coin in coins]
                processsed = [f"{exchange__.upper()}:{coin}" for coin in coins]

                crypto_tickers__ += coins
                crypto_tickers_with_exchange__ += processsed

            except AssertionError:
                raise Exception(f'{exchange__} exchange doesnt exist.')

        self.crypto_tickers = list(set(crypto_tickers__))
        self.crypto_tickers_with_exchange = crypto_tickers_with_exchange__

    def _load_stock_symbols(self):
        self.logger.info(f'Downloading stock symbols.')
        df = pd.DataFrame(iexfinance.get_available_symbols())
        self.stocks = list(df[df.isEnabled == True]['symbol'])


if __name__ == '__main__':
    x = ExchangeInterface()
    print(x.get_stock_top_gainer(10))
    # print(x.crypto_tickers))b
    # print(x.crypto_tickers_with_exchange)
    # print(x.stocks)
    # print(x.all_symbols)
    # print(x.get_random_symbols(9))
    # print(x.get_random_stock(9))
    # print(x.get_random_crypto(9))
