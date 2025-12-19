# Shared fixtures and generators for tests
from hypothesis import strategies as st
from src.constants import MAX_HP, AP_LIMIT, COURAGE_CAP

# Warrior attributes generator
warrior_attributes = st.fixed_dictionaries({
    "martial_arts": st.integers(min_value=1, max_value=100),
    "agility": st.integers(min_value=1, max_value=100),
    "strength": st.integers(min_value=1, max_value=100),
    "courage": st.integers(min_value=0, max_value=COURAGE_CAP),
    "sp": st.integers(min_value=1000, max_value=10000),
})

# Warrior state generator
warrior_state = st.fixed_dictionaries({
    "hp": st.integers(min_value=0, max_value=MAX_HP),
    "sp": st.integers(min_value=0, max_value=10000),
    "ap": st.floats(min_value=0, max_value=AP_LIMIT * 2, allow_nan=False, allow_infinity=False),
})
