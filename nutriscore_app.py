import streamlit as st
import pandas as pd
import io

# ----------------------------
# Category-specific scoring thresholds
# ----------------------------
CATEGORY_THRESHOLDS = {
    "general": [(-float("inf"), 0, "A"), (1, 2, "B"), (3, 10, "C"), (11, 18, "D"), (19, float("inf"), "E")],
    "drink": [(0, 2, "B"), (3, 6, "C"), (7, 9, "D"), (10, float("inf"), "E")],
    "fat": [(-float("inf"), -6, "A"), (-5, 2, "B"), (3, 10, "C"), (11, 18, "D"), (19, float("inf"), "E")]
}

CATEGORY_MAP = {
    "General food (incl. red meat and cheese)": "general",
    "Fats, oils, nuts and seeds": "fat",
    "Beverages": "drink"
}

# ----------------------------
# Component thresholds by category
# ----------------------------
SUGAR_SCORING = {
    "general": [(4.5, 0), (9, 1), (13.5, 2), (18, 3), (22.5, 4), (27, 5), (31, 6), (36, 7), (40, 8), (45, 9)],
    "drink": [(0, 0), (1.5, 1), (3, 2), (4.5, 3), (6, 4), (7.5, 5), (9, 6), (10.5, 7), (12, 8), (13.5, 9)],
    "fat": [(4.5, 0), (9, 1), (13.5, 2), (18, 3), (22.5, 4), (27, 5), (31, 6), (36, 7), (40, 8), (45, 9)]
}

ENERGY_SCORING = {
    "general": [(335, 0), (670, 1), (1005, 2), (1340, 3), (1675, 4), (2010, 5), (2345, 6), (2680, 7), (3015, 8), (3350, 9)],
    "drink": [(30, 0), (90, 1), (150, 2), (210, 3), (240, 4), (270, 5), (300, 6), (330, 7), (360, 8), (390, 9)],
    "fat": [(120, 0), (240, 1), (360, 2), (480, 3), (600, 4), (720, 5), (840, 6), (960, 7), (1080, 8), (1200, 9)]
}

SAT_FAT_SCORING = {
    "general": [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9)],
    "drink": [(0.1, 0), (0.2, 1), (0.3, 2), (0.4, 3), (0.5, 4), (0.6, 5), (0.7, 6), (0.8, 7), (0.9, 8), (1.0, 9)],
    "fat": [(2, 0), (4, 1), (6, 2), (8, 3), (10, 4), (12, 5), (14, 6), (16, 7), (18, 8), (20, 9)]
}

SODIUM_SCORING = {
    "general": [(90, 0), (180, 1), (270, 2), (360, 3), (450, 4), (540, 5), (630, 6), (720, 7), (810, 8), (900, 9)],
    "drink": [(30, 0), (60, 1), (90, 2), (120, 3), (150, 4), (180, 5), (210, 6), (240, 7), (270, 8), (300, 9)],
    "fat": [(90, 0), (180, 1), (270, 2), (360, 3), (450, 4), (540, 5), (630, 6), (720, 7), (810, 8), (900, 9)]
}

FRUIT_SCORING = {
    "general": [(40, 0), (60, 1), (80, 2)],
    "drink": [(40, 0), (60, 1), (80, 2)],
    "fat": [(40, 0), (60, 1), (80, 2)]
}

FIBER_SCORING = {
    "general": [(0.9, 0), (1.9, 1), (2.8, 2), (3.7, 3), (4.7, 4)],
    "drink": [(0.9, 0), (1.9, 1), (2.8, 2), (3.7, 3), (4.7, 4)],
    "fat": [(0.9, 0), (1.9, 1), (2.8, 2), (3.7, 3), (4.7, 4)]
}

PROTEIN_SCORING = {
    "general": [(1.6, 0), (3.2, 1), (4.8, 2), (6.4, 3), (8.0, 4)],
    "drink": [(0.9, 0), (1.9, 1), (2.8, 2), (3.7, 3), (4.7, 4)],
    "fat": [(0.9, 0), (1.9, 1), (2.8, 2), (3.7, 3), (4.7, 4)]
}

# ----------------------------
# Component scoring functions
# ----------------------------

def get_sugar_points(value, category):
    for threshold, point in SUGAR_SCORING[category]:
        if value <= threshold:
            return point
    return 10

def get_energy_points(kj, category):
    for threshold, point in ENERGY_SCORING[category]:
        if kj <= threshold:
            return point
    return 10

def get_sat_fat_points(sat_fat, category):
    for threshold, point in SAT_FAT_SCORING[category]:
        if sat_fat <= threshold:
            return point
    return 10

def get_sodium_points(sodium, category):
    for threshold, point in SODIUM_SCORING[category]:
        if sodium <= threshold:
            return point
    return 10

def get_fruit_points(percent, category):
    for threshold, point in FRUIT_SCORING[category]:
        if percent <= threshold:
            return point
    return 5

def get_fiber_points(fiber, category):
    for threshold, point in FIBER_SCORING[category]:
        if fiber <= threshold:
            return point
    return 5

def get_protein_points(protein, category):
    for threshold, point in PROTEIN_SCORING[category]:
        if protein <= threshold:
            return point
    return 5

def compute_score(row, category):
    fiber = row['Fibre (g/100 g)'] if pd.notnull(row['Fibre (g/100 g)']) else 0
    fruits = row['Fruits, vegetables, pulses, nuts, and rapeseed...'] if pd.notnull(row['Fruits, vegetables, pulses, nuts, and rapeseed...']) else 0
    protein = row['Protein (g/100 g)'] if pd.notnull(row['Protein (g/100 g)']) else 0
    energy = row['Energy (kJ/100 g)']
    sugar = row['Sugar (g/100 g)']
    sat_fat = row['Saturates (g/100 g)']
    sodium = row['Sodium (mg/100 g)']

    neg_energy = get_energy_points(energy, category)
    neg_sugar = get_sugar_points(sugar, category)
    neg_sat_fat = get_sat_fat_points(sat_fat, category)
    neg_sodium = get_sodium_points(sodium, category)
    neg = neg_energy + neg_sugar + neg_sat_fat + neg_sodium

    pos_fiber = get_fiber_points(fiber, category)
    pos_fruit = get_fruit_points(fruits, category)
    pos_protein = get_protein_points(protein, category)

    return neg, pos_protein, pos_fiber, pos_fruit

# ----------------------------
# Streamlit interface
# ----------------------------
st.title("Nutri-Score Calculator")

category_display = st.selectbox("Select food category:", list(CATEGORY_MAP.keys()))
category = CATEGORY_MAP[category_display]

uploaded = st.file_uploader("Upload Excel file", type="xlsx")

if uploaded:
    df = pd.read_excel(uploaded)

    def enrich(row):
        neg, prot, fib, fruit = compute_score(row, category)
        n_p = neg - (prot + fib + fruit)
        grade = next((g for low, high, g in CATEGORY_THRESHOLDS[category] if low <= n_p <= high), "?")
        return pd.Series({
            "NutriScore Grade": grade,
            "N-points": neg,
            "Protein points": prot,
            "Fiber points": fib,
            "Fruit/Veg points": fruit,
            "N-P calculation": n_p,
        })

    results = df.apply(enrich, axis=1)
    st.dataframe(pd.concat([df, results], axis=1))
