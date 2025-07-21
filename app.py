from flask import Flask, request, render_template_string
from lesson_planner import generate_lesson_plan
import pandas as pd

app = Flask(__name__)

df = pd.read_excel("pmn_master july 15 2025.xlsx")
series_options = sorted(df['Series'].unique())
# Build book options as list of (book_title, book_order) tuples for each series
book_options = {
    s: [(row['Book Title'], row['Book Order']) for _, row in df[df['Series'] == s][['Book Title', 'Book Order']].drop_duplicates().sort_values('Book Order').iterrows()]
    for s in series_options
}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    selected_series = series_options[0]
    selected_book = book_options[selected_series][0][1]
    selected_book_title = book_options[selected_series][0][0]
    selected_page = 1
    if request.method == 'POST':
        selected_series = request.form['series']
        selected_book = int(request.form['book'])
        selected_book_title = next((title for title, order in book_options[selected_series] if order == selected_book), book_options[selected_series][0][0])
        page_value = request.form['page']
        if not page_value or not page_value.isdigit():
            pages_for_book = sorted(df[(df['Series'] == selected_series) & (df['Book Order'] == selected_book)]['Page'].unique())
            selected_page = pages_for_book[0] if pages_for_book else 1
        else:
            selected_page = int(page_value)
        result = generate_lesson_plan(selected_series, selected_book, selected_page)
    else:
        selected_book_title = book_options[selected_series][0][0]
    # Get all unique pages for the selected book, as integers (all pages from min to max)
    book_pages = df[(df['Series'] == selected_series) & (df['Book Order'] == selected_book)]['Page']
    book_pages_int = [int(p) for p in book_pages if str(p).isdigit()]
    if book_pages_int:
        min_page = min(book_pages_int)
        max_page = max(book_pages_int)
        pages_for_book = list(range(min_page, max_page + 1))
    else:
        pages_for_book = [1]
    return render_template_string('''
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Poller+One&family=Quicksand:wght@400;700&display=swap" rel="stylesheet">
        <style>
        .selector-area-bg {
            background: url('https://treefrogsolutions.co/wp-content/uploads/2025/07/Piano-Method-Navigator-Header-6.png') center center / cover no-repeat;
            padding: 30px 0 40px 0;
            border-radius: 12px;
            margin-bottom: 20px;
            width: 100%;
        }
        .widget-title {
            font-family: 'Poller One', cursive;
            font-size: 2.1em;
            text-align: center;
            color: #291909;
            letter-spacing: 1px;
            margin-bottom: 18px;
            text-transform: uppercase;
        }
        label { font-family: 'Poller One', cursive; font-size: 1.1em; margin-right: 10px; }
        select { font-family: 'Quicksand', sans-serif; font-size: 1em; height: 38px; }
        button[type=submit] {
            background: #84894a;
            color: #FFFDF9;
            font-family: 'Poller One', cursive;
            font-size: 1.1em;
            border: none;
            border-radius: 6px;
            padding: 8px 28px;
            cursor: pointer;
            margin-left: 10px;
            text-transform: uppercase;
        }
        .selection-summary {
            font-family: 'Quicksand', sans-serif;
            font-size: 1.1em;
            color: #291909;
            margin-bottom: 18px;
            margin-top: 18px;
        }
        /* Main output and grid full width, fixed for what's next */
        .main-output-container { max-width: 1200px; width: 100%; margin: 0 auto; margin-top: 30px; }
        .pmn-whats-next-pages { max-width: 100%; width: 100%; display: grid; grid-template-columns: repeat(4, 1fr); gap: 40px; box-sizing: border-box; overflow: hidden; }
        .pmn-whats-next-pagecard { min-width: 0; max-width: 100%; background: #FFFDF9; border-radius: 6px; padding: 10px; min-height: 80px; box-sizing: border-box; }
        /* Tab styling */
        .tab-btn { font-family: 'Quicksand', sans-serif; font-size: 16px; border-radius: 6px 6px 0 0; padding: 8px 20px; cursor: pointer; border: 2px solid #F2E0B5; background: #FFFDF9; color: #291909; margin-right: 4px; transition: background 0.2s, border 0.2s; }
        .tab-btn.selected { background: #F2E0B5; border-bottom: 2px solid #F2E0B5; }
        .tab-btn:not(.selected) { background: #FFFDF9; border: 2px solid #F2E0B5; }
        .tab-btn:focus { outline: none; }
        .tab-btn:hover { border-color: #84894a; }
        .tab-content { margin-top: 0; }
        .subtitle-italic { font-style: italic; font-size: 1.1em; color: #291909; margin-bottom: 10px; display: block; }
        </style>
        </head>
        <div class="selector-area-bg">
            <div class="widget-title">LESSON PLANNING ASSISTANT TOOL (BETA)</div>
            <form method="post" style="margin-bottom: 10px; text-align: center;">
                <label>Series:
                    <select name="series" onchange="this.form.submit()">
                        {% for s in series_options %}
                            <option value="{{s}}" {% if s == selected_series %}selected{% endif %}>{{s}}</option>
                        {% endfor %}
                    </select>
                </label>
                <label>Book:
                    <select name="book" onchange="this.form.submit()">
                        {% for title, order in book_options[selected_series] %}
                            <option value="{{order}}" {% if order == selected_book %}selected{% endif %}>{{title}}</option>
                        {% endfor %}
                    </select>
                </label>
                <label>Page:
                    <select name="page" style="width: 80px;">
                        {% for p in page_options %}
                            <option value="{{p}}" {% if p == selected_page %}selected{% endif %}>{{p}}</option>
                        {% endfor %}
                    </select>
                </label>
                <button type="submit">LET'S PLAN</button>
            </form>
        </div>
        {% if result %}
        <div class="selection-summary">
            You have selected: <strong>{{selected_series}}</strong> – <strong>{{selected_book_title}}</strong>, Page <strong>{{selected_page}}</strong>
        </div>
        <div class="main-output-container">{{ result|safe }}</div>
        {% endif %}
        <script>
        // Tab logic with outlined unselected tab
        function showTab(tab) {
            var byBookBtn = document.getElementById('tab-by-book');
            var byCatBtn = document.getElementById('tab-by-category');
            var byBookContent = document.getElementById('tab-content-by-book');
            var byCatContent = document.getElementById('tab-content-by-category');
            if (tab === 'by-book') {
                byBookBtn.classList.add('selected');
                byCatBtn.classList.remove('selected');
                byBookContent.style.display = '';
                byCatContent.style.display = 'none';
            } else {
                byBookBtn.classList.remove('selected');
                byCatBtn.classList.add('selected');
                byBookContent.style.display = 'none';
                byCatContent.style.display = '';
            }
        }
        // Set default tab
        showTab('by-book');
        </script>
    ''',
    series_options=series_options,
    book_options=book_options,
    selected_series=selected_series,
    selected_book=selected_book,
    selected_book_title=selected_book_title,
    selected_page=selected_page,
    page_options=pages_for_book,
    result=result)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
