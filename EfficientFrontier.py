import pandas as pd
import numpy as np
import scipy.optimize as sco
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import math
from AssetClassesData import close_price, daily_return, daily_rf, monthly_rf, annual_rf

##### Define variables below:
#min allocation in each asset ( if 0 no short selling allowed)
min_allocation = 0
# max allocation in each asset
max_allocation = 0.5
# num portfolios randomly generated:
num_portfolios = 10000

# range of target returns for the efficient frontier:
target_ret = 0.15
range_target_ret = np.linspace(0, 0.20, 50)

def gen_random_portfolios(num_portfolios, mu, sigma, rf):
    weights_record = []
    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        if np.any(weights > max_allocation):
            pass
        else:
            weights_record.append(weights)
    p_perf = np.zeros((3,len(weights_record)))
    for i in range(len(weights_record)):
        p_std_dev, p_return = portfolio_volatility(weights_record[i], mu, sigma), portfolio_return(weights_record[i], mu)
        p_perf[0,i] = p_std_dev
        p_perf[1,i] = p_return
        p_perf[2,i] = (p_return - rf) / p_std_dev
    return p_perf, weights_record

def portfolio_return(weights, mu):
    p_returns = np.sum(mu*weights) * 252 #ANNUAL
    return p_returns

def portfolio_volatility(weights, mu, sigma):
    p_std = (np.dot(weights.T, np.dot(sigma, weights))* 252)**0.5 # ANNUAL
    return p_std
    
def port_parameters(close_price):
    daily_returns = (close_price - close_price.shift(1)) / close_price.shift(1)
    mu = daily_returns.mean()
    sigma = daily_returns.cov() #var cov matrix
    num_assets = len(mu)
    return mu, sigma, num_assets

def efficient_returns(mu, sigma, target_ret,max_allocation, min_allocation):
    num_assets = len(mu)
    args = (mu, sigma)

    def port_return(weights):
        return portfolio_return(weights, mu)
        
    constraints = ({'type': 'eq', 'fun': lambda x: port_return(x) - target_ret}, #
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}) # sum of weights = 1
    bounds = tuple(( min_allocation, max_allocation) for asset in range(num_assets))

    ef_ret = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    
    return ef_ret

def efficient_frontier(mu, sigma, target_ret):
    ef_port = []
    range_target_ret = np.linspace(0.03, target_ret, 100)
    for i in range(len(range_target_ret)):

        ef_port.append(efficient_returns(mu, sigma, range_target_ret[i],max_allocation, min_allocation))

    return ef_port

def eff_portfolio_perf(mu, sigma, target_ret):
    efficient_portfolios = efficient_frontier(mu, sigma, target_ret)
    w = [p['x'] for p in efficient_portfolios]
    X = []
    Y = []
    for i in range(len(w)):
        X.append(portfolio_volatility(w[i] ,mu,sigma))
        Y.append(portfolio_return(w[i] , mu))
    # returns annual ret, vol and portfolio weights
    return X, Y, w


mu, sigma, num_assets =  port_parameters(close_price)

p_perf, weights = gen_random_portfolios(num_portfolios, mu, sigma, daily_rf.mean())

X, Y, w = eff_portfolio_perf(mu, sigma, target_ret)

SR = []
for i in range(len(X)):
    SR.append((Y[i]-annual_rf.mean())/X[i])

## Maximum Sharpe Ratio Portfolio:

sr_weights = weights[np.argmax(p_perf[2])]

sr_ret = p_perf[1][np.argmax(p_perf[2])]

sr_vol = p_perf[0][np.argmax(p_perf[2])]

## Minimum Variance Portfolio:

mv_weights = weights[np.argmin(p_perf[0])]

mv_ret = p_perf[1][np.argmin(p_perf[0])]

mv_vol = p_perf[0][np.argmin(p_perf[0])]

