from AssetClassesData import monthly_return
from EfficientFrontier import sr_weights, mv_weights, crra_weights
import plotly.express as px
import numpy as np
import pandas as pd
from scipy.stats import norm
import chart_studio.plotly as py
from plotly.graph_objs import *
import plotly.graph_objects as go
from plotly.validators.scatter.marker import SymbolValidator

### Distribution of daily return:

hist_ret = pd.DataFrame(columns = ['sr', 'mv', 'crra'], index = monthly_return.index)

for i in range(1, len(monthly_return)): # starts in Mar 31, 2008
    mu = monthly_return.iloc[i,:]
    hist_ret['sr'][i] = np.sum(mu*sr_weights/100)
    hist_ret['mv'][i] = np.sum(mu*mv_weights/100)

hist_ret['Date'] = hist_ret.index

### Daily VaR:
VaR = pd.DataFrame(columns = ['sr', 'mv'], index = ['1%'])

VaR.iloc[0,0] = norm.ppf(1-0.99, np.mean(hist_ret['sr']), np.std(hist_ret['sr']))
VaR.iloc[0,1] = norm.ppf(1-0.99, np.mean(hist_ret['mv']), np.std(hist_ret['mv']))

def plot_risk(value):
        if value < 0:
            if value == -1:
                port = 'mv'
                xax = 'Minimum Variance Portfolio Returns'
            else:
                port = 'sr'
                xax = 'Maximum Sharpe Ratio Portfolio Returns'

            fig_risk = px.histogram(hist_ret, x=port, y = 'Date',
            color_discrete_sequence=['#DC4D37'])
            fig_risk.add_shape(
                    go.layout.Shape(type='line', xref='x',
                                    x0=VaR[port][0], y0=0, x1=VaR[port][0],y1=250, line={'dash': 'dash'}),row=1, col=1, name= "VaR at 99% C.I.")
            fig_risk.update_layout(height=400, 
            plot_bgcolor='rgb(236,236,236)', 
            xaxis_title_text = xax,
            yaxis_title_text = "Count")

            fig_risk.add_annotation(
                    x=VaR[port][0],
                    y=100,
                    xref="x",
                    yref="y",
                    text="99% VaR: {:.02f}%".format(VaR[port][0]*100),
                    showarrow=True,
                    font=dict(
                        family="Courier New, monospace",
                        size=16,
                        color="#ffffff"
                        ),
                    align="center",
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#636363",
                    ax=20,
                    ay=-30,
                    bordercolor="#c7c7c7",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#ff7f0e",
                    opacity=0.8
                    )
        else:
            rsk_av = risk_aversion(value)
            for i in range(1, len(monthly_return)):
                mu = monthly_return.iloc[i,:]
                hist_ret['crra'][i] = np.sum(mu*crra_weights(rsk_av))

            VaR_crra = norm.ppf(1-0.99, np.mean(hist_ret['crra']), np.std(hist_ret['crra']))
            fig_risk = px.histogram(hist_ret, x='crra', y = 'Date',

            color_discrete_sequence=['#DC4D37'])
            fig_risk.add_shape(
                go.layout.Shape(type='line', xref='x',
                            x0=VaR_crra , y0=0, x1=VaR_crra,y1=250, line={'dash': 'dash'}),row=1, col=1, name= "VaR at 99% C.I.")
            fig_risk.update_layout(height=400, 
                            plot_bgcolor='rgb(236,236,236)', 
                            yaxis_title_text = "Count",
                            xaxis_title_text = "Two-Fund Separation Theorem Portfolio Returns" )
            fig_risk.add_annotation(
                    x=VaR_crra,
                    y=100,
                    xref="x",
                    yref="y",
                    text="99% VaR: {:.02f}%".format(VaR_crra*100),
                    showarrow=True,
                    font=dict(
                        family="Courier New, monospace",
                        size=16,
                        color="#ffffff"
                        ),
                    align="center",
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#636363",
                    ax=20,
                    ay=-30,
                    bordercolor="#c7c7c7",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#ff7f0e",
                    opacity=0.8
                    )

        return fig_risk

def risk_aversion(sum_questionnaire):
    if type(sum_questionnaire) is int:
        if sum_questionnaire < 4:
            rsk_av = 5
        elif sum_questionnaire < 7:
            rsk_av = 4
        elif sum_questionnaire < 10:
            rsk_av = 3
        elif sum_questionnaire <13:
            rsk_av = 2
        else: 
            rsk_av = 1
    return rsk_av


def port_perf_data(sum_questionnaire):
    rsk_av = risk_aversion(sum_questionnaire)

   # A value is trying to be set on a copy of a slice from a DataFrame
    hist_ret_crra = []
    for i in range(1, len(monthly_return)):
        mu = monthly_return.iloc[i,:]
        hist_ret_crra.append(np.sum(mu*crra_weights(rsk_av)))

    figure = {'data': [
                    {'x': hist_ret.index,
                    'y': hist_ret['sr'], 
                    'type': 'line', 
                    'name': 'Max Sharpe Ratio Portfolio', 
                    'color':'(0,204,102)',
                    'showlegend': True,},
                    {'x': hist_ret.index,
                    'y': hist_ret['mv'], 
                    'type': 'line', 
                    'name': 'Minimum Variance Portfolio', 
                    'color':'(0,0,255)',
                    'showlegend': True,},
                    {'x': hist_ret.index,
                    'y': hist_ret_crra, 
                    'type': 'line', 
                    'name': 'Two-Fund Separation Theorem Portfolio', 
                    'color':'(255,255,0)',
                    'showlegend': True,},],
                'layout': {
                 #   'legend': dict(orientation='h', xanchor = 'center'),
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
    return figure

 
