# analysis_engine.py
import pandas as pd

def analyze_genre_trends_by_decade(df, subject_col='subjects', decade_col='decade_proxy'):
    """Analyzes genre/subject trends over decades for the market data."""
    if df is None or df.empty:
        print("Market DataFrame is empty. Cannot analyze genre trends.")
        return None, "No market data available for genre trend analysis."

    try:
        if not pd.api.types.is_string_dtype(df[subject_col]):
             df[subject_col] = df[subject_col].astype(str)

        # Subjects are semicolon-separated in data_handler
        subjects_expanded = df.assign(subject=df[subject_col].str.split('; ')).explode('subject')
        subjects_expanded['subject'] = subjects_expanded['subject'].str.strip().str.lower()
        
        common_subjects_to_filter = ['fiction', 'literature', '', 'english language', 'text', 'unspecified', 'general'] # Added more
        subjects_expanded = subjects_expanded[~subjects_expanded['subject'].isin(common_subjects_to_filter)]
        subjects_expanded = subjects_expanded[subjects_expanded['subject'].str.len() > 3]


        if subjects_expanded.empty or subjects_expanded[decade_col].isnull().all():
            print("No valid subjects or decades found in market data after expansion/filtering.")
            return None, "Insufficient market data for genre trend analysis after processing subjects."

        genre_trends = subjects_expanded.groupby([decade_col, 'subject']).size().reset_index(name='book_count')
        top_subjects = subjects_expanded['subject'].value_counts().nlargest(10).index.tolist()
        genre_trends_top = genre_trends[genre_trends['subject'].isin(top_subjects)]

        if genre_trends_top.empty:
            return None, "No trend data for top subjects in market data. Dataset might be too small or subjects too sparse."

        pivot_trends = genre_trends_top.pivot_table(index=decade_col, columns='subject', values='book_count', fill_value=0)
        
        summary_lines = ["General Market Genre Trend Analysis Summary (based on author birth year proxy decaded):"]
        for subject in pivot_trends.columns:
            subject_data = pivot_trends[subject]
            if subject_data.sum() == 0: continue
            
            peak_decade = subject_data.idxmax()
            peak_count = subject_data.max()
            total_count = subject_data.sum()
            summary_lines.append(
                f"- '{subject.capitalize()}': Total {total_count} books. "
                f"Appeared most frequently in works by authors born in the {int(peak_decade)}s (with {int(peak_count)} books in that decade proxy)."
            )
            non_zero_decades = subject_data[subject_data > 0].index
            if len(non_zero_decades) > 1:
                first_decade_count = subject_data.loc[non_zero_decades.min()]
                last_decade_count = subject_data.loc[non_zero_decades.max()]
                if last_decade_count > first_decade_count:
                    summary_lines[-1] += " Shows a general increase in representation over the observed period by authors."
                elif last_decade_count < first_decade_count:
                    summary_lines[-1] += " Shows a general decrease in representation over the observed period by authors."
        analysis_summary = "\n".join(summary_lines)
        print("\n--- General Market Genre Trend Analysis ---")
        # print(analysis_summary) # Keep console output tidy, will be in Excel
        return pivot_trends, analysis_summary
    
    except KeyError as e:
        print(f"KeyError during market genre trend analysis: {e}. Check column names.")
        return None, f"Error in market analysis: Missing column {e}."
    except Exception as e:
        print(f"An unexpected error occurred during market genre trend analysis: {e}")
        return None, f"Unexpected error in market analysis: {e}"


