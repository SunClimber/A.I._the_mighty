# main.py
import pandas as pd
from data_handler import load_data_from_csv, fetch_gutenberg_data_api, clean_market_data
from analysis_engine import (
    analyze_genre_trends_by_decade, 
    analyze_prolific_authors,
    analyze_download_activity 
)
from generative_ai_handler import generate_text_from_prompt
from visualization_handler import (
    plot_genre_trends, plot_top_authors, 
    plot_subject_distribution, plot_persona_interest_summary
)
import time 
import os 
import re 

# --- Helper function to format DataFrames for Markdown (remains same) ---
def df_to_markdown_table(df, title=""):
    # ... (keep as is) ...
    if df is None or df.empty:
        return f"#### {title}\n\nNo data available for this section.\n\n" if title else "No data available.\n\n"
    header = f"#### {title}\n\n" if title else ""
    return header + df.to_markdown(index=False) + "\n\n"

# --- User Input Function (remains same) ---
def get_user_book_details():
    # ... (keep as is) ...
    print("\n--- User Book Details Input ---")
    title = input("Enter the title of the book: ").strip()
    author = input("Enter the author (optional): ").strip()
    subjects = input("Primary subjects/genres (semicolon-separated, e.g., Fantasy; Epic): ").strip()
    synopsis = input("Enter a brief (1-3 sentences) synopsis of the book: ").strip()
    
    year_str = input("Approx. publication year (optional): ").strip()
    page_count_str = input("Estimated page count (optional): ").strip()
    author_gender_str = input("Author's gender (optional): ").strip()
    author_age_str = input("Author's current age (if known/relevant, optional): ").strip()

    num_personas_str = input("How many targeted reader personas to generate? (e.g., 2-4, default 3): ").strip()
    num_personas_val = 3 
    if num_personas_str:
        try:
            num_p = int(num_personas_str)
            if 1 <= num_p <= 5: num_personas_val = num_p
            else: print("  Invalid number of personas (must be 1-5). Using default 3.")
        except ValueError: print("  Invalid input for number of personas. Using default 3.")

    year, page_count, author_age = None, None, None
    if year_str:
        try: year = int(year_str)
        except ValueError: print(f"Warning: Invalid year '{year_str}'.")
    if page_count_str:
        try: page_count = int(page_count_str)
        except ValueError: print(f"Warning: Invalid page count '{page_count_str}'.")
    if author_age_str: 
        try: author_age = int(author_age_str)
        except ValueError: print(f"Warning: Invalid author age '{author_age_str}'.")

    if not title or not subjects or not synopsis:
        print("Error: Title, Subjects/Genres, and Synopsis are required for a meaningful analysis.")
        return None
    return {
        "title": title, "author": author if author else "Unknown Author", "subjects": subjects,
        "synopsis": synopsis, "publication_year": year, "page_count": page_count,
        "author_gender": author_gender_str if author_gender_str else "Not specified",
        "author_age": author_age, 
        "num_personas_to_generate": num_personas_val
    }

# --- AI Interaction Functions ---

