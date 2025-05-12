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
# Component scoring tables
# ----------------------------
ENERGY_SCORING = {
    "general": [(0, 335, 0), (335, 670, 1), (670, 1005, 2), (1005, 1340, 3), (1340, 1675, 4), 
                (1675, 2010, 5), (2010, 2345, 6), (2345, 2680, 7), (2680, 3015, 8), (3015, 3350, 9), 
                (3350, float("inf"), 10)],
    "drink": [(0, 30, 0), (30, 90, 1), (90, 150, 2), (150, 210, 3), (210, 240, 4), 
             (240, 270, 5), (270, 300, 6), (300, 330, 7), (330, 360, 8), (360, 390, 9), 
             (390, float("inf"), 10)],
    "fat": [(0, 120, 0), (120, 240, 1), (240, 360, 2), (360, 480, 3), (480, 600, 4), 
           (600, 720, 5), (720, 840, 6), (840, 960, 7), (960, 1080, 8), (1080, 1200, 9), 
           (1200, float("inf"), 10)]
}

SUGAR_SCORING = {
    "general": [(0, 3.4, 0), (3.4, 6.8, 1), (6.8, 10, 2), (10, 14, 3), (14, 17, 4), 
                (17, 20, 5), (20, 24, 6), (24, 27, 7), (27, 31, 8), (31, 34, 9), 
                (34, 37, 10), (37, 41, 11), (41, 44, 12), (44, 48, 13), (48, 51, 14), 
                (51, float("inf"), 15)],
    "drink": [(0, 0.5, 0), (0.5, 2, 1), (2, 3.5, 2), (3.5, 5, 3), (5, 6, 4), 
             (6, 7, 5), (7, 8, 6), (8, 9, 7), (9, 10, 8), (10, 11, 9), 
             (11, float("inf"), 10)],
    "fat": [(0, 3.4, 0), (3.4, 6.8, 1), (6.8, 10, 2), (10, 14, 3), (14, 17, 4), 
           (17, 20, 5), (20, 24, 6), (24, 27, 7), (27, 31, 8), (31, 34, 9), 
           (34, 37, 10), (37, 41, 11), (41, 44, 12), (44, 48, 13), (48, 51, 14), 
           (51, float("inf"), 15)]
}

SAT_FAT_SCORING = {
    "general": [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4), (5, 6, 5), 
                (6, 7, 6), (7, 8, 7), (8, 9, 8), (9, 10, 9), (10, float("inf"), 10)],
    "drink": [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4), (5, 6, 5), 
             (6, 7, 6), (7, 8, 7), (8, 9, 8), (9, 10, 9), (10, float("inf"), 10)],
    "fat": [(0, 10, 0), (10, 16, 1), (16, 22, 2), (22, 28, 3), (28, 34, 4), (34, 40, 5), 
           (40, 46, 6), (46, 52, 7), (52, 58, 8), (58, 64, 9), (64, float("inf"), 10)]
}

SALT_SCORING = {
    "general": [(0, 0.2, 0), (0.2, 0.4, 1), (0.4, 0.6, 2), (0.6, 0.8, 3), (0.8, 1.0, 4), 
                (1.0, 1.2, 5), (1.2, 1.4, 6), (1.4, 1.6, 7), (1.6, 1.8, 8), (1.8, 2.0, 9), 
                (2.0, 2.2, 10), (2.2, 2.4, 11), (2.4, 2.6, 12), (2.6, 2.8, 13), (2.8, 3.0, 14), 
                (3.0, 3.2, 15), (3.2, 3.4, 16), (3.4, 3.6, 17), (3.6, 3.8, 18), (3.8, 4.0, 19), 
                (4.0, float("inf"), 20)],
    "drink": [(0, 0.2, 0), (0.2, 0.4, 1), (0.4, 0.6, 2), (0.6, 0.8, 3), (0.8, 1.0, 4), 
             (1.0, 1.2, 5), (1.2, 1.4, 6), (1.4, 1.6, 7), (1.6, 1.8, 8), (1.8, 2.0, 9), 
             (2.0, 2.2, 10), (2.2, 2.4, 11), (2.4, 2.6, 12), (2.6, 2.8, 13), (2.8, 3.0, 14), 
             (3.0, 3.2, 15), (3.2, 3.4, 16), (3.4, 3.6, 17), (3.6, 3.8, 18), (3.8, 4.0, 19), 
             (4.0, float("inf"), 20)],
    "fat": [(0, 0.2, 0), (0.2, 0.4, 1), (0.4, 0.6, 2), (0.6, 0.8, 3), (0.8, 1.0, 4), 
           (1.0, 1.2, 5), (1.2, 1.4, 6), (1.4, 1.6, 7), (1.6, 1.8, 8), (1.8, 2.0, 9), 
           (2.0, 2.2, 10), (2.2, 2.4, 11), (2.4, 2.6, 12), (2.6, 2.8, 13), (2.8, 3.0, 14), 
           (3.0, 3.2, 15), (3.2, 3.4, 16), (3.4, 3.6, 17), (3.6, 3.8, 18), (3.8, 4.0, 19), 
           (4.0, float("inf"), 20)]
}

