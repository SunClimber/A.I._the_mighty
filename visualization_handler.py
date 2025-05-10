# visualization_handler.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from collections import Counter

SCRIPT_DIR_VH = os.path.dirname(os.path.abspath(__file__))

# --- plot_genre_trends, plot_top_authors (publication based), plot_subject_distribution (publication based), plot_persona_interest_summary
# --- remain the same as the last good "Markdown-focused" version.
# --- I will add the new plot functions below them.

# (Paste your existing good versions of plot_genre_trends, plot_top_authors (by publication), 
#  plot_subject_distribution (by publication), and plot_persona_interest_summary here)

def plot_genre_trends(pivot_trends_df, user_book_title, output_dir="output"):
    if pivot_trends_df is None or pivot_trends_df.empty:
        print("  No market data pivot table to plot for historical genre publication trends.")
        return None
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=pivot_trends_df, dashes=False, markers='o', linewidth=2)
    plt.title(f'Historical Genre Publication Popularity (Author Birth Decades)\nContext for "{user_book_title[:30]}"', fontsize=14)
    plt.xlabel('Decade (Author Birth Year Proxy)', fontsize=12)
    plt.ylabel('Number of Books Published', fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.legend(title='Subject', bbox_to_anchor=(1.03, 1), loc='upper left', frameon=True, shadow=True)
    plt.tight_layout(rect=[0, 0, 0.85, 1]) 
    plt.grid(True, linestyle=':', alpha=0.6)
    
    os.makedirs(output_dir, exist_ok=True)
    clean_title_for_path = "".join(c if c.isalnum() else "_" for c in user_book_title)[:20]
    plot_filename = f"hist_genre_pub_trends_for_{clean_title_for_path}.png" # Clarified filename
    full_output_path = os.path.join(output_dir, plot_filename)
    try:
        plt.savefig(full_output_path, dpi=150)
        print(f"  Historical genre publication trends plot saved to {full_output_path}")
        plt.close(); return plot_filename
    except Exception as e:
        print(f"  Error saving historical genre publication trends plot: {e}"); plt.close(); return None

def plot_top_authors(top_authors_df, user_book_title, output_dir="output", top_n=7, plot_type="publication"):
    """Plots top authors by publication volume OR download count."""
    if top_authors_df is None or top_authors_df.empty:
        print(f"  No top authors data to plot for type: {plot_type}.")
        return None
    
    count_col = 'book_count' if plot_type == "publication" else 'download_count'
    if count_col not in top_authors_df.columns:
        print(f"  Count column '{count_col}' not found in DataFrame for plot_top_authors ({plot_type}).")
        return None

    top_authors_df_plot = top_authors_df.sort_values(by=count_col, ascending=False).head(top_n)
    if top_authors_df_plot.empty:
        print(f"  Not enough author data to plot for top authors ({plot_type})."); return None

    plt.figure(figsize=(10, max(5, len(top_authors_df_plot) * 0.7))) 
    sns.barplot(x=count_col, y='name' if 'name' in top_authors_df_plot.columns else 'individual_author', 
                data=top_authors_df_plot, palette="viridis_r" if plot_type=="publication" else "mako_r", dodge=False) 
    title_prefix = "Prolific Authors by Historical Publication Volume" if plot_type == "publication" else "Top Authors by PG Download Activity"
    plt.title(f'{title_prefix}\nContext for "{user_book_title[:30]}"', fontsize=14)
    plt.xlabel('Number of Books' if plot_type == "publication" else "Total PG Downloads", fontsize=12)
    plt.ylabel('Author', fontsize=12); plt.yticks(fontsize=10); plt.xticks(fontsize=10)
    plt.tight_layout(); plt.grid(axis='x', linestyle=':', alpha=0.6)

    os.makedirs(output_dir, exist_ok=True)
    clean_title_for_path = "".join(c if c.isalnum() else "_" for c in user_book_title)[:20]
    plot_filename = f"top_authors_by_{plot_type}_for_{clean_title_for_path}.png"
    full_output_path = os.path.join(output_dir, plot_filename)
    try:
        plt.savefig(full_output_path, dpi=150); print(f"  Top authors by {plot_type} plot saved to {full_output_path}")
        plt.close(); return plot_filename
    except Exception as e:
        print(f"  Error saving top authors by {plot_type} plot: {e}"); plt.close(); return None

def plot_subject_distribution(subject_counts_series, user_book_title, top_n=7, output_dir="output", plot_type="publication"):
    """Plots subject distribution by publication volume OR download count."""
    if subject_counts_series is None or subject_counts_series.empty:
        print(f"  No subject distribution data to plot for type: {plot_type}.")
        return None

    top_subjects = subject_counts_series.nlargest(top_n)
    if len(subject_counts_series) > top_n:
        others_count = subject_counts_series.iloc[top_n:].sum()
        if others_count > 0.01 * subject_counts_series.sum() and others_count > 1: top_subjects['Others'] = others_count
    if top_subjects.empty: print(f"  No data in top_subjects to plot for distribution ({plot_type})."); return None

    plt.figure(figsize=(9, 9)); colors = plt.cm.Spectral(range(len(top_subjects)))
    patches, texts, autotexts = plt.pie(
        top_subjects.values, labels=None, autopct='%1.1f%%', startangle=90,
        wedgeprops={"edgecolor":"white", 'linewidth': 0.7}, pctdistance=0.80, colors=colors)
    for autotext in autotexts: autotext.set_color('black'); autotext.set_fontsize(9)
    
    title_prefix = "Historical Subject Distribution by Publication Volume" if plot_type == "publication" else "Top Subjects by PG Download Activity"
    plt.title(f'{title_prefix}\nContext for "{user_book_title[:30]}"', fontsize=14)
    plt.axis('equal'); legend_labels = [f'{label} ({int(top_subjects[label])})' for label in top_subjects.index]
    plt.legend(patches, legend_labels, loc="center left", bbox_to_anchor=(1.05, 0.5), fontsize=10, frameon=False)
    plt.tight_layout(rect=[0, 0, 0.78, 1])

    os.makedirs(output_dir, exist_ok=True)
    clean_title_for_path = "".join(c if c.isalnum() else "_" for c in user_book_title)[:20]
    plot_filename = f"subject_dist_by_{plot_type}_for_{clean_title_for_path}.png"
    full_output_path = os.path.join(output_dir, plot_filename)
    try:
        plt.savefig(full_output_path, dpi=150); print(f"  Subject distribution by {plot_type} plot saved to {full_output_path}")
        plt.close(); return plot_filename
    except Exception as e:
        print(f"  Error saving subject distribution by {plot_type} plot: {e}"); plt.close(); return None

def plot_persona_interest_summary(interest_levels_list, user_book_title, output_dir="output"):
    if not interest_levels_list: print("  No interest levels to plot for persona summary."); return None
    counts = Counter(interest_levels_list)
    defined_levels = ["High", "Medium", "Low", "Not Interested", "Unknown"]
    levels_to_plot = [level for level in defined_levels if level in counts] 
    values_to_plot = [counts[level] for level in levels_to_plot]
    if not levels_to_plot: print("  No valid interest level data for plotting summary."); return None

    plt.figure(figsize=(8, 6))
    color_map = {"High": "#4CAF50", "Medium": "#FFC107", "Low": "#FF9800", "Not Interested": "#F44336", "Unknown": "#9E9E9E"}
    bar_colors = [color_map.get(level, "#BDBDBD") for level in levels_to_plot]
    bars = plt.bar(levels_to_plot, values_to_plot, color=bar_colors, edgecolor='dimgrey', linewidth=0.7)
    plt.title(f"Persona Interest Summary for '{user_book_title[:30]}...'", fontsize=14)
    plt.xlabel("Interest Level", fontsize=12); plt.ylabel("Number of Personas", fontsize=12)
    max_val = 0; 
    if values_to_plot: max_val = max(values_to_plot)
    plt.yticks(range(0, max_val + 2, 1 if max_val < 10 else (max_val // 5 if max_val // 5 > 0 else 1) ))
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    for bar in bars:
        yval = bar.get_height()
        if yval > 0: plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, int(yval), ha='center', va='bottom', fontsize=10, color='dimgray')
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    clean_title_for_path = "".join(c if c.isalnum() else "_" for c in user_book_title)[:20]
    plot_filename = f"persona_interest_summary_for_{clean_title_for_path}.png"
    full_output_path = os.path.join(output_dir, plot_filename)
    try:
        plt.savefig(full_output_path, dpi=150); print(f"  Persona interest summary plot saved to {full_output_path}")
        plt.close(); return plot_filename
    except Exception as e:
        print(f"  Error saving persona interest plot: {e}"); plt.close(); return None

# (Keep your __main__ test block here for isolated testing of plotting functions)