# summarize_historical_and_pg_download_context_md (remains same)
def summarize_historical_and_pg_download_context_md(
    historical_genre_summary_text, 
    pg_download_activity_summary_text,
    genre_plot_filename=None, 
    subject_dist_plot_filename=None
    ):
    # ... (keep as is) ...
    if not historical_genre_summary_text or not historical_genre_summary_text.strip():
        historical_genre_summary_text = "Detailed historical trend data was not available."
    if not pg_download_activity_summary_text or not pg_download_activity_summary_text.strip():
        pg_download_activity_summary_text = "Download activity analysis was not available."

    print("  Generating brief summary of historical context & PG download insights (AI)...")
    
    context_blocks = []
    if historical_genre_summary_text and "not available" not in historical_genre_summary_text.lower():
        context_blocks.append(f"Historical Literary Publication Trends (from classic, public domain works):\n{historical_genre_summary_text[:1000]}\n")
    if pg_download_activity_summary_text and "not available" not in pg_download_activity_summary_text.lower():
        context_blocks.append(f"Inferred Enduring Preferences (from current Project Gutenberg download activity for classics):\n{pg_download_activity_summary_text[:1000]}\n")

    if not context_blocks:
        return "No significant historical or Project Gutenberg download context was available to summarize.\n"
    combined_detailed_context = "\n".join(context_blocks)

    plot_references = []
    if genre_plot_filename: plot_references.append(f"historical genre publication trends ([view plot]({os.path.join('output', genre_plot_filename)}))")
    if subject_dist_plot_filename: plot_references.append(f"overall historical subject distribution by publication ([view plot]({os.path.join('output', subject_dist_plot_filename)}))")
    
    plot_links_text = ""
    if plot_references:
        plot_links_text = "You can explore visuals for " + " and ".join(plot_references) + " for more details."

    prompt = f"""
    Here's a compilation of analyses:
    --- DETAILED CONTEXT ---
    {combined_detailed_context}
    --- END DETAILED CONTEXT ---

    Please provide a very brief (1-2 short paragraphs, conversational, layman's terms) overview. 
    First, touch upon the general historical literary publication patterns. 
    Then, discuss any inferred enduring preferences based on current Project Gutenberg download activity for these classics.
    Conclude by naturally incorporating the following plot information if provided:
    {plot_links_text if plot_links_text else "No specific plot links to mention, just summarize the findings."}
    """
    brief_summary = generate_text_from_prompt(prompt)
    final_summary_md = ""
    if brief_summary and brief_summary.strip():
        final_summary_md = brief_summary.strip()
        if plot_links_text and not all(ref_part in final_summary_md.lower() for ref_part in ["genre publication", "subject distribution"]) and not "view plot" in final_summary_md.lower() :
             final_summary_md += f"\n\n{plot_links_text}"
    else: 
        final_summary_md = "A brief look at historical literary trends and current Project Gutenberg download patterns provides some context."
        if plot_links_text: final_summary_md += f" {plot_links_text}"
    return final_summary_md.strip() + "\n\n"


# generate_targeted_personas_md (remains same)
def generate_targeted_personas_md(user_book_details, combined_context_summary="", num_personas=3):
    # ... (keep as is) ...
    book_desc = (f"Title: '{user_book_details['title']}', Author: {user_book_details['author']} (Age: {user_book_details.get('author_age', 'N/A')}), "
                 f"Subjects: '{user_book_details['subjects']}'. Synopsis: {user_book_details['synopsis']}")
    if user_book_details['publication_year']: book_desc += f", Year: {user_book_details['publication_year']}"
    if user_book_details['page_count']: book_desc += f", ~{user_book_details['page_count']} pages"
    if user_book_details['author_gender'] != "Not specified": book_desc += f", Author Gender: {user_book_details['author_gender']}"

    prompt_context = f"Considering a book with these characteristics: {book_desc}.\n"
    if combined_context_summary: 
        prompt_context += f"\nBackground context (historical literary patterns & inferred enduring classic preferences from PG downloads):\n{combined_context_summary}\n"

    persona_format_instruction = """
For each persona, provide the following information clearly using Markdown list format:
- **Persona Name:** [Catchy, descriptive name]
- **Core Appeal for THIS Book Type:** [Why this specific type of book, with its given synopsis and subjects, appeals to them? Consider author's age if relevant.]
- **Reading Habits for THIS Book Type:** [How they consume such books]
- **Other Complementary Preferences:** [Other genres/themes they enjoy that align]
- **Key Expectations for THIS Specific Book:** [Specific elements they hope for in THIS book, given its title and synopsis]

Separate each complete persona description with a line containing only '---NEXT PERSONA---'.
"""
    prompt = f"""
    {prompt_context}
    Based PRIMARILY on the characteristics of the specific book described, generate {num_personas} distinct reader personas.
    If the background context (historical patterns or enduring classic preferences) offers relevant contrasts or parallels that would shape a modern reader persona for THIS book type, you may subtly incorporate that.
    {persona_format_instruction}
    """
    print(f"  Generating {num_personas} Targeted AI Personas for User's Book (Markdown focus)...")
    response_text = generate_text_from_prompt(prompt)
    if not response_text or not response_text.strip(): return []
    return [block.strip() for block in response_text.split("---NEXT PERSONA---") if block.strip()]

