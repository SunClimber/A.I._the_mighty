# Project Title: AI-Powered Book Vetting & Market Strategy Assistant 
**(Choose a catchy and descriptive title for your project)**

**Course:** Generative AI for Business and Data Analysis
**Author:** Sam Reynebeau
**Date:** 05/10/2025

**Go to step 6 for instructions to run project**

## 1. Overview & Goal

This project implements a Generative AI–driven solution to assist a hypothetical publishing company in vetting new book proposals. The primary goal is to analyze a user-submitted book concept against a backdrop of historical literary trends and inferred enduring reader preferences (derived from Project Gutenberg data) to:

1.  Generate targeted reader personas for the proposed book.
2.  Gauge the potential interest of these personas in the specific book.
3.  Suggest a preliminary go-to-market strategy.
4.  Provide an overall recommendation on whether the company should pursue the book.

The solution aims to offer data-informed insights beyond simple intuition, leveraging AI for qualitative generation and analysis.

## 2. The Data-Centric Problem Addressed

Publishing companies constantly face the challenge of evaluating new manuscripts and book ideas. This involves significant risk and investment. Key questions include:
*   Who is the target audience for this book?
*   How might different reader segments react to it?
*   How does it fit within broader (albeit historical, in this project's context) literary patterns or currently resonating classic themes?
*   What are effective ways to market it?
*   Is it a worthwhile investment?

This project addresses this by providing a structured, AI-assisted workflow to tackle these data-related questions, offering a preliminary assessment to guide decision-making.

## 3. Use of Generative AI & Value Add

This project incorporates a Large Language Model (LLM - Google's Gemini 1.5 Flash via API) in several key stages, adding genuine value beyond what a simple chat session could provide:

1.  **Targeted Persona Generation:** The AI creates distinct reader personas tailored specifically to the *user's input book type* (title, subjects, synopsis, author age). This is informed by the user's book details and optionally by a brief, AI-generated summary of historical literary context and inferred enduring preferences from Project Gutenberg download activity.
    *   *Value:* Moves beyond generic personas by grounding them in the specifics of the book being vetted and a broader (historical) literary context.
2.  **Contextualized Interest Gauging:** The AI, embodying each targeted persona, evaluates the user's specific book. Crucially, it's prompted to provide not only its direct interest but also an "Analyst's Note" (still AI-generated, but in a third-person analytical voice) reflecting on how the persona's interest relates to/contrasts with both historical publication patterns and enduring classic preferences inferred from PG downloads.
    *   *Value:* Provides a multi-layered assessment, simulating how a target reader might react both intrinsically and in relation to broader (historical) literary currents.
3.  **Strategic Brainstorming (Go-To-Market & Recommendation):** The AI synthesizes the user's book details, persona feedback (which includes contextual reflections), and context summaries to suggest GTM strategy points and, most importantly, an overall recommendation on pursuing the book.
    *   *Value:* Offers creative and context-aware strategic starting points that are directly tied to the preceding analysis, rather than generic advice.

The system's value lies in its **structured workflow**, the **integration of multiple AI generation steps contingent on prior analysis and user input**, and the **generation of nuanced, context-aware outputs** that would require significant manual effort or multiple, carefully guided LLM interactions to replicate.

## 4. Key Features & Workflow

The program follows this general workflow:

1.  **User Input:** Prompts the user for details about the book to be vetted (title, author, subjects, synopsis, publication year, page count, author age, desired number of personas).
2.  **Contextual Analysis (Python-driven):**
    *   Fetches metadata for a sample of ~500 classic books from the Gutendex API (Project Gutenberg data).
    *   Analyzes this data to identify:
        *   Historical publication trends by genre (based on author birth decades as a proxy).
        *   Historically prolific authors (by publication volume).
        *   Inferred enduring reader preferences for classic genres/authors (based on recent Project Gutenberg download counts).
    *   These analyses produce detailed textual summaries and data for plots.
3.  **AI-Powered Brief Context Summary:** An AI call summarizes the detailed historical and PG download analyses into a brief, conversational overview for the report's appendix and as light context for persona generation.
4.  **AI - Targeted Persona Generation:** Generates reader personas specifically for the user's book type.
5.  **AI - Persona Interest Gauging & Analyst's Note:** Each persona "evaluates" the user's book, providing direct feedback. The AI then adds an "Analyst's Note" contextualizing this feedback against historical trends and PG download insights.
6.  **AI - Go-To-Market Strategy:** Suggests marketing strategies based on all preceding information.
7.  **AI - Overall Recommendation:** Provides a final recommendation on whether to pursue the book.
8.  **Output:**
    *   A detailed **Markdown (.md) report** is generated in a book-specific subfolder within `output/`. This report includes all user inputs, AI-generated content (personas, interest feedback, analyst's notes, GTM, recommendation), and the AI-generated brief summary of historical/PG context.
    *   Several **PNG plot files** are saved to the same subfolder, visualizing historical trends and persona interest. These are referenced in the Markdown report.

## 5. Data Sources

*   **Primary User Input:** Details of the book to be vetted, provided by the user via command-line prompts.
*   **Contextual Data:** Metadata for classic literature fetched from the **Gutendex API** ([http://gutendex.com/](http://gutendex.com/)), which mirrors Project Gutenberg. This includes titles, authors, subjects, author birth/death years, and recent download counts.
    *   *Note:* The "historical market trends" are derived from this public domain corpus and reflect patterns in classic literature, not contemporary commercial book sales. Download counts reflect activity on the Project Gutenberg platform.


## 6. How to Run the Project

### a. Prerequisites

*   Python 3.9+
*   `pip` (Python package installer)

### b. Setup & Dependencies

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone https://github.com/SunClimber/A.I._the_mighty.git
    cd into A.I._the_mighty folder
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    The `requirements.txt` file should include:
    ```
    pandas
    requests
    matplotlib
    seaborn
    python-dotenv
    google-generativeai
    tabulate # For df.to_markdown()
    # openpyxl (if you ever re-enable Excel output)
    ```
3.  **Set up API Key:**
    *   Create a `.env` file in the root of the project directory (e.g., alongside `main.py`).
    *   Add your Google Generative AI API key to it:
        ```env
        API_KEY = "YOUR_API_KEY_HERE"
        ```
    *   If needed, obtain your API key from [Google AI Studio](https://aistudio.google.com/).

### c. Execution

1.  Navigate to the project's root directory in your terminal (A.I._the_mighty).
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  The program will then prompt you to enter details for the book you wish to vet. Follow the on-screen instructions.

### d. Output

*   Upon completion, a new subfolder will be created inside the `output/` directory. The subfolder will be named based on the title of the book you analyzed (e.g., `output/Your_Book_Title_Analysis/`).
*   This subfolder will contain:
    *   A `book_analysis_report_[Your_Book_Title].md` Markdown file with the complete analysis.
    *   Several `.png` image files for the generated plots (e.g., historical trends, persona interest summary). These are linked within the Markdown report.

You can view the Markdown file using any Markdown viewer (e.g., VS Code preview, Typora, online viewers) or convert it to PDF using tools like Pandoc.