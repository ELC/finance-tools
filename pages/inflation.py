import numpy as np
import pandas as pd

import altair as alt

from .plotting import select_nearest, get_selectors, add_rules, mark_years, add_text

__description__ = """
This application adjusts an initial capital for inflation. Inflation can be
given by providing an optimistic (minimum), a pessimistic (maximum) and a
realistic (mode) estimate.

The compounding frequency can be either annually (by default) or daily (with
the checkbox marked), The results are similar but the interpretation of the
rates are different when using daily compounding.

This app does not consider any type of interest or gain, to check the effects
of compounding interests, check the "Compound Interest" and the "Flex Term vs
Fixed Term" apps in the sidebar.
"""


def inflation_simulation(st, **state):
    st.title("Inflation Simulation")
    st.write(__description__)

    st.write("## Initial Capital")
    initial_capital = st.number_input("Capital", value=10_000.0)

    st.write("## Inflation Estimation")

    left, middle, right = st.columns(3)

    optimistic = left.number_input("Optimistic Inflation (%)", value=2.0, min_value=0.0)

    realistic_value = max(2.5, optimistic + 0.01)
    realistic = middle.number_input(
        "Realistic Inflation (%)", value=realistic_value, min_value=optimistic
    )

    pessimistic_value = max(3.5, realistic + 0.01)
    pessimistic = right.number_input(
        "Pessimistic Inflation (%)", value=pessimistic_value, min_value=realistic
    )

    daily_conpound = st.checkbox("Daily Compounding", value=False)

    years = st.slider("Years", min_value=1, max_value=15, value=2)

    st.write("## Simulation Results")

    median_capital, min_capital, max_capital = simulate_inflation(
        initial_capital, optimistic, realistic, pessimistic, years, daily_conpound
    )

    st.write("### Capital at the End")

    left, middle, right = st.columns(3)

    max_delta = (initial_capital - max_capital[-1]) / initial_capital * 100
    left.metric("Optimistic Case", f"${max_capital[-1]:.2f}", f"-{max_delta:.2f}%")

    min_delta = (initial_capital - min_capital[-1]) / initial_capital * 100
    right.metric("Pessimistic Case", f"${min_capital[-1]:.2f}", f"-{min_delta:.2f}%")

    median_delta = (initial_capital - median_capital[-1]) / initial_capital * 100
    middle.metric(
        "Realistic Case", f"${median_capital[-1]:.2f}", f"-{median_delta:.2f}%"
    )

    plot_comparison(st, median_capital, min_capital, max_capital)


def simulate_inflation(
    initial_capital, optimistic, realistic, pessimistic, years, daily_conpound
):
    runs = 5_000
    days = years * 365
    data = np.tile(initial_capital, (runs, days))

    optimistic_rate = optimistic / 100
    realistic_rate = realistic / 100
    pessimistic_rate = pessimistic / 100

    generator = np.random.default_rng()
    rate = generator.triangular(
        optimistic_rate, realistic_rate, pessimistic_rate, size=(runs, days)
    )

    # Kept as legacy formula
    # interest_rate = rate if daily_conpound else rate * np.linspace(1, 365, days)
    # exponent = np.arange(days) if daily_conpound else years

    interest_rate = rate / 365 if daily_conpound else np.power(1 + rate, 1 / 365) - 1
    exponent = np.arange(days)

    rate_compound = (1 + interest_rate) ** exponent

    data /= rate_compound

    median_data = np.median(data, axis=0)
    minimum_bound = np.quantile(data, 0.05, axis=0)
    maximum_bound = np.quantile(data, 0.95, axis=0)

    return median_data, minimum_bound, maximum_bound


def plot_comparison(st, median_capital, min_capital, max_capital):
    lenght = len(median_capital)

    positions = np.arange(lenght)

    coordinates = [
        f"({pos}, {value:.2f})" for pos, value in zip(positions, median_capital)
    ]

    data = {
        "x": positions,
        "median": median_capital,
        "minimal": min_capital,
        "maximum": max_capital,
        "coordinates": np.array(coordinates),
    }

    df = pd.DataFrame(data)

    axis = alt.Axis(labelFontSize=20, titleFontSize=22)

    line = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X(
                "x",
                axis=axis,
                title="Time (days)",
                scale=alt.Scale(domain=[0, lenght], clamp=False, nice=False),
            ),
            y=alt.Y("median", axis=axis, title="Capital", scale=alt.Scale(zero=False)),
        )
    )

    area = (
        alt.Chart(df)
        .mark_area()
        .encode(x=alt.X("x"), y="minimal:Q", y2="maximum:Q", opacity=alt.value(0.2))
    )

    nearest = select_nearest()
    selectors = get_selectors(df, nearest)
    text = add_text(line, "coordinates:N", nearest)
    rules = add_rules(df, nearest)
    years = mark_years(df)

    points = line.mark_point().transform_filter(nearest)

    chart = (
        alt.layer(line, area, selectors, points, rules, text, years)
        .interactive()
        .properties(
            width=1600, height=500, title="Real Value over Time Adjusted for Inflation"
        )
        .configure_title(fontSize=24)
    )

    st.altair_chart(chart, use_container_width=True)
