# analysis_engine.py
import pandas as pd

# --- analyze_genre_trends_by_decade remains the same as the last good version ---
def analyze_genre_trends_by_decade(df, subject_col='subjects', decade_col='decade_proxy'):
    """
    Analyzes historical genre/subject publication trends over decades based on author birth year.
    Returns: pivot_table, textual_summary, series_of_overall_subject_counts_by_publication
    """
    if df is None or df.empty:
        print("  Market DataFrame is empty. Cannot analyze historical genre publication trends.")
        return None, "No market data available for historical genre publication trend analysis.", None
    try:
        if not pd.api.types.is_string_dtype(df[subject_col]):
             df[subject_col] = df[subject_col].astype(str)

        subjects_expanded = df.assign(subject=df[subject_col].str.split('; ')).explode('subject')
        subjects_expanded['subject'] = subjects_expanded['subject'].str.strip().str.lower()
        
        common_subjects_to_filter = ['fiction', 'literature', '', 'english language', 'text', 'unspecified', 'general', 'language and languages']
        subjects_expanded = subjects_expanded[~subjects_expanded['subject'].isin(common_subjects_to_filter)]
        subjects_expanded = subjects_expanded[subjects_expanded['subject'].str.len() > 3]

        if subjects_expanded.empty:
            print("  No valid subjects found in market data after filtering for historical publication trends.")
            return None, "Insufficient market data for historical genre publication trend analysis.", None

        subject_overall_counts_by_publication = subjects_expanded['subject'].value_counts()

        if decade_col not in df.columns or df[decade_col].isnull().all(): # Check if decade_col exists and has non-null values
            print(f"  Decade column '{decade_col}' not found or all nulls in market data. Cannot perform decade trend analysis for historical publications.")
            # Still return subject_overall_counts if available, but pivot and summary will be limited
            return None, "Historical genre publication trend (decade) analysis could not be performed due to missing/all-null decade data.", subject_overall_counts_by_publication

        genre_trends = subjects_expanded.groupby([decade_col, 'subject']).size().reset_index(name='book_count')
        num_top_subjects_for_trends = min(10, subject_overall_counts_by_publication.nunique())
        top_subjects_for_trends_list = subject_overall_counts_by_publication.nlargest(num_top_subjects_for_trends).index.tolist()
        
        genre_trends_top = genre_trends[genre_trends['subject'].isin(top_subjects_for_trends_list)]

        pivot_trends = None
        analysis_summary_lines = ["Summary of Historical Literary Genre Publication Trends (by Author Birth Decade):"]

        if not genre_trends_top.empty:
            pivot_trends = genre_trends_top.pivot_table(index=decade_col, columns='subject', values='book_count', fill_value=0)
            if pivot_trends is not None and not pivot_trends.empty: # Ensure pivot is not empty before sorting
                 pivot_trends = pivot_trends.sort_index()

            # Iterate over columns of the created pivot_trends
            if pivot_trends is not None and not pivot_trends.empty:
                for subject_item in pivot_trends.columns: 
                    subject_data = pivot_trends[subject_item]
                    if subject_data.sum() == 0: continue
                    peak_decade = subject_data.idxmax()
                    peak_count = subject_data.max()
                    total_count_for_subject_in_pivot = subject_data.sum()
                    analysis_summary_lines.append(
                        f"- '{subject_item.capitalize()}': Historically published frequently by authors born around the {int(peak_decade)}s (total {int(total_count_for_subject_in_pivot)} books among top subjects shown in trend plot)."
                    ) 
        else:
            analysis_summary_lines.append("No sufficient trend data for top subjects to generate detailed historical publication summaries.")
        
        analysis_summary = "\n".join(analysis_summary_lines)
        return pivot_trends, analysis_summary, subject_overall_counts_by_publication
    
    except KeyError as e:
        print(f"  KeyError during historical genre publication trend analysis: {e}.")
        return None, f"Error: Missing column {e} for historical publication trends.", None
    except Exception as e:
        print(f"  An unexpected error during historical genre publication trend analysis: {e}")
        return None, f"Unexpected error in historical publication trends: {e}", None