# gauge_persona_interest_md (remains same)
def gauge_persona_interest_md(user_book_details, persona_text_block, historical_pub_trends_summary, pg_download_inferred_prefs_summary):
    # ... (keep as is) ...
    persona_name_for_log = persona_text_block.splitlines()[0][:70] 
    print(f"  Gauging interest for Persona: {persona_name_for_log}...")
    book_desc = (f"Title: '{user_book_details['title']}', Subjects: '{user_book_details['subjects']}', "
                 f"Author Age: {user_book_details.get('author_age', 'N/A')}. Synopsis: {user_book_details['synopsis']}")
    if user_book_details['publication_year']: book_desc += f", Year: {user_book_details['publication_year']}"

    interest_format_instruction = """
Please structure your response with the following clear sections, using Markdown list format:
- **Interest Level:** [High, Medium, Low, or Not Interested]
- **Reasoning (Persona-Based):** [Your explanation based on your persona profile AND the specific book details (title, synopsis, author age etc.)]
- **Reflection on Historical Publication Patterns:** [How does this book align or contrast with general historical publication patterns for similar genres/themes (as described in historical context)? Does this historical background make the book more or less appealing to you?]
- **Reflection on Enduring Classic Preferences (from PG Downloads):** [How does this book relate to the types of classic themes/stories that show ongoing engagement on PG (as described in PG download context)? Does this make the book more or less appealing to you?]
- **Key Factor for Interest:** [The single most important factor influencing your interest in THIS specific book]
"""
    prompt = f"""
    You are a reader persona with the following profile:
    {persona_text_block}

    You are considering this specific book: {book_desc}

    Contextual Information:
    1. General historical literary PUBLICATION trends (from classic literature by author birth eras) indicate:
       {historical_pub_trends_summary if historical_pub_trends_summary else "No specific historical publication trends provided."}
    2. Inferred enduring preferences based on current Project Gutenberg DOWNLOAD activity for classics suggest:
       {pg_download_inferred_prefs_summary if pg_download_inferred_prefs_summary else "No specific PG download preference insights provided."}

    Please provide your feedback on the specific book using the following structure:
    {interest_format_instruction}
    """
    response_text = generate_text_from_prompt(prompt)
    parsed_interest_level = "Unknown"
    if response_text:
        match = re.search(r"\*\*Interest Level:\*\*\s*(High|Medium|Low|Not Interested)", response_text, re.IGNORECASE)
        if match: parsed_interest_level = match.group(1).capitalize()
    return response_text if response_text else "No AI response for this persona's interest.", parsed_interest_level


# --- CORRECTED generate_gtm_strategy_md function signature and internal usage ---
def generate_gtm_strategy_md(user_book_details, 
                             aggregated_persona_interest_summary, 
                             historical_pub_trends_summary,        # Now a separate argument
                             pg_download_inferred_prefs_summary):  # Now a separate argument
    """Generates GTM strategy, incorporating all contexts."""
    print("  Generating Go-To-Market Strategy (Markdown focus)...")
    book_desc_for_gtm = (f"Title: '{user_book_details['title']}', Author: {user_book_details['author']}, "
                         f"Subjects: '{user_book_details['subjects']}', Author Age: {user_book_details.get('author_age', 'N/A')}. "
                         f"Synopsis: {user_book_details['synopsis']}")

    # Use the passed individual summaries
    historical_context_str = "General Historical Literary Publication Patterns:\n" + \
                             (historical_pub_trends_summary if historical_pub_trends_summary and historical_pub_trends_summary.strip() else "N/A")
    pg_download_context_str = "Inferred Enduring Preferences from Classic PG Downloads:\n" + \
                              (pg_download_inferred_prefs_summary if pg_download_inferred_prefs_summary and pg_download_inferred_prefs_summary.strip() else "N/A")

    gtm_format_instruction = """
Please structure your Go-To-Market strategy with the following clear sections, using Markdown:
- **Overall Market Positioning:** [Briefly, how this book fits. (2-3 sentences)]
- **Key Target Personas (for GTM):** [Identify 1-2 most promising personas. Briefly state why.]
- **Marketing Strategy Points (3-4 points):** For each point:
    - **Strategy [Number] - Action:** [Specific marketing action]
    - **Strategy [Number] - Rationale:** [Link to the book's specifics, persona insights, and how it relates to historical patterns OR enduring classic preferences (from PG downloads). E.g., 'Leverage the novel's fresh take on [theme] which contrasts with historical norms but aligns with enduring interest in [classic theme from PG downloads].']
- **Potential Challenge & Mitigation:** [One hurdle and how to address it.]
""" # Added [Number] to Strategy points for clarity
    prompt = f"""
    Develop a concise go-to-market strategy for the book: {book_desc_for_gtm}.

    Supporting Information:
    1.  Context from Historical Literary Publication Patterns: {historical_context_str}
    2.  Context from Inferred Enduring Preferences (via PG Downloads): {pg_download_context_str}
    3.  Summary of Targeted Persona Interest in this book (after considering above contexts): {aggregated_persona_interest_summary}

    Provide the GTM strategy using the structure below:
    {gtm_format_instruction}
    """
    response_text = generate_text_from_prompt(prompt)
    return response_text if response_text else "Could not generate GTM strategy from AI."

