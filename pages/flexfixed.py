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

from .plotting import select_nearest, get_selectors, add_rules, mark_years, add_text

## Based on https://calculadoras.omareducacionfinanciera.com/


def flexfixed(st, **state):
    st.title("Flex Term vs Fixed Term Comparison")

    left, right = st.columns(2)

    left.write("### Flex Term")

    flex_defaults = {"initial_capital": 800.0, "apr": 12.0, "recurring_deposits": 30.0}

    (
        flex_initial_capital,
        flex_apr_decimal,
        flex_compound_frequency,
        flex_compound_frequency_value,
        flex_recurring_deposits,
        flex_recurring_frequency,
    ) = show_inputs(
        left,
        compound_frequency_options,
        recurring_frequency_options,
        "Flex",
        flex_defaults,
    )
    flex_proportional_interest = (
        1 + flex_apr_decimal / compounding_frequencies[flex_compound_frequency]
    )

    right.write("### Fixed Term")

    fixed_defaults = {
        "initial_capital": 500.0,
        "apr": 15.0,
        "recurring_deposits": 50.0,
        "compound_frequency_index": 1,
    }
    (
        fixed_initial_capital,
        fixed_apr_decimal,
        fixed_compound_frequency,
        fixed_compound_frequency_value,
        fixed_recurring_deposits,
        fixed_recurring_frequency,
    ) = show_inputs(
        right,
        compound_frequency_options,
        recurring_frequency_options,
        "Fixed",
        fixed_defaults,
    )
    fixed_proportional_interest = (
        1 + fixed_apr_decimal / compounding_frequencies[fixed_compound_frequency]
    )

    years_to_invest = st.slider("Years to Simulate", min_value=1, max_value=15, value=2)

    st.write("---")

    (
        flex_total_interest,
        flex_total_deposists,
        flex_total_capital,
        flex_capital_over_time,
    ) = simulate(
        flex_initial_capital,
        flex_proportional_interest,
        flex_compound_frequency,
        flex_recurring_frequency,
        years_to_invest,
        flex_recurring_deposits,
    )
    (
        fixed_total_interest,
        fixed_total_deposists,
        fixed_total_capital,
        fixed_capital_over_time,
    ) = simulate(
        fixed_initial_capital,
        fixed_proportional_interest,
        fixed_compound_frequency,
        fixed_recurring_frequency,
        years_to_invest,
        fixed_recurring_deposits,
    )

    st.write("### Simulation Results")

    left_results, right_results = st.columns(2)
    left_results.write("#### Flex Results")
    left_results.metric("Total Capital", f"${flex_total_capital:.2f}")
    left_results.metric("Total Deposists", f"${flex_total_deposists:.2f}")
    left_results.metric("Total Interest", f"${flex_total_interest:.2f}")

    right_results.write("#### Fixed Results")
    right_results.metric("Total Capital", f"${fixed_total_capital:.2f}")
    right_results.metric("Total Deposists", f"${fixed_total_deposists:.2f}")
    right_results.metric("Total Interest", f"${fixed_total_interest:.2f}")

    st.write("#### Comparison")

    best = "Fixed" if fixed_total_interest > flex_total_interest else "Flex"
    amount = abs(fixed_total_interest - flex_total_interest)
    proportion = max(fixed_total_interest, flex_total_interest) / min(
        fixed_total_interest, flex_total_interest
    )
    percentage = (proportion - 1) * 100

    difference = np.abs(flex_capital_over_time - fixed_capital_over_time)
    time_to_pass = np.argmin(difference)

    if time_to_pass == len(difference) - 2:
        time_to_pass = 0

    st.write(
        f"The best one was the **{best}** alternative, yielding **${amount:.2f} ({percentage:.2f}%)** more than the alternative. It took {time_to_pass} days to match the alternative."
    )
    left, middle_left, middle_right, right = st.columns(4)
    left.metric("Best Strategy", best)
    middle_left.metric("Difference (abs)", f"${amount:.2f}")
    middle_right.metric("Difference (%)", f"{percentage:.2f}%")
    right.metric("Time to match", f"{time_to_pass} days")

    plot_comparison(st, flex_capital_over_time, fixed_capital_over_time, time_to_pass)


def plot_comparison(st, flex_capital_over_time, fixed_capital_over_time, time_to_pass):
    lenght = len(fixed_capital_over_time)
    positions = np.arange(lenght)

    flex_coordinates = [
        f"({pos}, {value:.2f})" for pos, value in zip(positions, flex_capital_over_time)
    ]

    flex_data = {
        "x": positions,
        "value": flex_capital_over_time + (np.ones(lenght) * 1e-10).cumsum(),
        "type": "Flex",
        "coordinates": flex_coordinates,
    }

    fixed_coordinates = [
        f"({pos}, {value:.2f})"
        for pos, value in zip(positions, fixed_capital_over_time)
    ]

    fixed_data = {
        "x": positions,
        "value": fixed_capital_over_time + (np.ones(lenght) * 1e-10).cumsum(),
        "type": "Fixed",
        "coordinates": fixed_coordinates,
    }

    flex_df = pd.DataFrame(flex_data)
    fixed_df = pd.DataFrame(fixed_data)

    df = pd.concat([flex_df, fixed_df])

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
            y=alt.Y("value", axis=axis, title="Capital", scale=alt.Scale(zero=False)),
            color=alt.Color("type:N", legend=alt.Legend(title="Type")),
        )
    )

    nearest = select_nearest()
    selectors = get_selectors(df, nearest)
    text = add_text(line, "coordinates:N", nearest)
    rules = add_rules(df, nearest)
    years = mark_years(df)
    points = line.mark_point().transform_filter(nearest)

    match_point = (
        alt.Chart(pd.DataFrame({"x": [time_to_pass]}))
        .mark_rule(color="white")
        .encode(x="x", strokeWidth=alt.value(2))
    )

    chart = (
        alt.layer(line, selectors, points, rules, text, years, match_point)
        .interactive()
        .properties(width=1600, height=500, title="Capital with Compound Interest")
        .configure_title(fontSize=24)
    )

    st.altair_chart(chart, use_container_width=True)
