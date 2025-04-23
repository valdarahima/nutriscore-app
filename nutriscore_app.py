import streamlit as st
import pandas as pd

# ----------------------------
# Category-specific scoring thresholds
# ----------------------------
CATEGORY_THRESHOLDS = {
    "general": [(-float("inf"), 0, "A"), (1, 2, "B"), (3, 10, "C"), (11, 18, "D"), (19, float("inf"), "E")],
    "drink": [(-float("inf"), 0, "A"), (1, 2, "B"), (3, 6, "C"), (7, 9, "D"), (10, float("inf"), "E")],
    "fat": [(-float("inf"), -6, "A"), (-5, 2, "B"), (3, 10, "C"), (11, 18, "D"), (19, float("inf"), "E")]
}

CATEGORY_MAP = {
    "General food (incl. red meat and cheese)": "general",
    "Fats, oils, nuts and seeds": "fat",
    "Beverages": "drink"
}

# ----------------------------
# Component scoring tables (updated for beverages)
# ----------------------------
ENERGY_SCORING = {
    "general": [(0, 335, 0), (335, 670, 1), (670, 1005, 2), (1005, 1340, 3), (1340, 1675, 4), (1675, 2010, 5), (2010, 2345, 6), (2345, 2680, 7), (2680, 3015, 8), (3015, 3350, 9), (3350, float("inf"), 10)],
    "drink": [(0, 0, 0), (0, 30, 0), (30, 60, 1), (60, 90, 2), (90, 120, 3), (120, 150, 4), (150, 180, 5), (180, 210, 6), (210, 240, 7), (240, 270, 8), (270, float("inf"), 9)],
    "fat": [(0, 120, 0), (120, 240, 1), (240, 360, 2), (360, 480, 3), (480, 600, 4), (600, 720, 5), (720, 840, 6), (840, 960, 7), (960, 1080, 8), (1080, 1200, 9), (1200, float("inf"), 10)]
}

SUGAR_SCORING = {
    "general": [(0, 4.5, 0), (4.5, 9, 1), (9, 13.5, 2), (13.5, 18, 3), (18, 22.5, 4), (22.5, 27, 5), (27, 31, 6), (31, 36, 7), (36, 40, 8), (40, 45, 9), (45, float("inf"), 10)],
    "drink": [
    (float("-inf"), 1, 0),
    (1, 2, 1),
    (2, 3, 2),
    (3, 4, 3),
    (4, 5, 4),
    (5, 6, 5),
    (6, 7, 6),
    (7, 8, 7),
    (8, 9, 8),
    (9, 10, 9),
    (10, float("inf"), 10)
    ],
    "fat": [(0, 4.5, 0), (4.5, 9, 1), (9, 13.5, 2), (13.5, 18, 3), (18, 22.5, 4), (22.5, 27, 5), (27, 31, 6), (31, 36, 7), (36, 40, 8), (40, 45, 9), (45, float("inf"), 10)]
}

SAT_FAT_SCORING = {
    "general": [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4), (5, 6, 5), (6, 7, 6), (7, 8, 7), (8, 9, 8), (9, 10, 9), (10, float("inf"), 10)],
    "drink": [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4), (5, 6, 5), (6, 7, 6), (7, 8, 7), (8, 9, 8), (9, 10, 9), (10, float("inf"), 10)],
    "fat": [(0, 10, 0), (10, 16, 1), (16, 22, 2), (22, 28, 3), (28, 34, 4), (34, 40, 5), (40, 46, 6), (46, 52, 7), (52, 58, 8), (58, 64, 9), (64, float("inf"), 10)]
}

SALT_SCORING = {
    "general": [(0, 90, 0), (90, 180, 1), (180, 270, 2), (270, 360, 3), (360, 450, 4), (450, 540, 5), (540, 630, 6), (630, 720, 7), (720, 810, 8), (810, 900, 9), (900, float("inf"), 10)],
    "drink": [(0, 90, 0), (90, 180, 1), (180, 270, 2), (270, 360, 3), (360, 450, 4), (450, 540, 5), (540, 630, 6), (630, 720, 7), (720, 810, 8), (810, 900, 9), (900, float("inf"), 10)]
}

