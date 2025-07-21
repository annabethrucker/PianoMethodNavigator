import pandas as pd

# Load your data once at the top
df = pd.read_excel("pmn_master july 15 2025.xlsx")

def extract_category(concept_name):
    if ':' in concept_name:
        category = concept_name.split(':')[0].strip()
        category = category.capitalize()
        return category
    return 'Other'

def get_concept_tags(row, show_intro_type=False):
    intro_type = str(row.get('Intro Type', '')).lower()
    review_status = str(row.get('Review Status', '')).lower()
    tags = []
    if show_intro_type:
        intro_tag = 'formal' if intro_type == 'formal' else 'informal'
        tags.append(intro_tag)
    review_tag = 'review' if review_status == 'review' else 'first-time'
    tags.append(review_tag)
    return f"({', '.join(tags)})"

def get_concept_display_name(concept_name):
    if ':' in concept_name:
        return concept_name.split(':', 1)[1].strip()
    return concept_name.strip()

def render_knows_by_book(current_concepts, series):
    dark_brown = '#291909'
    style_quicksand = "font-family: 'Quicksand', sans-serif;"
    html = ""
    if not current_concepts.empty:
        for book_order in sorted(current_concepts['Book Order'].unique()):
            book_concepts = current_concepts[current_concepts['Book Order'] == book_order]
            book_title = book_concepts['Book Title'].iloc[0]
            html += f'<h4 style="margin: 15px 0 5px 0; color: {dark_brown}; font-family: Poller One, cursive;">{series} - {book_title}:</h4>'
            for category in sorted(book_concepts['Category'].unique()):
                cat_concepts = book_concepts[book_concepts['Category'] == category]
                html += f'<div style="margin-left: 20px; margin-bottom: 10px; {style_quicksand}"><strong>{category}:</strong> '
                concept_list = []
                for _, row in cat_concepts.iterrows():
                    concept_name = get_concept_display_name(row['Concept'])
                    intro_type = str(row.get('Intro Type', '')).lower()
                    if intro_type == 'formal':
                        concept_list.append(f'<span style="color: {dark_brown};">{concept_name}</span>')
                    else:
                        concept_list.append(f'<span style="color: #666; font-style: italic;">{concept_name} (informal)</span>')
                html += ", ".join(concept_list)
                html += "</div>"
    else:
        html += f"<p style='color: #666; {style_quicksand}'>No concepts found up to this point.</p>"
    return html

def render_knows_by_category(current_concepts):
    dark_brown = '#291909'
    style_quicksand = "font-family: 'Quicksand', sans-serif;"
    html = ""
    if not current_concepts.empty:
        for category in sorted(current_concepts['Category'].unique()):
            cat_concepts = current_concepts[current_concepts['Category'] == category]
            html += f'<div style="margin-bottom: 10px; {style_quicksand}"><strong>{category}:</strong> '
            concept_list = []
            for _, row in cat_concepts.iterrows():
                concept_name = get_concept_display_name(row['Concept'])
                intro_type = str(row.get('Intro Type', '')).lower()
                if intro_type == 'formal':
                    concept_list.append(f'<span style="color: {dark_brown};">{concept_name}</span>')
                else:
                    concept_list.append(f'<span style="color: #666; font-style: italic;">{concept_name} (informal)</span>')
            html += ", ".join(concept_list)
            html += "</div>"
    else:
        html += f"<p style='color: #666; {style_quicksand}'>No concepts found up to this point.</p>"
    return html

