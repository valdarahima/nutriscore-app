import streamlit as st
import pandas as pd

# NutriScore calculation functions (simplified from EU logic)
def get_energy_points(kj):
    if kj <= 335: return 0
    elif kj <= 670: return 1
    elif kj <= 1005: return 2
    elif kj <= 1340: return 3
    elif kj <= 1675: return 4
    elif kj <= 2010: return 5
    elif kj <= 2345: return 6
    elif kj <= 2680: return 7
    elif kj <= 3015: return 8
    elif kj <= 3350: return 9
    else: return 10

def get_sugar_points(sugar):
    if sugar <= 4.5: return 0
    elif sugar <= 9: return 1
    elif sugar <= 13.5: return 2
    elif sugar <= 18: return 3
    elif sugar <= 22.5: return 4
    elif sugar <= 27: return 5
    elif sugar <= 31: return 6
    elif sugar <= 36: return 7
    elif sugar <= 40: return 8
    elif sugar <= 45: return 9
    else: return 10

def get_sat_fat_points(sat_fat):
    if sat_fat <= 1: return 0
    elif sat_fat <= 2: return 1
    elif sat_fat <= 3: return 2
    elif sat_fat <= 4: return 3
    elif sat_fat <= 5: return 4
    elif sat_fat <= 6: return 5
    elif sat_fat <= 7: return 6
    elif sat_fat <= 8: return 7
    elif sat_fat <= 9: return 8
    elif sat_fat <= 10: return 9
    else: return 10

def get_sodium_points(sodium):
    if sodium <= 90: return 0
    elif sodium <= 180: return 1
    elif sodium <= 270: return 2
    elif sodium <= 360: return 3
    elif sodium <= 450: return 4
    elif sodium <= 540: return 5
    elif sodium <= 630: return 6
    elif sodium <= 720: return 7
    elif sodium <= 810: return 8
    elif sodium <= 900: return 9
    else: return 10

def get_fruit_points(percent):
    if percent <= 40: return 0
    elif percent <= 60: return 1
    elif percent <= 80: return 2
    else: return 5

def get_fiber_points(fiber):
    if fiber <= 0.9: return 0
    elif fiber <= 1.9: return 1
    elif fiber <= 2.8: return 2
    elif fiber <= 3.7: return 3
    elif fiber <= 4.7: return 4
    else: return 5

def get_protein_points(protein):
    if protein <= 1.6: return 0
    elif protein <= 3.2: return 1
    elif protein <= 4.8: return 2
    elif protein <= 6.4: return 3
    elif protein <= 8.0: return 4
    else: return 5

def classify_nutriscore(score):
    if score <= -1: return "A"
    elif score <= 2: return "B"
    elif score <= 10: return "C"
    elif score <= 18: return "D"
    else: return "E"

st.title("NutriScore Bulk Calculator")
st.write("Upload your Excel file with product info and get NutriScore grades calculated for each item.")

uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)

    # Rename columns to standard names (assumed from gov sheet)
    df.columns = [col.strip().split("\n")[0].strip() for col in df.columns]
    required = ['Products', 'Energy (kJ/100 g)', 'Sugar (g/100 g)', 'Saturates (g/100 g)',
                'Sodium (mg/100 g)', 'Fruits, vegetables, pulses, nuts, and rapeseed...',
                'Fibre (g/100 g)', 'Protein (g/100 g)']

    missing = [r for r in required if r not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
    else:
        def compute_score(row):
            neg = (
                get_energy_points(row[required[1]]) +
                get_sugar_points(row[required[2]]) +
                get_sat_fat_points(row[required[3]]) +
                get_sodium_points(row[required[4]])
            )
            pos = (
                get_fruit_points(row[required[5]]) +
                get_fiber_points(row[required[6]]) +
                get_protein_points(row[required[7]])
            )
            score = neg - pos
            return score, classify_nutriscore(score)

        df[['NutriScore Points', 'NutriScore Grade']] = df.apply(lambda row: pd.Series(compute_score(row)), axis=1)

        st.success("NutriScore calculated for all products!")
        st.dataframe(df[['Products', 'NutriScore Points', 'NutriScore Grade']])

        st.download_button(
            label="Download Results as Excel",
            data=df.to_excel(index=False, engine='openpyxl'),
            file_name="nutriscore_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
