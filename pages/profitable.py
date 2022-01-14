import numpy as np
import pandas as pd
from scipy import signal

import yfinance as yf

import altair as alt


__description__ = """
This app allows to analyze the history of an assets' performance, first a
Ticker is selected, then an Investment Time is defined, and the number of years
can be also set.

The app will backtrack which were the profits/losses of investing in the given
asset after waiting the set investment time. This is by no means a way to
predict future returns but rather to assess the stability and potential
performance of an asset. That being said, unpredicted events can cause
unpredicted results (e.g. a pandemic).

The ticker information is downloaded from [Yahoo
Finance](https://finance.yahoo.com/).

A good way to balance and compare profits is with the traditional low-risk
fixed/flex term investment, which can be experimented with in the "Compounded
Interest" app on the sidebar.

Remember: *"Past performance is no guarantee of future results"*
"""


def profitability_assessment(st, **state):
    st.title("Asset Profitability Analyser")
    st.write(__description__)

    st.write("### Input Parameters")

    ticker = st.text_input("Ticker Name", max_chars=10, placeholder="Stocks like 'AAPL' or cryptos like 'BTC-USD'")
    shift = st.number_input("Investment Time (days)", value=30, min_value=1)

    years_ = st.number_input("Years to Consider (0 for max)", value=2, min_value=0)
    years = f"{years_}y" if years_ else "max"

    if years_ and shift // 365 >= years_:
        st.warning(
            "The 'Investment Time' cannot be larger than the 'Years to Consider'"
        )
        return

    data = get_data(ticker, shift, years)

    show_metrics(st, data)

    plot_profit(st, data)


def get_data(ticker, shift, years):
    ticker_data = yf.Ticker(ticker)
    history = ticker_data.history(period=years)
    history["average"] = history["Open"] + history["Close"] / 2
    data = history["average"]

    shifted_data = data.shift(shift)
    df = pd.DataFrame()
    df.index = data.index
    df["absolute"] = data - shifted_data
    df["percentage"] = df["absolute"] / shifted_data * 100

    df = df.dropna()
    df = df.reset_index()
    return df[-5000:]


def show_metrics(st, data_):

    st.write("## Streak Information")
    # Adapted from https://stackoverflow.com/a/57517727/7690767
    data = data_["percentage"]
    positive = np.clip(data, 0, 1).astype(bool).cumsum()
    negative = np.clip(data, -1, 0).astype(bool).cumsum()

    streaks = np.where(
        data >= 0,
        positive - np.maximum.accumulate(np.where(data <= 0, positive, 0)),
        -negative + np.maximum.accumulate(np.where(data >= 0, negative, 0)),
    )

    positive_peaks = streaks[streaks > 0]
    negative_peaks = -streaks[streaks < 0]

    left, left_middle, right_middle, right = st.columns(4)
    left.metric("Longest Positive Streak", f"{np.max(positive_peaks, initial=0)} days")
    left_middle.metric(
        "Shortest Positive Streak", f"{np.min(positive_peaks, initial=0)} days"
    )
    right_middle.metric(
        "Longest Negative Streak", f"{np.max(negative_peaks, initial=0)} days"
    )
    right.metric(
        "Shortest Negative Streak", f"{np.min(negative_peaks, initial=0)} days"
    )

    st.write("## Proportion Information")

    average_positive = data[data > 0].mean()
    average_positive = 0 if np.isnan(average_positive) else average_positive
    average_negative = data[data < 0].mean()
    average_negative = 0 if np.isnan(average_negative) else average_negative
    median_positive = data[data > 0].median()
    median_positive = 0 if np.isnan(median_positive) else median_positive
    median_negative = data[data < 0].median()
    median_negative = 0 if np.isnan(median_negative) else median_negative

    left, left_middle, right_middle, right = st.columns(4)
    left.metric("Mean Percentage Profit", f"{average_positive:.2f}%")
    left_middle.metric("Median Percentage Profit", f"{median_positive:.2f}%")
    right_middle.metric("Mean Percentage Loss", f"{average_negative:.2f}%")
    right.metric("Median Percentage Loss", f"{median_negative:.2f}%")


def plot_profit(st, data):
    chart_data = alt.Chart(data)

    color_condition = alt.condition(
        "datum.percentage > 0", alt.value("forestgreen"), alt.value("firebrick")
    )

    line = (
        chart_data.mark_bar(size=5)
        .encode(
            x=alt.X("yearmonthdate(Date):O", title="Date"),
            y=alt.Y("percentage:Q", title="Percentage"),
            color=color_condition,
            opacity=alt.value(0.6),
        )
        .properties(
            height=500,
            width=1600,
            title="Profit/Loss Percentage after set Investment Time",
        )
    )

    st.altair_chart(line, use_container_width=True)
