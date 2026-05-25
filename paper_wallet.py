import json
import os

WALLET_FILE = "wallet.json"

default_wallet = {
    "cash": 1000000,

    "holdings": {
        "BTC/IDR": 0,
        "ETH/IDR": 0,
        "SOL/IDR": 0
    },

    "last_buy_price": {
        "BTC/IDR": 0,
        "ETH/IDR": 0,
        "SOL/IDR": 0
    },

    "last_trade_time": 0,

    "total_trades": 0,
    "winning_trades": 0,
    "losing_trades": 0
}

def load_wallet():

    if not os.path.exists(WALLET_FILE):

        save_wallet(default_wallet)

    with open(WALLET_FILE, "r") as file:

        return json.load(file)

def save_wallet(data):

    with open(WALLET_FILE, "w") as file:

        json.dump(data, file, indent=4)