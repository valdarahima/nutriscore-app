import streamlit as st
import pandas as pd

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
# Component scoring tables (capped as per Nutri-Score guidelines)
# ----------------------------
ENERGY_SCORING = {
    "general": [(0, 335, 0), (335, 670, 1), (670, 1005, 2), (1005, 1340, 3), (1340, 1675, 4), (1675, 2010, 5), (2010, 2345, 6), (2345, 2680, 7), (2680, 3015, 8), (3015, 3350, 9), (3350, float("inf"), 10)],
    "drink": [(0, 30, 0), (30, 90, 1), (90, 150, 2), (150, 210, 3), (210, 240, 4), (240, 270, 5), (270, 300, 6), (300, 330, 7), (330, 360, 8), (360, 390, 9), (390, float("inf"), 10)],
    "fat": [(0, 120, 0), (120, 240, 1), (240, 360, 2), (360, 480, 3), (480, 600, 4), (600, 720, 5), (720, 840, 6), (840, 960, 7), (960, 1080, 8), (1080, 1200, 9), (1200, float("inf"), 10)]
}

SUGAR_SCORING = {
    "general": [(0, 3.4, 0), (3.4, 6.8, 1), (6.8, 10, 2), (10, 14, 3), (14, 17, 4), (17, 20, 5), (20, 24, 6), (24, 27, 7), (27, 31, 8), (31, 34, 9), (34, 37, 10), (37, 41, 11), (41, 44, 12), (44, 48, 13), (48, 51, 14), (51, float("inf"), 15)],
    "drink": [(0, 0.5, 0), (0.5, 2, 1), (2, 3.5, 2), (3.5, 5, 3), (5, 6, 4), (6, 7, 5), (7, 8, 6), (8, 9, 7), (9, 10, 8), (10, 11, 9), (11, float("inf"), 10)],
    "fat": [(0, 3.4, 0), (3.4, 6.8, 1), (6.8, 10, 2), (10, 14, 3), (14, 17, 4), (17, 20, 5), (20, 24, 6), (24, 27, 7), (27, 31, 8), (31, 34, 9), (34, 37, 10), (37, 41, 11), (41, 44, 12), (44, 48, 13), (48, 51, 14), (51, float("inf"), 15)]
}

SAT_FAT_SCORING = {
    "general": [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4), (5, 6, 5), (6, 7, 6), (7, 8, 7), (8, 9, 8), (9, 10, 9), (10, float("inf"), 10)],
    "drink": [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4), (5, 6, 5), (6, 7, 6), (7, 8, 7), (8, 9, 8), (9, 10, 9), (10, float("inf"), 10)],
    "fat": [(0, 10, 0), (10, 16, 1), (16, 22, 2), (22, 28, 3), (28, 34, 4), (34, 40, 5), (40, 46, 6), (46, 52, 7), (52, 58, 8), (58, 64, 9), (64, float("inf"), 10)]
}

SODIUM_SCORING = {
    "general": [(0, 0.2, 0), (0.2, 0.4, 1), (0.4, 0.6, 2), (0.6, 0.8, 3), (0.8, 1, 4), (1, 1.2, 5), (1.2, 1.4, 6), (1.4, 1.6, 7), (1.6, 1.8, 8), (1.8, 2, 9), (2, 2.2, 10), (2.2, 2.4, 11), (2.4, 2.6, 12), (2.6, 2.8, 13), (2.8, 3.0, 14), (3.0, 3.2, 15), (3.2, 3.4, 16), (3.4, 3.6, 17), (3.6, 3.8, 18), (3.8, 4.0, 19), (4.0, float("inf"), 20)],
    "drink": [(0, 0.2, 0), (0.2, 0.4, 1), (0.4, 0.6, 2), (0.6, 0.8, 3), (0.8, 1, 4), (1, 1.2, 5), (1.2, 1.4, 6), (1.4, 1.6, 7), (1.6, 1.8, 8), (1.8, 2, 9), (2, 2.2, 10), (2.2, 2.4, 11), (2.4, 2.6, 12), (2.6, 2.8, 13), (2.8, 3.0, 14), (3.0, 3.2, 15), (3.2, 3.4, 16), (3.4, 3.6, 17), (3.6, 3.8, 18), (3.8, 4.0, 19), (4.0, float("inf"), 20)]
}

FRUIT_SCORING = {
    "general": [(0, 40, 0), (40, 60, 1), (60, 80, 2), (80, float("inf"), 5)],
    "drink": [(0, 40, 0), (40, 60, 2), (60, 80, 4), (80, float("inf"), 5)],
    "fat": [(0, 40, 0), (40, 60, 1), (60, 80, 2), (80, float("inf"), 6)]
}

FIBRE_SCORING = {
    "general": [(0, 3.0, 0), (3.0, 4.1, 1), (4.1, 5.2, 2), (5.2, 6.3, 3), (6.3, 7.4, 4), (7.4, float("inf"), 5)],
    "drink": [(0, 3.0, 0), (3.0, 4.1, 1), (4.1, 5.2, 2), (5.2, 6.3, 3), (6.3, 7.4, 4), (7.4, float("inf"), 5)],
    "fat": [(0, 3.0, 0), (3.0, 4.1, 1), (4.1, 5.2, 2), (5.2, 6.3, 3), (6.3, 7.4, 4), (7.4, float("inf"), 5)]
}

