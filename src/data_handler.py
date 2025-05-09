# data_handler.py
import pandas as pd
import requests # For fetching from an API like Gutendex

# --- Option 1: Load from a local CSV ---
def load_data_from_csv(file_path="data/gutenberg_metadata.csv"):
    """Loads data from a local CSV file."""
    try:
        df = pd.read_csv(file_path)
        print(f"Data loaded successfully from {file_path}. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# --- Option 2: Fetch from Gutendex API (Example for ~32k books) ---
def fetch_gutenberg_data_api(limit=1000):
    """Fetches data from Gutendex API.
       Note: Gutendex API can be paginated. This is a simplified example.
       For a full fetch, you'd need to handle pagination.
    """
    print(f"Fetching up to {limit} records from Gutendex API...")
    all_books = []
    page_url = f"http://gutendex.com/books/?page_size={min(limit, 32)}" # API has page_size limit

    records_fetched = 0
    while page_url and records_fetched < limit:
        try:
            response = requests.get(page_url)
            response.raise_for_status() # Raise an exception for HTTP errors
            data = response.json()
            
            for book_data in data.get('results', []):
                if records_fetched >= limit:
                    break
                subjects = "; ".join(book_data.get('subjects', []))
                authors = ", ".join([author['name'] for author in book_data.get('authors', [])])
                languages = ", ".join(book_data.get('languages', []))
                # Try to get a release date (birth_year and death_year of author might be more available)
                # Project Gutenberg release date isn't original publication date.
                # For this example, we'll use author's birth year if available as a proxy for 'era'
                release_year = None
                if book_data.get('authors'):
                    release_year = book_data['authors'][0].get('birth_year')


                all_books.append({
                    'id': book_data.get('id'),
                    'title': book_data.get('title'),
                    'authors': authors,
                    'languages': languages,
                    'subjects': subjects, # Often contains genre-like terms
                    'download_count': book_data.get('download_count'),
                    'release_year_proxy': release_year # Using author birth year as proxy
                })
                records_fetched += 1
            
            page_url = data.get('next') # URL for the next page
            print(f"Fetched {records_fetched} records...")
            if not page_url:
                print("No more pages to fetch or API limit reached.")
                break

        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            page_url = None # Stop trying on error
        except Exception as e:
            print(f"An unexpected error occurred during API fetch: {e}")
            page_url = None


    if not all_books:
        print("No books fetched. Returning empty DataFrame.")
        return pd.DataFrame()
        
    df = pd.DataFrame(all_books)
    print(f"Fetched {len(df)} books from Gutendex API.")
    # Basic cleaning
    df.dropna(subset=['title', 'authors', 'subjects'], inplace=True)
    df['release_year_proxy'] = pd.to_numeric(df['release_year_proxy'], errors='coerce')
    print(f"Data shape after basic cleaning: {df.shape}")
    return df


def clean_data(df):
    """Basic data cleaning steps."""
    if df is None:
        return None
    print("Cleaning data...")
    # Example: Convert release_date to datetime, handle missing values
    # df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    # df['year'] = df['release_date'].dt.year

    # For subjects (often |-separated or list-like strings)
    # This is highly dependent on your actual data format
    # df['genres'] = df['subjects'].apply(lambda x: x.split('|')[0] if pd.notnull(x) else 'Unknown')
    df.dropna(subset=['release_year_proxy'], inplace=True) # Ensure we have a year for trend analysis
    df['decade_proxy'] = (df['release_year_proxy'] // 10) * 10


    print("Data cleaning complete.")
    return df

if __name__ == '__main__':
    # Test CSV loading
    # Create a dummy CSV for testing if you don't have one
    # import pandas as pd
    # dummy_data = {'title': ['Book A', 'Book B'], 'author': ['Auth1', 'Auth2'], 'release_date': ['2020-01-01', '2021-01-01'], 'subjects': ['Fiction|Adventure', 'Sci-Fi|Robots']}
    # pd.DataFrame(dummy_data).to_csv('data/gutenberg_metadata.csv', index=False)
    # df_csv = load_data_from_csv()
    # if df_csv is not None:
    #     print("\nCSV Data Head:")
    #     print(df_csv.head())

    # Test API fetching
    df_api = fetch_gutenberg_data_api(limit=50) # Fetch a small number for testing
    if df_api is not None and not df_api.empty:
        df_api_cleaned = clean_data(df_api.copy())
        print("\nAPI Data Head (Cleaned):")
        print(df_api_cleaned.head())
        print("\nAPI Data Info:")
        df_api_cleaned.info()

        # Save a sample to CSV for easier inspection / future use
        # df_api_cleaned.to_csv("data/gutenberg_sample_api.csv", index=False)
        # print("\nSample API data saved to data/gutenberg_sample_api.csv")

    else:
        print("Could not fetch or process API data.")