FRUIT_SCORING = {
    "general": [(0, 40, 0), (40, 60, 1), (60, 80, 2), (80, float("inf"), 5)],
    "drink": [(0, 40, 0), (40, 60, 2), (60, 80, 4), (80, float("inf"), 6)],
    "fat": [(0, 40, 0), (40, 60, 1), (60, 80, 2), (80, float("inf"), 5)]
}

FIBRE_SCORING = {
    "general": [(0, 0.9, 0), (0.9, 1.9, 1), (1.9, 2.8, 2), (2.8, 3.7, 3), (3.7, 4.7, 4), (4.7, float("inf"), 5)],
    "drink": [(0, 0.9, 0), (0.9, 1.9, 1), (1.9, 2.8, 2), (2.8, 3.7, 3), (3.7, 4.7, 4), (4.7, float("inf"), 5)],
    "fat": [(0, 0.9, 0), (0.9, 1.9, 1), (1.9, 2.8, 2), (2.8, 3.7, 3), (3.7, 4.7, 4), (4.7, float("inf"), 5)]
}

PROTEIN_SCORING = {
    "general": [(0, 1.6, 0), (1.6, 3.2, 1), (3.2, 4.8, 2), (4.8, 6.4, 3), (6.4, 8.0, 4), (8.0, float("inf"), 5)],
    "drink": [(0, 1.6, 0), (1.6, 3.2, 1), (3.2, 4.8, 2), (4.8, 6.4, 3), (6.4, 8.0, 4), (8.0, float("inf"), 5)],
    "fat": [(0, 1.6, 0), (1.6, 3.2, 1), (3.2, 4.8, 2), (4.8, 6.4, 3), (6.4, 8.0, 4), (8.0, float("inf"), 5)]
}

# ----------------------------
# Nutrient scoring functions
# ----------------------------
def score_component(value, scoring_table, rule_type="inclusive"):
    for low, high, point in scoring_table:
        if rule_type == "inclusive":
            if low <= value <= high:
                return point
        elif rule_type == "exclusive_lower":
            if low < value <= high:
                return point
        elif rule_type == "fruit_bev":
            if low < value <= high or (value == 80 and point == 6):
                return point
    return scoring_table[-1][2]  # fallback

def get_energy_points(value, category):
    return score_component(value, ENERGY_SCORING[category])

def get_energy_from_sat_fat_points(sat_fat_value, category):
    energy_from_sfa = sat_fat_value * 37  # kJ/g
    return score_component(energy_from_sfa, ENERGY_SCORING[category])

def get_sugar_points(value, category):
    return score_component(value, SUGAR_SCORING[category])

def get_sat_fat_points(value, category):
    rule = "exclusive_lower" if category == "drink" else "inclusive"
    return score_component(value, SAT_FAT_SCORING[category], rule)

def get_sodium_points(value, category):
    return score_component(value, SALT_SCORING[category])

def get_fruit_points(value, category):
    rule = "fruit_bev" if category == "drink" else "inclusive"
    return score_component(value, FRUIT_SCORING[category], rule)

def get_fibre_points(value, category):
    return score_component(value, FIBRE_SCORING[category])

def get_protein_points(value, category, is_red_meat=False):
    points = score_component(value, PROTEIN_SCORING[category])
    if category == "general" and is_red_meat:
        points = min(points, 2)
    return points

# ----------------------------
# Individual scores calculation
# ----------------------------
def get_individual_scores(row, category):
    scores = {}

    # N-component scores
    if category == "fat":
        scores["Energy Score"] = get_energy_from_sat_fat_points(row["Saturates (g/100 g)"], category)
    else:
        scores["Energy Score"] = get_energy_points(row["Energy (kJ/100 g)"], category)
    
    scores["Sugar Score"] = get_sugar_points(row["Sugar (g/100 g)"], category)
    scores["Saturates Score"] = get_sat_fat_points(row["Saturates (g/100 g)"], category)
    scores["Salt Score"] = get_sodium_points(row["Salt (g/100 g)"], category)
    
    # Sweetener penalty for beverages
    if category == "drink" and row.get("Contains sweeteners", False):
        scores["Sweetener Penalty"] = 4
    else:
        scores["Sweetener Penalty"] = 0
    
    # P-component scores
    scores["Fruit Score"] = get_fruit_points(row["Fruits, vegetables, and pulses (%)"], category)
    scores["Fibre Score"] = get_fibre_points(row["Fibre (g/100 g)"], category)
    
    is_red_meat = row.get("Is red meat", False)
    scores["Protein Score"] = get_protein_points(row["Protein (g/100 g)"], category, is_red_meat)
    
    return scores

