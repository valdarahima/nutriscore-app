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
# FIXED: Updated tables based on PDF documentation
ENERGY_SCORING = {
    "general": [(0, 335, 0), (335, 670, 1), (670, 1005, 2), (1005, 1340, 3), (1340, 1675, 4), 
               (1675, 2010, 5), (2010, 2345, 6), (2345, 2680, 7), (2680, 3015, 8), 
               (3015, 3350, 9), (3350, float("inf"), 10)],
    "drink": [
        (float("-inf"), 30, 0),
        (30, 90, 1),
        (90, 150, 2),
        (150, 210, 3),
        (210, 240, 4),
        (240, 270, 5),
        (270, 300, 6),
        (300, 330, 7),
        (330, 360, 8),
        (360, 390, 9),
        (390, float("inf"), 10)
    ],
    "fat": [(0, 120, 0), (120, 240, 1), (240, 360, 2), (360, 480, 3), (480, 600, 4), 
           (600, 720, 5), (720, 840, 6), (840, 960, 7), (960, 1080, 8), 
           (1080, 1200, 9), (1200, float("inf"), 10)]
}

SUGAR_SCORING = {
    "general": [(0, 3.4, 0), (3.4, 6.8, 1), (6.8, 10, 2), (10, 14, 3), (14, 17, 4), 
               (17, 20, 5), (20, 24, 6), (24, 27, 7), (27, 31, 8), 
               (31, 34, 9), (34, float("inf"), 10)],
    "drink": [
        (float("-inf"), 0.5, 0),
        (0.5, 2, 1),
        (2, 3.5, 2),
        (3.5, 5, 3),
        (5, 6, 4),
        (6, 7, 5),
        (7, 8, 6),
        (8, 9, 7),
        (9, 10, 8),
        (10, 11, 9),
        (11, float("inf"), 10)
    ],
    "fat": [(0, 3.4, 0), (3.4, 6.8, 1), (6.8, 10, 2), (10, 14, 3), (14, 17, 4), 
           (17, 20, 5), (20, 24, 6), (24, 27, 7), (27, 31, 8), 
           (31, 34, 9), (34, float("inf"), 10)]
}

# FIXED: Updated to match PDF documentation exactly for beverages
SAT_FAT_SCORING = {
    "general": [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4), 
               (5, 6, 5), (6, 7, 6), (7, 8, 7), (8, 9, 8), 
               (9, 10, 9), (10, float("inf"), 10)],
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
    "fat": [(0, 10, 0), (10, 16, 1), (16, 22, 2), (22, 28, 3), (28, 34, 4), 
           (34, 40, 5), (40, 46, 6), (46, 52, 7), (52, 58, 8), 
           (58, 64, 9), (64, float("inf"), 10)]
}

# FIXED: Salt scoring for beverages from the PDF
SALT_SCORING = {
    "general": [(0, 0.2, 0), (0.2, 0.4, 1), (0.4, 0.6, 2), (0.6, 0.8, 3), (0.8, 1.0, 4), 
               (1.0, 1.2, 5), (1.2, 1.4, 6), (1.4, 1.6, 7), (1.6, 1.8, 8), 
               (1.8, 2.0, 9), (2.0, float("inf"), 10)],
    "drink": [
        (float("-inf"), 0.2, 0),
        (0.2, 0.4, 1),
        (0.4, 0.6, 2),
        (0.6, 0.8, 3),
        (0.8, 1.0, 4),
        (1.0, 1.2, 5),
        (1.2, 1.4, 6),
        (1.4, 1.6, 7),
        (1.6, 1.8, 8),
        (1.8, 2.0, 9),
        (2.0, float("inf"), 10)
    ],
    "fat": [(0, 0.2, 0), (0.2, 0.4, 1), (0.4, 0.6, 2), (0.6, 0.8, 3), (0.8, 1.0, 4), 
           (1.0, 1.2, 5), (1.2, 1.4, 6), (1.4, 1.6, 7), (1.6, 1.8, 8), 
           (1.8, 2.0, 9), (2.0, float("inf"), 10)]
}

# FIXED: Updated fruit scoring for beverages per PDF
FRUIT_SCORING = {
    "general": [(0, 40, 0), (40, 60, 1), (60, 80, 2), (80, float("inf"), 5)],
    "drink": [
        (0, 40, 0),
        (40, 60, 2),
        (60, 80, 4),
        (80, float("inf"), 6)
    ],
    "fat": [(0, 40, 0), (40, 60, 1), (60, 80, 2), (80, float("inf"), 5)]
}

FIBRE_SCORING = {
    "general": [(0, 3.0, 0), (3.0, 4.1, 1), (4.1, 5.2, 2), (5.2, 6.3, 3), (6.3, 7.4, 4), (7.4, float("inf"), 5)],
    "drink": [
        (float("-inf"), 3.0, 0),
        (3.0, 4.1, 1),
        (4.1, 5.2, 2),
        (5.2, 6.3, 3),
        (6.3, 7.4, 4),
        (7.4, float("inf"), 5)
    ],
    "fat": [(0, 3.0, 0), (3.0, 4.1, 1), (4.1, 5.2, 2), (5.2, 6.3, 3), (6.3, 7.4, 4), (7.4, float("inf"), 5)]
}