# Table Weights:
def table_weights(rel_risk_aversion):

    port_weights = pd.DataFrame(columns = ['Portfolio','US Equity', 'Treasury Bonds','Real Estate', 'Commodities', 'ESG', 'Risk Free Rate'], index = [0 , 1, 2])
    port_weights['Portfolio'] =['Max Sharpe Ratio', 'Min Variance', 'Two-Fund Portfolio' ] 
    
    crra_w = crra_weights(rel_risk_aversion)
    if len(crra_w) == 2:
        for i in range(port_weights.shape[1]-2):
            port_weights.iloc[0,i+1] = sr_weights[i]*100
            port_weights.iloc[1,i+1] = mv_weights[i]*100
            port_weights.iloc[2,i+1] = sr_weights[i]*crra_w[0]*100
        
        port_weights.iloc[2,6] = crra_w[1]*100

    else:
        for i in range(port_weights.shape[1]-2):
            port_weights.iloc[0,i+1] = sr_weights[i]*100
            port_weights.iloc[1,i+1] = mv_weights[i]*100
            port_weights.iloc[2,i+1] = crra_w[i]*100
        port_weights.iloc[2,6] = 0

    port_weights.iloc[0,6] = 0
    port_weights.iloc[1,6] = 0

    port_weights['US Equity']=port_weights['US Equity'].map('{:,.2f}%'.format)
    port_weights['Treasury Bonds']=port_weights['Treasury Bonds'].map('{:,.2f}%'.format)
    port_weights['Real Estate']=port_weights['Real Estate'].map('{:,.2f}%'.format)
    port_weights['Commodities']=port_weights['Commodities'].map('{:,.2f}%'.format)
    port_weights['ESG']=port_weights['ESG'].map('{:,.2f}%'.format)
    port_weights['Risk Free Rate']=port_weights['Risk Free Rate'].map('{:,.2f}%'.format)
    return port_weights

hist_perf_sr = pd.DataFrame(columns = ['Return', 'Volatility', 'Sharpe Ratio'], index = close_price.index[253:len(close_price)])
hist_perf_mv = pd.DataFrame(columns = ['Return', 'Volatility', 'Sharpe Ratio'], index = close_price.index[253:len(close_price)])

for i in range(len(close_price)-253): # starts in Mar 31, 2008
    mu, sigma, num_assets =  port_parameters(close_price.iloc[0+i:i+252,:])
    
    hist_perf_sr['Return'][i] = portfolio_return(sr_weights, mu)
    hist_perf_sr['Volatility'][i] = portfolio_volatility(sr_weights, mu, sigma)
    hist_perf_sr['Sharpe Ratio'][i] = (hist_perf_sr['Return'][i] - annual_rf.mean()) / hist_perf_sr['Volatility'][i]
    hist_perf_mv['Return'][i] = portfolio_return(mv_weights, mu)
    hist_perf_mv['Volatility'][i] = portfolio_volatility(mv_weights, mu, sigma)
    hist_perf_mv['Sharpe Ratio'][i] = (hist_perf_mv['Return'][i] - annual_rf.mean()) / hist_perf_mv['Volatility'][i]

########### Utility function

## CAL
cal_x = np.linspace(0, 0.15, 100)
beta = (sr_ret-annual_rf.mean())/sr_vol
cal_y = []
for i in range(100):
    cal_y.append(annual_rf.mean() + beta*cal_x[i])

crra_ret = []
crra_vol = []
for i in range(len(cal_x)):
    if cal_y[i] <= sr_ret:
        crra_ret.append(cal_y[i])
        crra_vol.append(cal_x[i])
for i in range(len(Y)):
    if Y[i] > sr_ret:
        crra_ret.append(Y[i])
        crra_vol.append(X[i])

# CRRA Lognormal case
def crra_utility(port_return,port_volatility, rel_risk_aversion):
    return math.log(1+port_return) - (rel_risk_aversion/2)*port_volatility**2

