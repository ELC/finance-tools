from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt

from .common import compounding_frequencies, compound_frequency_options


__description__ = """

"""


def fee_recovery(st, **state):
    st.title("Fee Recovery Simulation")
    st.write(__description__)

    st.write("## Initial Capital")
    initial_capital = st.number_input("Capital", value=10_000.0)

    st.write("## Fee Information")

    fee = st.number_input("Fee", value=2.0, min_value=0.0)
    percentage = st.checkbox("Percentage", value=True)

    if percentage:
        fee /= 100

    st.write("## Interest Information")

    left, right = st.columns(2)

    apr = left.number_input("Annual Percentage Rate", value=2.0, min_value=0.0)

    noise = right.number_input("± Noise", value=0.1)

    compound_frequency = st.selectbox(
        "Compound Frequency", compound_frequency_options.keys(), index=2
    )

    compound_frequency_value = compound_frequency_options[compound_frequency]

    proportional_interest = apr / 100 / compounding_frequencies[compound_frequency]
    proportional_noise = noise / 100 / compounding_frequencies[compound_frequency]

    years = st.slider("Years", min_value=1, max_value=15, value=2)

    st.write("## Simulation Results")

    median_capital, min_capital, max_capital = simulate_fee(
        initial_capital,
        fee,
        percentage,
        proportional_interest,
        proportional_noise,
        years,
        compound_frequency_value,
    )

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

    st.write("### Capital over Time in 'Today Money'")
    plot_comparison(st, initial_capital, median_capital, min_capital, max_capital)


def simulate_fee(
    initial_capital,
    fee,
    percentage,
    proportional_interest,
    noise,
    years,
    compound_frequency_value,
):
    runs = 1_000
    days = years * 366

    if percentage:
        initial_capital *= 1 - fee
    else:
        initial_capital -= fee

    data = np.tile(initial_capital, (runs, days))

    generator = np.random.default_rng()

    interest_rate = 1 + (
        proportional_interest + generator.normal(0, noise, size=(runs, days))
    )
    print(np.max(interest_rate))

    exponent = np.arange(days) // compound_frequency_value + 1

    rate_compound = (interest_rate) ** exponent

    data *= rate_compound

    median_data = np.median(data, axis=0)
    minimum_bound = np.quantile(data, 0.05, axis=0)
    maximum_bound = np.quantile(data, 0.95, axis=0)

    return median_data, minimum_bound, maximum_bound


def plot_comparison(st, initial_capital, median_capital, min_capital, max_capital):
    plt.style.use("bmh")

    fig = plt.figure(figsize=(16, 6))

    positions = np.arange(len(median_capital))

    plt.plot(positions, median_capital, alpha=0.6)
    plt.fill_between(positions, min_capital, max_capital, alpha=0.2)

    for day in range(364, len(median_capital), 364):
        plt.axvline(day, color="darkgray", ls="--")

    plt.axhline(initial_capital, color="darkgray", ls="-.")

    plt.xlim(0, len(median_capital))

    plt.title("Real Value over Time Adjusted for Inflation", fontsize=20)
    plt.tight_layout()

    st.pyplot(fig)
