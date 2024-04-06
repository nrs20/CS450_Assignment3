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
PAGE_SIZE = 6

#to display an initially empty datatable.
df_empty = pd.DataFrame(columns=['RawTweet'])


#extract the months into a list to use for the dropdown
months = df['Month'].unique()

app=dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H2('Month:',  style={'display': 'inline-block', 
                                      'margin-right': '10px', 'font-family': 'Georgia','font-size': '15px'}),

            #dropdown for month
            dcc.Dropdown(
                id='month',
                options=[{'label': i, 'value': i} for i in months],
                value=months[0],
                style={'width': '50%','justifyContent': 'center','alignItems': 'center'}
            ),
            html.H2('Sentiment Score',  style={'display': 'inline-block', 'margin-right': '10px', 'font-family': 'Georgia','font-size': '15px'}),
           #range slider for sentiment score
            dcc.RangeSlider(
                id='sentiment_score_slider',
                min=df['Sentiment'].min(),
                max=df['Sentiment'].max(),
                step=0.1,
                marks={mark: str(float(mark)) for mark in range(int(df['Sentiment'].min()), int(df['Sentiment'].max()+1)) if mark!= 0},
                value=[int(df['Sentiment'].min()), int(df['Sentiment'].max())],
                className='black-slider'  
            ),
            html.H2('Subjectivity Score', style={'display': 'inline-block', 'margin-right': '10px', 'font-family': 'Georgia','font-size': '15px'}),
           #range slider for subjectivity score
            dcc.RangeSlider(
                id='subjectvity_score_slider',
                min=df['Subjectivity'].min(),
                max=df['Subjectivity'].max(),
                step=0.1,
                marks={mark: str(float(mark)) for mark in range(int(df['Subjectivity'].min()), int(df['Subjectivity'].max()+1))},
                value=[df['Subjectivity'].min(), df['Subjectivity'].max()],
                className='black-slider'  
            )
        ], style={'width': '70%'}, className='container')
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
    
    html.Div([
        dcc.Graph(id='sentiment')
        
        #make modebar appear vertically?     
    ], style={'width': '100%'}),
    
    html.Div([
        dash_table.DataTable(
            
            id='tweet_table',
                    columns=[{"name": i, "id": i} for i in df_empty.columns],
         data=df_empty.to_dict('records')  # This will be an empty list so i can display an empty datatable initially
,
           style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
    },
            style_cell={'textAlign': 'center'},
              page_current=0,
    page_size=PAGE_SIZE,
    page_action='custom'
        )
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center','margin-left':'50px'}),
    
    html.Div([
    html.Div(id='table-container')
])
])



# Show the texts of selected tweets in a table format. Update the table based on scatter plot selections.
@app.callback(
    dash.dependencies.Output('tweet_table', 'data'),
    [
        dash.dependencies.Input('sentiment', 'selectedData'),
        #add input for sliders and month dropdown
        
        dash.dependencies.Input('month', 'value'),
        dash.dependencies.Input('sentiment_score_slider', 'value'),
        dash.dependencies.Input('subjectvity_score_slider', 'value'),
        dash.dependencies.Input('tweet_table', "page_current"),
        dash.dependencies.Input('tweet_table', "page_size")
    ]
)
def display_selected_data(points_chosen, month, sentiment_score_slider, subjectvity_score_slider, page_current, page_size):
    if points_chosen is not None: 
           
        lasso_points = points_chosen['points']
        selected_indices = [point['pointIndex'] for point in lasso_points]
    
        print("SELECTED POINTS",lasso_points)
        print("SELECTED INDICES",selected_indices)
    
        tableEntries = df.iloc[selected_indices][['RawTweet']]
    
         # Apply filters based on month, sentiment, and subjectivity scores (already applied in other callback.)
        #filtered_entries = tableEntries[(df['Month'] == month) & (df['Sentiment'] >= sentiment_score_slider[0]) & (df['Sentiment'] <= sentiment_score_slider[1]) & (df['Subjectivity'] >= subjectvity_score_slider[0]) & (df['Subjectivity'] <= subjectvity_score_slider[1])]
    
         # Apply pagination (via dash documentation)
        paginated_entries = tableEntries.iloc[page_current*page_size:(page_current+1)*page_size]
    
        data = paginated_entries.to_dict('records')
        return data
    else:
        return []


# Implement callbacks to update the scatter plot based on the selected month and the ranges selected for sentiment and subjectivity.

@app.callback(
    dash.dependencies.Output('sentiment', 'figure'),
    [
        dash.dependencies.Input('month', 'value'),
        dash.dependencies.Input('sentiment_score_slider', 'value'),
        dash.dependencies.Input('subjectvity_score_slider', 'value')
    ]
)

def onGraphUpdate(month, sentiment_score_slider, subjectvity_score_slider):
    print(month, sentiment_score_slider, subjectvity_score_slider)
    # Filter the data based on the selected month and the sentiment and subjectivity scores
    filtered_df = df[(df['Month'] == month) & (df['Sentiment'] >= sentiment_score_slider[0]) & (df['Sentiment'] <= sentiment_score_slider[1]) & (df['Subjectivity'] >= subjectvity_score_slider[0]) & (df['Subjectivity'] <= subjectvity_score_slider[1])]
    
    # Create the scatter plot
    fig = px.scatter(filtered_df, x='Dimension 1', y='Dimension 2')
    
    # remove the axes labels
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    
    #remove axis titles
    fig.update_yaxes(title=None)
    fig.update_xaxes(title=None)
    
    #remove gridlines like in the video
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    
   # fig.update_xaxes(showline=False, showgrid=False)
   
   #make modebar appear vertically
    fig.update_layout(
        modebar={
            'orientation': 'v'
        }
)
    return fig



if __name__ == '__main__':
    app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)