import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import numpy as npclea
from dash.dependencies import Input, Output
from dash_html_components import H1, Div
from dash_core_components import Dropdown, Slider, RadioItems
import dash_table
from pandas_datareader import data as web
from AssetClassesData import close_price, annual_return, Assets
from EfficientFrontier import X, Y, p_perf, plot_portfolios, table_weights
from Risk import plot_risk, risk_aversion, port_perf_data

app = dash.Dash(__name__)
server = app.server


text_style = {'font-size': '26px', 'font-family': 'verdana', 'textAlign': 'center', 'color': '#7F90AC'}
subtext_style = {'font-size': '20px', 'font-family': 'verdana', 'textAlign': 'left', 'color': '#7F90AC'}
paragraph_style = {'font-size': '16px', 'font-family': 'verdana', 'textAlign': 'left', 'color': '#7688a3'}
disclaimer_style = {'font-size': '12px', 'font-family': 'verdana', 'textAlign': 'left', 'color': '#7F90AC'}
color_line = ['rgb(67, 67, 67)','rgb(68, 68, 68)','rgb(22, 96, 167)','rgb(55, 128, 191)','rgb(0, 0, 0)','rgb(20, 20, 20)','rgb(50, 50, 50)','rgb(100, 100, 0)','rgb(200, 200, 200)']

app.layout = html.Div([
        html.H1('Robo-Advisor: Portfolio Management Application', style={'font-size': '32px', 'font-family': 'verdana', 'textAlign': 'center', 'color': '#3D81AF'}),
        dcc.Graph(
            id='assets_price_hist',
            figure = {
                    'data': [
                        {'x': annual_return.index,
                        'y': annual_return[Assets[0]], 
                        'type': 'line', 
                        'name': Assets[0], 
                        'color':color_line[0],
                        'showlegend': True, 
                        },
                        {'x': annual_return.index,
                        'y': annual_return[Assets[1]], 
                        'type': 'line', 
                        'name': Assets[1], 
                        'color':color_line[1],
                        'showlegend': True, 
                        },
                        {'x': annual_return.index,
                        'y': annual_return[Assets[2]], 
                        'type': 'line', 
                        'name': Assets[2], 
                        'color':color_line[2],
                        'showlegend': True, 
                        },
                        {'x': annual_return.index,
                        'y': annual_return[Assets[3]], 
                        'type': 'line', 
                        'name': Assets[3], 
                        'color':color_line[3],
                        'showlegend': True, 
                        },
                        {'x': annual_return.index,
                        'y': annual_return[Assets[4]], 
                        'type': 'line', 
                        'name': Assets[4], 
                        'color':color_line[4],
                        'showlegend': True, 
                        },
                    
                            ],
                'layout': {
                    'title' :'History of Assets Annual Rolling Returns from December 2010 to March 2020',
                    'titlefont': dict(
                                    family = 'verdana',
                                    size = 24,
                                    color = '#7F90AC'),
                    'xaxis': dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1,
                                    label='1m',
                                    step='month',
                                    stepmode='backward'),
                                dict(count=6,
                                    label='6m',
                                    step='month',
                                    stepmode='backward'),
                                dict(count=1,
                                    label='YTD',
                                    step='year',
                                    stepmode='todate'),
                                dict(count=1,
                                    label='1y',
                                    step='year',
                                    stepmode='backward'),
                                dict(step='all')
                                ])
                            )
                        )
                    }
                }
            ),
        html.H2('Investor Profile', style=text_style),
        html.P('Please respond the following questionnaire to compute your coefficient of risk aversion.',style=paragraph_style),
        html.Label(['We toss a coin once. You may choose one of the following two options:',
                dcc.Dropdown(
                    id = 'quest1',
                 #   style = {'font-family': 'verdana'},
                    options=[
                            {'label': "You receive $ 1'000 with either heads or tails", 'value': 0},
                            {'label': "With heads you receive $ 2'000, with tails you don't receive anything at all.", 
                            'value': 4},
                            ],
                        placeholder='Select an option'
                                )
                    ]),
        html.Label(['Which of the following two options would you choose?', 
                dcc.Dropdown(
                    id = 'quest2',
                        placeholder='Select an option'
                                )
                ]),
        html.Label(['Which of the following two options would you choose?', 
                dcc.Dropdown(
                    id = 'quest3',
                        placeholder='Select an option'
                                )
                ]),
        html.Label(['Which of the following two options would you choose?', 
                dcc.Dropdown(
                    id = 'quest4',
                        placeholder='Select an option'
                                )
                ]),
        html.Label(["We toss a coin once. Would you accept the following agreement? Heads, you win $ 1'500. Tails, you lose $ 1'000", 
                dcc.Dropdown(
                    id = 'quest5',
                        placeholder='Select an option'
                                )
                ]),
        html.P('The next question is about your shortfall risk constraint. Here it is defined a level of risk accepted in case a rare disaster event occurs. The expected shortfall risk is estimated at 99% confidence interval.',style=paragraph_style),
        html.Label(['How much of your investment (in percentage) you accept to lose in one month in the worst case scenario (1% of probability to occur)?', 
                dcc.Dropdown(
                    id = 'quest6',
                    options=[
                            {'label': 'I accept losing no more than 15%', 'value': -0.15},
                            {'label': 'I accept losing no more than 10%', 'value': -0.1},
                            {'label': 'I accept losing no more than 5%', 'value': -0.05},
                            ],
                        placeholder='Select an option'
                                )
                ]),
            html.Div(id='output-quest-button5',
                    children='Enter a value and press submit'),
            html.Div(id='output-quest-button6',
                    children='Enter a value and press submit'),
            html.Button('Submit', id='quest-button'),
            html.H3('Recommendation', style=text_style),
            html.H4("Markowitz's Mean and Variance Portfolios", style=subtext_style),
            html.P('Here it is recommended 3 portfolios which the allocation weights are expressed in the table below. You can compare the return vs. risk relation of each one in the efficient frontier graph.',style=paragraph_style),
            dcc.Graph(
                id='efficient_frontier',
                ),
            
            html.H5('Portfolio Weights', style=text_style),
            html.P('Allocation of weights in each asset class in percentage points.', style=paragraph_style),
            dash_table.DataTable(
                id = 'table',
                data = [{}],
                columns = [{"name": i, "id": i} for i in ['Portfolio', 'US Equity', 'Treasury Bonds', 'Real Estate','Commodities', 'ESG', 'Risk Free Rate']],
                style_table = {'width': '100%'},
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,}
            ),
            html.H6('Portfolio Risk Analysis', style=text_style),
            html.H6('Distribution of Historical Monthly Portfolio Returns', style=subtext_style),
            html.P('Please select one of the portfolios to see the probability distribution of the returns.', style=paragraph_style),
            html.P(id = 'risk_paragraph1', style=paragraph_style),
            dcc.RadioItems(
                id = 'port_select'), 
 
            dcc.Graph(
                id = 'risk',
            ),
            html.H6('Historical Monthly Portfolio Returns from January 2010 to December 2020', style=subtext_style),
            dcc.Graph(
            id='port_performance',      
            ),
            html.P('Disclaimer: This application is part of the Field Project on Data Science of Barbara Silva de Almeida from Neuchatel University. The use of this content is exclusively for university purposes.', style=disclaimer_style),
                ])
            