# --- analyze_prolific_authors (based on publication volume) ---
def analyze_prolific_authors(df, author_col='authors', subject_col='subjects', n_top_authors=7):
    if df is None or df.empty:
        print("  Market DataFrame is empty. Cannot analyze prolific authors by publication.")
        return None, "No market data available for prolific author (publication) analysis."
    try:
        df[author_col] = df[author_col].fillna('').astype(str) # Ensure string and handle NaNs

        temp_df = df.assign(individual_author=df[author_col].str.split(';')).explode('individual_author')
        temp_df['individual_author'] = temp_df['individual_author'].str.strip()
        temp_df = temp_df[temp_df['individual_author'] != '']
        temp_df = temp_df.dropna(subset=['individual_author'])

        if temp_df.empty:
             return None, "No valid author data after processing for prolific author (publication) analysis."

        top_authors_counts = temp_df['individual_author'].value_counts().nlargest(n_top_authors)

        if top_authors_counts.empty:
            return None, "No author data to analyze or count in market data for prolific authors (publication)."

        summary_lines = [f"Top {len(top_authors_counts)} Most Prolific Authors (by Historical Publication Volume):"]
        author_details_list = []

        for author_full_name, count in top_authors_counts.items():
            # Simplified summary for this part, as detailed subject analysis per author is complex
            summary_lines.append(f"- {author_full_name}: {count} books published.")
            author_details_list.append({
                "name": author_full_name, 
                "book_count": count, 
                "common_subjects": "N/A for this high-level summary" # Keep it simple for the text summary
            })
        
        analysis_summary_text = "\n".join(summary_lines)
        authors_df_for_table = pd.DataFrame(author_details_list)
        return authors_df_for_table, analysis_summary_text
        
    except KeyError as e:
        print(f"  KeyError during prolific author (publication) analysis: {e}.")
        return None, f"Error: Missing column {e} for prolific author (publication) analysis."
    except Exception as e:
        print(f"  An unexpected error during prolific author (publication) analysis: {e}")
        return None, f"Unexpected error in prolific author (publication) analysis: {e}"


# --- NEW FUNCTION: analyze_download_activity ---
def analyze_download_activity(df, subject_col='subjects', author_col='authors', download_col='download_count', top_n=5):
    if df is None or df.empty or download_col not in df.columns:
        print(f"  Market DataFrame is empty or missing '{download_col}' column. Cannot analyze download activity.")
        return "Download activity analysis could not be performed due to missing data.", None, None

    df[download_col] = pd.to_numeric(df[download_col], errors='coerce').fillna(0)
    df = df[df[download_col] >= 0]

    if df.empty:
        return "No data with valid download counts for analysis.", None, None

    # --- Analyze top subjects by download ---
    df[subject_col] = df[subject_col].fillna('').astype(str) # Ensure string
    subjects_exploded_for_downloads = df.assign(subject=df[subject_col].str.split('; ')).explode('subject')
    subjects_exploded_for_downloads['subject'] = subjects_exploded_for_downloads['subject'].str.strip().str.lower()
    
    common_subjects_to_filter = ['fiction', 'literature', '', 'english language', 'text', 'unspecified', 'general', 'language and languages']
    subjects_exploded_for_downloads = subjects_exploded_for_downloads[~subjects_exploded_for_downloads['subject'].isin(common_subjects_to_filter)]
    subjects_exploded_for_downloads = subjects_exploded_for_downloads[subjects_exploded_for_downloads['subject'].str.len() > 3]
    
    df_top_subjects_by_download = None
    top_downloaded_subject_names = []
    if not subjects_exploded_for_downloads.empty:
        top_subjects_by_dl_series = subjects_exploded_for_downloads.groupby('subject')[download_col].sum().nlargest(top_n) # Keep as Series
        if not top_subjects_by_dl_series.empty:
            df_top_subjects_by_download = top_subjects_by_dl_series.reset_index() # Convert to DF for return if needed by plotting
            top_downloaded_subject_names = [s.capitalize() for s in df_top_subjects_by_download['subject'].tolist()]

    # --- Analyze top authors by download ---
    df[author_col] = df[author_col].fillna('').astype(str) # Ensure string
    authors_exploded_for_downloads = df.assign(individual_author=df[author_col].str.split(';')).explode('individual_author')
    authors_exploded_for_downloads['individual_author'] = authors_exploded_for_downloads['individual_author'].str.strip()
    authors_exploded_for_downloads = authors_exploded_for_downloads[authors_exploded_for_downloads['individual_author'] != '']
    
    df_top_authors_by_download = None
    top_downloaded_author_names = [] # CORRECTED VARIABLE NAME
    if not authors_exploded_for_downloads.empty:
        top_authors_by_dl_series = authors_exploded_for_downloads.groupby('individual_author')[download_col].sum().nlargest(top_n) # Keep as Series
        if not top_authors_by_dl_series.empty:
            df_top_authors_by_download = top_authors_by_dl_series.reset_index() # Convert to DF for return
            top_downloaded_author_names = df_top_authors_by_download['individual_author'].tolist() # CORRECTED VARIABLE NAME

    summary_parts = ["Insights from Project Gutenberg Download Activity (Recent Interest in Classics):"]
    if top_downloaded_subject_names:
        summary_parts.append(f"- Classic subjects like '{', '.join(top_downloaded_subject_names[:3])}' continue to attract reader engagement on Project Gutenberg.")
        inferred_subject_prefs = []
        # Simplified inference logic
        if any(s_keyword in ' '.join(top_downloaded_subject_names).lower() for s_keyword in ['adventure', 'detective', 'mystery', 'spy', 'sea stories', 'horror']):
            inferred_subject_prefs.append("engaging plots and suspenseful narratives")
        if any(s_keyword in ' '.join(top_downloaded_subject_names).lower() for s_keyword in ['love', 'domestic', 'romance', 'social', 'bildun']): # 'bildun' for bildungsroman
            inferred_subject_prefs.append("character-driven stories and emotional/social exploration")
        if inferred_subject_prefs:
            summary_parts.append(f"  This may indicate an ongoing, albeit niche, interest in classics offering {', and '.join(inferred_subject_prefs)}.")
        else:
            summary_parts.append("  The popularity of these subjects suggests specific classic themes remain appealing.")
            
    if top_downloaded_author_names: # CORRECTED VARIABLE NAME
        summary_parts.append(f"- Works by classic authors such as '{', '.join(top_downloaded_author_names[:3])}' are frequently downloaded, suggesting their narrative styles or thematic explorations still resonate.")

    if len(summary_parts) == 1: 
        summary_parts.append("No strong signals of currently popular classic genres or authors were identified from Project Gutenberg download data in this sample.")
    
    final_summary = "\n".join(summary_parts)
    
    # Return Series for plotting subject distribution, DataFrames for author tables/plots
    return final_summary, top_subjects_by_dl_series if 'top_subjects_by_dl_series' in locals() and not top_subjects_by_dl_series.empty else None, \
           df_top_authors_by_download