PROTEIN_SCORING = {
    "general": [(0, 2.4, 0), (2.4, 4.8, 1), (4.8, 7.2, 2), (7.2, 9.6, 3), (9.6, 12, 4), (12, 14, 5), (14, 17, 6), (17, float("inf"), 7)],
    "drink": [(0, 1.2, 0), (1.2, 1.5, 1), (1.5, 1.8, 2), (1.8, 2.1, 3), (2.1, 2.4, 4), (2.4, 2.7, 5), (2.7, 3.0, 6), (3.0, float("inf"), 7)],
    "fat": [(0, 2.4, 0), (2.4, 4.8, 1), (4.8, 7.2, 2), (7.2, 9.6, 3), (9.6, 12, 4), (12, 14, 5), (14, 17, 6), (17, float("inf"), 7)]
}

# ----------------------------
# Nutrient scoring functions
# ----------------------------
def score_component(value, scoring_table):
    for low, high, point in scoring_table:
        if low < value <= high:
            return point
    return scoring_table[-1][2]

def get_energy_points(value, category):
    return score_component(value, ENERGY_SCORING[category])

def get_energy_from_sat_fat_points(sat_fat_value, category):
    # Calculate energy from saturated fatty acids (sat_fat × 37 kJ/g)
    energy_from_sat_fat = sat_fat_value * 37
    return score_component(energy_from_sat_fat, ENERGY_SCORING[category])

def get_sugar_points(value, category):
    return score_component(value, SUGAR_SCORING[category])

def get_sat_fat_points(value, category):
    return score_component(value, SAT_FAT_SCORING[category])

def get_sodium_points(value, category):
    return score_component(value, SODIUM_SCORING[category])

def get_fruit_points(value, category):
    return score_component(value, FRUIT_SCORING[category])

def get_fibre_points(value, category):
    return score_component(value, FIBRE_SCORING[category])

def get_protein_points(value, category, is_red_meat=False):
    points = score_component(value, PROTEIN_SCORING[category])
    # Apply cap of 2 points for red meat products
    if category == "general" and is_red_meat:
        points = min(points, 2)
    return points

# ----------------------------
# Main Nutri-Score computation
# ----------------------------
def compute_score(row, category):
    # Get unfavorable components (N)
    if category == "fat":
        # For fats/oils, use energy from saturated fatty acids
        n_energy = get_energy_from_sat_fat_points(row["Saturates (g/100 g)"], category)
    else:
        n_energy = get_energy_points(row["Energy (kJ/100 g)"], category)
    
    n_sugar = get_sugar_points(row["Sugar (g/100 g)"], category)
    n_sat_fat = get_sat_fat_points(row["Saturates (g/100 g)"], category)
    n_sodium = get_sodium_points(row["Salt (g/100 g)"], category)
    
    # Add sweeteners penalty for beverages
    sweetener_points = 4 if category == "drink" and row.get("Contains sweeteners", False) else 0
    
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
    is_cheese = row.get("Is cheese", False)
    
    if category == "drink":
        # For beverages: always subtract all P points
        score = n_total - p_total
    elif category == "fat":
        # For fats, oils, nuts and seeds
        if n_total >= 7:
            score = n_total - (p_fibre + p_fruit)
        else:
            score = n_total - p_total
    else:  # General foods (incl. red meat and cheese)
        if n_total >= 11 and not is_cheese:
            score = n_total - (p_fibre + p_fruit)
        else:
            score = n_total - p_total
            
    return score

# ----------------------------
# Helper functions
# ----------------------------
def get_individual_scores(row, category):
    """Calculate and return individual component scores"""
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

def get_grade(score, category):
    """Determine the Nutri-Score grade based on the score and category"""
    # Special case for water
    if category == "drink" and score <= 0 and "is_water" in row and row["is_water"]:
        return "A"
    
    # Regular scoring
    for low, high, grade in CATEGORY_THRESHOLDS[category]:
        if low < score <= high:
            return grade
    return "E"  # Default to E if no threshold matched

# ----------------------------
# Streamlit App UI
# ----------------------------
st.title("Nutri-Score Calculator")

uploaded_file = st.file_uploader("Upload your product data (Excel file):", type=[".xlsx"])
category_display = st.selectbox("Select food category:", list(CATEGORY_MAP.keys()))
category = CATEGORY_MAP[category_display]

# Display category-specific input fields
if category == "general":
    st.info("For general foods, you should include 'Is red meat' and 'Is cheese' columns in your Excel file to apply special rules.")
elif category == "drink":
    st.info("For beverages, you should include a 'Contains sweeteners' column (Boolean) and optional 'is_water' column in your Excel file.")
elif category == "fat":
    st.info("For fats/oils category, energy is calculated from saturated fatty acids (Saturates × 37 kJ/g).")

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
            result_df["Nutri-Score Grade"] = result_df.apply(lambda row: get_grade(row["Nutri-Score Points"], category), axis=1)
            
            # Calculate N and P totals for display
            result_df["N-points Total"] = result_df["Energy Score"] + result_df["Sugar Score"] + \
                                          result_df["Saturates Score"] + result_df["Salt Score"] + \
                                          result_df["Sweetener Penalty"]
            
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
