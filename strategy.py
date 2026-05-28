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
    rsi_indicator = RSIIndicator(
        df['close'],
        window=14
    )

    df['rsi'] = rsi_indicator.rsi()

    # EMA50
    ema50_indicator = EMAIndicator(
        close=df['close'],
        window=50
    )

    df['ema50'] = ema50_indicator.ema_indicator()

    # EMA200
    ema200_indicator = EMAIndicator(
        close=df['close'],
        window=200
    )

    df['ema200'] = ema200_indicator.ema_indicator()

    current_rsi = df['rsi'].iloc[-1]

    current_ema50 = df['ema50'].iloc[-1]
    current_ema200 = df['ema200'].iloc[-1]

    print(f"Current RSI: {current_rsi:.2f}")
    print(f"EMA50: {current_ema50:.2f}")
    print(f"EMA200: {current_ema200:.2f}")

    # BUY
    if (
        current_ema50 > current_ema200
        and current_rsi < 45
    ):

        signal = "BUY"

    # SELL
    elif current_rsi > 70:

        signal = "SELL"

    else:

        signal = "HOLD"

    return signal, current_rsi, current_ema200