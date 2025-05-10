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
    if df is None or df.empty:
        return f"#### {title}\n\nNo data available for this section.\n\n" if title else "No data available.\n\n"
    header = f"#### {title}\n\n" if title else ""
    return header + df.to_markdown(index=False) + "\n\n"

# --- User Input Function (remains same) ---
def get_user_book_details():
    # ... (keep as is from the version with author_age, synopsis, num_personas) ...
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
        "author_age": author_age, "num_personas_to_generate": num_personas_val
    }

# --- AI Interaction Functions (summarize_historical..., generate_targeted_personas..., gauge_persona_interest..., generate_gtm..., generate_overall_recommendation...) ---
# --- These remain the same as the last "Analyst's Note" version. ---
# --- For brevity, I will not repeat them here, assume they are the same. ---
# (Make sure to copy those functions from the previous response into this main.py)
def summarize_historical_and_pg_download_context_md(
    historical_genre_summary_text, pg_download_activity_summary_text,
    genre_plot_filename=None, subject_dist_plot_filename=None ):
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
    if not context_blocks: return "No significant historical or Project Gutenberg download context was available to summarize.\n"
    combined_detailed_context = "\n".join(context_blocks)
    plot_references = []
    # Use os.path.basename for cleaner display in the summary text
    if genre_plot_filename: plot_references.append(f"historical genre publication trends ([view plot]({os.path.basename(genre_plot_filename)}))")
    if subject_dist_plot_filename: plot_references.append(f"overall historical subject distribution by publication ([view plot]({os.path.basename(subject_dist_plot_filename)}))")
    plot_links_text = ""
    if plot_references: plot_links_text = "You can explore visuals for " + " and ".join(plot_references) + " for more details."
    prompt = f"""
    Here's a compilation of analyses:
    --- DETAILED CONTEXT ---
    {combined_detailed_context}
    --- END DETAILED CONTEXT ---
    Please provide a very brief (1-2 short paragraphs, conversational, layman's terms) overview. 
    First, touch upon the general historical literary publication patterns. 
    Then, discuss any inferred enduring preferences based on current Project Gutenberg download activity for these classics.
    Conclude by naturally incorporating the following plot information if provided:
    {plot_links_text if plot_links_text else "No specific plot links to mention, just summarize the findings."}"""
    brief_summary = generate_text_from_prompt(prompt)
    final_summary_md = ""
    if brief_summary and brief_summary.strip():
        final_summary_md = brief_summary.strip()
        if plot_links_text and not all(ref_part in final_summary_md.lower() for ref_part in ["genre publication", "subject distribution"]) and not "view plot" in final_summary_md.lower() :
             final_summary_md += f"\n\n{plot_links_text}" # Append if AI missed
    else: 
        final_summary_md = "A brief look at historical literary trends and current Project Gutenberg download patterns provides some context."
        if plot_links_text: final_summary_md += f" {plot_links_text}"
    return final_summary_md.strip() + "\n\n"

def generate_targeted_personas_md(user_book_details, combined_context_summary="", num_personas=3):
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
    If the background context (historical patterns or enduring classic preferences) offers relevant contrasts or parallels that would shape a modern reader persona for THIS book type, you may subtly incorporate that into their profile.
    {persona_format_instruction}"""
    print(f"  Generating {num_personas} Targeted AI Personas for User's Book (Markdown focus)...")
    response_text = generate_text_from_prompt(prompt)
    if not response_text or not response_text.strip(): return []
    return [block.strip() for block in response_text.split("---NEXT PERSONA---") if block.strip()]

def gauge_persona_interest_md(user_book_details, persona_text_block, historical_pub_trends_summary, pg_download_inferred_prefs_summary):
    persona_name_for_log = persona_text_block.splitlines()[0][:70] 
    print(f"  Gauging interest for Persona: {persona_name_for_log}...")
    book_desc = (f"Title: '{user_book_details['title']}', Subjects: '{user_book_details['subjects']}', "
                 f"Author Age: {user_book_details.get('author_age', 'N/A')}. Synopsis: {user_book_details['synopsis']}")
    if user_book_details['publication_year']: book_desc += f", Year: {user_book_details['publication_year']}"
    persona_feedback_instruction = """
