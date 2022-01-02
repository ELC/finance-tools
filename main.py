import streamlit as st
from datetime import datetime, timedelta

## Based on https://calculadoras.omareducacionfinanciera.com/


initial_capital = st.sidebar.number_input("Initial Capital", value=1000., step=100., format="%.2f")

apr = st.sidebar.number_input("Annual Percentage Rate (APR)", value=15., step=0.5, min_value=0., max_value=200., format="%.2f")
apr_decimal = apr / 100

compound_frequency_options = {
    "Annualy": 365,
    "Monthly": 30,
    "Daily": 1
}

compound_frequency = st.sidebar.selectbox('Compound Frequency', compound_frequency_options.keys(), index=2)
compound_frequency_value = compound_frequency_options[compound_frequency]

years_to_invest = st.sidebar.slider('Years', min_value=1, max_value=15, value=2)

recurring_deposits = st.sidebar.number_input("Recurring Deposits", step=1., format="%.2f", value=50.)

recurring_frequency_options = ["Same as Compound"] + list(compound_frequency_options.keys())
recurring_frequency = st.sidebar.selectbox("Recurring Frequency", recurring_frequency_options, index=2)

if recurring_frequency == "Same as Compound":
    recurring_frequency = compound_frequency
    recurring_frequency_value = compound_frequency_value
else:
    recurring_frequency_value = compound_frequency_options[recurring_frequency]

if recurring_frequency_value < compound_frequency_value:
    st.sidebar.warning("The Recurry frequency is greater than the compound frequency, results might be unexpected")


initial_date = datetime(2022, 1, 2)

capital_over_time = [initial_capital]
deposits = [0]
interests = [0]

compounding_frequencies = {
    "Annualy": 1,
    "Monthly": 12,
    "Daily": 365
}

proportional_interest = 1 + apr_decimal / compounding_frequencies[compound_frequency]

def check_date(frequency: str, today: datetime) -> bool:
    if frequency == "Daily":
        return True
    elif frequency == "Monthly":
        return today.day == 1
    elif frequency == "Annualy":
        return today.day == 31 and today.month == 12

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

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("bmh")

fig = plt.figure(figsize=(10, 6))

total_simulation_time = len(capital_over_time)
positions = np.arange(total_simulation_time)

total_interest = interests[-1]
total_deposists = deposits[-1]
initial_capital_beginning = initial_capital

initial_capital = np.repeat(initial_capital, total_simulation_time)
deposits = initial_capital + np.array(deposits)
interests = deposits + np.array(interests)

plt.plot(positions, initial_capital, alpha=0.6, label=f"Initial Capital: ${initial_capital_beginning:.2f}$")
plt.fill_between(positions, initial_capital, step="pre", alpha=0.2)

plt.plot(positions, deposits, alpha=0.6, label=f"Acummulated Deposits: ${total_deposists:.2f}$")
plt.fill_between(positions, deposits, initial_capital, step="pre", alpha=0.2)

plt.plot(positions, interests, alpha=0.6, label=f"Acummulated Interests: ${total_interest:.2f}$")
plt.fill_between(positions, interests, deposits, step="pre", alpha=0.2)

interval = 30 * total_simulation_time // 365

plt.xticks(np.arange(0, total_simulation_time, interval))

plt.legend()

plt.title(f"Revenue using Compound Interest - Capital at the end: ${capital_over_time[-1]:.2f}$")

st.pyplot(fig)

st.write(total_interest + total_deposists + initial_capital_beginning)
st.write(capital_over_time[-1])

