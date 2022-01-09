from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt

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


def flexfixed(st, **state):
    st.title("Flex Term vs Fixed Term Comparison")

    left, right = st.columns(2)

    left.write("### Flex Term")
    (
        flex_initial_capital,
        flex_apr_decimal,
        flex_compound_frequency,
        flex_compound_frequency_value,
        flex_recurring_deposits,
        flex_recurring_frequency,
    ) = show_inputs(
        left, compound_frequency_options, recurring_frequency_options, "Flex"
    )
    flex_proportional_interest = (
        1 + flex_apr_decimal / compounding_frequencies[flex_compound_frequency]
    )

    right.write("### Fixed Term")
    (
        fixed_initial_capital,
        fixed_apr_decimal,
        fixed_compound_frequency,
        fixed_compound_frequency_value,
        fixed_recurring_deposits,
        fixed_recurring_frequency,
    ) = show_inputs(
        right, compound_frequency_options, recurring_frequency_options, "Fixed"
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
    proportion = max(fixed_total_interest, flex_total_interest) / min(fixed_total_interest, flex_total_interest)
    percentage = (proportion - 1) * 100

    difference = np.abs(flex_capital_over_time - fixed_capital_over_time)
    time_to_pass = np.argmin(difference)

    st.write(f"The best one was the **{best}** alternative, yielding **${amount:.2f} ({percentage:.2f}%)** more than the alternative. It took {time_to_pass} days to match the alternative.")
    left, middle_left, middle_right, right = st.columns(4)
    left.metric("Best Strategy", best)
    middle_left.metric("Difference (abs)", f"${amount:.2f}")
    middle_right.metric("Difference (%)", f"{percentage:.2f}%")
    right.metric("Time to match", f"{time_to_pass} days")

    plot_comparison(st, flex_capital_over_time, fixed_capital_over_time)


def plot_comparison(st, flex_capital_over_time, fixed_capital_over_time):
    plt.style.use("bmh")

    fig = plt.figure(figsize=(16, 6))

    total_simulation_time = len(flex_capital_over_time)
    positions = np.arange(total_simulation_time)

    plt.plot(positions, flex_capital_over_time, alpha=0.6, label="Flex Capital")
    plt.plot(positions, fixed_capital_over_time, alpha=0.6, label="Fixed Capital")

    interval = 30 * total_simulation_time // 365

    plt.xticks(np.arange(0, total_simulation_time, interval))
    plt.xlabel("Time (Days)", fontsize=16)
    plt.xlim(0, total_simulation_time)

    plt.ylabel("Capital ($)", fontsize=16)

    plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=16)

    plt.title("Revenue using Compound Interest", fontsize=20)
    plt.tight_layout()

    st.pyplot(fig)
