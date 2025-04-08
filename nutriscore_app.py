import streamlit as st
import pandas as pd
import io

# ----------------------------
# Category-specific scoring thresholds
# ----------------------------
CATEGORY_THRESHOLDS = {
    "general": [(-float("inf"), 0, "A"), (1, 2, "B"), (3, 10, "C"), (11, 18, "D"), (19, float("inf"), "E")],
    "drink": [(float("nan"), float("nan"), "A"), (0, 2, "B"), (3, 6, "C"), (7, 9, "D"), (10, float("inf"), "E")],
    "fat": [(-float("inf"), -6, "A"), (-5, 2, "B"), (3, 10, "C"), (11, 18, "D"), (19, float("inf"), "E")]
}

# ----------------------------
# Component scoring functions (simplified)
# ----------------------------
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

# ----------------------------
# Grade classification based on category
# ----------------------------
def classify_nutriscore(score, category):
    for low, high, grade in CATEGORY_THRESHOLDS[category]:
        if low <= score <= high:
            return grade
    return "?"

# ----------------------------
# Streamlit App Interface
# ----------------------------
st.title("NutriScore Bulk Calculator")
st.write("Upload your Excel file with product info and get NutriScore grades calculated for each item.")

category = st.selectbox("Select product category", ["general", "drink", "fat"], format_func=lambda x: x.capitalize())

uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)
    df.columns = [col.strip().split("\n")[0].strip() for col in df.columns]

    required = ['Products', 'Energy (kJ/100 g)', 'Sugar (g/100 g)', 'Saturates (g/100 g)',
                'Sodium (mg/100 g)', 'Fruits, vegetables, pulses, nuts, and rapeseed...',
                'Fibre (g/100 g)', 'Protein (g/100 g)']

    missing = [r for r in required if r not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
    else:
        warning_rows = []

        def compute_score(row):
            try:
                fiber = row[required[6]] if pd.notnull(row[required[6]]) else 0
                fruits = row[required[5]] if pd.notnull(row[required[5]]) else 0
                protein = row[required[7]] if pd.notnull(row[required[7]]) else 0

                critical_missing = []
                for idx in [1, 2, 3, 4]:
                    if pd.isnull(row[required[idx]]):
                        critical_missing.append(required[idx])

                if critical_missing:
                    warning_rows.append((row[required[0]], critical_missing))
                    return None, "Missing critical data"

                neg = (
                    get_energy_points(row[required[1]]) +
                    get_sugar_points(row[required[2]]) +
                    get_sat_fat_points(row[required[3]]) +
                    get_sodium_points(row[required[4]])
                )

                pos_fiber = get_fiber_points(fiber)
                pos_fruit = get_fruit_points(fruits)
                pos_protein = get_protein_points(protein)

                if category == "fat":
                    if neg >= 7:
                        score = neg - pos_fiber - pos_fruit
                    else:
                        score = neg - (pos_protein + pos_fiber + pos_fruit)
                elif category == "general":
                    if neg > 11:
                        pos_protein = min(pos_protein, 2)
                        score = neg - pos_fiber - pos_fruit - pos_protein
                    else:
                        score = neg - (pos_protein + pos_fiber + pos_fruit)
                else:  # drink
                    score = neg - (pos_protein + pos_fiber + pos_fruit)

                return score, classify_nutriscore(score, category)
            except:
                return None, "Error"

        df[['NutriScore Points', 'NutriScore Grade']] = df.apply(lambda row: pd.Series(compute_score(row)), axis=1)

        if warning_rows:
            st.warning("Some products have missing critical values (energy, sugar, saturated fat, sodium):")
            for product, fields in warning_rows:
                st.write(f"\n- {product}: missing {', '.join(fields)}")

        st.success("NutriScore calculated for all products!")
        st.dataframe(df[['Products', 'NutriScore Points', 'NutriScore Grade']])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="Download Results as Excel",
            data=output,
            file_name="nutriscore_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