@app.callback(
    dash.dependencies.Output('quest2','options'),
   [dash.dependencies.Input('quest1','value')] 
)
def update_quest2(value):
    options=[
        {'label': "You draw a lottery ticket with an 80% chance to win $ 45 (if you loose, you don't get anything at all)", 'value': value+3},
        {'label': 'You win $ 30, no matter which ticket is drawn.', 'value': value},]
    return options
@app.callback(
    dash.dependencies.Output('quest3','options'),
   [dash.dependencies.Input('quest2','value')] 
)
def update_quest3(value):
    options=[
        {'label': "You draw a lottery ticket with a 25% chance to win $ 100 (if you loose, you don't get anything at all)", 'value': value},
        {'label': "You draw a lottery ticket with a 20% chance to win $ 130 (if you loose, you don't get anything at all)", 'value': value+2},
        ]
    return options

@app.callback(
    dash.dependencies.Output('quest4','options'),
   [dash.dependencies.Input('quest3','value')] 
)
def update_quest4(value):
    options=[
        {'label': "You draw a lottery ticket with a 2% chance of winning $ 3000 (if you loose, you don't get anything at all)", 'value': value},
        {'label': "You draw a lottery ticket with a 1% chance of winning $ 6000 (if you loose, you don't get anything at all)", 'value': value+1},
        ]
    return options

@app.callback(
    dash.dependencies.Output('quest5','options'),
   [dash.dependencies.Input('quest4','value')] 
)
def update_quest5(value):
    options=[
        {'label': "Yes", 'value': value+5},
        {'label': "No", 'value': value},
        ]
    return options

@app.callback(
    dash.dependencies.Output('output-quest-button5', 'children'),
    [dash.dependencies.Input('quest-button', 'n_clicks')],
    [dash.dependencies.State('quest5', 'value')])
def update_output_quest2(n_clicks, value):
    return 'Your coefficient of risk aversion is "{}"'.format(
        risk_aversion(value)
    )

@app.callback(
    dash.dependencies.Output('output-quest-button6', 'children'),
    [dash.dependencies.Input('quest-button', 'n_clicks')],
    [dash.dependencies.State('quest6', 'value')])
def update_output_quest3(n_clicks, value):
    return 'Your annual shortfall constraint is "{}"%'.format(
        value*100
    )

@app.callback(
    dash.dependencies.Output('efficient_frontier','figure'),
    [dash.dependencies.Input('quest5', 'value')])
def update_plot(value):
    return plot_portfolios(risk_aversion(value), X, Y, p_perf)

@app.callback(
    dash.dependencies.Output('table','data'),
    [dash.dependencies.Input('quest5', 'value')])
def update_table(value):
    return table_weights(risk_aversion(value))

@app.callback(
    dash.dependencies.Output('port_select','options'),
    [dash.dependencies.Input('quest5', 'value')])
def update_port_risk(value):
    options = [
        {'label': 'Min Variance Portfolio', 'value': -1},
        {'label': 'Max Sharpe Ratio Portfolio', 'value': -2},
        {'label': 'Two-Fund Separation Theorem Portfolio', 'value': value}
        ]
    return options

@app.callback(
    dash.dependencies.Output('risk','figure'),
    [dash.dependencies.Input('port_select', 'value')])
def update_plot_risk(value):
    return plot_risk(value)

@app.callback(
    Output('risk_paragraph1','children'),
    [dash.dependencies.Input('quest6', 'value')])
def update_paragraph1(value):
    return 'You can compare your annual shortfall constraint of "{}"% to the value at risk (VaR) of each portfolio.'.format(
        value*100
    )

@app.callback(
    dash.dependencies.Output('port_performance','figure'),
    [dash.dependencies.Input('quest5', 'value')])
def update_plot_perf(value):
    return port_perf_data(value)