PROTEIN_SCORING = {
    "general": [(0, 2.4, 0), (2.4, 4.8, 1), (4.8, 7.2, 2), (7.2, 9.6, 3), (9.6, 12.0, 4), (12.0, float("inf"), 5)],
    "drink": [
        (float("-inf"), 1.2, 0),
        (1.2, 1.5, 1),
        (1.5, 1.8, 2),
        (1.8, 2.1, 3),
        (2.1, 2.4, 4),
        (2.4, float("inf"), 5)
    ],
    "fat": [(0, 2.4, 0), (2.4, 4.8, 1), (4.8, 7.2, 2), (7.2, 9.6, 3), (9.6, 12.0, 4), (12.0, float("inf"), 5)]
}

# ----------------------------
# Nutrient scoring functions - FIXED: Updated to handle thresholds correctly
# ----------------------------
def score_component(value, scoring_table):
    """Score a component using its scoring table with proper threshold handling.
    Now uses "less than or equal to" for the upper bound, which matches the PDF tables."""
    for low, high, point in scoring_table:
        if low < value <= high:
            return point
    # If no match found, return the highest points value (for values exceeding the highest threshold)
    return scoring_table[-1][2]

def get_energy_points(value, category):
    return score_component(value, ENERGY_SCORING[category])

def get_energy_from_sat_fat_points(sat_fat_value, category):
    energy_from_sfa = sat_fat_value * 37  # kJ/g
    return score_component(energy_from_sfa, ENERGY_SCORING[category])

def get_sugar_points(value, category):
    return score_component(value, SUGAR_SCORING[category])

def get_sat_fat_points(value, category):
    return score_component(value, SAT_FAT_SCORING[category])

def get_sodium_points(value, category):
    return score_component(value, SALT_SCORING[category])

def get_fruit_points(value, category):
    return score_component(value, FRUIT_SCORING[category])

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
    # Special case for water - should always get an A
    if category == "drink" and row is not None and row.get("is_water", False):
        return "A"
    
    # Regular scoring
    for low, high, grade in CATEGORY_THRESHOLDS[category]:
        if low <= score <= high:
            return grade
    return "E"  # Default to E if no match found

# ----------------------------
# Data processing functions (MOVED UP - this was causing the NameError)
# ----------------------------
def process_dataframe(df, category):
    """Process a dataframe to calculate Nutri-Score values"""
    # Calculate individual component scores
    component_scores = df.apply(lambda row: get_individual_scores(row, category), axis=1)
    component_df = pd.DataFrame(component_scores.tolist())
    
    # Include original nutrient values
    raw_nutrients = df[[
        "Energy (kJ/100 g)", "Sugar (g/100 g)", "Saturates (g/100 g)",
        "Salt (g/100 g)", "Fruits, vegetables, and pulses (%)",
        "Fibre (g/100 g)", "Protein (g/100 g)"
    ]].copy()

    # Add flags if they exist
    if "Contains sweeteners" in df.columns:
        raw_nutrients["Contains sweeteners"] = df["Contains sweeteners"]
    if "Is red meat" in df.columns:
        raw_nutrients["Is red meat"] = df["Is red meat"]
    if "is_water" in df.columns:
        raw_nutrients["Is Water"] = df["is_water"]
    
    # Add product name if it exists
    if "Product Name" in df.columns:
        raw_nutrients["Product Name"] = df["Product Name"]
                
    # Combine everything
    result_df = pd.concat([raw_nutrients, component_df], axis=1)
    
    # Calculate final score and grade
    result_df["Nutri-Score Points"] = df.apply(lambda row: compute_score(row, category), axis=1)
    result_df["Nutri-Score Grade"] = result_df.apply(
        lambda row: get_grade(row["Nutri-Score Points"], category, row), axis=1
    )
    
    # Calculate N and P component totals
    result_df["N-points Total"] = (
        result_df["Energy Score"] + 
        result_df["Sugar Score"] + 
        result_df["Saturates Score"] + 
        result_df["Salt Score"] + 
        result_df.get("Sweetener Penalty", 0)
    )
    
    result_df["P-points Total"] = (
        result_df["Fruit Score"] + 
        result_df["Fibre Score"] + 
        result_df["Protein Score"]
    )
    
    return result_df