# --- __main__ block for testing ---
if __name__ == '__main__':
    # Simplified dummy data for testing analysis_engine.py directly
    dummy_market_data = {
        'id': range(1, 11),
        'title': [f'Book {i}' for i in range(1, 11)],
        'authors': ['Austen, Jane', 'Twain, Mark; Cable, G.W.', 'Shakespeare, William', 'Dickens, Charles', 'Austen, Jane', 
                    'Twain, Mark', 'Poe, Edgar Allan', 'Melville, Herman', 'Shakespeare, William', 'Alcott, Louisa May'],
        'author_birth_year': [1775, 1835, 1564, 1812, 1775, 1835, 1809, 1819, 1564, 1832],
        'subjects': ['Love stories; Domestic fiction', 'Adventure stories; Humorous stories', 'Tragedies; Drama', 'Social criticism; Bildungsromans', 'Domestic fiction; Satire',
                     'Adventure stories; Mississippi River', 'Horror tales; Short stories', 'Sea stories; Adventure stories', 'Comedies; Drama', 'Domestic fiction; Bildungsromans'],
        'download_count': [5000, 4500, 4000, 3800, 3500, 3200, 3000, 2800, 2500, 2200]
    }
    test_df_market = pd.DataFrame(dummy_market_data)
    
    # Perform cleaning steps that would normally happen in data_handler.py for this test
    test_df_market['author_birth_year'] = pd.to_numeric(test_df_market['author_birth_year'], errors='coerce')
    test_df_market.dropna(subset=['author_birth_year'], inplace=True) # Crucial for decade_proxy
    test_df_market['decade_proxy'] = (test_df_market['author_birth_year'] // 10) * 10
    test_df_market['download_count'] = pd.to_numeric(test_df_market['download_count'], errors='coerce').fillna(0).astype(int)


    print("--- Testing Historical Genre Publication Trends ---")
    genre_pivot, genre_pub_summary, subject_pub_counts = analyze_genre_trends_by_decade(test_df_market.copy())
    if genre_pub_summary: print(genre_pub_summary)
    if genre_pivot is not None: print("\nSample Genre Publication Pivot:\n", genre_pivot.head())
    if subject_pub_counts is not None: print("\nSubject Publication Counts:\n", subject_pub_counts.head())
    
    print("\n--- Testing Historical Prolific Authors (by Publication Volume) ---")
    authors_pub_df, authors_pub_summary = analyze_prolific_authors(test_df_market.copy())
    if authors_pub_summary: print(authors_pub_summary)
    if authors_pub_df is not None: print("\nTop Authors by Publication DF:\n", authors_pub_df.head())

    print("\n--- Testing PG Download Activity Analysis ---")
    download_summary, series_top_subj_dl, df_top_auth_dl = analyze_download_activity(test_df_market.copy())
    print(download_summary)
    if series_top_subj_dl is not None: print("\nTop Subjects by PG Download (Series):\n", series_top_subj_dl)
    if df_top_auth_dl is not None: print("\nTop Authors by PG Download (DF):\n", df_top_auth_dl)