import os
import subprocess
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
from score import build_score_card, build_codebert_card
from complexity_calculator import calculate_complexity

# SonarQube Configuration
SONARQUBE_URL = 'http://localhost:9000'
SONARQUBE_TOKEN = 'sqa_31f4c45b4b8668015cb71376367fd9d54c2c705a'
PROJECT_KEY = 'test-code-quality1'

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
            dbc.Col(html.H4("SonarQube Analysis")),
            html.Div(id='sonar-output')
        ])
    ])
])

def run_sonar_scanner():
    """Run SonarScanner and return the output."""
    try:
        # Running the SonarScanner using subprocess
        result = subprocess.run([
            "pysonar-scanner",
            f"-Dsonar.projectKey={PROJECT_KEY}",
            f"-Dsonar.sources=.",
            f"-Dsonar.host.url={SONARQUBE_URL}",
            f"-Dsonar.login={SONARQUBE_TOKEN}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return "SonarQube analysis completed successfully!", result.stdout
        else:
            return f"Error in SonarQube analysis: {result.stderr}"
    
    except Exception as e:
        return f"Failed to run SonarQube analysis: {str(e)}"

@app.callback(
    Output('codebert-suggestions', 'children'),
    Output('complexity-metrics', 'children'),
    Output('sonar-output', 'children'),
    Input('upload-code', 'contents')
)
def analyze_code_and_display_metrics(contents):
    if contents is None:
        return "No code uploaded", [], "No SonarQube analysis"

    code_snippet = parse_code(contents)
    
    # CodeBERT suggestions
    codebert_card = build_codebert_card(code_snippet)
    
    # Complexity metrics
    complexity_metrics = calculate_complexity(code_snippet)
    complexity_list = [html.Li(f"{m['name']}: Complexity {m['complexity']} (Rank: {m['rank']})") for m in complexity_metrics]
    
    # SonarQube analysis
    sonar_message, sonar_output = run_sonar_scanner()
    
    return codebert_card, html.Ul(complexity_list), html.Pre(f"{sonar_message}\n\n{sonar_output}")

if __name__ == '__main__':
    app.run_server(debug=True)
