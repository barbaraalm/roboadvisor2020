from AssetClassesData import monthly_return, annual_rf, daily_return
from EfficientFrontier import sr_weights, mv_weights, ccra_weights
import plotly.express as px
import numpy as np
import pandas as pd
import math
from scipy.stats import norm
from plotly.graph_objs import *
import plotly.graph_objects as go

# Distribution of daily return:
m_ret = pd.concat([monthly_return, annual_rf], axis=1).dropna(subset=['US Equity'])
m_ret['rf_annual'] = m_ret['rf_annual']/12

d_ret = pd.concat([daily_return, annual_rf], axis=1).dropna(subset=['US Equity'])
d_ret['rf_annual'] = d_ret['rf_annual']/251

def risk_aversion(sum_questionnaire):
    if type(sum_questionnaire) is int:
        if sum_questionnaire < 4:
            rsk_av = 20
        elif sum_questionnaire < 7:
            rsk_av = 16
        elif sum_questionnaire < 10:
            rsk_av = 12
        elif sum_questionnaire <13:
            rsk_av = 8
        else: 
            rsk_av = 4
    return rsk_av

def risk_category(value):
    if type(value) is int:
        if value < 5:
            rsk_cat = "Very low risk aversion"
        elif value < 9:
            rsk_cat = "Low risk aversion"
        elif value < 13:
            rsk_cat = "Moderate risk aversion"
        elif value < 17:
            rsk_cat = "High risk aversion"
        else: 
            rsk_cat = "Very high risk aversion"
    return rsk_cat

def hist_ret(value,m_ret):
    rsk_av = value
    df = (m_ret*ccra_weights(rsk_av)).fillna(0)
    ret = df['US Equity'] + df['Treasury Bonds'] + df['Real Estate'] + df['Commodities'] + df['ESG'] + df['rf_annual']
    hist_returns = pd.DataFrame(data=ret)
    hist_returns = hist_returns.rename(columns = {0:'ccra'})
    return hist_returns

def plot_risk(value):
    rsk_av = value
    ret = hist_ret(value, m_ret)
    ret['Date'] = ret.index
    VaR_ccra = norm.ppf(1-0.99, np.mean(ret['ccra']), np.std(ret['ccra']))
    fig_risk = px.histogram(
        ret, 
        x='ccra', 
        y = 'Date', 
        color_discrete_sequence=['#DC4D37']
        )
        
    fig_risk.add_shape(
        go.layout.Shape(
            type='line',
            xref='x',
            x0=VaR_ccra ,
            y0=0,
            x1=VaR_ccra,
            y1=250,
            line={'dash': 'dash'}
            ),
            row=1,
            col=1,
            name= "VaR at 99% C.I."
            )
    fig_risk.update_layout(height=400,
    plot_bgcolor='rgb(236,236,236)', 
    yaxis_title_text = "Count",
    xaxis_title_text = "Optimal Portfolio Returns"
    )
    fig_risk.add_annotation(
        x=VaR_ccra,
        y=100,
        xref="x",
        yref="y",
        text="99% VaR: {:.02f}%".format(VaR_ccra*100),
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

def port_perf_data(value):
    hist_ret_ccra = hist_ret(value, d_ret)
    lnret = []
    for i in range(len(hist_ret_ccra)):
        lnret.append(math.log(1 + hist_ret_ccra['ccra'][i]))

    hist_ret_ccra['lnret'] = lnret

    cum_daily_return = np.exp(hist_ret_ccra['lnret'].cumsum())

    figure = {'data': [
                    {'x': hist_ret_ccra.index,
                    'y': cum_daily_return, 
                    'type': 'line', 
                    'name': 'Optimal Portfolio', 
                    'color':'(255,255,0)',
                    'showlegend': True,},],
                'layout': {
                    'title' :'Historical Cumulative Daily Returns of Optimal Portfolio allocation from January 2006 to March 2020',
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
    return figure
