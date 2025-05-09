# main.py
import pandas as pd
from data_handler import load_data_from_csv, fetch_gutenberg_data_api, clean_market_data
from analysis_engine import analyze_genre_trends_by_decade, analyze_prolific_authors
from generative_ai_handler import generate_text_from_prompt
from visualization_handler import plot_genre_trends, save_data_to_excel
import time 
import os # For dynamic output filenames

def get_user_book_details():
    """Prompts the user for details about the book they want to vet."""
    print("\n--- User Book Details Input ---")
    title = input("Enter the title of the book: ").strip()
    author = input("Enter the author (optional, leave blank if unknown): ").strip()
    
    print("Enter primary subjects/genres, separated by semicolons (e.g., Science fiction; Space opera; Adventure).")
    subjects = input("Subjects/Genres: ").strip()
    
    year_str = input("Approx. publication year (optional): ").strip()
    page_count_str = input("Estimated page count (optional): ").strip()
    author_gender_str = input("Author's gender (e.g., male, female, non-binary - optional): ").strip()

    year = None
    if year_str:
        try: year = int(year_str)
        except ValueError: print(f"Warning: Invalid year '{year_str}'.")

    page_count = None
    if page_count_str:
        try: page_count = int(page_count_str)
        except ValueError: print(f"Warning: Invalid page count '{page_count_str}'.")

    if not title or not subjects:
        print("Error: Title and Subjects/Genres are required.")
        return None

    return {
        "title": title,
        "author": author if author else "Unknown Author",
        "subjects": subjects,
        "publication_year": year,
        "page_count": page_count,
        "author_gender": author_gender_str if author_gender_str else "Not specified"
    }

def generate_targeted_personas_for_user_book(user_book_details, market_context_summary="", num_personas=3):
    """Generates personas specifically for the user's book type, optionally using market context."""
    book_desc = (f"Title: '{user_book_details['title']}', Author: {user_book_details['author']}, "
                 f"Subjects: '{user_book_details['subjects']}'")
    if user_book_details['publication_year']: book_desc += f", Year: {user_book_details['publication_year']}"
    if user_book_details['page_count']: book_desc += f", ~{user_book_details['page_count']} pages"
    if user_book_details['author_gender'] != "Not specified": book_desc += f", Author Gender: {user_book_details['author_gender']}"

    prompt_context = f"Consider a book with these characteristics: {book_desc}.\n"
    if market_context_summary:
        prompt_context += f"\nFor broader context, here's a summary of general book market trends (based on historical data):\n{market_context_summary}\n"

    prompt = f"""
    {prompt_context}
    Based PRIMARILY on the characteristics of the specific book described above (and secondarily on any general market context provided), please generate {num_personas} distinct reader personas who would typically be most interested in THIS KIND of book.

    For each persona:
    1.  **Persona Name:** A catchy, descriptive name (e.g., "The Hardboiled Detective Aficionado" for a noir book).
    2.  **Core Appeal:** Why would this specific type of book appeal to them? What are they seeking?
    3.  **Reading Habits:** How do they typically consume books of this nature? (e.g., binge-read, savor slowly, discuss in book clubs).
    4.  **Other Preferences:** What other specific genres, sub-genres, authors, or themes do they likely enjoy that are SIMILAR or COMPLEMENTARY to this book type?
    5.  **Key Expectations for THIS Book:** What specific elements (e.g., plot pace, character depth, writing style, thematic exploration) would they hope to find in a book like the one described?

    Format each persona clearly, starting with "Persona Name:". Make them highly relevant and specific to the book type.
    """
    print("\n--- Generating Targeted AI Personas for User's Book ---")
    response_text = generate_text_from_prompt(prompt)
    
    personas_list = []
    if response_text:
        print("Generated Targeted Personas Text from AI:")
        # print(response_text) # Keep console cleaner, will be in Excel
        # Basic parsing - can be improved with regex or more structured AI output request
        current_persona = {}
        for line in response_text.split('\n'):
            line_strip = line.strip()
            if not line_strip: continue

            if line_strip.startswith("Persona Name:") or "**Persona Name:**" in line_strip:
                if current_persona: personas_list.append(current_persona)
                current_persona = {"full_text": line_strip} # Store full line for name
                try:
                    current_persona["name"] = line_strip.split(":",1)[1].strip().replace("*","")
                except:
                    current_persona["name"] = f"Persona {len(personas_list)+1}"
            elif current_persona: # Append lines to the current persona's full text
                 current_persona["full_text"] += "\n" + line_strip
                 # Attempt to parse individual fields (optional, full_text is fallback)
                 if "Core Appeal:" in line_strip: current_persona["appeal"] = line_strip.split(":",1)[1].strip()
                 elif "Reading Habits:" in line_strip: current_persona["habits"] = line_strip.split(":",1)[1].strip()
                 elif "Other Preferences:" in line_strip: current_persona["other_prefs"] = line_strip.split(":",1)[1].strip()
                 elif "Key Expectations for THIS Book:" in line_strip: current_persona["expectations"] = line_strip.split(":",1)[1].strip()
        if current_persona: personas_list.append(current_persona)
        
        if not personas_list and response_text: # Fallback if parsing is minimal
            return [{"name": "Unparsed Targeted Personas", "full_text": response_text}]
        return personas_list
    return []


