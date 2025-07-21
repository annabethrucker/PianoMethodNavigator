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
    # Get all unique pages for the selected book
    pages_for_book = sorted(df[(df['Series'] == selected_series) & (df['Book Order'] == selected_book)]['Page'].unique())
    return render_template_string('''
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Poller+One&family=Quicksand:wght@400;700&display=swap" rel="stylesheet">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
        <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
        <style>
        label { font-family: 'Poller One', cursive; font-size: 1.1em; margin-right: 10px; }
        select, .select2-selection__rendered, .select2-results__option { font-family: 'Quicksand', sans-serif !important; font-size: 1em; }
        .select2-container--default .select2-selection--single { height: 38px; }
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
        }
        .selection-summary {
            font-family: 'Quicksand', sans-serif;
            font-size: 1.1em;
            color: #291909;
            margin-bottom: 18px;
        }
        </style>
        </head>
        <form method="post" style="margin-bottom: 10px;">
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
                <select id="page-select" name="page" style="width: 80px;">
                    <option></option>
                    {% for p in page_options %}
                        <option value="{{p}}" {% if p == selected_page %}selected{% endif %}>{{p}}</option>
                    {% endfor %}
                </select>
            </label>
            <button type="submit">Let's Plan</button>
        </form>
        <div class="selection-summary">
            You have selected: <strong>{{selected_series}}</strong> – <strong>{{selected_book_title}}</strong>, Page <strong>{{selected_page}}</strong>
        </div>
        <div>{{ result|safe }}</div>
        <script>
        $(document).ready(function() {
            $('#page-select').select2({
                tags: true,
                width: '80px',
                dropdownAutoWidth: true,
                theme: 'default',
                placeholder: 'Type or select number',
                allowClear: true
            });
        });
        document.querySelector('select[name=series]').addEventListener('change', function() {
            this.form.submit();
        });
        document.querySelector('select[name=book]').addEventListener('change', function() {
            this.form.submit();
        });
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
    app.run(debug=True)