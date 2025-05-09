# main.py
import pandas as pd
from data_handler import load_data_from_csv, fetch_gutenberg_data_api, clean_data
from analysis_engine import analyze_genre_trends_by_decade, analyze_prolific_authors
from generative_ai_handler import generate_text_from_prompt
from visualization_handler import plot_genre_trends, save_data_to_excel

def generate_ai_personas(analysis_summaries_dict, num_personas=2):
    """
    Generates reader personas based on analysis summaries.
    analysis_summaries_dict: A dictionary where keys are analysis types (e.g., "Genre Trends")
                             and values are the textual summaries.
    """
    combined_summary = "Key insights from book metadata analysis:\n"
    for key, summary_text in analysis_summaries_dict.items():
        if summary_text and isinstance(summary_text, str): # Ensure it's a non-empty string
            combined_summary += f"\n--- {key} ---\n{summary_text}\n"

    if len(combined_summary) < 50: # Arbitrary threshold for meaningful summary
        print("Not enough analysis summary to generate personas meaningfully.")
        return []

    prompt = f"""
    Based on the following data analysis summaries from a collection of book metadata:
    {combined_summary}

    Please generate {num_personas} distinct reader personas that would likely exist within the audience interested in these types of books.
    For each persona, provide:
    1. A catchy Persona Name (e.g., "The Historical Voyager", "The Sci-Fi Futurist").
    2. A brief Description of their reading habits, preferences, and motivations, directly informed by the provided data insights.
    3. Likely Preferred Genres/Subjects (be specific, drawing from the analysis).
    4. Key characteristics or expectations they might have for a book.

    Format each persona clearly.
    """
    print("\n--- Generating AI Personas ---")
    # print(f"Persona Prompt: {prompt}") # For debugging
    response_text = generate_text_from_prompt(prompt)
    
    if response_text:
        print("Generated Personas Text from AI:")
        print(response_text)
        # Further parsing might be needed here to structure the personas if you need them as objects
        # For now, we'll return the raw text. You can split by "Persona Name:" or similar patterns.
        # This is a good place for more robust parsing in a real application.
        personas = []
        current_persona = {}
        for line in response_text.split('\n'):
            if line.strip().startswith("Persona Name:") or "Persona Name:" in line:
                if current_persona: # save previous persona
                    personas.append(current_persona)
                current_persona = {"name": line.split(":",1)[1].strip()}
            elif line.strip().startswith("Description:") and current_persona:
                current_persona["description"] = line.split(":",1)[1].strip()
            elif line.strip().startswith("Likely Preferred Genres/Subjects:") and current_persona:
                current_persona["preferences"] = line.split(":",1)[1].strip()
            elif line.strip().startswith("Key characteristics or expectations:") and current_persona:
                current_persona["expectations"] = line.split(":",1)[1].strip()
        if current_persona: # Append the last persona
            personas.append(current_persona)
        
        if not personas and response_text: # Fallback if parsing fails but text exists
            print("Could not parse personas into structured list, returning raw text block.")
            return [response_text] # Return as a list with one item: the raw text
        
        return personas if personas else [response_text] # Ensure we return a list

    return []