def gauge_persona_interest_with_market_trends(user_book_details, targeted_personas, market_trends_summary):
    """
    For each targeted persona, gauge their interest in the user's specific book,
    considering general market trends.
    """
    print("\n--- Gauging Targeted Persona Interest (Considering Market Trends) ---")
    interest_feedback_list = []
    
    book_desc = (f"Title: '{user_book_details['title']}', Author: {user_book_details['author']}, "
                 f"Subjects: '{user_book_details['subjects']}'")
    if user_book_details['publication_year']: book_desc += f", Year: {user_book_details['publication_year']}"
    # Add other details if needed

    for persona in targeted_personas:
        persona_name = persona.get("name", "Unnamed Persona")
        persona_description = persona.get("full_text", "No description available.")

        prompt = f"""
        You are '{persona_name}'. Your profile is:
        {persona_description}

        You are considering a specific book:
        Book Details: {book_desc}

        Now, consider the following general book market trends (based on historical data):
        {market_trends_summary}

        Questions for you, '{persona_name}':
        1.  **Interest Level:** How interested are you in reading this specific book (High, Medium, Low, Not Interested)?
        2.  **Reasoning (Persona-Based):** Explain your interest level based on your persona's core appeal and preferences for this type of book.
        3.  **Impact of Market Trends:** How do the general market trends (e.g., popularity of certain genres, prolific authors in related areas) influence your decision or perception of this book? Does it make you more or less likely to read it, or does it not matter much to you? Explain why.
        4.  **Key Factor:** What is the single most important factor (either from the book's details or market trends) influencing your interest?
        """
        # print(f"Interest Prompt for {persona_name} (with market trends):\n{prompt[:400]}...") # Debug
        response_text = generate_text_from_prompt(prompt)
        
        feedback_entry = {"persona_name": persona_name}
        if response_text:
            # print(f"\nResponse from {persona_name} (re: market trends):")
            # print(response_text) # Keep console cleaner
            feedback_entry["interest_and_trend_reaction_AI"] = response_text
            # Try to parse out the interest level if possible
            if "Interest Level: High" in response_text: feedback_entry["parsed_interest"] = "High"
            elif "Interest Level: Medium" in response_text: feedback_entry["parsed_interest"] = "Medium"
            elif "Interest Level: Low" in response_text: feedback_entry["parsed_interest"] = "Low"
            elif "Interest Level: Not Interested" in response_text: feedback_entry["parsed_interest"] = "Not Interested"
        else:
            feedback_entry["interest_and_trend_reaction_AI"] = "No response generated."
        
        interest_feedback_list.append(feedback_entry)
        # time.sleep(2) # Small delay if making many calls
        
    return interest_feedback_list

def generate_gtm_strategy_for_user_book(user_book_details, targeted_personas_feedback, market_analysis_summaries):
    """Generates Go-To-Market strategy for the user's book."""
    print("\n--- Generating Go-To-Market Strategy for User's Book ---")

    book_desc_for_gtm = (f"a book titled '{user_book_details['title']}' by {user_book_details['author']}, "
                         f"focusing on subjects '{user_book_details['subjects']}'")
    # Add other details to book_desc_for_gtm as needed

    market_summary_str = "General Market Insights:\n"
    for key, summary in market_analysis_summaries.items():
        market_summary_str += f"- {key}: {summary.splitlines()[0]}\n" # First line of each summary

    persona_feedback_str = "Targeted Persona Feedback (considering market trends):\n"
    if targeted_personas_feedback:
        for feedback in targeted_personas_feedback:
            persona_feedback_str += (f"- {feedback['persona_name']} (Interest: {feedback.get('parsed_interest', 'N/A')}): "
                                     f"{feedback['interest_and_trend_reaction_AI'].splitlines()[1 if len(feedback['interest_and_trend_reaction_AI'].splitlines()) > 1 else 0]}\n") # Snippet
    else:
        persona_feedback_str = "No specific persona feedback available.\n"

    prompt = f"""
    We are developing a go-to-market strategy for a specific book: {book_desc_for_gtm}.

    Supporting Information:
    1.  General Market Context:
        {market_summary_str}
    2.  Feedback from Targeted Reader Personas (who considered the book against market trends):
        {persona_feedback_str}

    Based on all this information, please provide:
    A.  **Overall Market Positioning:** Briefly, how does this book fit into the current market based on trends and persona reactions? (2-3 sentences)
    B.  **Key Target Personas:** Identify the 2 most promising personas (from the feedback) to target for initial marketing.
    C.  **Actionable GTM Strategy Points (3-4 points):**
        For each point, suggest a specific marketing action. Explain the reasoning, linking it directly to:
        -   The user's book characteristics.
        -   The targeted personas' preferences or their reaction to market trends.
        -   Relevant general market trends.
    D.  **Potential Challenges & Mitigation (1-2 points):** What are potential hurdles, and how might they be addressed?

    Be specific and practical in your recommendations.
    """
    # print(f"GTM Prompt:\n{prompt[:500]}...") # Debug
    response_text = generate_text_from_prompt(prompt)
    if response_text:
        # print("\nGo-To-Market Strategy Idea from AI:")
        # print(response_text) # Keep console cleaner
        return response_text
    return "Could not generate go-to-market strategy for the user's book."


