# visualization_handler.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

# --- Path Setup ---
# Assuming this script is in the project root.
SCRIPT_DIR_VH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GENRE_TRENDS_PNG_VH = os.path.join(SCRIPT_DIR_VH, "output", "market_genre_trends.png") # Make specific
DEFAULT_EXCEL_OUTPUT_VH = os.path.join(SCRIPT_DIR_VH, "output", "project_analysis_default.xlsx")
# --- End Path Setup ---

def plot_genre_trends(pivot_trends_df, output_path=DEFAULT_GENRE_TRENDS_PNG_VH):
    """Plots genre trends over decades from market data."""
    if pivot_trends_df is None or pivot_trends_df.empty:
        print("No market data pivot table to plot for genre trends.")
        return

    plt.figure(figsize=(14, 8))
    sns.lineplot(data=pivot_trends_df, dashes=False, markers=True)
    plt.title('Popularity of Top Book Subjects Over Decades (Market Data - Author Birth Year Proxy)')
    plt.xlabel('Decade (Author Birth Year Proxy)')
    plt.ylabel('Number of Books Published')
    plt.xticks(rotation=45)
    plt.legend(title='Subject', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"Market genre trends plot saved to {output_path}")
    plt.close() # Close the plot to free memory

def save_data_to_excel(data_dict, output_path=DEFAULT_EXCEL_OUTPUT_VH):
    """Saves multiple DataFrames/text to sheets in an Excel file."""
    if not data_dict:
        print("No data to save to Excel.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df_to_save in data_dict.items():
            if isinstance(df_to_save, pd.DataFrame) and not df_to_save.empty:
                try:
                    df_to_save.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"DataFrame saved to sheet: {sheet_name}")
                except Exception as e:
                    print(f"Error saving DataFrame to sheet {sheet_name}: {e}. Saving as text.")
                    # Fallback to save as text if error (e.g., too many columns for old Excel)
                    error_df = pd.DataFrame({'Error': [f"Could not save DataFrame: {e}"], 'Data_Head': [str(df_to_save.head())]})
                    error_df.to_excel(writer, sheet_name=f"{sheet_name}_Error", index=False)

            elif isinstance(df_to_save, str): 
                summary_df = pd.DataFrame({'Summary': [line for line in df_to_save.split('\n') if line.strip()]})
                summary_df.to_excel(writer, sheet_name=sheet_name, index=False, header=True) # Use header for summary
                print(f"Text summary saved to sheet: {sheet_name}")
            else:
                print(f"Skipping sheet '{sheet_name}' due to empty or invalid data type: {type(df_to_save)}.")
    print(f"All data saved to Excel file: {output_path}")


if __name__ == '__main__':
    os.makedirs(os.path.join(SCRIPT_DIR_VH, "output"), exist_ok=True) # Ensure output dir for tests
    # ... (your existing test code for visualization_handler, ensure output paths are correct)
    dummy_pivot_data = { # ... as before ... 
    }
    # ...