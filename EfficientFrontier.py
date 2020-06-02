import pandas as pd
import numpy as np
import scipy.optimize as sco
import seaborn as sns
import matplotlib.pyplot as plt
from sympy import symbols, Eq, solve
from plotly.graph_objs import *
from AssetClassesData import close_price, daily_return, annual_rf

# range of target returns for the efficient frontier:
target_ret = 0.15
range_target_ret = np.linspace(0, 0.20, 50)

def gen_random_portfolios( mu, sigma, rf):
    weights_record = []
    for i in range(50000):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        if np.any(weights > [0.7, 0.7, 0.2, 0.2, 0.2 ]):
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

def efficient_returns(mu, sigma, target_ret):
    num_assets = len(mu)
    args = (mu, sigma)

    def port_return(weights):
        return portfolio_return(weights, mu)
        
    constraints = ({'type': 'eq', 'fun': lambda x: port_return(x) - target_ret}, #
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}) # sum of weights = 1
    bounds = ((0, 0.7), (0, 0.7), (0, 0.2), (0, 0.2), (0, 0.2))

    ef_ret = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    
    return ef_ret

def efficient_frontier(mu, sigma, target_ret):
    ef_port = []
    range_target_ret = np.linspace(0.03, target_ret, 100)
    for i in range(len(range_target_ret)):

        ef_port.append(efficient_returns(mu, sigma, range_target_ret[i]))

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

p_perf, weights = gen_random_portfolios( mu, sigma, annual_rf.mean())

X, Y, w = eff_portfolio_perf(mu, sigma, target_ret)

## Maximum Sharpe Ratio Portfolio:

sr_weights = np.round(weights[np.argmax(p_perf[2])]*100)

sr_ret = p_perf[1][np.argmax(p_perf[2])]

sr_vol = p_perf[0][np.argmax(p_perf[2])]

## Minimum Variance Portfolio:

mv_weights = np.round(weights[np.argmin(p_perf[0])]*100)

mv_ret = p_perf[1][np.argmin(p_perf[0])]

mv_vol = p_perf[0][np.argmin(p_perf[0])]

def table_weights(rel_risk_aversion):
    ccra_w = np.round(ccra_weights(rel_risk_aversion)*100)

    port_weights = [{'Portfolio': 'Optimal Portfolio',
                    'US Equity': ccra_w[0],
                    'Treasury Bonds': ccra_w[1],
                    'Real Estate': ccra_w[2],
                    'Commodities': ccra_w[3],
                    'ESG': ccra_w[4],
                    'Risk Free Rate': ccra_w[5]}]

    return port_weights

# CAL - Capital Allocation Line
cal_x = np.linspace(0, 0.15, 100)
beta = (sr_ret-annual_rf.mean())/sr_vol
cal_y = []
for i in range(100):
    cal_y.append(annual_rf.mean() + beta*cal_x[i])

port_line_ret = []
port_line_vol = []
for i in range(len(cal_x)):
    if cal_y[i] <= sr_ret:
        port_line_ret.append(cal_y[i])
        port_line_vol.append(cal_x[i])
for i in range(len(Y)):
    if Y[i] > sr_ret:
        port_line_ret.append(Y[i])
        port_line_vol.append(X[i])

# Utility function: CCRA Lognormal case
def ccra_utility(port_return,port_volatility, rel_risk_aversion):
    return (1+port_return) - (rel_risk_aversion/2)*port_volatility**2

def ccra_weights(rel_risk_aversion):
    ccra = []
    for i in range(len(port_line_ret)):
        ccra.append(ccra_utility(port_line_ret[i], port_line_vol[i] , rel_risk_aversion))
    ccra_y=[port_line_ret[np.argmax(ccra)]]
    if ccra_y >= sr_ret: 
        ccra_weight = w[Y.index(ccra_y)]
        ccra_weight = np.append(ccra_weight, 0)
    else:
        ccra_weight = cal_weights(sr_ret,annual_rf.mean(),ccra_y)
    return ccra_weight
            
def cal_weights(sr_ret,rf, ccra_y):
    x, y = symbols('x y')
    eq1 = Eq((x*sr_ret) + (y*rf) - ccra_y[0])
    eq2 = Eq(x + y - 1)

    weights = solve((eq1,eq2), (x, y))

    port_w = sr_weights/100*float(weights[x])
    port_w = np.append(port_w, float(weights[y]))
    
    return port_w

#Plot Efficient Frontier

def plot_portfolios(rel_risk_aversion, X, Y,p_perf):
    layout = Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        #width= 1000,
        xaxis_title='Volatility',
        yaxis_title='Return',
        legend=dict( y=-0.2),
      #  legend_orientation="h",   
    )
    fig_frontier = Figure( layout=layout)
    fig_frontier.add_trace(
        Scatter(
            name = 'Portfolios',
            mode='markers',
            x=p_perf[0],
            y=p_perf[1],
            marker=dict(
                color = p_perf[2], 
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
            name= 'Feasible Portfolios',
            mode='lines',
            x = port_line_vol,
            y = port_line_ret,
          line = dict(color='Blue', width=2),
        )
    )
    fig_frontier.add_trace(
        Scatter(
            x=[X[np.argmin(X)]],
            y=[Y[np.argmin(X)]],
            mode="markers+text",
            marker= dict(color = 'Black'),
            name="Minimum Variance Portfolio",
            text=["MV"],
            textposition="bottom left"
            ))  
    fig_frontier.add_trace(
        Scatter(
            x=[p_perf[0][np.argmax(p_perf[2])]],
            y=[p_perf[1][np.argmax(p_perf[2])]],
            mode="markers+text",
            marker= dict(color = 'Black'),
            name="Tangency Portfolio",
            text=["TP"],
            textposition="top center"
            ))  
    ccra = []
    for i in range(len(port_line_ret)):
        ccra.append(ccra_utility(port_line_ret[i], port_line_vol[i] , rel_risk_aversion))

    fig_frontier.add_trace(
        Scatter(
            name = 'Optimal Portfolio',
            mode='markers',
            x=[port_line_vol[np.argmax(ccra)]],
            y=[port_line_ret[np.argmax(ccra)]],
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