def gauge_book_interest_with_personas(book_metadata_example, personas_list):
    """
    Uses generated personas to gauge interest in a sample book.
    book_metadata_example: A dictionary or string describing a sample book.
                           e.g., {"title": "The Lost City of Z", "author": "David Grann", "subjects": "Adventure; Exploration; History", "year": 2009}
    personas_list: A list of persona descriptions (strings or dictionaries from generate_ai_personas).
    """
    if not personas_list:
        print("No personas available to gauge book interest.")
        return {}

    print("\n--- Gauging Book Interest with Personas ---")
    interest_feedback = {}

    # Ensure book_metadata is a string for the prompt
    if isinstance(book_metadata_example, dict):
        book_details_str = ", ".join([f"{k}: {v}" for k, v in book_metadata_example.items()])
    else:
        book_details_str = str(book_metadata_example)


    for i, persona_data in enumerate(personas_list):
        # Construct persona description string for the prompt
        if isinstance(persona_data, dict) and 'name' in persona_data:
            persona_name = persona_data.get('name', f"Persona {i+1}")
            persona_description_for_prompt = f"Persona Name: {persona_name}\n"
            persona_description_for_prompt += f"Description: {persona_data.get('description', 'N/A')}\n"
            persona_description_for_prompt += f"Preferences: {persona_data.get('preferences', 'N/A')}"
        elif isinstance(persona_data, str): # If personas are just text blocks
            persona_name = f"Persona {i+1} (details below)"
            persona_description_for_prompt = persona_data
        else:
            print(f"Skipping invalid persona data: {persona_data}")
            continue
            
        prompt = f"""
        You are the reader persona described below:
        --- START PERSONA ---
        {persona_description_for_prompt}
        --- END PERSONA ---

        Now, consider the following book:
        Book Details: {book_details_str}

        Based on your persona, please provide:
        1. Your likely level of interest (e.g., High, Medium, Low, Not Interested).
        2. A brief explanation for your interest level, referencing your preferences and the book's details.
        3. One specific aspect of the book (based on its metadata) that particularly appeals or disinterests you.
        """
        # print(f"Interest Prompt for {persona_name}: {prompt}") # For debugging
        response_text = generate_text_from_prompt(prompt)
        if response_text:
            print(f"Response from {persona_name}:")
            print(response_text)
            interest_feedback[persona_name] = response_text
        else:
            interest_feedback[persona_name] = "No response generated."
            
    return interest_feedback

def generate_go_to_market_summary(analysis_summaries_dict, persona_interest_feedback, target_book_example_str="a newly discovered classic novel"):
    """
    Generates a go-to-market strategy summary.
    analysis_summaries_dict: Dictionary of analysis summaries.
    persona_interest_feedback: Dictionary of persona interest levels.
    target_book_example_str: A string describing the type of book the strategy is for.
    """
    print("\n--- Generating Go-To-Market Strategy Summary ---")
    
    combined_analysis_summary = "Key insights from book metadata analysis:\n"
    for key, summary_text in analysis_summaries_dict.items():
        if summary_text and isinstance(summary_text, str):
             combined_analysis_summary += f"\n--- {key} ---\n{summary_text}\n"
    
    persona_feedback_summary = "Persona Interest Feedback:\n"
    if persona_interest_feedback:
        for persona, feedback in persona_interest_feedback.items():
            persona_feedback_summary += f"- {persona}: {feedback.splitlines()[0] if feedback else 'N/A'}\n" # First line of feedback
    else:
        persona_feedback_summary = "No specific persona feedback available for this book type yet.\n"

    prompt = f"""
    Context: We are a publishing/media company looking to market books effectively.
    We have the following data analysis insights about book trends and author popularity:
    {combined_analysis_summary}

    We also simulated how different reader personas might react to a book like "{target_book_example_str}":
    {persona_feedback_summary}

    Based on all this information, please generate:
    1. A concise overall summary of the market landscape related to "{target_book_example_str}" (2-3 sentences).
    2. Three distinct, actionable go-to-market strategy points or recommendations for promoting "{target_book_example_str}". For each point, briefly explain the reasoning based on the data or persona insights.
    3. Identify one potential challenge or consideration for marketing this type of book.
    """
    # print(f"GTM Prompt: {prompt}") # For debugging
    response_text = generate_text_from_prompt(prompt)
    if response_text:
        print("Go-To-Market Strategy Idea from AI:")
        print(response_text)
        return response_text
    return "Could not generate go-to-market strategy."