def analyze_prolific_authors(df, author_col='authors', subject_col='subjects', n_top_authors=5):
    """Identifies most prolific authors (full names) and their common subjects from market data."""
    if df is None or df.empty:
        print("Market DataFrame is empty. Cannot analyze prolific authors.")
        return None, "No market data available for prolific author analysis."

    try:
        # `df[author_col]` contains "Last1, First1; Last2, First2" or just "Last, First" (due to data_handler change)
        # Step 1: Explode by the multi-author separator (';')
        temp_df = df.assign(individual_author=df[author_col].str.split(';')).explode('individual_author')
        
        # Step 2: Clean up each individual author name (strip whitespace)
        temp_df['individual_author'] = temp_df['individual_author'].str.strip()
        
        # Step 3: Filter out empty strings that might result from splitting
        temp_df = temp_df[temp_df['individual_author'] != '']
        temp_df = temp_df.dropna(subset=['individual_author']) # Ensure no NaN authors

        # Step 4: Count occurrences of each full individual author name
        top_authors_counts = temp_df['individual_author'].value_counts().nlargest(n_top_authors)

        if top_authors_counts.empty:
            return None, "No author data to analyze or count in market data."

        summary_lines = [f"Top {n_top_authors} Most Prolific Authors (from Market Data, based on book count):"]
        author_details_for_ai = []

        for author_full_name, count in top_authors_counts.items():
            # Get books by this specific author from the temp_df (which has one author per row)
            author_books_this_author = temp_df[temp_df['individual_author'] == author_full_name]
            
            # To get subjects for these books, we use the original DataFrame's indices
            original_indices = author_books_this_author.index.unique() # Get unique indices
            author_books_original_df = df.loc[original_indices]

            if not pd.api.types.is_string_dtype(author_books_original_df[subject_col]):
                author_books_original_df[subject_col] = author_books_original_df[subject_col].astype(str)

            # Subjects are semicolon-separated in data_handler
            author_subjects_expanded = author_books_original_df.assign(subject=author_books_original_df[subject_col].str.split('; ')).explode('subject')
            author_subjects_expanded['subject'] = author_subjects_expanded['subject'].str.strip().str.lower()
            
            common_subjects_to_filter = ['fiction', 'literature', '', 'english language', 'text', 'unspecified', 'general']
            author_subjects_expanded = author_subjects_expanded[~author_subjects_expanded['subject'].isin(common_subjects_to_filter)]
            author_subjects_expanded = author_subjects_expanded[author_subjects_expanded['subject'].str.len() > 3]

            top_3_subjects = author_subjects_expanded['subject'].value_counts().nlargest(3).index.tolist()
            top_3_subjects_str = ", ".join(s.capitalize() for s in top_3_subjects) if top_3_subjects else "various subjects"

            summary_lines.append(f"- {author_full_name}: {count} books. Common subjects include: {top_3_subjects_str}.")
            author_details_for_ai.append({
                "name": author_full_name,
                "book_count": count,
                "common_subjects": top_3_subjects
            })
        
        analysis_summary = "\n".join(summary_lines)
        print("\n--- General Market Prolific Author Analysis ---")
        # print(analysis_summary) # Keep console tidy
        return pd.DataFrame(author_details_for_ai), analysis_summary

    except KeyError as e:
        print(f"KeyError during market prolific author analysis: {e}. Check column names.")
        return None, f"Error in market analysis: Missing column {e}."
    except Exception as e:
        print(f"An unexpected error occurred during market prolific author analysis: {e}")
        return None, f"Unexpected error in market analysis: {e}"


if __name__ == '__main__':
    # Dummy data for testing (assuming authors are semicolon-separated if multiple for one book)
    dummy_market_data = {
        'id': [1, 2, 3, 4, 5, 6],
        'title': [f'Book {i}' for i in range(1, 7)],
        'authors': [
            'Austen, Jane', 'Shakespeare, William', 'Austen, Jane', 
            'Twain, Mark; Warner, Charles Dudley', 'Shakespeare, William', 'Twain, Mark'
        ],
        'author_birth_year': [1775, 1564, 1775, 1835, 1564, 1835],
        'subjects': [
            'Love stories; Domestic fiction', 'Tragedies; Drama', 'Bildungsromans',
            'Satire; Picaresque', 'Comedies; Drama', 'Adventure stories; Boys -- fiction'
        ]
    }
    test_df_market = pd.DataFrame(dummy_market_data)
    test_df_market['decade_proxy'] = (test_df_market['author_birth_year'] // 10) * 10

    print("--- Testing Market Genre Trends ---")
    genre_pivot, genre_summary = analyze_genre_trends_by_decade(test_df_market.copy())
    if genre_pivot is not None:
        print(genre_pivot.head())
        print(genre_summary)

    print("\n--- Testing Market Prolific Authors ---")
    top_authors_df, authors_summary = analyze_prolific_authors(test_df_market.copy())
    if top_authors_df is not None:
        print(top_authors_df)
        print(authors_summary)