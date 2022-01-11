import numpy as np
import pandas as pd
import altair as alt

from streamlit_multipage import MultiPage

from .common import (
    interest_metrics,
    show_metrics,
    check_date,
    simulate,
    compounding_frequencies,
    compound_frequency_options,
    recurring_frequency_options,
    show_inputs,
)

## Based on https://calculadoras.omareducacionfinanciera.com/


def compound_interest(st, **state):
    st.title("Compound Interest Calculator")

    st.write("### Input Parameters")

    (
        initial_capital,
        apr_decimal,
        compound_frequency,
        compound_frequency_value,
        recurring_deposits,
        recurring_frequency,
    ) = show_inputs(st, compound_frequency_options, recurring_frequency_options, "")

    years_to_invest = st.slider("Years", min_value=1, max_value=15, value=2)

    zero_start = st.checkbox("Start at Zero", value=False)

    st.write("---")

    proportional_interest = (
        1 + apr_decimal / compounding_frequencies[compound_frequency]
    )

    (
        total_interest,
        total_deposists,
        total_capital,
        capital_over_time,
        deposits,
        interests,
    ) = simulate(
        initial_capital,
        proportional_interest,
        compound_frequency,
        recurring_frequency,
        years_to_invest,
        recurring_deposits,
        extras=True,
    )

    st.write("### Simulation Results")
    st.write("#### Capital at the end")

    labels = ["Total Capital", "Total Deposists", "Total Interest"]
    values = [
        f"${total_capital:.2f}",
        f"${total_deposists:.2f}",
        f"${total_interest:.2f}",
    ]
    columns = st.columns(3)
    show_metrics(columns, labels, values)

    st.write("#### Interests at the beginning")
    interest_metrics(
        st.container(),
        apr_decimal,
        compound_frequency,
        compounding_frequencies,
        initial_capital,
    )

    st.write("#### Interests at the end")
    interest_metrics(
        st.container(),
        apr_decimal,
        compound_frequency,
        compounding_frequencies,
        total_capital,
    )

    plot_compound(st, deposits, interests, initial_capital, zero_start)


def plot_compound(st, deposits_, interests_, initial_capital_, zero_start):
    lenght = len(deposits_)

    positions = np.arange(lenght)

    initial_capital = np.repeat(initial_capital_, lenght)
    deposits = initial_capital + np.array(deposits_)
    interests = deposits + np.array(interests_)

    initial_coordinates = [
        f"({pos}, {value:.2f})" for pos, value in zip(positions, initial_capital)
    ]

    initial_data = {
        "x": positions,
        "acummulated_value": initial_capital,
        "value": initial_capital,
        "type": "Initial Capital",
        "coordinates": initial_coordinates,
    }

    deposits_coordinates = [
        f"({pos}, {value:.2f})" for pos, value in zip(positions, deposits)
    ]

    deposits_data = {
        "x": positions,
        "acummulated_value": deposits,
        "value": deposits_,
        "type": "Recurrent Deposits",
        "coordinates": deposits_coordinates,
    }

    interests_coordinates = [
        f"({pos}, {value:.2f})" for pos, value in zip(positions, interests)
    ]

    interests_data = {
        "x": positions,
        "acummulated_value": interests,
        "value": interests_,
        "type": "Interests",
        "coordinates": interests_coordinates,
    }

    initial_df = pd.DataFrame(initial_data)
    deposits_df = pd.DataFrame(deposits_data)
    interests_df = pd.DataFrame(interests_data)

    df = pd.concat([initial_df, deposits_df, interests_df])

    axis = alt.Axis(labelFontSize=20, titleFontSize=22)

    lower_limit = 0 if zero_start else initial_capital_

    line = (
        alt.Chart(df)
        .mark_line(interpolate="basis")
        .encode(
            x=alt.X(
                "x",
                axis=axis,
                title="Time (days)",
                scale=alt.Scale(domain=[0, lenght], clamp=False, nice=False),
            ),
            y=alt.Y(
                "acummulated_value",
                axis=axis,
                title="Capital",
                scale=alt.Scale(domainMin=lower_limit),
            ),
            color=alt.Color("type:N", legend=alt.Legend(title="Type")),
        )
    )

    area_order = {"Initial Capital": 0, "Recurrent Deposits": 1, "Interests": 2}
    area = (
        alt.Chart(df)
        .transform_calculate(order=f"{area_order}[datum.variable]")
        .mark_area()
        .encode(
            x="x",
            y=alt.Y("value:Q", stack=True),
            color=alt.Color("type:N", sort=alt.SortField("order", "descending")),
            order="order:O",
            opacity=alt.value(0.4),
        )
    )

    nearest = alt.selection(
        type="single",
        nearest=True,
        on="mouseover",
        fields=["x"],
        empty="none",
        clear="mouseout",
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

    points = line.mark_point().transform_filter(nearest)

    text = (
        line.mark_text(
            align="right",
            dx=-5,
            dy=-12,
            color="white",
            fontSize=18,
        )
        .encode(text="coordinates:N")
        .transform_filter(nearest)
    )

    rules = (
        alt.Chart(df).mark_rule(color="gray").encode(x="x:Q").transform_filter(nearest)
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

    chart = (
        alt.layer(line, area, selectors, points, rules, text, years)
        .interactive()
        .properties(width=1600, height=500, title="Capital with Compound Interest")
        .configure_title(fontSize=24)
    )

    st.altair_chart(chart, use_container_width=True)