def display_results(result_df):
    """Display the results in a formatted table"""
    # Create a clean display table
    display_df = pd.DataFrame()
    
    # Product identification
    if "Product Name" in result_df.columns:
        display_df["Products"] = result_df["Product Name"]
    else:
        display_df["Products"] = [f"Product {i+1}" for i in range(len(result_df))]
    
    # Water indicator
    display_df["Water (without any addition)"] = result_df.get("Is Water", False)
    
    # Nutritional values
    display_df["Energy (kJ/100 mL or 100 g)"] = result_df["Energy (kJ/100 g)"]
    display_df["Sugar (g/100 mL or 100 g)"] = result_df["Sugar (g/100 g)"]
    display_df["Saturates (g/100 mL or 100 g)"] = result_df["Saturates (g/100 g)"]
    display_df["Salt (g/100 mL or 100 g)"] = result_df["Salt (g/100 g)"]
    display_df["Presence of non-nutritive sweetener (YES/NO)"] = result_df.get("Contains sweeteners", False)
    display_df["Fruits, vegetables and legumes (%)"] = result_df["Fruits, vegetables, and pulses (%)"]
    display_df["Fibre (g/100 mL or 100 g)"] = result_df["Fibre (g/100 g)"]
    display_df["Protein (g/100 mL or 100 g)"] = result_df["Protein (g/100 g)"]
    
    # Component scores
    display_df["Energy points"] = result_df["Energy Score"]
    display_df["Sugar points"] = result_df["Sugar Score"]
    display_df["SFA points"] = result_df["Saturates Score"]
    display_df["Salt points"] = result_df["Salt Score"]
    display_df["Sweetener Penalty"] = result_df.get("Sweetener Penalty", 0)
    display_df["FVL points"] = result_df["Fruit Score"]
    display_df["Fibre points"] = result_df["Fibre Score"]
    display_df["Protein points"] = result_df["Protein Score"]
    
    # Final calculations
    display_df["Points A"] = result_df["N-points Total"]
    display_df["Points C"] = result_df["P-points Total"]
    display_df["Score"] = result_df["Nutri-Score Points"]
    display_df["Nutri-Score"] = result_df["Nutri-Score Grade"]
    
    # Display the table
    st.subheader("Nutri-Score Results")
    st.dataframe(display_df)
    
    # Provide CSV download
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="Download results as CSV",
        data=csv,
        file_name="nutri_score_results.csv",
        mime="text/csv",
    )

# ----------------------------
# Streamlit App UI
# ----------------------------
def main():
    st.title("Nutri-Score Calculator")
    
    uploaded_file = st.file_uploader("Upload your product data (Excel file):", type=["xlsx", "xls", "csv"])
    category_display = st.selectbox("Select food category:", list(CATEGORY_MAP.keys()))
    category = CATEGORY_MAP[category_display]
    
    # Add options for manual entry
    use_manual_entry = st.checkbox("Enter product data manually")
    
    if use_manual_entry:
        st.subheader("Enter Product Details")
        product_name = st.text_input("Product Name")
        energy = st.number_input("Energy (kJ/100g or mL)", min_value=0.0)
        sugar = st.number_input("Sugar (g/100g or mL)", min_value=0.0)
        saturates = st.number_input("Saturated Fat (g/100g or mL)", min_value=0.0)
        salt = st.number_input("Salt (g/100g or mL)", min_value=0.0)
        fruit_veg = st.number_input("Fruits, vegetables, and pulses (%)", min_value=0.0, max_value=100.0)
        fiber = st.number_input("Fiber (g/100g or mL)", min_value=0.0)
        protein = st.number_input("Protein (g/100g or mL)", min_value=0.0)
        contains_sweeteners = st.checkbox("Contains sweeteners")
        is_water = st.checkbox("Is water (without any addition)")
        
        if st.button("Calculate Nutri-Score"):
            # Create a single-row DataFrame from manual inputs
            manual_data = {
                "Product Name": [product_name],
                "Energy (kJ/100 g)": [energy],
                "Sugar (g/100 g)": [sugar],
                "Saturates (g/100 g)": [saturates],
                "Salt (g/100 g)": [salt],
                "Fruits, vegetables, and pulses (%)": [fruit_veg],
                "Fibre (g/100 g)": [fiber],
                "Protein (g/100 g)": [protein],
                "Contains sweeteners": [contains_sweeteners],
                "is_water": [is_water]
            }
            df = pd.DataFrame(manual_data)
            
            # Calculate and display results just like with uploaded files
            result_df = process_dataframe(df, category)
            display_results(result_df)
    
    elif uploaded_file:
        try:
            # Detect file type and read accordingly
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

                        # Clean FVL column to ensure correct numeric type and no formatting issues
            if "Fruits, vegetables, and pulses (%)" in df.columns:
                df["Fruits, vegetables, and pulses (%)"] = (
                    pd.to_numeric(
                        df["Fruits, vegetables, and pulses (%)"]
                        .astype(str)
                        .str.strip()
                        .str.replace(",", "."),  # Handles commas used in European-style decimals
                        errors="coerce"
                    ).fillna(0)  # Any invalid value becomes 0
                )

            
            # Check required columns
            required_columns = ["Energy (kJ/100 g)", "Sugar (g/100 g)", "Saturates (g/100 g)", 
                             "Salt (g/100 g)", "Fruits, vegetables, and pulses (%)", 
                             "Fibre (g/100 g)", "Protein (g/100 g)"]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
            else:
                result_df = process_dataframe(df, category)
                display_results(result_df)
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.exception(e)  # Show detailed error for debugging
    
    st.sidebar.header("About")
    st.sidebar.info(
        """
        This app calculates the Nutri-Score for food products based on the 
        updated 2023 algorithm. The Nutri-Score helps consumers make healthier food choices 
        by providing a simple A to E rating.
        """
    )

if __name__ == "__main__":
    main()