PART 1: Persona's Direct Feedback
Please structure your response (as the persona) with the following clear sections, using Markdown list format:
- **Interest Level:** [High, Medium, Low, or Not Interested]
- **Reasoning (Persona-Based):** [Your explanation based on your persona profile AND the specific book details (title, synopsis, author age etc.) for THIS book.]
- **Key Factor for Interest:** [The single most important factor (from book details or your persona profile) influencing your interest in THIS specific book.]
---END PERSONA FEEDBACK---"""
    analyst_note_instruction = """
PART 2: Analyst's Note on Context (Third-Person Perspective)
Now, acting as a literary market analyst, provide a brief (1-2 sentences each) contextual note regarding the persona's feedback above.
- **Note on Historical Publication Context:** [How does this persona's interest/disinterest in this specific modern book relate to or contrast with the general historical PUBLICATION patterns previously identified for similar genres/themes from classic literature? (e.g., 'This aligns with historical trends of X genre...' or 'This contrasts sharply with older Y genre conventions...')]
- **Note on Enduring Classic Preferences (PG Downloads):** [How does this persona's interest/disinterest in this specific modern book relate to or contrast with the inferred enduring preferences for certain classic story elements/genres as suggested by Project Gutenberg DOWNLOAD activity? (e.g., 'The persona's attraction to [theme] echoes the enduring popularity of similar themes in downloaded classics.' or 'This book's modern approach diverges from the more traditional elements that see high PG downloads.')]
---END ANALYST NOTE---"""
    prompt = f"""
    You will perform two tasks in sequence.
    **Task 1: Embody the Persona**
    You are a reader persona with the following profile:
    {persona_text_block}
    You are considering this specific book: {book_desc}
    Provide your feedback on this specific book using the format specified in PART 1 below.
    {persona_feedback_instruction}
    **Task 2: Provide an Analyst's Perspective**
    After providing the persona's feedback, switch to a third-person, analytical perspective.
    Use the persona's feedback you just generated and the contextual information below to write the Analyst's Note as specified in PART 2.
    Contextual Information for Analyst's Note:
    1. General historical literary PUBLICATION trends (from classic literature by author birth eras) indicate:
       {historical_pub_trends_summary if historical_pub_trends_summary and historical_pub_trends_summary.strip() else "No specific historical publication trends provided for deep context."}
    2. Inferred enduring preferences based on current Project Gutenberg DOWNLOAD activity for classics suggest:
       {pg_download_inferred_prefs_summary if pg_download_inferred_prefs_summary and pg_download_inferred_prefs_summary.strip() else "No specific PG download preference insights provided for deep context."}
    {analyst_note_instruction}"""
    response_text = generate_text_from_prompt(prompt)
    persona_direct_feedback = "No AI response for persona's direct feedback."
    analysts_note = "Analyst's note could not be generated."
    parsed_interest_level = "Unknown"
    if response_text:
        parts = response_text.split("---END PERSONA FEEDBACK---")
        if len(parts) > 0:
            persona_direct_feedback = parts[0].replace("PART 1: Persona's Direct Feedback", "").strip()
            match = re.search(r"\*\*Interest Level:\*\*\s*(High|Medium|Low|Not Interested)", persona_direct_feedback, re.IGNORECASE)
            if match: parsed_interest_level = match.group(1).capitalize()
        if len(parts) > 1:
            analyst_part = parts[1].replace("---END ANALYST NOTE---", "").replace("PART 2: Analyst's Note on Context (Third-Person Perspective)", "").strip()
            analysts_note = analyst_part
        elif "Analyst's Note on Context" in response_text : 
            analysts_note = response_text.split("Analyst's Note on Context (Third-Person Perspective)")[1].replace("---END ANALYST NOTE---", "").strip()
    return persona_direct_feedback, analysts_note, parsed_interest_level

def generate_gtm_strategy_md(user_book_details, aggregated_persona_interest_summary, 
                             historical_pub_trends_summary, pg_download_inferred_prefs_summary):
    print("  Generating Go-To-Market Strategy (Markdown focus)...")
    book_desc_for_gtm = (f"Title: '{user_book_details['title']}', Author: {user_book_details['author']} (Age: {user_book_details.get('author_age', 'N/A')}), "
                         f"Subjects: '{user_book_details['subjects']}'. Synopsis: {user_book_details['synopsis']}")
    historical_context_str = "General Historical Literary Publication Patterns:\n" + \
                             (historical_pub_trends_summary if historical_pub_trends_summary and historical_pub_trends_summary.strip() else "Not available for GTM.")
    pg_download_context_str = "Inferred Enduring Preferences from Classic PG Downloads:\n" + \
                              (pg_download_inferred_prefs_summary if pg_download_inferred_prefs_summary and pg_download_inferred_prefs_summary.strip() else "Not available for GTM.")
    gtm_format_instruction = """
Please structure your Go-To-Market strategy with the following clear sections, using Markdown:
- **Overall Market Positioning:** [Briefly, how this book fits. (2-3 sentences)]
- **Key Target Personas (for GTM):** [Identify 1-2 most promising personas from the feedback. Briefly state why.]
- **Marketing Strategy Points (3-4 points):** For each point:
    - **Strategy [Number] - Action:** [Specific marketing action]
    - **Strategy [Number] - Rationale:** [Link to the book's specifics, persona insights, and how it relates to historical patterns OR enduring classic preferences (from PG downloads). E.g., 'Leverage the novel's fresh take on [theme] which contrasts with historical norms but aligns with enduring interest in [classic theme from PG downloads].']
- **Potential Challenge & Mitigation:** [One hurdle and how to address it.]"""
    prompt = f"""
    Develop a concise go-to-market strategy for the book: {book_desc_for_gtm}.
    Supporting Information:
    1.  Context from Historical Literary Publication Patterns: {historical_context_str}
    2.  Context from Inferred Enduring Preferences (via PG Downloads): {pg_download_context_str}
    3.  Summary of Targeted Persona Interest in this book (after considering above contexts): {aggregated_persona_interest_summary}
    Provide the GTM strategy using the structure below:
    {gtm_format_instruction}"""
    response_text = generate_text_from_prompt(prompt)
    return response_text if response_text else "Could not generate GTM strategy from AI."

def generate_overall_recommendation_md(user_book_details, aggregated_persona_interest_summary, gtm_highlights=""):
    print("  Generating Overall Recommendation...")
    book_desc = (f"Title: '{user_book_details['title']}', Subjects: '{user_book_details['subjects']}', "
                 f"Author Age: {user_book_details.get('author_age', 'N/A')}. Synopsis: {user_book_details['synopsis']}")
    recommendation_format_instruction = """
Please provide your recommendation with the following structure, using Markdown:
- **Overall Recommendation:** [Clearly state one: Strongly Recommend Pursuit, Recommend Pursuit with Considerations, Approach with Caution, or Not Recommended at this time.]
- **Key Justification (2-4 sentences):** [Explain your recommendation, highlighting key factors from the persona interest analysis. Briefly mention if GTM seems viable based on the provided GTM highlights.]
- **Confidence Score (Optional):** [Low/Medium/High]"""
    prompt = f"""
    You are an experienced publishing consultant. Based on the following information for a book ({book_desc}):
    - Summary of Targeted Persona Interest (which included reflection on historical literary patterns and enduring classic preferences from PG downloads): {aggregated_persona_interest_summary}
    - Highlights of potential Go-To-Market approach: {gtm_highlights if gtm_highlights else "GTM considerations to be detailed."}
    Provide an overall recommendation to a publishing company on whether to pursue this book. Use the structure below:
    {recommendation_format_instruction}"""
    response_text = generate_text_from_prompt(prompt)
    return response_text if response_text else "Could not generate an overall recommendation."


# --- Main Orchestration ---
def main():
    print("--- Starting Book Vetting & Marketing Analysis Workflow (Markdown Output) ---")
    
    user_book = get_user_book_details()
    if not user_book: return

    # --- Create a book-specific output directory ---
    base_output_dir = "output" # Main output folder
    # Sanitize title for folder name (more restrictive than for filenames)
    folder_name_safe = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '' for c in user_book['title']).strip()
    folder_name_safe = re.sub(r'\s+', '_', folder_name_safe)[:50] # Replace spaces with underscores, limit length
    if not folder_name_safe: folder_name_safe = "untitled_book_analysis" # Fallback
    
    book_specific_output_dir = os.path.join(base_output_dir, folder_name_safe)
    os.makedirs(book_specific_output_dir, exist_ok=True)
    print(f"Output for '{user_book['title']}' will be saved in: {book_specific_output_dir}")
    # --- End directory setup ---

    clean_title_for_report_filename = "".join(c if c.isalnum() else "_" for c in user_book['title'])[:25]
    if not clean_title_for_report_filename: clean_title_for_report_filename = "untitled_book"
    
    report_md_lines = [f"# Book Vetting Analysis: {user_book['title']}\n"]

    report_md_lines.append("## I. User-Provided Book Details\n")
    for key, value in user_book.items():
        display_key = key.replace("_", " ").title()
        report_md_lines.append(f"- **{display_key}:** {value}\n")
    report_md_lines.append("\n")

    recommendation_placeholder_index = len(report_md_lines) 
    report_md_lines.append("## II. Overall Recommendation & Justification\n\n_[Generating recommendation...this will be updated.]_\n\n")

    print("\nStep 1: Analyzing Context (Historical Literary Trends & PG Download Activity)...")
    appendix_md_lines = ["## VI. Appendix: Contextual Analysis Details\n"] 
    df_market = fetch_gutenberg_data_api(limit=500) 

    hist_genre_pub_summary_text = "Historical genre publication trend data not available for context."
    pg_download_activity_summary_text = "Project Gutenberg download activity analysis not available for context."
    genre_trends_plot_filename, subject_dist_pub_plot_filename = None, None

    if df_market is not None and not df_market.empty:
        df_market_cleaned = clean_market_data(df_market.copy())
        if df_market_cleaned is not None and not df_market_cleaned.empty:
            genre_pivot, hist_genre_sum_text_detailed, subject_pub_counts = analyze_genre_trends_by_decade(df_market_cleaned.copy())
            if hist_genre_sum_text_detailed: hist_genre_pub_summary_text = hist_genre_sum_text_detailed 
            if genre_pivot is not None: 
                # Pass book_specific_output_dir to plotting functions
                genre_trends_plot_filename = plot_genre_trends(genre_pivot, user_book['title'], output_dir=book_specific_output_dir)
            if subject_pub_counts is not None and not subject_pub_counts.empty:
                subject_dist_pub_plot_filename = plot_subject_distribution(subject_pub_counts, user_book['title'], output_dir=book_specific_output_dir, plot_type="publication")
            
            authors_df_pub_table, _ = analyze_prolific_authors(df_market_cleaned.copy())
            if authors_df_pub_table is not None:
                 plot_top_authors(authors_df_pub_table, user_book['title'], output_dir=book_specific_output_dir, plot_type="publication")

            pg_dl_sum_text_detailed, _, _ = analyze_download_activity(df_market_cleaned.copy()) # Don't need DFs here
            if pg_dl_sum_text_detailed: pg_download_activity_summary_text = pg_dl_sum_text_detailed
            
            # Pass full paths or ensure summarize_historical... knows the dir for Markdown links
            brief_overall_context_summary_for_appendix = summarize_historical_and_pg_download_context_md(
                hist_genre_pub_summary_text, pg_download_activity_summary_text,
                # Pass only filenames, links will be relative to the MD file location
                genre_plot_filename=os.path.basename(genre_trends_plot_filename) if genre_trends_plot_filename else None,
                subject_dist_plot_filename=os.path.basename(subject_dist_pub_plot_filename) if subject_dist_pub_plot_filename else None
            )
            appendix_md_lines.append("### Brief Overview of Historical Literary Context & PG Download Insights\n")
            appendix_md_lines.append(brief_overall_context_summary_for_appendix)
        else: appendix_md_lines.append("Historical market data cleaning failed; context limited.\n")
    else: appendix_md_lines.append("Historical market data could not be fetched; context limited.\n")
    appendix_md_lines.append("\n")

    print("\nStep 2: Generating Targeted Reader Personas for Your Book...")
    report_md_lines.append("## III. Targeted Reader Personas for Your Book\n")
    context_for_persona_ai = brief_overall_context_summary_for_appendix if 'brief_overall_context_summary_for_appendix' in locals() and \
                             "not available" not in brief_overall_context_summary_for_appendix.lower() else \
                             (hist_genre_pub_summary_text + "\n" + pg_download_activity_summary_text)
    num_personas_to_gen = user_book.get("num_personas_to_generate", 3)
    targeted_persona_text_blocks = generate_targeted_personas_md(user_book, context_for_persona_ai, num_personas=num_personas_to_gen)
    
    if targeted_persona_text_blocks:
        for i, persona_block in enumerate(targeted_persona_text_blocks):
            persona_name_match = re.search(r"\*\*Persona Name:\*\*\s*(.*)", persona_block, re.IGNORECASE)
            persona_heading_name = persona_name_match.group(1).strip() if persona_name_match else f"Persona {i+1}"
            report_md_lines.append(f"### {persona_heading_name}\n")
            report_md_lines.append(persona_block + "\n\n")
    else: report_md_lines.append("Could not generate targeted personas.\n")

    all_interest_levels_for_plot = [] 
    aggregated_persona_feedback_for_gtm_and_reco = ["Persona Interest Summaries:"]
    
    if targeted_persona_text_blocks : 
        print("\nStep 3: Gauging Persona Interest in Your Book (with Context)...")
        report_md_lines.append("## IV. Persona Interest in Your Book (Contextualized)\n")
        
        for i, persona_full_text_block in enumerate(targeted_persona_text_blocks):
            persona_direct_feedback, analysts_note, parsed_level = gauge_persona_interest_md(
                user_book, persona_full_text_block, 
                hist_genre_pub_summary_text, pg_download_activity_summary_text )
            
            persona_name_match = re.search(r"\*\*Persona Name:\*\*\s*(.*)", persona_full_text_block, re.IGNORECASE)
            current_persona_name_for_heading = persona_name_match.group(1).strip() if persona_name_match else f"Persona {i+1}"

            report_md_lines.append(f"### Feedback from: {current_persona_name_for_heading}\n")
            report_md_lines.append("#### Persona's Direct Thoughts\n")
            report_md_lines.append(persona_direct_feedback + "\n")
            report_md_lines.append("#### Analyst's Note on Context\n")
            report_md_lines.append(analysts_note + "\n\n")
            
            key_factor_match = re.search(r"\*\*Key Factor for Interest:\*\*(.*)", persona_direct_feedback, re.IGNORECASE | re.DOTALL)
            key_factor_text = key_factor_match.group(1).strip() if key_factor_match else "See full feedback."

            aggregated_persona_feedback_for_gtm_and_reco.append(
                f"- {current_persona_name_for_heading}: Interest Level '{parsed_level}'. Key Factor: {key_factor_text.splitlines()[0]}" # First line of key factor
            )
            if parsed_level != "Unknown": all_interest_levels_for_plot.append(parsed_level)
    else:
        report_md_lines.append("Skipping detailed persona interest gauging (no personas generated).\n")
        aggregated_persona_feedback_for_gtm_and_reco.append("No persona feedback generated.")

    persona_interest_plot_filename = None
    if all_interest_levels_for_plot:
        # Pass book_specific_output_dir
        persona_interest_plot_filename = plot_persona_interest_summary(all_interest_levels_for_plot, user_book['title'], output_dir=book_specific_output_dir)
        if persona_interest_plot_filename:
            try: 
                idx_interest_header = report_md_lines.index("## IV. Persona Interest in Your Book (Contextualized)\n")
                # Link relative to the MD file in the same folder
                report_md_lines.insert(idx_interest_header + 1, f"\n_(Aggregated interest levels - [view plot]({os.path.basename(persona_interest_plot_filename)}))_\n\n")
            except ValueError: 
                report_md_lines.append(f"\n_(Aggregated interest levels - [view plot]({os.path.basename(persona_interest_plot_filename)}))_\n\n")

    print("\nStep 4: Generating Go-To-Market Strategy for Your Book...")
    report_md_lines.append("## V. Go-To-Market Strategy Suggestions\n")
    gtm_strategy_text = generate_gtm_strategy_md(user_book, "\n".join(aggregated_persona_feedback_for_gtm_and_reco), 
                                                 hist_genre_pub_summary_text, pg_download_activity_summary_text)
    report_md_lines.append(gtm_strategy_text + "\n\n")

    print("\nStep 5: Generating Overall Recommendation...")
    gtm_highlights_for_reco = "GTM strategy outlined."
    if "Error" in gtm_strategy_text or "Could not generate" in gtm_strategy_text or not gtm_strategy_text.strip():
        gtm_highlights_for_reco = "GTM strategy generation was inconclusive or faced issues."
    elif gtm_strategy_text:
        match_positioning = re.search(r"\*\*Overall Market Positioning:\*\*\s*(.*)", gtm_strategy_text, re.IGNORECASE)
        if match_positioning: gtm_highlights_for_reco = f"Key GTM Insight - Market Positioning: {match_positioning.group(1).strip()[:150]}..."
            
    overall_recommendation_text = generate_overall_recommendation_md(user_book, "\n".join(aggregated_persona_feedback_for_gtm_and_reco), gtm_highlights_for_reco)
    actual_recommendation_section_md = f"## II. Overall Recommendation & Justification\n{overall_recommendation_text}\n\n"
    report_md_lines[recommendation_placeholder_index] = actual_recommendation_section_md

    report_md_lines.extend(appendix_md_lines)

    print("\nStep 6: Finalizing Report...")
    final_markdown_report_str = "".join(report_md_lines)
    
    print("\n\n--- Executive Summary & Recommendation (from Report) ---")
    print(overall_recommendation_text if overall_recommendation_text else "Recommendation could not be generated.")
    print("\n--- Aggregated Persona Interest ---")
    print("\n".join(aggregated_persona_feedback_for_gtm_and_reco))

    # Save Markdown report inside the book-specific folder
    output_md_filename = os.path.join(book_specific_output_dir, f"book_analysis_report_{clean_title_for_report_filename}.md")
    try:
        with open(output_md_filename, "w", encoding="utf-8") as f: f.write(final_markdown_report_str)
        print(f"\n--- Analysis Complete for '{user_book['title']}' ---")
        print(f"Markdown report saved to: {output_md_filename}")
        print(f"Plots saved in '{book_specific_output_dir}' directory.") # Updated path
    except Exception as e: print(f"Error saving Markdown report: {e}")

if __name__ == "__main__":
    main()