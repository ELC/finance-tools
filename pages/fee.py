import numpy as np
import pandas as pd
import altair as alt

from .common import compounding_frequencies, compound_frequency_options


__description__ = """

"""


def fee_recovery(st, **state):
    st.title("Fee Recovery Simulation")
    st.write(__description__)

    st.write("## Initial Capital")
    initial_capital = st.number_input("Capital", value=10_000.0)

    st.write("## Fee Information")

    fee = st.number_input("Fee", value=5.0, min_value=0.0)
    percentage = st.checkbox("Percentage", value=True)

    if percentage:
        fee /= 100

    st.write("## Interest Information")

    left, right = st.columns(2)

    apr = left.number_input("Annual Percentage Rate", value=3.0, min_value=0.0)

    noise = right.number_input("± Noise", value=0.2)

    compound_frequency = st.selectbox(
        "Compound Frequency", compound_frequency_options.keys(), index=2
    )

    compound_frequency_value = compound_frequency_options[compound_frequency]

    proportional_interest = apr / 100 / compounding_frequencies[compound_frequency]
    proportional_noise = noise / 100 / compounding_frequencies[compound_frequency]

    st.write("## Simulation Results")

    median_capital, min_capital, max_capital, years = simulate_fee(
        initial_capital,
        fee,
        percentage,
        proportional_interest,
        proportional_noise,
        compound_frequency_value,
    )

    if years == -1:
        st.warning("The fee will not be recovered in more than 15 years")

    st.write("### Fee Recovery")

    minimum_difference = np.abs(initial_capital - max_capital)
    minimum_time_to_recover = np.argmin(minimum_difference)

    median_difference = np.abs(initial_capital - median_capital)
    median_time_to_recover = np.argmin(median_difference)

    maximum_difference = np.abs(initial_capital - min_capital)
    maximum_time_to_recover = np.argmin(maximum_difference)

    left, middle, right = st.columns(3)

    left.metric("Minimum Time to Recover", f"{minimum_time_to_recover} days")
    middle.metric("Median Time to Recover", f"{median_time_to_recover} days")
    right.metric("Maximum Time to Recover", f"{maximum_time_to_recover} days")

    plot_comparison(st, initial_capital, median_capital, min_capital, max_capital)


def simulate_fee(
    initial_capital_,
    fee,
    percentage,
    proportional_interest,
    noise,
    compound_frequency_value,
):
    runs = 5_000

    if percentage:
        initial_capital = initial_capital_ * (1 - fee)
    else:
        initial_capital = initial_capital_ - fee

    for years in [1, 2, 3, 5, 10, 15]:
        days = years * 366

        data = np.tile(initial_capital, (runs, days))

        generator = np.random.default_rng()

        interest_rate = 1 + (
            proportional_interest + generator.normal(0, noise, size=(runs, days))
        )

        exponent = np.arange(days) // compound_frequency_value + 1

        rate_compound = (interest_rate) ** exponent

        data *= rate_compound

        median_data = np.median(data, axis=0)
        minimum_bound = np.quantile(data, 0.05, axis=0)
        maximum_bound = np.quantile(data, 0.95, axis=0)

        if np.max(minimum_bound - initial_capital_) > 0:
            return median_data, minimum_bound, maximum_bound, years

    return median_data, minimum_bound, maximum_bound, -1


def plot_comparison(st, initial_capital, median_capital, min_capital, max_capital):
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

    nearest = alt.selection(
        type="single", nearest=True, on="mouseover", fields=["median"], empty="none"
    )

    selectors = (
        alt.Chart(df)
        .mark_point()
        .encode(
            x="x:Q",
            opacity=alt.value(0),
        )
        .add_selection(nearest)
    )

    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = line.mark_text(
        align="right",
        dx=-5,
        dy=-5,
        color="white",
        fontSize=18,
    ).encode(text=alt.condition(nearest, alt.Text("coordinates:N"), alt.value(" ")))

    rules = (
        alt.Chart(df)
        .mark_rule(color="gray")
        .encode(
            x="x:Q",
        )
        .transform_filter(nearest)
    )

    years = (
        alt.Chart(df)
        .mark_rule(color="white")
        .encode(
            x="x:Q",
            strokeDash=alt.value([5, 5]),
            strokeWidth=alt.value(2),
        )
        .transform_filter(alt.datum.x % 365 == 0)
    )

    initial_capital = (
        alt.Chart(pd.DataFrame({"y": [initial_capital]}))
        .mark_rule(color="white")
        .encode(
            y="y",
            strokeDash=alt.value([5, 5]),
            strokeWidth=alt.value(2),
        )
    )

    chart = (
        alt.layer(line, area, selectors, points, rules, text, years, initial_capital)
        .interactive()
        .properties(width=1600, height=500, title="Capital with Compound Interest")
        .configure_title(fontSize=24)
    )

    st.altair_chart(chart, use_container_width=True)
