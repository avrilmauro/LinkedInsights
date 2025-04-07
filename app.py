import dash
from dash import dcc, html, Input, Output
import dash_cytoscape as cyto
import pandas as pd
import numpy as np

df = pd.read_csv('linkedin_df.csv')
unique_sectors = df['Sector'].unique()
salary_min, salary_max = df['normalized_salary'].min(), df['normalized_salary'].max()

# Function to generate elements for a sector
def generate_elements(sector):
    elements = []
    sector_df = df[df['Sector'] == sector]

    # Central sector node
    elements.append({
        'data': {'id': sector, 'label': sector},
        'position': {'x': 0, 'y': 0},
        'classes': 'sector'
    })

    # Industry nodes (linked directly to sector), colored and sized by avg salary
    industries = sector_df.groupby('first_industry')['normalized_salary'].mean().reset_index()
    angle_step = 360 / len(industries) if len(industries) > 0 else 0
    radius = 300

    for i, row in industries.iterrows():
        industry = row['first_industry']
        avg_salary = row['normalized_salary']

        norm = (avg_salary - salary_min) / (salary_max - salary_min)
        color = f"rgb(0,{int(114 * (1 - norm)**2)},{int(177 * (1 - norm)**2)})"
        size = 20 + 40 * norm

        angle_rad = (angle_step * i) * 3.14159 / 180
        x = radius * np.cos(angle_rad)
        y = radius * np.sin(angle_rad)

        elements.append({
            'data': {
                'id': industry,
                'label': industry
            },
            'position': {'x': x, 'y': y},
            'style': {
                'background-color': color,
                'width': size,
                'height': size
            },
            'classes': 'industry'
        })

        elements.append({
            'data': {
                'source': sector,
                'target': industry,
                'label': f"${avg_salary:,.0f}"
            }
        })

    return elements

# Dash App
app = dash.Dash(__name__)
default_sector = "Technology & IT Services"
app.layout = html.Div([
        html.Link(
        href="https://fonts.googleapis.com/css2?family=Roboto&display=swap",
        rel="stylesheet"),
    html.H1("Interactive Job Sector Network", style={'font-size': '20px', 'font-family': 'Roboto'}),
    dcc.Dropdown(
        id='sector-dropdown',
        options=[{'label': s, 'value': s} for s in unique_sectors],
        value=default_sector,
        style={'font-size': '12px', 'font-family': 'Roboto'}
    ),
    cyto.Cytoscape(
        id='cytoscape-network',
        layout={
            'name': 'preset',  # Using manual positioning
            'fit': True,
            'padding': 100,
            'animate': True
        },
        style={'width': '100%', 'height': '700px'},
        elements=generate_elements(default_sector),
        stylesheet=[
            {'selector': '.sector', 'style': {
                'width': 140, 'height': 140, 'background-color': 'orange',
                'label': 'data(label)', 'font-size': '10px',
                'color': 'white', 'font-weight': 'bold', 'font-family': 'Roboto',
                'text-valign': 'center', 'text-halign': 'center'}},
            {'selector': '.industry', 'style': {
                'label': 'data(label)', 'background-opacity': 1,
                'font-size': '8px', 'text-valign': 'top', 'text-halign': 'center',
                'font-family': 'Roboto'}},
            {'selector': 'edge', 'style': {
                'line-color': '#ccc', 'label': 'data(label)', 'font-size': '8px',
                'text-background-color': '#fff', 'text-background-opacity': 1,
                'font-family': 'Roboto'}}
        ]
    )
])



@app.callback(
    Output('cytoscape-network', 'elements'),
    Input('sector-dropdown', 'value')
)
def update_elements(sector):
    return generate_elements(sector)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True)
