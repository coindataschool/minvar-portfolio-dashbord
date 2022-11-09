import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib.patches as mpatches
import numpy as np
import os 
from helper import generate_weights, calc_portfolio_ret_avg, calc_portfolio_ret_std

plt.rcParams['figure.figsize'] = (8, 5)
plt.style.use("fivethirtyeight")

# read price data and calculate daily returns
fnames = os.listdir('data')
df = pd.concat([pd.read_pickle(os.path.join('data',fnm)) for fnm in fnames])
simple_rets = df.pct_change().dropna()
# simple_rets.head()

# calculates min-variance portfolios for different start dates
minvar_stds = []
minvar_rets = []
minvar_wts_gmx = []
minvar_wts_gns = []
n = int(len(simple_rets) * 0.7)  # use at least 30% data for calculation to ensure robustness of results
for i in range(n):
    ha = simple_rets.iloc[i:]
    rets = []
    stds = []
    wts = []
    for i in range(500): # generate 500 pairs of weights and hence 500 new portfolios.
        weights = generate_weights(2)
        rets.append(calc_portfolio_ret_avg(ha.mean(), weights))
        stds.append(calc_portfolio_ret_std(ha, weights))
        wts.append(weights)
    minvar_stds.append(min(stds)) 
    minvar_rets.append(rets[stds.index(min(stds))])
    minvar_wts_gmx.append(wts[stds.index(min(stds))][0])
    minvar_wts_gns.append(wts[stds.index(min(stds))][1])
    
# collect all the min-variance portfolios into a data frame
minvar_portfolios = pd.DataFrame(
    {"std": minvar_stds, "ret": minvar_rets, 
     "GMX %":minvar_wts_gmx, "GNS %":minvar_wts_gns}, 
    index=simple_rets.index[:n])
minvar_portfolios.index.name = 'start date'

# --- analyze and plot these portfolios --- #

def plt_histogram(x, title, xlab, nbins=50, xaxis_nticks=8):
    _, ax = plt.subplots()
    ax.hist(x, bins=nbins)
    plt.title(title)
    plt.gca().xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    steps  = (max(x) - min(x)) / xaxis_nticks
    plt.xticks(np.arange(min(x), max(x)+steps, steps))
    plt.xlabel(xlab)
    plt.ylabel('Frequency')  
        
os.makedirs('png', exist_ok=True)  
        
# plot distribution of mean returns
fig_title = 'Distribution of Mean Returns of\nMin-Variance Portfolios with Different Start Dates'
plt_histogram(minvar_portfolios['ret'], fig_title, xlab='Mean Return')
# make legend to show the median value
med = minvar_portfolios['ret'].median()
l1 = mpatches.Patch(color='black',  label='Median = {:.0%}'.format(med))
plt.legend(handles=[l1], loc='upper right')
# save
plt.tight_layout()
plt.savefig(os.path.join('png', 'minvar_portfolios_meanrets.png'), dpi=300)

# plot distribution of volatilities
fig_title = 'Distribution of Volatilities of\nMin-Variance Portfolios with Different Start Dates'
plt_histogram(minvar_portfolios['std'], fig_title, xlab='Volatility', xaxis_nticks=9)
# make legend to show the median value
med = minvar_portfolios['std'].median()
l1 = mpatches.Patch(color='black',  label='Median = {:.0%}'.format(med))
plt.legend(handles=[l1], loc='upper right')
# save
plt.tight_layout()
plt.savefig(os.path.join('png', 'minvar_portfolios_vols.png'), dpi=300)

# plot distribution of GMX proportions
fig_title = 'Distribution of GMX Weights of\nMin-Variance Portfolios with Different Start Dates'
plt_histogram(minvar_portfolios['GMX %'], fig_title, xlab='GMX Proportion')
# make legend to show the median value
med = minvar_portfolios['GMX %'].median()
l1 = mpatches.Patch(color='black',  label='Median = {:.0%}'.format(med))
plt.legend(handles=[l1], loc='upper right')
# save
plt.tight_layout()
plt.savefig(os.path.join('png', 'minvar_portfolios_weights_gmx.png'), dpi=300)

# plot distribution of GNS proportions
fig_title = 'Distribution of GNS Weights of\nMin-Variance Portfolios with Different Start Dates'
plt_histogram(minvar_portfolios['GNS %'], fig_title, xlab='GNS Proportion', xaxis_nticks=9)
# make legend to show the median value
med = minvar_portfolios['GNS %'].median()
l1 = mpatches.Patch(color='black',  label='Median = {:.0%}'.format(med))
plt.legend(handles=[l1], loc='upper right')
# save
plt.tight_layout()
plt.savefig(os.path.join('png', 'minvar_portfolios_weights_gns.png'), dpi=300)