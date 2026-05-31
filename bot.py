import ccxt
import csv

from datetime import datetime, timedelta

from config import (
    API_KEY,
    SECRET,
    PAIRS,
    TELEGRAM_TOKEN,
    CHAT_ID
)

from strategy import check_signal

import paper_wallet

wallet = paper_wallet.load_wallet()

import requests

exchange = ccxt.indodax({
    'apiKey': API_KEY,
    'secret': SECRET,
})

def send_telegram(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_TOKEN}/sendMessage"
    )

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)

def log_trade(action, pair, price):

    with open('trades.csv', mode='a', newline='') as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now(),
            pair,
            action,
            price,
            wallet["cash"],
            wallet["holdings"][pair]
        ])

def run_bot():

    print("\nChecking market...")
    telegram_report = "Checking market...\n\n"

    try:

        for pair in PAIRS:

            print(f"\nScanning {pair}...")

            ohlcv = exchange.fetch_ohlcv(
                pair,
                timeframe='1h',
                limit=250
            )

            ticker = exchange.fetch_ticker(pair)

            current_price = ticker['last']

            signal, rsi, ema200 = check_signal(ohlcv)

            # # COOLDOWN CHECK
            # if wallet["last_trade_time"]:

            #     cooldown = (
            #         datetime.now()
            #         - wallet["last_trade_time"]
            #     )

            #     if cooldown < timedelta(hours=3):

            #         print("Cooldown active.")

            #         signal = "HOLD"

            print(f"Price: Rp{current_price}")
            print(f"Signal: {signal}")

            telegram_report += (
                 f"{pair}\n"
                 f"RSI: {round(rsi, 2)}\n"
                f"EMA200: {round(ema200, 2)}\n"
                f"Price: Rp{current_price}\n"
                f"Signal: {signal}\n\n"
            )

            # BUY
            if signal == "BUY" and wallet["cash"] > 0:

                amount_btc = (
                    wallet["cash"] / current_price
                )

                wallet["holdings"][pair] = amount_btc
                wallet["cash"] = 0

                wallet["last_buy_price"][pair] = current_price

                print(
                    f"SIMULATED BUY {pair} at Rp{current_price}"
                )

                send_telegram(
                    f"BUY SIGNAL\n{pair}\nPrice: Rp{current_price}"
                )

                log_trade(
                    "BUY",
                    pair,
                    current_price
                )

                wallet["last_trade_time"] = datetime.now().isoformat()
                paper_wallet.save_wallet(wallet)

            # SELL MANAGEMENT
            elif wallet["holdings"][pair] > 0:

                buy_price = wallet["last_buy_price"][pair]

                change_percent = (
                    (current_price - buy_price)
                    / buy_price
                ) * 100

                print(
                    f"Current P/L: {change_percent:.2f}%"
                )

                # TAKE PROFIT
                if change_percent >= 3:

                    wallet["cash"] = (
                        wallet["holdings"][pair] * current_price
                    )

                    wallet["holdings"][pair] = 0

                    print(
                        f"TAKE PROFIT {pair} at Rp{current_price}"
                    )

                    send_telegram(
                        f"TAKE PROFIT\n{pair}\nPrice: Rp{current_price}"
                    )

                    log_trade(
                        "TAKE_PROFIT",
                        pair,
                        current_price
                    )

                    wallet["total_trades"] += 1
                    wallet["winning_trades"] += 1
                    wallet["last_trade_time"] = datetime.now().isoformat()
                    paper_wallet.save_wallet(wallet)

                # STOP LOSS
                elif change_percent <= -2:

                    wallet["cash"] = (
                        wallet["holdings"][pair] * current_price
                    )

                    wallet["holdings"][pair] = 0

                    print(
                        f"STOP LOSS {pair} at Rp{current_price}"
                    )

                    send_telegram(
                        f"STOP LOSS\n{pair}\nPrice: Rp{current_price}"
                    )

                    log_trade(
                        "STOP_LOSS",
                        pair,
                        current_price
                    )

                    wallet["total_trades"] += 1
                    wallet["losing_trades"] += 1
                    wallet["last_trade_time"] = datetime.now().isoformat()
                    paper_wallet.save_wallet(wallet)

                # RSI SELL
                elif signal == "SELL":

                    wallet["cash"] = (
                        wallet["holdings"][pair] * current_price
                    )

                    wallet["holdings"][pair] = 0

                    print(
                        f"RSI SELL {pair} at Rp{current_price}"
                    )

                    send_telegram(
                        f"SELL SIGNAL\n{pair}\nPrice: Rp{current_price}"
                    )

                    log_trade(
                        "SELL",
                        pair,
                        current_price
                    )

                    wallet["total_trades"] += 1
                    wallet["last_trade_time"] = datetime.now().isoformat()
                    paper_wallet.save_wallet(wallet)

                else:
                    log_trade(
                        "HOLD",
                        pair,
                        current_price
                    )

            else:
                log_trade(
                    "HOLD",
                    pair,
                    current_price
                )

            portfolio_value = (
                wallet["cash"]
                + (wallet["holdings"][pair] * current_price)
            )

            print(f"Cash: Rp{wallet['cash']:,.0f}")
            coin_name = pair.split('/')[0]

            print(
                f"{coin_name}: "
                f"{wallet['holdings'][pair]}"
            )

            print(
                f"Portfolio Value: Rp{portfolio_value:,.0f}"
            )

            print(
                f"Total Trades: {wallet['total_trades']}"
            )

            print(
                f"Wins: {wallet['winning_trades']}"
            )

            print(
                f"Losses: {wallet['losing_trades']}"
            )
            coin_name = pair.split('/')[0]

            telegram_report += (
                f"Cash: Rp{wallet['cash']:,.0f}\n"
                f"{coin_name}: "
                f"{wallet['holdings'][pair]}\n"
                f"Portfolio Value: Rp{portfolio_value:,.0f}\n"
                f"Total Trades: {wallet['total_trades']}\n"
                f"Wins: {wallet['winning_trades']}\n"
                f"Losses: {wallet['losing_trades']}\n\n"
            )
        send_telegram(telegram_report)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":

    print("Paper trading bot started...")

    send_telegram("Paper trading bot started.")

    run_bot()