# ----------------------------
# Main Nutri-Score computation
# ----------------------------
def compute_score(row, category):
    # Special case for water - should always be A grade
    if category == "drink" and row.get("is_water", False):
        return 0
    
    # Get unfavorable components (N)
    if category == "fat":
        n_energy = get_energy_from_sat_fat_points(row["Saturates (g/100 g)"], category)
    else:
        n_energy = get_energy_points(row["Energy (kJ/100 g)"], category)
    
    n_sugar = get_sugar_points(row["Sugar (g/100 g)"], category)
    n_sat_fat = get_sat_fat_points(row["Saturates (g/100 g)"], category)
    n_sodium = get_sodium_points(row["Salt (g/100 g)"], category)
    
    # Sweetener penalty for beverages
    sweetener_points = 4 if (category == "drink" and row.get("Contains sweeteners", False)) else 0
    
    # Get favorable components (P)
    p_fruit = get_fruit_points(row["Fruits, vegetables, and pulses (%)"], category)
    p_fibre = get_fibre_points(row["Fibre (g/100 g)"], category)
    
    # Apply red meat protein cap if needed
    is_red_meat = row.get("Is red meat", False)
    p_protein = get_protein_points(row["Protein (g/100 g)"], category, is_red_meat)
    
    # Calculate total points
    n_total = n_energy + n_sugar + n_sat_fat + n_sodium + sweetener_points
    p_total = p_fruit + p_fibre + p_protein
    
    # Calculate score based on category and algorithm
    if category == "drink":
        score = n_total - p_total
    elif category == "fat":
        score = n_total - (p_fruit + p_fibre) if n_total >= 7 else n_total - p_total
    else:  # General foods
        score = n_total - (p_fruit + p_fibre) if n_total >= 11 else n_total - p_total
            
    return score

def get_grade(score, category, row=None):
    """Determine the Nutri-Score grade based on the score and category"""
    # Special case for water
    if category == "drink" and row is not None and row.get("is_water", False):
        return "A"
    
    # Regular scoring
    for low, high, grade in CATEGORY_THRESHOLDS[category]:
        if low < score <= high:
            return grade
    return "E"

# ----------------------------
# Streamlit App UI
# ----------------------------
st.title("Nutri-Score Calculator")

uploaded_file = st.file_uploader("Upload your product data (Excel file):", type=["xlsx", "xls"])
category_display = st.selectbox("Select food category:", list(CATEGORY_MAP.keys()))
category = CATEGORY_MAP[category_display]

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        # Ensure required columns exist
        required_columns = ["Energy (kJ/100 g)", "Sugar (g/100 g)", "Saturates (g/100 g)", 
                          "Salt (g/100 g)", "Fruits, vegetables, and pulses (%)", 
                          "Fibre (g/100 g)", "Protein (g/100 g)"]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
        else:
            # Calculate Nutri-Score
            df["Nutri-Score Points"] = df.apply(lambda row: compute_score(row, category), axis=1)
            
            # Add individual component scores
            component_scores = df.apply(lambda row: get_individual_scores(row, category), axis=1)
            component_df = pd.DataFrame(component_scores.tolist())
            
            # Combine dataframes
            result_df = pd.concat([df, component_df], axis=1)
            
            # Calculate final grade
            result_df["Nutri-Score Grade"] = result_df.apply(
                lambda row: get_grade(row["Nutri-Score Points"], category, row), axis=1)
            
            # Calculate N and P totals for display
            result_df["N-points Total"] = result_df["Energy Score"] + result_df["Sugar Score"] + \
                                        result_df["Saturates Score"] + result_df["Salt Score"] + \
                                        result_df.get("Sweetener Penalty", 0)
            
            result_df["P-points Total"] = result_df["Fruit Score"] + result_df["Fibre Score"] + \
                                        result_df["Protein Score"]
            
            # Display the results
            st.subheader("Nutri-Score Results")
            st.dataframe(result_df)
            
            # Download button for results
            csv = result_df.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="nutri_score_results.csv",
                mime="text/csv",
            )
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