# generate_overall_recommendation_md (remains same)
def generate_overall_recommendation_md(user_book_details, aggregated_persona_interest_summary, gtm_highlights=""):
    # ... (keep as is) ...
    print("  Generating Overall Recommendation...")
    book_desc = (f"Title: '{user_book_details['title']}', Subjects: '{user_book_details['subjects']}', "
                 f"Author Age: {user_book_details.get('author_age', 'N/A')}. Synopsis: {user_book_details['synopsis']}")

    recommendation_format_instruction = """
Please provide your recommendation with the following structure, using Markdown:
- **Overall Recommendation:** [Clearly state one: Strongly Recommend Pursuit, Recommend Pursuit with Considerations, Approach with Caution, or Not Recommended at this time.]
- **Key Justification (2-4 sentences):** [Explain your recommendation, highlighting key factors from the persona interest analysis. Briefly mention if GTM seems viable based on the provided GTM highlights.]
- **Confidence Score (Optional):** [Low/Medium/High]
"""
    prompt = f"""
    You are an experienced publishing consultant. Based on the following information for a book ({book_desc}):
    - Summary of Targeted Persona Interest (which included reflection on historical literary patterns and enduring classic preferences from PG downloads): {aggregated_persona_interest_summary}
    - Highlights of potential Go-To-Market approach: {gtm_highlights if gtm_highlights else "GTM considerations to be detailed."}

    Provide an overall recommendation to a publishing company on whether to pursue this book. Use the structure below:
    {recommendation_format_instruction}
    """
    response_text = generate_text_from_prompt(prompt)
    return response_text if response_text else "Could not generate an overall recommendation."

