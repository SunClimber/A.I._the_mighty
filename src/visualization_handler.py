# visualization_handler.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_genre_trends(pivot_trends_df, output_path="output/genre_trends.png"):
    """Plots genre trends over decades."""
    if pivot_trends_df is None or pivot_trends_df.empty:
        print("No data to plot for genre trends.")
        return

    plt.figure(figsize=(14, 8))
    sns.lineplot(data=pivot_trends_df, dashes=False, markers=True)
    plt.title('Popularity of Top Book Subjects Over Decades (by Author Birth Year Proxy)')
    plt.xlabel('Decade (Author Birth Year Proxy)')
    plt.ylabel('Number of Books Published')
    plt.xticks(rotation=45)
    plt.legend(title='Subject', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Ensure output directory exists
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"Genre trends plot saved to {output_path}")
    # plt.show() # Uncomment to display plot interactively

def save_data_to_excel(data_dict, output_path="output/project_analysis_output.xlsx"):
    """Saves multiple DataFrames to different sheets in an Excel file."""
    if not data_dict:
        print("No data to save to Excel.")
        return

    # Ensure output directory exists
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df_to_save in data_dict.items():
            if isinstance(df_to_save, pd.DataFrame) and not df_to_save.empty:
                df_to_save.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"DataFrame saved to sheet: {sheet_name}")
            elif isinstance(df_to_save, str): # Save text summaries to a sheet
                # Create a simple DataFrame for the text
                summary_df = pd.DataFrame({'Summary': [line for line in df_to_save.split('\n') if line.strip()]})
                summary_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                print(f"Text summary saved to sheet: {sheet_name}")
            else:
                print(f"Skipping sheet '{sheet_name}' due to empty or invalid data.")
    print(f"All data saved to {output_path}")


if __name__ == '__main__':
    # Dummy data for testing plotting (use from analysis_engine test if possible)
    dummy_pivot_data = {
        'decade_proxy': [1900, 1910, 1920, 1930, 1940],
        'adventure': [10, 15, 20, 12, 8],
        'science fiction': [5, 8, 12, 18, 22],
        'mystery': [3, 6, 9, 10, 7]
    }
    dummy_pivot_df = pd.DataFrame(dummy_pivot_data).set_index('decade_proxy')
    
    plot_genre_trends(dummy_pivot_df)

    # Dummy data for Excel saving
    df1 = pd.DataFrame({'colA': [1,2], 'colB': [3,4]})
    df2 = pd.DataFrame({'colX': [5,6], 'colY': [7,8]})
    text_summary_example = "This is a test summary.\nIt has multiple lines."
    
    save_data_to_excel({
        "Sheet1_Data": df1, 
        "Sheet2_Data": df2,
        "AnalysisSummaryText": text_summary_example,
        "EmptySheetTest": pd.DataFrame() # Test empty df handling
        })