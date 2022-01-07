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

    plot_compound(st, capital_over_time, deposits, interests, initial_capital)


def plot_compound(st, capital_over_time, deposits, interests, initial_capital):

    plt.style.use("bmh")

    fig = plt.figure(figsize=(16, 6))

    total_simulation_time = len(capital_over_time)
    positions = np.arange(total_simulation_time)

    initial_capital = np.repeat(initial_capital, total_simulation_time)
    deposits = initial_capital + np.array(deposits)
    interests = deposits + np.array(interests)

    plt.plot(positions, initial_capital, alpha=0.6, label="Initial Capital")
    plt.fill_between(positions, initial_capital, step="pre", alpha=0.2)

    plt.plot(positions, deposits, alpha=0.6, label="Acummulated Deposits")
    plt.fill_between(positions, deposits, initial_capital, step="pre", alpha=0.2)

    plt.plot(positions, interests, alpha=0.6, label="Acummulated Interests")
    plt.fill_between(positions, interests, deposits, step="pre", alpha=0.2)

    interval = 30 * total_simulation_time // 365

    plt.xticks(np.arange(0, total_simulation_time, interval))
    plt.xlabel("Time (Days)", fontsize=16)
    plt.xlim(0, total_simulation_time)

    plt.ylabel("Capital ($)", fontsize=16)
    plt.ylim(bottom=0)

    plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=16)

    plt.title("Revenue using Compound Interest", fontsize=20)
    plt.tight_layout()

    st.pyplot(fig)