def generate_lesson_plan(series, book_order, page):
    # Color palette
    olive = '#84894a'
    cream = '#F2E0B5'
    dark_brown = '#291909'
    off_white = '#FFFDF9'
    accent = '#63372C'
    cream_light = '#FFFDF9'
    olive_light = '#bfc28a'
    cream_dark = '#e5d3a2'
    style_quicksand = "font-family: 'Quicksand', sans-serif;"
    style_poller = "font-family: 'Poller One', cursive;"

    # Data prep
    df_clean = df.copy()
    df_clean['Category'] = df_clean['Concept'].apply(extract_category)
    if 'Weight' not in df_clean.columns:
        df_clean['Weight'] = 0.25
    if 'Review Status' not in df_clean.columns:
        df_clean['Review Status'] = 'first-time'

    # Find the correct book title
    try:
        current_book_title = df_clean[
            (df_clean['Series'] == series) & (df_clean['Book Order'] == int(book_order))
        ]['Book Title'].iloc[0]
    except IndexError:
        return "<div>Invalid book selection.</div>"

    # Find the correct page column
    if 'Page' in df_clean.columns:
        page_col = 'Page'
    else:
        return "<div>Error: No page column found!</div>"

    # Convert page to numeric for filtering
    df_clean_numeric = df_clean.copy()
    df_clean_numeric['page_numeric'] = pd.to_numeric(df_clean_numeric[page_col], errors='coerce')

    # Get concepts up to and including this page
    current_concepts = df_clean_numeric[
        (df_clean_numeric['Series'] == series) & (
            (df_clean_numeric['Book Order'] < int(book_order)) |
            ((df_clean_numeric['Book Order'] == int(book_order)) & (df_clean_numeric['page_numeric'] <= int(page)))
        )
    ].copy()

    # Concepts on this page
    current_page_concepts = df_clean_numeric[
        (df_clean_numeric['Series'] == series) &
        (df_clean_numeric['Book Order'] == int(book_order)) &
        (df_clean_numeric['page_numeric'] == int(page))
    ].copy()

    # Recently learned concepts (last 5 before this page)
    recent_concepts = df_clean_numeric[
        (df_clean_numeric['Series'] == series) &
        (df_clean_numeric['Book Order'] == int(book_order)) &
        (df_clean_numeric['page_numeric'] < int(page))
    ].copy()
    recent_concepts = recent_concepts.sort_values('page_numeric', ascending=False).head(5)

    # --- What's Next: Next 4 pages with concepts, 2x2 grid, add next book block if end reached ---
    after_current = df_clean_numeric[
        (df_clean_numeric['Series'] == series) &
        (df_clean_numeric['Book Order'] == int(book_order)) &
        (df_clean_numeric['page_numeric'] > int(page))
    ]
    pages_with_concepts = after_current[page_col].drop_duplicates().sort_values().tolist()
    next4_pages = pages_with_concepts[:4]
    whats_next_by_page = []
    for p in next4_pages:
        page_concepts = after_current[after_current[page_col] == p]
        whats_next_by_page.append((p, page_concepts))
    more_pages_exist = len(pages_with_concepts) > 4
    # If not more pages exist, add next book block if there is a next book
    next_book_block = None
    if not more_pages_exist:
        next_book_order = int(book_order) + 1
        next_book_data = df_clean_numeric[
            (df_clean_numeric['Series'] == series) &
            (df_clean_numeric['Book Order'] == next_book_order)
        ]
        if not next_book_data.empty:
            next_book_title = next_book_data['Book Title'].iloc[0]
            next_book_pages = next_book_data[next_book_data['Concept'].notna() & (next_book_data['Concept'] != '')][page_col].drop_duplicates().sort_values().tolist()
            first3_pages = next_book_pages[:3]
            concepts_with_pages = []
            for p in first3_pages:
                page_concepts = next_book_data[next_book_data[page_col] == p]
                for _, row in page_concepts.iterrows():
                    concept_name = get_concept_display_name(row['Concept'])
                    tags = get_concept_tags(row, show_intro_type=True)
                    concepts_with_pages.append((p, concept_name, tags))
            next_book_block = {
                'title': next_book_title,
                'concepts': concepts_with_pages
            }
    if next_book_block and len(whats_next_by_page) < 4:
        whats_next_by_page.append(('next_book', next_book_block))

    # --- HTML Output ---
    html_output = ""

    # Card 1: Review Concepts
    html_output += f"""
    <div style=\"margin-bottom: 20px;\">
        <div style=\"background-color: {cream}; padding: 15px; border-radius: 8px; border-left: 4px solid {olive};\">
            <h3 style=\"margin: 0 0 10px 0; color: {olive}; font-family: 'Poller One', cursive;\">Review Concepts</h3>
            <span class=\"subtitle-italic\">The most recent concepts your student has learned.</span>
        </div>
    </div>
    <div style=\"margin-bottom: 20px;\"></div>
    """
    if not recent_concepts.empty:
        for _, row in recent_concepts.iterrows():
            concept_name = get_concept_display_name(row['Concept'])
            page_num = row[page_col]
            html_output += f'<div style="margin-left: 20px; margin-bottom: 5px; font-family: Quicksand, sans-serif;"><span style="color: {dark_brown};">P.{page_num} - {concept_name}</span></div>'
    else:
        html_output += f"<p style='color: #666; font-family: Quicksand, sans-serif;'>No recent concepts found.</p>"
    html_output += "</div>"

    # Card 2: New Concepts on This Page
    html_output += f"""
    <div style=\"margin-bottom: 20px;\">
        <div class='pmn-new-concepts-card'>
            <h3 style=\"font-family: 'Poller One', cursive; color: #FFFDF9;\">New Concepts on This Page</h3>
    """
    if not current_page_concepts.empty:
        for _, row in current_page_concepts.iterrows():
            concept_name = get_concept_display_name(row['Concept'])
            tags = get_concept_tags(row, show_intro_type=False)
            html_output += f'<div style="margin-left: 20px; margin-bottom: 5px;"><span>{concept_name}</span> {tags}</div>'
    else:
        html_output += f"<p style='color: #FFFDF9; font-family: Quicksand, sans-serif;'>No concepts introduced on this page!</p>"
    html_output += "</div>"

    # Card 3: What's Next (Concepts Coming Up Next)
    html_output += f"""
    <div style=\"margin-bottom: 20px;\">
        <div style=\"background-color: {cream}; padding: 15px; border-radius: 8px; border-left: 4px solid {olive}; width: 100%; box-sizing: border-box;\">
            <h3 style=\"margin: 0 0 10px 0; color: {olive}; font-family: 'Poller One', cursive;\">Concepts Coming Up Next</h3>
    """
    if whats_next_by_page:
        html_output += f'<div class="pmn-whats-next-pages" style="width: 100%; box-sizing: border-box;">'
        for idx in range(4):
            if idx < len(whats_next_by_page):
                p, page_concepts = whats_next_by_page[idx]
                if p == 'next_book':
                    html_output += f'<div style="min-width: 0; max-width: 100%; background: #84894A; border-radius: 6px; padding: 10px; min-height: 80px; box-sizing: border-box;">'
                    html_output += f'<div class="pmn-end-of-book-msg" style="font-family: Poller One, cursive; font-size: 1.1em; margin-bottom: 8px; color: #FFFDF9;">You&#39;ve reached the end of this book!<br><br>Next Book: {page_concepts["title"]}</div>'
                    for page_num, concept, tags in page_concepts['concepts']:
                        html_output += f'<div style="color: #FFFDF9; font-family: Quicksand, sans-serif; margin-bottom: 3px;">P.{page_num} - {concept} {tags}</div>'
                    html_output += f'<div style="margin-top: 10px; font-size: 0.95em; font-family: Quicksand, sans-serif; color: #FFFDF9;"><em>For transition options to other series, visit the <a href="https://treefrogsolutions.co/transition-guide-piano-method-navigator/" target="_blank" style="color: #FFFDF9; text-decoration: underline;">Piano Method Navigator Transition Guide</a>.</em></div>'
                    html_output += '</div>'
                else:
                    html_output += f'<div style="min-width: 0; max-width: 100%; background: {off_white}; border-radius: 6px; padding: 10px; min-height: 80px; box-sizing: border-box;">'
                    html_output += f'<div style="font-family: Poller One, cursive; color: {olive}; font-size: 1.1em; margin-bottom: 8px;">Page {p}</div>'
                    for _, row in page_concepts.iterrows():
                        concept_name = get_concept_display_name(row['Concept'])
                        tags = get_concept_tags(row, show_intro_type=True)
                        html_output += f'<div style="color: {dark_brown}; font-family: Quicksand, sans-serif; margin-bottom: 3px;">{concept_name} {tags}</div>'
                    html_output += '</div>'
            else:
                html_output += f'<div style="min-width: 0; max-width: 100%; background: transparent; border: none;"></div>'
        html_output += '</div>'
    else:
        html_output += f'<div style="margin-left: 20px; margin-bottom: 5px; color: #666; font-family: Quicksand, sans-serif;">No concepts left in this book.</div>'
    html_output += "</div></div>"

    # Card 4: Progress Overview (Concepts Your Student Knows)
    # --- Tabbed view: By Book and By Entire Category ---
    by_book_html = render_knows_by_book(current_concepts, series)
    by_cat_html = render_knows_by_category(current_concepts)
    html_output += f'''
    <div style="margin-bottom: 20px;">
        <div style="background-color: {off_white}; padding: 15px; border-radius: 8px; border-left: 4px solid {dark_brown};">
            <h3 style="margin: 0 0 10px 0; color: {dark_brown}; font-family: 'Poller One', cursive;">Progress Overview</h3>
            <span class="subtitle-italic">All concepts your student has learned in this series up to the current page.</span>
            <div style="margin-bottom: 10px;"></div>
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <button id="tab-by-book" class="tab-btn" onclick="showTab('by-book')">By Book</button>
                <button id="tab-by-category" class="tab-btn" onclick="showTab('by-category')">By Entire Category</button>
            </div>
            <div id="tab-content-by-book" class="tab-content">{by_book_html}</div>
            <div id="tab-content-by-category" class="tab-content" style="display:none;">{by_cat_html}</div>
        </div>
    </div>
    '''

    return html_output
