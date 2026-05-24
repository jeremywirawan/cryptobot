import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

def check_signal(ohlcv):

    df = pd.DataFrame(
        ohlcv,
        columns=[
            'timestamp',
            'open',
            'high',
            'low',
            'close',
            'volume'
        ]
    )

    # RSI
    rsi_indicator = RSIIndicator(df['close'], window=14)
    df['rsi'] = rsi_indicator.rsi()

    # EMA200
    ema_indicator = EMAIndicator(
        close=df['close'],
        window=200
    )

    df['ema200'] = ema_indicator.ema_indicator()

    current_rsi = df['rsi'].iloc[-1]

    current_ema200 = df['ema200'].iloc[-1]

    current_price = df['close'].iloc[-1]

    print(f"Current RSI: {current_rsi:.2f}")
    print(f"Current EMA200: {current_ema200:.2f}")

    # SIGNAL LOGIC
    if (
        current_rsi < 40
        and current_price > current_ema200
    ):
        signal = "BUY"

    elif current_rsi > 65:
        signal = "SELL"

    else:
        signal = "HOLD"

    return signal, current_rsi, current_ema200