# --- Main Orchestration ---
def main():
    print("--- Starting Book Vetting & Marketing Analysis Workflow (Markdown Output) ---")
    os.makedirs("output", exist_ok=True) 

    user_book = get_user_book_details()
    if not user_book: return
    clean_title_for_files = "".join(c if c.isalnum() else "_" for c in user_book['title'])[:25]
    if not clean_title_for_files: clean_title_for_files = "untitled_book"
    
    report_md_lines = [f"# Book Vetting Analysis: {user_book['title']}\n"]

    report_md_lines.append("## I. User-Provided Book Details\n")
    for key, value in user_book.items():
        display_key = key.replace("_", " ").title()
        report_md_lines.append(f"- **{display_key}:** {value}\n")
    report_md_lines.append("\n")

    recommendation_placeholder_index = len(report_md_lines) 
    report_md_lines.append("## II. Overall Recommendation & Justification\n\n_[Generating recommendation...this will be updated.]_\n\n")

    # --- Contextual Analysis ---
    print("\nStep 1: Analyzing Context (Historical Literary Trends & PG Download Activity)...")
    appendix_md_lines = ["## VI. Appendix: Contextual Analysis Details\n"] 
    
    df_market = fetch_gutenberg_data_api(limit=500) 
    output_plots_dir = "output"

    historical_genre_pub_summary_text = "Historical genre publication trend data not available for context." # Default
    pg_download_activity_summary_text = "Project Gutenberg download activity analysis not available for context." # Default
    genre_trends_plot_file, subject_dist_pub_plot_file = None, None
    # Optional download plots: subject_download_plot_file, author_download_plot_file = None, None


    if df_market is not None and not df_market.empty:
        df_market_cleaned = clean_market_data(df_market.copy())
        if df_market_cleaned is not None and not df_market_cleaned.empty:
            # 1a. Historical Publication Trends
            genre_pivot, hist_genre_sum_text_detailed, subject_pub_counts = analyze_genre_trends_by_decade(df_market_cleaned.copy())
            if hist_genre_sum_text_detailed: historical_genre_pub_summary_text = hist_genre_sum_text_detailed # Use the detailed one for AI context
            if genre_pivot is not None: 
                genre_trends_plot_file = plot_genre_trends(genre_pivot, user_book['title'], output_dir=output_plots_dir)
            if subject_pub_counts is not None and not subject_pub_counts.empty:
                subject_dist_pub_plot_file = plot_subject_distribution(subject_pub_counts, user_book['title'], output_dir=output_plots_dir, plot_type="publication")
            
            # Prolific authors (by pub vol) - not directly used in main report text but plot can be in appendix
            authors_df_pub_table, _ = analyze_prolific_authors(df_market_cleaned.copy())
            if authors_df_pub_table is not None:
                 plot_top_authors(authors_df_pub_table, user_book['title'], output_dir=output_plots_dir, plot_type="publication")


            # 1b. Project Gutenberg Download Activity Analysis
            pg_dl_sum_text_detailed, df_top_subj_dl, df_top_auth_dl = analyze_download_activity(df_market_cleaned.copy())
            if pg_dl_sum_text_detailed: pg_download_activity_summary_text = pg_dl_sum_text_detailed # Use detailed for AI context
            # Optional: Plots for download activity
            # if df_top_subj_dl is not None: subject_download_plot_file = plot_subject_distribution(df_top_subj_dl.set_index('subject')['download_count'], user_book['title'], output_dir=output_plots_dir, plot_type="download")
            # if df_top_auth_dl is not None: author_download_plot_file = plot_top_authors(df_top_auth_dl, user_book['title'], output_dir=output_plots_dir, plot_type="download")

            # AI-Generated Brief Summary for Appendix using the detailed summaries
            brief_overall_context_summary = summarize_historical_and_pg_download_context_md(
                historical_genre_pub_summary_text, 
                pg_download_activity_summary_text,
                genre_plot_filename=genre_trends_plot_file,
                subject_dist_plot_filename=subject_dist_pub_plot_file
            )
            appendix_md_lines.append("### Brief Overview of Historical Literary Context & PG Download Insights\n")
            appendix_md_lines.append(brief_overall_context_summary)
        else:
            appendix_md_lines.append("Historical market data cleaning failed; context limited.\n")
    else:
        appendix_md_lines.append("Historical market data could not be fetched; context limited.\n")
    appendix_md_lines.append("\n")

    # 2. Generate Targeted Personas
    print("\nStep 2: Generating Targeted Reader Personas for Your Book...")
    report_md_lines.append("## III. Targeted Reader Personas for Your Book\n")
    # Use the brief AI-generated summary of all contexts for persona generation
    context_for_persona_ai = brief_overall_context_summary if 'brief_overall_context_summary' in locals() and brief_overall_context_summary else "General literary context not fully analyzed for this run."
    num_personas_to_gen = user_book.get("num_personas_to_generate", 3)
    targeted_persona_text_blocks = generate_targeted_personas_md(user_book, context_for_persona_ai, num_personas=num_personas_to_gen)
    
    if targeted_persona_text_blocks:
        for i, persona_block in enumerate(targeted_persona_text_blocks):
            persona_name_match = re.search(r"\*\*Persona Name:\*\*\s*(.*)", persona_block)
            persona_heading_name = persona_name_match.group(1).strip() if persona_name_match else f"Persona {i+1}"
            report_md_lines.append(f"### {persona_heading_name}\n")
            report_md_lines.append(persona_block + "\n\n")
    else:
        report_md_lines.append("Could not generate targeted personas.\n")

    # 3. Gauge Persona Interest
    persona_interest_feedbacks_md_blocks = [] 
    all_interest_levels_for_plot = [] 
    
    if targeted_persona_text_blocks : # Only need personas to proceed
        print("\nStep 3: Gauging Persona Interest in Your Book (with Context)...")
        report_md_lines.append("## IV. Persona Interest in Your Book (Contextualized)\n")
        
        # Pass the detailed (not AI-briefed) summaries for richer context during interest gauging
        for i, persona_full_text_block in enumerate(targeted_persona_text_blocks):
            interest_text_block, parsed_level = gauge_persona_interest_md(
                user_book, 
                persona_full_text_block, 
                historical_genre_pub_summary_text, 
                pg_download_activity_summary_text  
            )
            persona_name_match = re.search(r"\*\*Persona Name:\*\*\s*(.*)", persona_full_text_block)
            current_persona_name_for_heading = persona_name_match.group(1).strip() if persona_name_match else f"Persona {i+1}"
            report_md_lines.append(f"### Feedback from: {current_persona_name_for_heading}\n")
            report_md_lines.append(interest_text_block + "\n\n")
            persona_interest_feedbacks_md_blocks.append(f"Feedback from {current_persona_name_for_heading}:\n{interest_text_block}")
            if parsed_level != "Unknown": all_interest_levels_for_plot.append(parsed_level)
    else:
        report_md_lines.append("Skipping detailed persona interest gauging (no personas generated).\n")

    persona_interest_plot_file = None
    if all_interest_levels_for_plot:
        persona_interest_plot_file = plot_persona_interest_summary(all_interest_levels_for_plot, user_book['title'], output_dir=output_plots_dir)
        if persona_interest_plot_file:
            try: 
                idx_interest_header = report_md_lines.index("## IV. Persona Interest in Your Book (Contextualized)\n")
                report_md_lines.insert(idx_interest_header + 1, f"\n_(Aggregated interest levels - [view plot]({os.path.join(output_plots_dir, persona_interest_plot_file)}))_\n\n")
            except ValueError: 
                report_md_lines.append(f"\n_(Aggregated interest levels - [view plot]({os.path.join(output_plots_dir, persona_interest_plot_file)}))_\n\n")

    # 4. Generate Go-To-Market Strategy
    print("\nStep 4: Generating Go-To-Market Strategy for Your Book...")
    report_md_lines.append("## V. Go-To-Market Strategy Suggestions\n")
    aggregated_interest_summary_for_gtm = "Overall persona interest levels: " + (", ".join(all_interest_levels_for_plot) if all_interest_levels_for_plot else "Not determined.")
    # Pass detailed summaries to GTM as well
    gtm_strategy_text = generate_gtm_strategy_md(user_book, aggregated_interest_summary_for_gtm, 
                                                 historical_genre_pub_summary_text, 
                                                 pg_download_activity_summary_text) # CORRECTED CALL
    report_md_lines.append(gtm_strategy_text + "\n\n")

    # 5. Generate Overall Recommendation
    print("\nStep 5: Generating Overall Recommendation...")
    gtm_highlights_for_reco = "GTM strategy outlined."
    if "Error" in gtm_strategy_text or "Could not generate" in gtm_strategy_text or not gtm_strategy_text.strip():
        gtm_highlights_for_reco = "GTM strategy generation was inconclusive or faced issues."
    elif gtm_strategy_text:
        match_positioning = re.search(r"\*\*Overall Market Positioning:\*\*\s*(.*)", gtm_strategy_text, re.IGNORECASE)
        if match_positioning: gtm_highlights_for_reco = f"Key GTM Insight - Market Positioning: {match_positioning.group(1).strip()[:150]}..."
            
    overall_recommendation_text = generate_overall_recommendation_md(user_book, aggregated_interest_summary_for_gtm, gtm_highlights_for_reco)
    actual_recommendation_section_md = f"## II. Overall Recommendation & Justification\n{overall_recommendation_text}\n\n"
    report_md_lines[recommendation_placeholder_index] = actual_recommendation_section_md

    report_md_lines.extend(appendix_md_lines)

    # 6. Save Markdown file & Print key parts
    print("\nStep 6: Finalizing Report...")
    final_markdown_report_str = "".join(report_md_lines)
    
    print("\n\n--- Executive Summary & Recommendation (from Report) ---")
    print(overall_recommendation_text if overall_recommendation_text else "Recommendation could not be generated.")
    print("\n--- Aggregated Persona Interest ---")
    print(aggregated_interest_summary_for_gtm)

    output_md_filename = os.path.join(output_plots_dir, f"book_analysis_report_{clean_title_for_files}.md")
    try:
        with open(output_md_filename, "w", encoding="utf-8") as f: f.write(final_markdown_report_str)
        print(f"\n--- Analysis Complete for '{user_book['title']}' ---")
        print(f"Markdown report saved to: {output_md_filename}")
        print(f"Plots saved in '{output_plots_dir}' directory.")
    except Exception as e: print(f"Error saving Markdown report: {e}")

if __name__ == "__main__":
    main()