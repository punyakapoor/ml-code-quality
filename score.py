import dash_bootstrap_components as dbc
from dash import html
from typing import List
from codebert_analyzer import CodeBERTAnalyzer
from complexity_calculator import calculate_complexity

# Replace with custom or inline styles
card_header_class_name = "custom-card-header"

score_style = {
    'text-align': 'center',
    'color': 'primary',
    'margin-top': '10px',
}

progress_style = {
    'background-color': 'white',
    'border': '1px solid black',
    'border-radius': '0',
}

rows_style = {
    'margin-bottom': '10px'
}

progress_color = [
    (-10.0, 5.0, 'danger'),
    (5.0, 8.0, 'warning'),
    (8.0, 10.0, 'success'),
]

h4_style = {
    'text-align': 'center',
}

def get_progress_bar_color(score):
    for low, high, color in progress_color:
        if low <= score < high:
            return color

def progress_rows(recipe_scores: dict) -> list:
    rows = []
    sorted_recipe_scores = dict(sorted(recipe_scores.items(), key=lambda item: item[1], reverse=True))

    for key, value in sorted_recipe_scores.items():
        recipe_name = key
        recipe_score = value
        formatted_recipe_score = "{:.2f}".format(value)

        progress_bar = dbc.Progress(
            value=formatted_recipe_score,
            color=get_progress_bar_color(recipe_score),
            label=formatted_recipe_score,
            style=progress_style,
            max=10,
        )
        
        row = dbc.Row(
            [
                dbc.Col(html.P(recipe_name, style={'margin-right': '10px'}), width=4),
                dbc.Col(
                    progress_bar,
                    width=8,
                ),
            ],
            style=rows_style
        )
        
        rows.append(row)
    
    return rows

def build_score_card(score_calculator):
    title = "Project Score"
    total_score = score_calculator.total_score
    score_card = dbc.Card([
        dbc.CardHeader(html.B(title), className=card_header_class_name),
        dbc.CardBody([
            html.Div([
                html.H4("Project Total Score", style=h4_style),
                html.H2(f"{total_score:.2f} / 10.", style=score_style),
                dbc.Accordion(
                    dbc.AccordionItem(
                        progress_rows(score_calculator.recipe_scores),
                        title="More details",
                    ),
                    start_collapsed=True
                ),
            ]),
        ]),
    ])

    return score_card

def build_codebert_card(code_snippet: str):
    analyzer = CodeBERTAnalyzer()
    suggestions = analyzer.get_code_quality_suggestions(code_snippet)
    if suggestions:
        suggestions_list = [html.Li(f"{s['type']}: {s['message']}") for s in suggestions]
    else:
        suggestions_list = [html.P("No suggestions; code looks good!")]

    card_content = [
        html.H4("CodeBERT Analysis", style={'text-align': 'center'}),
        html.Ul(suggestions_list),
    ]

    codebert_card = dbc.Card([
        dbc.CardHeader(html.B("CodeBERT Results"), className=card_header_class_name),
        dbc.CardBody(card_content)
    ])

    return codebert_card
