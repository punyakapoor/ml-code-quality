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


# Helper function to parse the uploaded code content
def parse_code(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        # Assuming the uploaded file is a text file containing code
        return io.StringIO(decoded.decode('utf-8')).read()
    except Exception as e:
        return f"Error decoding file: {str(e)}"


@app.callback(
    Output('codebert-suggestions', 'children'),
    Output('complexity-metrics', 'children'),
    Output('project-score', 'children'),
    Input('upload-code', 'contents')
)
def analyze_code_and_display_metrics(contents):
    if contents is None:
        return "No code uploaded", "No complexity data available", "No project score available"

    code_snippet = parse_code(contents)
    
    # Handle cases where parsing failed
    if code_snippet.startswith("Error"):
        return code_snippet, "No complexity data available", "No project score available"
    
    # CodeBERT suggestions
    codebert_card = build_codebert_card(code_snippet)
    
    # Complexity metrics
    complexity_metrics = calculate_complexity(code_snippet)
    complexity_list = [html.Li(f"{m['name']}: Complexity {m['complexity']} (Rank: {m['rank']})") for m in complexity_metrics]
    
    # Project score card
    score_calculator = CodeBERTAnalyzer()  # Assuming the score uses the CodeBERT analyzer in some way
    score_card = build_score_card(score_calculator)
    
    return codebert_card, html.Ul(complexity_list), score_card


if __name__ == '__main__':
    app.run_server(debug=True)