def main():
    print("Starting Project Workflow...")
    # --- 1. Data Handling ---
    # df = load_data_from_csv("data/gutenberg_metadata.csv") # Option 1: Local CSV
    df = fetch_gutenberg_data_api(limit=2000) # Option 2: API, limit for speed in testing
                                            # For full run, increase limit or implement full pagination

    if df is None or df.empty:
        print("Failed to load or fetch data. Exiting.")
        return

    df_cleaned = clean_data(df.copy())
    if df_cleaned is None or df_cleaned.empty:
        print("Data cleaning resulted in empty DataFrame. Exiting.")
        return
    
    # Store data for Excel output later
    excel_data_sheets = {"RawData_Sample": df.head(100), "CleanedData_Sample": df_cleaned.head(100)}


    # --- 2. Data Analysis & Summary Generation ---
    analysis_summaries = {}

    genre_pivot_df, genre_summary = analyze_genre_trends_by_decade(df_cleaned.copy())
    if genre_summary:
        analysis_summaries["Genre Trends by Author Birth Decade Proxy"] = genre_summary
    if genre_pivot_df is not None:
        excel_data_sheets["GenreTrendsPivot"] = genre_pivot_df.reset_index() # Add pivot to Excel

    top_authors_df, authors_summary = analyze_prolific_authors(df_cleaned.copy(), n_top_authors=5)
    if authors_summary:
        analysis_summaries["Prolific Authors Analysis"] = authors_summary
    if top_authors_df is not None:
        excel_data_sheets["TopAuthors"] = top_authors_df


    # --- 3. Generative AI: Personas ---
    ai_personas_list = []
    if analysis_summaries:
        ai_personas_list = generate_ai_personas(analysis_summaries, num_personas=3)
        if ai_personas_list:
            # For Excel: if personas are dicts, convert to DataFrame. If text, save as text.
            if all(isinstance(p, dict) for p in ai_personas_list):
                excel_data_sheets["AI_Personas"] = pd.DataFrame(ai_personas_list)
            else: # Save raw text if parsing wasn't perfect or returned strings
                persona_text_for_excel = "\n\n---\n\n".join(str(p) for p in ai_personas_list)
                excel_data_sheets["AI_Personas_Text"] = persona_text_for_excel
        else:
            print("No personas were generated.")
    else:
        print("No analysis summaries available to generate personas.")
        
    # --- 4. Generative AI: Book Interest & Go-To-Market ---
    # Example book to test persona interest and GTM strategy
    sample_book_for_testing = {
        "title": "Chronicles of the Star Seeker",
        "author": "Jane Astro",
        "subjects": "Science fiction; Space opera; Adventure",
        "year_proxy": 2024 # (pretend it's a new book)
    }
    sample_book_str = f"a new Science Fiction Space Opera novel like '{sample_book_for_testing['title']}'"

    persona_interest_feedback = {}
    if ai_personas_list:
        persona_interest_feedback = gauge_book_interest_with_personas(sample_book_for_testing, ai_personas_list)
        if persona_interest_feedback:
            # Convert feedback to a more storable format for Excel
            feedback_df_data = []
            for p_name, p_feedback in persona_interest_feedback.items():
                feedback_df_data.append({"Persona": p_name, "Feedback": p_feedback})
            if feedback_df_data:
                excel_data_sheets["PersonaBookInterest"] = pd.DataFrame(feedback_df_data)
    else:
        print("Skipping book interest gauging as no personas were generated.")


    gtm_strategy_summary = generate_go_to_market_summary(analysis_summaries, persona_interest_feedback, target_book_example_str=sample_book_str)
    if gtm_strategy_summary:
        excel_data_sheets["GoToMarket_AI_Ideas"] = gtm_strategy_summary # Will be saved as text


    # --- 5. Visualization & Output ---
    if genre_pivot_df is not None and not genre_pivot_df.empty:
        plot_genre_trends(genre_pivot_df, output_path="output/genre_trends_plot.png")
    else:
        print("Skipping genre trend plotting due to missing data.")

    # Save all collected DataFrames and text summaries to Excel
    save_data_to_excel(excel_data_sheets, output_path="output/final_project_outputs.xlsx")

    print("\nProject Workflow Complete.")
    print("Check the 'output' directory for plots and Excel file.")

if __name__ == "__main__":
    main()