FRUIT_SCORING = {
    "general": [(0, 40, 0), (40, 60, 2), (60, 80, 5), (80, float("inf"), 5)],
    "drink": [(0, 40, 0), (40, 60, 2), (60, 80, 4), (80, float("inf"), 6)],
    "fat": [(0, 40, 0), (40, 60, 2), (60, 80, 5), (80, float("inf"), 5)]
}

FIBRE_SCORING = {
    "general": [(0, 3.0, 0), (3.0, 4.1, 2), (4.1, 5.2, 3), (5.2, 6.3, 4), (6.3, 7.4, 5), (7.4, float("inf"), 5)],
    "drink": [(0, 3.0, 0), (3.0, 4.1, 2), (4.1, 5.2, 3), (5.2, 6.3, 4), (6.3, 7.4, 5), (7.4, float("inf"), 5)],
    "fat": [(0, 3.0, 0), (3.0, 4.1, 2), (4.1, 5.2, 3), (5.2, 6.3, 4), (6.3, 7.4, 5), (7.4, float("inf"), 5)]
}

PROTEIN_SCORING = {
    "general": [(0, 1.2, 0), (1.2, 2.4, 1), (2.4, 4.8, 2), (4.8, 7.2, 3), (7.2, 9.6, 4), (9.6, 12.0, 5), 
                (12.0, 14.0, 6), (14.0, 17.0, 7), (17.0, float("inf"), 8)],
    "drink": [(0, 1.2, 0), (1.2, 1.5, 1), (1.5, 1.8, 2), (1.8, 2.1, 3), (2.1, 2.4, 4), (2.4, 2.7, 5), 
              (2.7, 3.0, 6), (3.0, float("inf"), 7)],
    "fat": [(0, 1.2, 0), (1.2, 2.4, 1), (2.4, 4.8, 2), (4.8, 7.2, 3), (7.2, 9.6, 4), (9.6, 12.0, 5), 
            (12.0, 14.0, 6), (14.0, 17.0, 7), (17.0, float("inf"), 8)]
}

# ----------------------------
# Scoring functions
# ----------------------------
def score_component(value, scoring_table):
    for low, high, point in scoring_table:
        if low <= value < high:
            return point
    # For the last range, include the upper bound
    for low, high, point in reversed(scoring_table):
        if value >= low:
            return point
    return 0  # Default fallback

def get_energy_points(value, category):
    return score_component(value, ENERGY_SCORING[category])

def get_sugar_points(value, category):
    return score_component(value, SUGAR_SCORING[category])

def get_saturates_points(value, category):
    return score_component(value, SAT_FAT_SCORING[category])

def get_salt_points(value, category):
    return score_component(value, SALT_SCORING[category])

def get_fruit_points(value, category):
    return score_component(value, FRUIT_SCORING[category])

def get_fibre_points(value, category):
    return score_component(value, FIBRE_SCORING[category])

def get_protein_points(value, category, is_red_meat=False):
    points = score_component(value, PROTEIN_SCORING[category])
    if category == "general" and is_red_meat:
        points = min(points, 2)  # Cap protein points at 2 for red meat
    return points

# ----------------------------
# Component scoring calculations
# ----------------------------
def calculate_component_scores(row, category):
    scores = {}
    
    # N-points (negative)
    scores["Energy Score"] = get_energy_points(row["Energy (kJ/100 g)"], category)
    scores["Sugar Score"] = get_sugar_points(row["Sugar (g/100 g)"], category)
    scores["Saturates Score"] = get_saturates_points(row["Saturates (g/100 g)"], category)
    scores["Salt Score"] = get_salt_points(row["Salt (g/100 g)"], category)
    
    # Sweetener penalty for beverages
    scores["Sweetener Penalty"] = 4 if category == "drink" and row.get("Contains sweeteners", False) else 0
    
    # P-points (positive)
    scores["Fruit Score"] = get_fruit_points(row["Fruits, vegetables, and pulses (%)"], category)
    scores["Fibre Score"] = get_fibre_points(row["Fibre (g/100 g)"], category)
    scores["Protein Score"] = get_protein_points(row["Protein (g/100 g)"], category, row.get("Is red meat", False))
    
    return scores

