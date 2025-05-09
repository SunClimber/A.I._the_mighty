# analysis_engine.py
import pandas as pd

def analyze_genre_trends_by_decade(df, subject_col='subjects', decade_col='decade_proxy'):
    """Analyzes genre/subject trends over decades."""
    if df is None or df.empty:
        print("DataFrame is empty. Cannot analyze genre trends.")
        return None, "No data available for genre trend analysis."

    # Explode subjects if they are semi-colon separated and extract main ones
    # This part is crucial and needs adjustment based on your 'subjects' column format
    try:
        # Attempt to split subjects and explode. Handle potential errors if column is not string.
        if not pd.api.types.is_string_dtype(df[subject_col]):
             df[subject_col] = df[subject_col].astype(str) # Convert to string if not already

        subjects_expanded = df.assign(subject=df[subject_col].str.split('; ')).explode('subject')
        subjects_expanded['subject'] = subjects_expanded['subject'].str.strip().str.lower()
        
        # Filter out very broad or non-descriptive subjects (example)
        common_subjects_to_filter = ['fiction', 'literature', '', 'english language', 'text']
        subjects_expanded = subjects_expanded[~subjects_expanded['subject'].isin(common_subjects_to_filter)]
        subjects_expanded = subjects_expanded[subjects_expanded['subject'].str.len() > 3] # Filter short/irrelevant subjects


        if subjects_expanded.empty or subjects_expanded[decade_col].isnull().all():
            print("No valid subjects or decades found after expansion/filtering.")
            return None, "Insufficient data for genre trend analysis after processing subjects."

        # Count books per subject per decade
        genre_trends = subjects_expanded.groupby([decade_col, 'subject']).size().reset_index(name='book_count')
        
        # Get top N subjects overall to focus the trend analysis
        top_subjects = subjects_expanded['subject'].value_counts().nlargest(10).index.tolist()
        genre_trends_top = genre_trends[genre_trends['subject'].isin(top_subjects)]

        if genre_trends_top.empty:
            return None, "No trend data for top subjects. The dataset might be too small or subjects too sparse."

        # Create a pivot table for easier plotting and summary
        pivot_trends = genre_trends_top.pivot_table(index=decade_col, columns='subject', values='book_count', fill_value=0)
        
        # --- Generate Textual Summary ---
        summary_lines = ["Genre Trend Analysis Summary (based on author birth year proxy decaded):"]
        for subject in pivot_trends.columns:
            subject_data = pivot_trends[subject]
            if subject_data.sum() == 0: continue # Skip if no books for this subject in the pivot
            
            peak_decade = subject_data.idxmax()
            peak_count = subject_data.max()
            total_count = subject_data.sum()
            summary_lines.append(
                f"- '{subject.capitalize()}': Total {total_count} books. "
                f"Appeared most frequently in works by authors born in the {int(peak_decade)}s (with {int(peak_count)} books in that decade proxy)."
            )
            # You could add more complex trend descriptions (e.g., increasing/decreasing)
            # For example, comparing first half vs second half of observed decades
            non_zero_decades = subject_data[subject_data > 0].index
            if len(non_zero_decades) > 1:
                first_decade_count = subject_data[non_zero_decades.min()]
                last_decade_count = subject_data[non_zero_decades.max()]
                if last_decade_count > first_decade_count:
                    summary_lines[-1] += " Shows a general increase in representation over the observed period by authors."
                elif last_decade_count < first_decade_count:
                    summary_lines[-1] += " Shows a general decrease in representation over the observed period by authors."


        analysis_summary = "\n".join(summary_lines)
        print("\n--- Genre Trend Analysis ---")
        print(analysis_summary)
        return pivot_trends, analysis_summary
    
    except KeyError as e:
        print(f"KeyError during genre trend analysis: {e}. Check column names.")
        return None, f"Error in analysis: Missing column {e}."
    except Exception as e:
        print(f"An unexpected error occurred during genre trend analysis: {e}")
        return None, f"Unexpected error in analysis: {e}"