def main():
    print("--- Starting Book Vetting & Marketing Analysis Workflow ---")

    user_book = get_user_book_details()
    if not user_book:
        print("Exiting due to incomplete user book details.")
        return

    excel_data_sheets = {"UserInput_BookDetails": pd.DataFrame([user_book])}

    # 1. General Market Analysis (from Gutendex)
    print("\nStep 1: Analyzing General Book Market Trends...")
    df_market = fetch_gutenberg_data_api(limit=500) # Adjust limit: more data = better general trends
    if df_market is None or df_market.empty:
        print("Market data could not be fetched. Some analyses will be limited.")
        market_analysis_summaries = {} # Ensure it's defined
    else:
        df_market_cleaned = clean_market_data(df_market.copy())
        if df_market_cleaned is not None and not df_market_cleaned.empty:
            excel_data_sheets["MarketData_RawSample"] = df_market.head(100)
            excel_data_sheets["MarketData_CleanedSample"] = df_market_cleaned.head(100)

            market_analysis_summaries = {}
            genre_pivot, genre_sum = analyze_genre_trends_by_decade(df_market_cleaned.copy())
            if genre_sum: market_analysis_summaries["Market Genre Trends"] = genre_sum
            if genre_pivot is not None: excel_data_sheets["Market_GenreTrendsPivot"] = genre_pivot.reset_index()

            authors_df, authors_sum = analyze_prolific_authors(df_market_cleaned.copy())
            if authors_sum: market_analysis_summaries["Market Prolific Authors"] = authors_sum
            if authors_df is not None: excel_data_sheets["Market_TopAuthors"] = authors_df
            
            if genre_pivot is not None and not genre_pivot.empty:
                plot_genre_trends(genre_pivot, output_path=f"output/market_genre_trends_plot_for_{user_book['title'][:20].replace(' ','_')}.png")
        else:
            print("Market data cleaning failed. Some analyses will be limited.")
            market_analysis_summaries = {}


    # 2. Generate Targeted Personas for User's Book
    print("\nStep 2: Generating Targeted Reader Personas for Your Book...")
    market_context_for_personas = "\n".join(market_analysis_summaries.values())
    targeted_personas = generate_targeted_personas_for_user_book(user_book, market_context_for_personas)
    if targeted_personas:
        df_personas_for_excel = pd.DataFrame(targeted_personas) # Uses 'name' and 'full_text' and other parsed fields
        excel_data_sheets["TargetedPersonas_UserBook"] = df_personas_for_excel
    else:
        print("Could not generate targeted personas for the user's book.")

    # 3. Gauge Persona Interest in User's Book (Considering Market Trends)
    all_market_trends_summary = "Overall Market Snapshot:\n" + market_context_for_personas
    persona_trend_feedback = []
    if targeted_personas and market_analysis_summaries: # Need both personas and market trends
        print("\nStep 3: Gauging Persona Interest in Your Book (with Market Context)...")
        persona_trend_feedback = gauge_persona_interest_with_market_trends(user_book, targeted_personas, all_market_trends_summary)
        if persona_trend_feedback:
            excel_data_sheets["PersonaInterest_MarketContext_UserBook"] = pd.DataFrame(persona_trend_feedback)
    elif not targeted_personas:
        print("Skipping interest gauging: No targeted personas.")
    elif not market_analysis_summaries:
        print("Skipping interest gauging: No market trend data for context.")


    # 4. Generate Go-To-Market Strategy
    print("\nStep 4: Generating Go-To-Market Strategy for Your Book...")
    gtm_strategy = generate_gtm_strategy_for_user_book(user_book, persona_trend_feedback, market_analysis_summaries)
    if gtm_strategy:
        excel_data_sheets["GTM_Strategy_UserBook_AI"] = gtm_strategy # Saved as text summary
    else:
        print("Could not generate GTM strategy.")


    # 5. Save all outputs
    print("\nStep 5: Saving All Analysis to Excel...")
    # Sanitize filename from user input title
    clean_title = "".join(c if c.isalnum() else "_" for c in user_book['title'])[:30] # Max 30 chars, alphanumeric
    output_excel_filename = f"output/book_analysis_{clean_title}.xlsx"
    save_data_to_excel(excel_data_sheets, output_path=output_excel_filename)

    print(f"\n--- Analysis Complete for '{user_book['title']}' ---")
    print(f"Results saved to: {output_excel_filename}")
    if any(plot_path for plot_path in os.listdir("output") if plot_path.startswith("market_genre_trends_plot")):
         print("Market trend plot also saved in 'output' directory.")

if __name__ == "__main__":
    main()