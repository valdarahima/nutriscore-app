"""
Nutri-Score Calculator – Beverages Demo (2023 Updated Algorithm)
================================================================

This Streamlit app is a demo version of the Nutri-Score calculator.

It reuses the SAME Nutri-Score algorithm implementation from
`nutriscore_app.py` (energy, sugar, saturated fat, salt, fibre, fruit/veg,
protein, sweetener penalty, water rule, category thresholds).

Limitations of this demo:
- Category fixed to **beverages (drink)**.
- Input mode: **manual entry for a single product**.
"""

import streamlit as st
import pandas as pd

# IMPORTANT:
# We import the processing + display functions from your existing file.
# That means ANY change you make to the algorithm in nutriscore_app.py
# is automatically reflected in this demo.
from nutriscore_app import process_dataframe, display_results


def main():
    st.title("Nutri-Score Calculator – Beverages Demo 🥤")

    # Category is hard-coded to beverages
    category = "drink"

    st.markdown("### Category: Beverages")
    st.caption(
        "This demo uses the updated **2023 Nutri-Score algorithm** "
        "for beverages only. The calculation logic is identical to the full app; "
        "only the interface is simplified for a single manual product."
    )

    # -----------------------------
    # Manual input form
    # -----------------------------
    st.subheader("Enter Product Details")

    product_name = st.text_input("Product Name")

    energy = st.number_input("Energy (kJ/100 mL)", min_value=0.0, step=1.0)
    sugar = st.number_input("Sugar (g/100 mL)", min_value=0.0, step=0.1)
    saturates = st.number_input("Saturated Fat (g/100 mL)", min_value=0.0, step=0.1)
    salt = st.number_input("Salt (g/100 mL)", min_value=0.0, step=0.01)

    fruit_veg = st.number_input(
        "Fruits, vegetables, and pulses (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.5,
    )
    fibre = st.number_input("Fibre (g/100 mL)", min_value=0.0, step=0.1)
    protein = st.number_input("Protein (g/100 mL)", min_value=0.0, step=0.1)

    contains_sweeteners = st.checkbox("Contains non-nutritive sweeteners")
    is_water = st.checkbox("Is water (without any addition)")

    if st.button("Calculate Nutri-Score"):
        # Create a single-row DataFrame from manual inputs.
        # Column names are kept EXACTLY the same as in nutriscore_app.py,
        # so process_dataframe() will behave identically.
        manual_data = {
            "Product Name": [product_name],
            "Energy (kJ/100 g)": [energy],
            "Sugar (g/100 g)": [sugar],
            "Saturates (g/100 g)": [saturates],
            "Salt (g/100 g)": [salt],
            "Fruits, vegetables, and pulses (%)": [fruit_veg],
            "Fibre (g/100 g)": [fibre],
            "Protein (g/100 g)": [protein],
            "Contains sweeteners": [contains_sweeteners],
            "is_water": [is_water],
        }

        df = pd.DataFrame(manual_data)

        # This uses the SAME algorithm as your main app:
        # - same scoring tables
        # - same sweetener penalty
        # - same water rule
        # - same N vs P rules
        result_df = process_dataframe(df, category)

        # And we reuse your existing display logic
        display_results(result_df)

    # Sidebar info
    st.sidebar.header("About")
    st.sidebar.info(
        """
        This is a demo version of the Nutri-Score calculator focused on
        **beverages**. All calculations are performed by the same
        2023 Nutri-Score algorithm implemented in `nutriscore_app.py`.
        """
    )


if __name__ == "__main__":
    main()

