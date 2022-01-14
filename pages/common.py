from datetime import datetime, timedelta

import numpy as np

compounding_frequencies = {"Annually": 1, "Monthly": 12, "Daily": 365}

compound_frequency_options = {"Annually": 365, "Monthly": 30, "Daily": 1}

recurring_frequency_options = ["Same as Compound"] + list(
    compound_frequency_options.keys()
)


def interest_metrics(
    st, apr_decimal, compound_frequency, compounding_frequencies, total_capital
):
    daily_interest = "N/A"
    if compound_frequency in ["Daily"]:
        daily_interest = (
            1 + apr_decimal / compounding_frequencies["Daily"]
        ) * total_capital - total_capital
        daily_interest = f"${daily_interest:.2f}"

    monthly_interest = "N/A"
    if compound_frequency in ["Daily", "Monthly"]:
        monthly_interest = (
            1 + apr_decimal / compounding_frequencies["Monthly"]
        ) * total_capital - total_capital
        monthly_interest = f"${monthly_interest:.2f}"

    annual_interest = "N/A"
    if compound_frequency in ["Daily", "Monthly", "Annually"]:
        annual_interest = (
            1 + apr_decimal / compounding_frequencies["Annually"]
        ) * total_capital - total_capital
        annual_interest = f"${annual_interest:.2f}"

    labels = ["Daily Interest", "Monthly Interest", "Annually Interest"]
    values = [daily_interest, monthly_interest, annual_interest]
    columns = st.columns(3)
    show_metrics(columns, labels, values)


def show_metrics(sts, labels, values):
    for st, label, value in zip(sts, labels, values):
        st.metric(label, value)


def check_date(frequency: str, today: datetime) -> bool:
    if frequency == "Daily":
        return True
    elif frequency == "Monthly":
        return today.day == 1
    elif frequency == "Annually":
        return today.day == 31 and today.month == 12


def show_inputs(
    st, compound_frequency_options, recurring_frequency_options, preffix, defaults=None
):

    if defaults is None:
        defaults = {}

    initial_capital_ = defaults.get("initial_capital", 1000.0)
    initial_capital = st.number_input(
        f"{preffix} Initial Capital", value=initial_capital_, step=100.0, format="%.2f"
    )

    apr_ = defaults.get("apr", 15.0)
    apr = st.number_input(
        f"{preffix} Annual Percentage Rate (APR)",
        value=apr_,
        step=0.5,
        min_value=0.0,
        max_value=200.0,
        format="%.2f",
    )
    apr_decimal = apr / 100

    compound_frequency_ = defaults.get("compound_frequency_index", 2)
    compound_frequency = st.selectbox(
        f"{preffix} Compound Frequency",
        compound_frequency_options.keys(),
        index=compound_frequency_,
    )
    compound_frequency_value = compound_frequency_options[compound_frequency]

    recurring_deposits_ = defaults.get("recurring_deposits", 50.0)
    recurring_deposits = st.number_input(
        f"{preffix} Recurring Deposits",
        step=1.0,
        format="%.2f",
        value=recurring_deposits_,
    )

    recurring_frequency_ = defaults.get("recurring_frequency_index", 2)
    recurring_frequency = st.selectbox(
        f"{preffix} Recurring Frequency",
        recurring_frequency_options,
        index=recurring_frequency_,
    )

    if recurring_frequency == "Same as Compound":
        recurring_frequency = compound_frequency
        recurring_frequency_value = compound_frequency_value
    else:
        recurring_frequency_value = compound_frequency_options[recurring_frequency]

    if recurring_frequency_value < compound_frequency_value:
        st.warning(
            "The Recurry frequency is greater than the compound frequency, results might be unexpected"
        )

    return (
        initial_capital,
        apr_decimal,
        compound_frequency,
        compound_frequency_value,
        recurring_deposits,
        recurring_frequency,
    )


def simulate(
    initial_capital,
    proportional_interest,
    compound_frequency,
    recurring_frequency,
    years_to_invest,
    recurring_deposits,
    extras=False,
):
    initial_date = datetime(2022, 1, 2)

    capital_over_time = [initial_capital]
    deposits = [0]
    interests = [0]

    today = initial_date
    while True:
        today_capital = capital_over_time[-1]
        deposits.append(deposits[-1])
        interests.append(interests[-1])

        if check_date(compound_frequency, today):
            interests[-1] += today_capital * (proportional_interest - 1)
            today_capital *= proportional_interest

        if check_date(recurring_frequency, today):
            today_capital += recurring_deposits
            deposits[-1] += recurring_deposits

        today_capital = round(today_capital, 2)
        capital_over_time.append(today_capital)

        today += timedelta(days=1)

        if (today.year - initial_date.year) == years_to_invest and today.day == 2:
            break

    total_interest = interests[-1]
    total_deposists = deposits[-1]
    total_capital = capital_over_time[-1]

    capital_over_time = np.array(capital_over_time)

    if not extras:
        return total_interest, total_deposists, total_capital, capital_over_time

    return (
        total_interest,
        total_deposists,
        total_capital,
        capital_over_time,
        deposits,
        interests,
    )
