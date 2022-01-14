from .compound_interest import compound_interest
from .flexfixed import flexfixed
from .inflation import inflation_simulation
from .fee import fee_recovery
from .profitable import profitability_assessment

pages = {
    "Compound Interest": compound_interest,
    "Flex Term vs Fixed Term": flexfixed,
    "Inflation Simulation": inflation_simulation,
    "Fee Recovery": fee_recovery,
    "Asset Profitability": profitability_assessment,
}