def analyze_prolific_authors(df, author_col='authors', subject_col='subjects', n_top_authors=5):
    """Identifies most prolific authors and their common subjects."""
    if df is None or df.empty:
        print("DataFrame is empty. Cannot analyze prolific authors.")
        return None, "No data available for prolific author analysis."

    try:
        # Assuming 'authors' can be comma-separated if multiple authors
        authors_expanded = df.assign(author_name=df[author_col].str.split(', ')).explode('author_name')
        authors_expanded['author_name'] = authors_expanded['author_name'].str.strip()
        
        # Filter out potential empty author names if split results in them
        authors_expanded = authors_expanded[authors_expanded['author_name'] != '']


        top_authors = authors_expanded['author_name'].value_counts().nlargest(n_top_authors)
        
        if top_authors.empty:
            return None, "No author data to analyze or count."

        summary_lines = [f"Top {n_top_authors} Most Prolific Authors (based on book count):"]
        author_details_for_ai = []

        for author, count in top_authors.items():
            author_books = df[df[author_col].str.contains(author, case=False, na=False)] # Find books by this author
            
            # Get common subjects for this author
            # This subject processing should mirror the one in genre_trends for consistency
            if not pd.api.types.is_string_dtype(author_books[subject_col]):
                author_books[subject_col] = author_books[subject_col].astype(str)

            author_subjects_expanded = author_books.assign(subject=author_books[subject_col].str.split('; ')).explode('subject')
            author_subjects_expanded['subject'] = author_subjects_expanded['subject'].str.strip().str.lower()
            
            common_subjects_to_filter = ['fiction', 'literature', '', 'english language', 'text'] # Consistent filtering
            author_subjects_expanded = author_subjects_expanded[~author_subjects_expanded['subject'].isin(common_subjects_to_filter)]
            author_subjects_expanded = author_subjects_expanded[author_subjects_expanded['subject'].str.len() > 3]


            top_3_subjects = author_subjects_expanded['subject'].value_counts().nlargest(3).index.tolist()
            top_3_subjects_str = ", ".join(s.capitalize() for s in top_3_subjects) if top_3_subjects else "various subjects"

            summary_lines.append(f"- {author}: {count} books. Common subjects include: {top_3_subjects_str}.")
            author_details_for_ai.append({
                "name": author,
                "book_count": count,
                "common_subjects": top_3_subjects
            })
        
        analysis_summary = "\n".join(summary_lines)
        print("\n--- Prolific Author Analysis ---")
        print(analysis_summary)
        # We return the textual summary and structured data for AI
        return pd.DataFrame(author_details_for_ai), analysis_summary

    except KeyError as e:
        print(f"KeyError during prolific author analysis: {e}. Check column names.")
        return None, f"Error in analysis: Missing column {e}."
    except Exception as e:
        print(f"An unexpected error occurred during prolific author analysis: {e}")
        return None, f"Unexpected error in analysis: {e}"


if __name__ == '__main__':
    # Create dummy data for testing
    dummy_data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        'title': [f'Book {i}' for i in range(1, 16)],
        'authors': ['Author A', 'Author B', 'Author A', 'Author C', 'Author B', 'Author A', 'Author D', 'Author A', 'Author B', 'Author C', 'Author A', 'Author D', 'Author A', 'Author E', 'Author E'],
        'release_year_proxy': [1900, 1900, 1910, 1910, 1920, 1920, 1900, 1930, 1930, 1910, 1940, 1940, 1920, 1950, 1950],
        'subjects': [
            'Adventure; Pirates', 'Science fiction; Robots', 'Adventure; Exploration', 'Mystery; Detectives',
            'Science fiction; Space travel', 'Adventure; Lost worlds', 'Historical fiction; Rome', 'Adventure; Jungle',
            'Science fiction; Aliens', 'Mystery; Crime', 'Adventure; Treasure', 'Historical fiction; Medieval',
            'Adventure; Survival', 'Romance; Contemporary', 'Romance; Historical'
        ],
        'languages': ['en']*15,
        'download_count': [100*i for i in range(1,16)]
    }
    test_df = pd.DataFrame(dummy_data)
    test_df['decade_proxy'] = (test_df['release_year_proxy'] // 10) * 10

    # Test Genre Trends
    genre_pivot, genre_summary = analyze_genre_trends_by_decade(test_df.copy())
    if genre_pivot is not None:
        print("\nGenre Pivot Table Head:")
        print(genre_pivot.head())

    # Test Prolific Authors
    top_authors_df, authors_summary = analyze_prolific_authors(test_df.copy())
    if top_authors_df is not None:
        print("\nTop Authors DataFrame:")
        print(top_authors_df)