# ----------------------------
# Nutri-Score calculation
# ----------------------------
def calculate_nutri_score(row, category):
    # Special case for water
    if category == "drink" and row.get("Is Water", False):
        return 0, "A"
    
    # Calculate component scores
    scores = calculate_component_scores(row, category)
    
    # Calculate point totals
    n_points = (scores["Energy Score"] + scores["Sugar Score"] + 
                scores["Saturates Score"] + scores["Salt Score"] + 
                scores["Sweetener Penalty"])
    
    p_points = (scores["Fruit Score"] + scores["Fibre Score"] + scores["Protein Score"])
    
    # Apply category-specific calculations
    if category == "drink":
        # For beverages, always subtract all P points
        final_score = n_points - p_points
    elif category == "fat":
        # For fats, if N points ≥ 7, only subtract fiber and fruit points
        if n_points >= 7:
            final_score = n_points - (scores["Fruit Score"] + scores["Fibre Score"])
        else:
            final_score = n_points - p_points
    else:  # General foods
        # For general foods, if N points ≥ 11, only subtract fiber and fruit points
        if n_points >= 11:
            final_score = n_points - (scores["Fruit Score"] + scores["Fibre Score"])
        else:
            final_score = n_points - p_points
    
    # Determine grade
    for low, high, grade in CATEGORY_THRESHOLDS[category]:
        if low <= final_score <= high:
            return final_score, grade
    
    return final_score, "E"  # Default fallback

# ----------------------------
# Streamlit App
# ----------------------------
st.title("Nutri-Score Calculator")

uploaded_file = st.file_uploader("Upload your product data (CSV file):", type=["csv", "xlsx", "xls"])
category_display = st.selectbox("Select food category:", list(CATEGORY_MAP.keys()))
category = CATEGORY_MAP[category_display]

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Ensure required columns exist
        required_columns = [
            "Energy (kJ/100 g)", "Sugar (g/100 g)", "Saturates (g/100 g)", 
            "Salt (g/100 g)", "Fruits, vegetables, and pulses (%)", 
            "Fibre (g/100 g)", "Protein (g/100 g)"
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
        else:
            # Calculate component scores for each row
            all_scores = []
            for _, row in df.iterrows():
                scores = calculate_component_scores(row, category)
                all_scores.append(scores)
            
            component_scores_df = pd.DataFrame(all_scores)
            
            # Calculate Nutri-Score values and grades
            nutri_scores = []
            for _, row in df.iterrows():
                score, grade = calculate_nutri_score(row, category)
                nutri_scores.append({"Score": score, "Grade": grade})
            
            nutri_scores_df = pd.DataFrame(nutri_scores)
            
            # Create final output dataframe with all data
            result_df = pd.DataFrame()
            
            # Add raw values
            result_df["Energy (kJ/100 g)"] = df["Energy (kJ/100 g)"]
            result_df["Sugar (g/100 g)"] = df["Sugar (g/100 g)"]
            result_df["Saturates (g/100 g)"] = df["Saturates (g/100 g)"]
            result_df["Salt (g/100 g)"] = df["Salt (g/100 g)"]
            result_df["Contains sweeteners"] = df.get("Contains sweeteners", False)
            result_df["Is Water"] = df.get("Is Water", False)
            result_df["Fruits, vegetables, and pulses (%)"] = df["Fruits, vegetables, and pulses (%)"]
            result_df["Fibre (g/100 g)"] = df["Fibre (g/100 g)"]
            result_df["Protein (g/100 g)"] = df["Protein (g/100 g)"]
            
            # Add component scores
            result_df["Energy Score"] = component_scores_df["Energy Score"]
            result_df["Sugar Score"] = component_scores_df["Sugar Score"] 
            result_df["Saturates Score"] = component_scores_df["Saturates Score"]
            result_df["Salt Score"] = component_scores_df["Salt Score"]
            result_df["Sweetener Penalty"] = component_scores_df["Sweetener Penalty"]
            result_df["Fruit Score"] = component_scores_df["Fruit Score"]
            result_df["Fibre Score"] = component_scores_df["Fibre Score"]
            result_df["Protein Score"] = component_scores_df["Protein Score"]
            
            # Calculate totals
            result_df["N-points Total"] = (result_df["Energy Score"] + result_df["Sugar Score"] + 
                                          result_df["Saturates Score"] + result_df["Salt Score"] + 
                                          result_df["Sweetener Penalty"])
            
            result_df["P-points Total"] = (result_df["Fruit Score"] + result_df["Fibre Score"] + 
                                          result_df["Protein Score"])
            
            # Add Nutri-Score
            result_df["Nutri-Score Points"] = nutri_scores_df["Score"]
            result_df["Nutri-Score Grade"] = nutri_scores_df["Grade"]
            
            # Display results
            st.subheader("Nutri-Score Results")
            st.dataframe(result_df)
            
            # Download results
            csv = result_df.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="nutri_score_results.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
