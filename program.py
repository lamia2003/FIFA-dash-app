# Link to site: https://fifa-wins-dash-app.onrender.com

import pandas as pd
from dash import dcc, html, Input, Output, Dash
import plotly.graph_objects as go

df = pd.read_csv('FIFA_data.csv')
df['Team'] = df['Team'].replace({'England': 'United Kingdom'})
df['Winners'] = pd.to_numeric(df['Winners'], errors='coerce')
winers_data = df[df['Winners'] > 0].copy()

finalists = {}
for _, row in df.iterrows():
    team = row['Team']
    years_won = row['Years won']
    if pd.notna(years_won) and years_won.strip() != '—':
        for year in years_won.split(','):
            year = year.strip()
            finalists.setdefault(year, {})['Winner'] = team
    years_runner = row['Years runners-up']
    if pd.notna(years_runner) and years_runner.strip() != '—':
        for year in years_runner.split(','):
            year = year.strip()
            finalists.setdefault(year, {})['Runner-up'] = team

winners_and_runners_per_year = []
for year, info in finalists.items():
    try:
        year_int = int(year)
    except ValueError:
        continue
    winners_and_runners_per_year.append({
        'Year': year_int,
        'Winner': info.get('Winner', 'N/A'),
        'Runner-up': info.get('Runner-up', 'N/A')
    })
finals_df = pd.DataFrame(winners_and_runners_per_year)
finals_df.sort_values(by='Year', inplace=True)

fig = go.Figure(go.Choropleth(
    locations=winers_data['Team'],
    locationmode='country names',
    z=winers_data['Winners'],
    colorscale='magma',
    colorbar_title='Number of Wins'
))
fig.update_layout(
    title_text='FIFA World Cup Winners on the Map',
    title_font_size=35,
    geo=dict(showframe=True, showcoastlines=True),
    height=1000
)

app = Dash()
server=app.server

app.layout = html.Div([
    html.H1(
        "FIFA World Cup Dashboard",
        style={
            'textAlign': 'center',
            'fontSize': '42px',
            'marginBottom': '20px',
            'color':'blue'
        }
    ),
    
    html.Div(
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in sorted(finals_df['Year'].unique())],
            placeholder="Choose a year",
            style={'width': '300px'}
        ),
        style={'marginBottom': '20px', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
    ),
    
    html.Div(
        id='year-info',
        style={
            'padding': '20px',
            'fontWeight': 'bold',
            'color': 'green',
            'textAlign': 'center',
            'fontSize': '20px'
        }
    ),
    
    html.Div(
        dcc.Graph(id='worldcup-choropleth', figure=fig, style={'width': '100%', 'margin': '0 auto'}),
        style={'textAlign': 'center'}
    )
])

@app.callback(
    Output('year-info', 'children'),
    Input('year-dropdown', 'value')
)

def years_winners_and_runner_up(year_chosen):
    if year_chosen is not None:
        year_val = int(year_chosen)
        row = finals_df[finals_df['Year'] == year_val]
        if not row.empty:
            winner = row.iloc[0]['Winner']
            runner_up = row.iloc[0]['Runner-up']
            return f"{year_val}- {winner} won with {runner_up} as the runner-up."
    return "Select a year to see the winner and runner up."

if __name__ == '__main__':
    app.run(debug=True)
