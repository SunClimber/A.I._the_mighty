# data_handler.py
import pandas as pd
import requests # For fetching from an API like Gutendex
import os

# --- Path Setup ---
# Assuming this script is in the project root. If it's in src/, adjust accordingly.
SCRIPT_DIR_DH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GUTENBERG_CSV_PATH_DH = os.path.join(SCRIPT_DIR_DH, "data", "gutenberg_metadata.csv")
DEFAULT_API_SAMPLE_SAVE_PATH_DH = os.path.join(SCRIPT_DIR_DH, "data", "gutenberg_sample_api.csv")
# --- End Path Setup ---


# --- Option 1: Load from a local CSV ---
def load_data_from_csv(file_path=DEFAULT_GUTENBERG_CSV_PATH_DH):
    """Loads data from a local CSV file."""
    try:
        df = pd.read_csv(file_path)
        print(f"Data loaded successfully from {file_path}. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}. Please ensure the 'data' directory exists and contains the file.")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# --- Option 2: Fetch from Gutendex API (Example for ~32k books) ---
def fetch_gutenberg_data_api(limit=1000):
    """Fetches data from Gutendex API.
       Note: Gutendex API can be paginated. This is a simplified example.
    """
    print(f"Fetching up to {limit} records from Gutendex API for general market analysis...")
    all_books = []
    # API page_size limit is often 32, so fetch in chunks that respect this
    # Effective page size should be min(limit, 32) for the first call, then 32 for subsequent.
    # Let's make page_size fixed and handle the limit by breaking the loop.
    page_size = 32 
    page_url = f"http://gutendex.com/books/?page_size={page_size}"

    records_fetched = 0
    while page_url and records_fetched < limit:
        try:
            response = requests.get(page_url)
            response.raise_for_status() 
            data = response.json()
            
            books_on_page = data.get('results', [])
            if not books_on_page: # No more results
                break

            for book_data in books_on_page:
                if records_fetched >= limit:
                    break
                
                # --- MODIFIED AUTHOR HANDLING ---
                author_names_list = []
                for author_detail in book_data.get('authors', []):
                    name = author_detail.get('name', '').strip()
                    if name: 
                        author_names_list.append(name)
                authors_str = "; ".join(author_names_list) # Join multiple authors of ONE book with a semicolon
                # --- END MODIFIED AUTHOR HANDLING ---
                
                subjects = "; ".join(book_data.get('subjects', [])) # Semicolon separated is good for consistency
                languages = ", ".join(book_data.get('languages', []))
                
                birth_year = None
                death_year = None
                # Use first author for birth/death year proxy if multiple authors
                if book_data.get('authors'):
                    author_info = book_data['authors'][0] 
                    birth_year = author_info.get('birth_year')
                    death_year = author_info.get('death_year')

                all_books.append({
                    'id': book_data.get('id'),
                    'title': book_data.get('title'),
                    'authors': authors_str, # Semicolon-separated string of authors for this book
                    'languages': languages,
                    'subjects': subjects, 
                    'download_count': book_data.get('download_count'),
                    'author_birth_year': birth_year, 
                    'author_death_year': death_year
                })
                records_fetched += 1
            
            page_url = data.get('next') 
            print(f"Fetched {records_fetched} records for market analysis...")
            if not page_url:
                print("No more pages to fetch or API limit reached.")
                break

        except requests.exceptions.RequestException as e:
            print(f"API request error during market data fetch: {e}")
            page_url = None 
        except Exception as e:
            print(f"An unexpected error occurred during market data API fetch: {e}")
            page_url = None

    if not all_books:
        print("No market analysis books fetched. Returning empty DataFrame.")
        return pd.DataFrame()
        
    df = pd.DataFrame(all_books)
    print(f"Fetched {len(df)} books from Gutendex API for market analysis.")
    
    # Basic cleaning for market data
    df.dropna(subset=['title', 'authors', 'subjects'], inplace=True) # Authors can be empty string now if no authors listed
    df = df[df['authors'] != ''] # Filter out rows with no authors after join
    
    df['author_birth_year'] = pd.to_numeric(df['author_birth_year'], errors='coerce')
    df['author_death_year'] = pd.to_numeric(df['author_death_year'], errors='coerce')
    print(f"Market data shape after basic cleaning: {df.shape}")
    return df


def clean_market_data(df):
    """Basic data cleaning steps for the general market dataset."""
    if df is None:
        return None
    print("Cleaning general market data...")
    
    # Ensure we have a year for trend analysis (using author_birth_year as proxy)
    df.dropna(subset=['author_birth_year'], inplace=True) 
    df['decade_proxy'] = (df['author_birth_year'] // 10) * 10

    print("Market data cleaning complete.")
    return df

if __name__ == '__main__':
    # Test CSV loading
    # os.makedirs(os.path.dirname(DEFAULT_GUTENBERG_CSV_PATH_DH), exist_ok=True) # Ensure 'data' dir exists
    # dummy_data_content = {'title': ['Book A'], 'authors': ['Austen, Jane'], 'subjects': ['Fiction'], 'author_birth_year': [1775]}
    # pd.DataFrame(dummy_data_content).to_csv(DEFAULT_GUTENBERG_CSV_PATH_DH, index=False)
    # df_csv = load_data_from_csv()
    # if df_csv is not None: print(df_csv.head())

    # Test API fetching
    df_api_market = fetch_gutenberg_data_api(limit=64) 
    if df_api_market is not None and not df_api_market.empty:
        df_api_market_cleaned = clean_market_data(df_api_market.copy())
        if df_api_market_cleaned is not None and not df_api_market_cleaned.empty:
            print("\nMarket API Data Head (Cleaned):")
            print(df_api_market_cleaned.head())
            print("\nMarket API Data Info:")
            df_api_market_cleaned.info()
            # os.makedirs(os.path.dirname(DEFAULT_API_SAMPLE_SAVE_PATH_DH), exist_ok=True)
            # df_api_market_cleaned.to_csv(DEFAULT_API_SAMPLE_SAVE_PATH_DH, index=False)
            # print(f"\nSample market API data saved to {DEFAULT_API_SAMPLE_SAVE_PATH_DH}")
        else:
            print("Market data cleaning resulted in empty or None DataFrame.")
    else:
        print("Could not fetch or process market API data.")