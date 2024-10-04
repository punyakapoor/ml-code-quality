import dash_bootstrap_components as dbc
from dash import html
from typing import List
from codebert_analyzer import CodeBERTAnalyzer
from complexity_calculator import calculate_complexity
import re

# Styles and configuration
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


# Scoring and recommendation logic
class Score:
    FIRST_PRIORITY_WEIGHT = 5
    SECOND_PRIORITY_WEIGHT = 1
    THIRD_PRIORITY_WEIGHT = 0.1

    RULE_WEIGHTS = {
        "F": FIRST_PRIORITY_WEIGHT,
        "E": SECOND_PRIORITY_WEIGHT,
        "W": SECOND_PRIORITY_WEIGHT,
        "D": SECOND_PRIORITY_WEIGHT,
        "N": SECOND_PRIORITY_WEIGHT,
        "S": SECOND_PRIORITY_WEIGHT,
        "PLE": SECOND_PRIORITY_WEIGHT,
        "PLR": SECOND_PRIORITY_WEIGHT,
        "PLC": SECOND_PRIORITY_WEIGHT,
        "PLW": SECOND_PRIORITY_WEIGHT,
    }

    def __init__(self, recipe_slocs: list, errors: list):
        self.recipe_slocs_dict = {key: int(value) for key, value in recipe_slocs}
        self.recipe_scores = {key: 0 for key in self.recipe_slocs_dict}
        self.total_score = 0.0
        self.errors = errors
        self.recommendations = {}

    def extract_prefix(self, s):
        pattern = r'^[A-Za-z]+'
        match = re.match(pattern, s)
        return match.group() if match else ''

    def calculate_scores(self):
        for error in self.errors:
            recipe, line, rule, detail = error
            rule_prefix = self.extract_prefix(rule)
            weight = self.RULE_WEIGHTS.get(rule_prefix, self.THIRD_PRIORITY_WEIGHT)
            self.recipe_scores[recipe] += weight

            # Generate recommendations
            recommendation = self.interpret_error(rule, detail)
            if recommendation:
                if recipe not in self.recommendations:
                    self.recommendations[recipe] = []
                self.recommendations[recipe].append((line, recommendation))

        total_sloc = sum(self.recipe_slocs_dict.values())
        for recipe, sloc in self.recipe_slocs_dict.items():
            self.recipe_scores[recipe] = max(10 - (self.recipe_scores[recipe] / sloc * 10), 0)
            self.total_score += self.recipe_scores[recipe] * sloc

        self.total_score /= total_sloc

    def interpret_error(self, rule, detail):
        if 'F' in rule:
            return "Fix logic errors in the code."
        elif 'E' in rule:
            return "Ensure code style aligns with PEP8 guidelines."
        elif 'W' in rule:
            return "Check potential security risks or inefficiencies."
        return None


# Score calculation card
def build_score_card(score_calculator):
    title = "Project Score"
    total_score = score_calculator.total_score  # Ensure this object has total_score attribute
    score_card = dbc.Card([
        dbc.CardHeader(html.B(title), class_name="card-header"),
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


# CodeBERT Analysis card
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
        dbc.CardHeader(html.B("CodeBERT Results"), class_name="card-header"),
        dbc.CardBody(card_content)
    ])

    return codebert_card