def crra_weights(rel_risk_aversion):
    crra = []
    for i in range(len(crra_ret)):
        crra.append(crra_utility(crra_ret[i], crra_vol[i] , rel_risk_aversion))
    crra_y=[crra_ret[np.argmax(crra)]]
    if crra_y >= sr_ret: 
        crra_weight = w[Y.index(crra_y)]
    else:
        crra_weight = cal_weights(sr_ret,annual_rf.mean(),crra_y)
    return crra_weight
            
def cal_weights(sr_ret,rf, crra_y):
    mu_crra = sr_ret , rf
    def objective(weight):
        ret = (weight[0]*mu_crra[0]) + (weight[1]*mu_crra[1])
        return ret - crra_y

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1}) # sum of weights = 1
    bounds = tuple(( 0, 1) for asset in range(2))
    p_ret = sco.minimize(objective, [0.5, 0.5], method='SLSQP', constraints=constraints, bounds = bounds)
    weights = p_ret['x']
    return weights

########### Efficient Frontier Plot

import chart_studio.plotly as py
from plotly.graph_objs import *
import plotly.graph_objects as go

py.sign_in('barbaraalm', 'dSt5JOv1kQ5GOmCzLvm2')


#Plot:
def plot_portfolios(rel_risk_aversion, X, Y,p_perf):
    layout = Layout(
        title = "Markowitz's Mean and Variance Portfolios",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        width= 1000,
        legend_orientation="h"
    )

    fig_frontier = Figure( layout=layout)
    fig_frontier.add_trace(
        Scatter(
            name = 'Portfolios',
            mode='markers',
            x=p_perf[0],
            y=p_perf[1],
            marker=dict(
                color = p_perf[2], #set color equal to a variable
                colorscale='Viridis',
                showscale=True,
                size=5,
                line=dict(
                    color='Black',
                    width=1
                )
            ),
            showlegend=True
        )
    )   
    fig_frontier.add_trace(
        Scatter(
            name= 'Efficient Frontier',
            mode='lines',
            x = X,
            y = Y,
          line = dict(color='Black', width=4, dash='dash'),
        )
    )
    fig_frontier.add_trace(
        Scatter(
            name= 'Capital Allocation Line',
            mode='lines',
            x = cal_x,
            y = cal_y,
          line = dict(color='Blue', width=2),
        )
    )
    fig_frontier.add_trace(
        Scatter(
            name = 'Minimum Variance',
            mode='markers',
            marker_symbol='star',
            x=[X[np.argmin(X)]],
            y=[Y[np.argmin(X)]],
            marker=dict(
                color='Blue',
                size=14,
                line=dict(
                    color='Black',
                    width=2
                )
            ),
            showlegend=True
        )
    )   
    fig_frontier.add_trace(
        Scatter(
            name = 'Max Sharpe Ratio',
            mode='markers',
         #   x = X[np.argmax(SR)],
          #  y = Y[np.argmax(SR)],
            x=[p_perf[0][np.argmax(p_perf[2])]],
            y=[p_perf[1][np.argmax(p_perf[2])]],
            marker_symbol='star',
            marker=dict(
                color='Green',
                size=14,
                line=dict(
                    color='Black',
                    width=2
                )
            ),
            showlegend=True
        )
    )
    crra = []
    for i in range(len(crra_ret)):
        crra.append(crra_utility(crra_ret[i], crra_vol[i] , rel_risk_aversion))

    fig_frontier.add_trace(
        Scatter(
            name = 'Two-Fund Separation Theorem Portfolio ',
            mode='markers',
            x=[crra_vol[np.argmax(crra)]],
            y=[crra_ret[np.argmax(crra)]],
            marker_symbol='star',
            marker=dict(
                color='Yellow',
                size=14,
                line=dict(
                    color='Black',
                    width=2
                )
            ),
            showlegend=True
        )
    )
    return fig_frontier

##########################################################


