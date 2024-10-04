import base64
import io
import dataiku
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
from codebert_analyzer import CodeBERTAnalyzer
from complexity_calculator import calculate_complexity
from score import build_score_card, build_codebert_card

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.NavbarSimple(
        brand="Code Quality Dashboard",
        color="primary",
        dark=True,
    ),
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H3("Upload Code for Analysis")),
            dcc.Upload(
                id="upload-code",
                children=html.Div(["Drag and Drop or ", html.A("Select Code Files")]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                }
            ),
            html.Div(id='output-code-upload'),
        ]),
        dbc.Row([
            dbc.Col(html.H4("CodeBERT Suggestions")),
            html.Div(id='codebert-suggestions')
        ]),
        dbc.Row([
            dbc.Col(html.H4("Code Complexity")),
            html.Div(id='complexity-metrics')
        ]),
        dbc.Row([
            dbc.Col(html.H4("Project Score")),
            html.Div(id='project-score')
        ])
    ])
])

@app.callback(
    Output('codebert-suggestions', 'children'),
    Output('complexity-metrics', 'children'),
    Output('project-score', 'children'),
    Input('upload-code', 'contents')
)
def analyze_code_and_display_metrics(contents):
    if contents is None:
        return "No code uploaded", [], []

    code_snippet = parse_code(contents)
    
    # CodeBERT suggestions
    codebert_card = build_codebert_card(code_snippet)
    
    # Complexity metrics
    complexity_metrics = calculate_complexity(code_snippet)
    complexity_list = [html.Li(f"{m['name']}: Complexity {m['complexity']} (Rank: {m['rank']})") for m in complexity_metrics]
    
    # Score calculation
    score_calculator = calculate_scores(complexity_metrics)
    score_card = build_score_card(score_calculator)
    
    return codebert_card, html.Ul(complexity_list), score_card


if __name__ == '__main__':
    app.run_server(debug=True)