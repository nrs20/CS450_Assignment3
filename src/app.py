import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import dash

from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc
from dash import dash_table

df = pd.read_csv('ProcessedTweets.csv')


#extract the months into a list to use for the dropdown
months = df['Month'].unique()

app=dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='month',
                options=[{'label': i, 'value': i} for i in months],
                value=months[0],
                style={'width': '50%','justifyContent': 'center','alignItems': 'center'}
            ),
            html.H2('Sentiment Score', style={'display': 'inline-block', 'margin-right': '10px'}),
            dcc.RangeSlider(
                id='sentiment_score',
                min=df['Sentiment'].min(),
                max=df['Sentiment'].max(),
                step=0.1,
                marks={i: str(i) for i in range(-1, 2)},
                value=[df['Sentiment'].min(), df['Sentiment'].max()],
                className='black-slider'  # Add this line to set the color of the slider to black
            ),
            html.H2('Subjectivity Score', style={'display': 'inline-block', 'margin-right': '10px'}),
            dcc.RangeSlider(
                id='subjectivity_score',
                min=df['Subjectivity'].min(),
                max=df['Subjectivity'].max(),
                step=0.1,
                marks={i: str(i) for i in range(int(df['Subjectivity'].min()), int(df['Subjectivity'].max())+1)},
                value=[df['Subjectivity'].min(), df['Subjectivity'].max()],
                className='black-slider'  # Add this line to set the color of the slider to black
            )
        ], style={'width': '70%'}, className='container')
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
    
    html.Div([
        dcc.Graph(id='sentiment')
    ], style={'width': '100%'}),
    
    html.Div([
        dash_table.DataTable(
            
            id='tweet_table',
            style_table={'height': '300px', 'overflowY': 'auto', 'width': '75%', 'margin-left':'20px', 'alignItems': 'center', 'justifyContent': 'center'},
            style_cell={'textAlign': 'center'}
        )
    ])
])
# Show the texts of selected tweets in a table format. Update the table based on scatter plot selections.
@app.callback(
    dash.dependencies.Output('tweet_table', 'data'),
    [
        dash.dependencies.Input('sentiment', 'selectedData')
    ]
)
def display_selected_data(selectedData):
    if selectedData is None:
        return []
    
    selected_points = selectedData['points']
    #print("Selected points:",selected_points)
    selected_indices = [point['pointIndex'] for point in selected_points]
    
    #print(selected_indices)
    
    #use the x and y coordinates of the selected_indices for each point to get the corresponding indices in the dataframe
    
    #the x coordinate corresponds to 'Dimension 1' and the y coordinate corresponds to 'Dimension 2'
    #grab the Raw Tweet matching the x and y coordinates of the selected points
    
    print("AQUI:",df.iloc[selected_indices][['RawTweet']])
    
    tableEntries = df.iloc[selected_indices][['RawTweet']]
    #display selected_indices in a table format
    
    
    
    
    #get the scores of the sentiment and subjectivity of the selected points
    selected_tweets = df.iloc[selected_indices][['Sentiment', 'Subjectivity']]
   # print("Selected tweets:",selected_tweets)
    
    #grab the tweets of the selected points
    
    #return the selected tweets and insert them into the table
    data = tableEntries.to_dict('records')
    return data



# Implement callbacks to update the scatter plot based on the selected month and the ranges selected for sentiment and subjectivity.

@app.callback(
    dash.dependencies.Output('sentiment', 'figure'),
    [
        dash.dependencies.Input('month', 'value'),
        dash.dependencies.Input('sentiment_score', 'value'),
        dash.dependencies.Input('subjectivity_score', 'value')
    ]
)
def update_graph(month, sentiment_score, subjectivity_score):
    print(month, sentiment_score, subjectivity_score)
    # Filter the data based on the selected month and the sentiment and subjectivity scores
    filtered_df = df[(df['Month'] == month) & (df['Sentiment'] >= sentiment_score[0]) & (df['Sentiment'] <= sentiment_score[1]) & (df['Subjectivity'] >= subjectivity_score[0]) & (df['Subjectivity'] <= subjectivity_score[1])]
    
    # Create the scatter plot
    fig = px.scatter(filtered_df, x='Dimension 1', y='Dimension 2')
    
    return fig



if __name__ == '__main__':
    app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)