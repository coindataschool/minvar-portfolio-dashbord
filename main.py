import numpy as np
import pandas as pd
from datetime import date, timedelta
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os 
from defillama2 import DefiLlama
from helper import generate_weights, calc_portfolio_ret_avg, calc_portfolio_ret_std

# constants
gmx_blue = '#000058'
avax_red = '#DE4437'
gns_green = '#3deca7'

# set_page_config() can only be called once per app, and must be called as the 
# first Streamlit command in your script.
st.set_page_config(page_title='gmx-gns-min-variance-portfolio', 
    layout='wide', page_icon='📈') 

st.header('Efficient Frontier & Min-Variance Portfolio of GMX and GNS')
st.subheader('Returns and volatilities are calculated based on daily prices at 00:00 UTC and do not include any staking yield. The numbers are annualized.')

# user input
c1, c2 = st.columns(2)
with c1:
    start_date = st.date_input(
        "Start Date", date(2022, 6, 1), min_value=date(2021, 11, 2), 
        max_value=date.today()-timedelta(days=30))
with c2:
    end_date = st.date_input(
        "End Date", date.today(), min_value=date(2021, 11, 2)+timedelta(days=90), 
        max_value=date.today())
# start_date = date(2021, 11, 2)
# end_date = date.today()
date_format = '%Y-%m-%d'
start_str = start_date.strftime(date_format)
end_str = end_date.strftime(date_format)

# read data from disk
fnames = os.listdir('data')
df = pd.concat([pd.read_pickle(os.path.join('data',fnm)) for fnm in fnames
                if fnm.endswith('.pkl')])
last_avail_date = df.index[-1].date()
if last_avail_date < end_date:
    # download newer data that weren't on disk
    obj = DefiLlama()
    dd = {
        '0xE5417Af564e4bFDA1c483642db72007871397896':'polygon', # GNS on polygon
        '0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a':'arbitrum', # GMX on arbitrum
        '0x62edc0692BD897D2295872a9FFCac5425011c661':'avax',  # GMX on avalanche
    }
    new_start = last_avail_date + timedelta(days=1)
    new_start_str = new_start.strftime(date_format)
    df_new = obj.get_tokens_hist_prices(dd, new_start_str, end_str, type='open')
    # stack previously and newly downloaded data 
    df = pd.concat([df, df_new]).dropna()
# st.dataframe(df.tail())

# subset prices with user specificed start and end dates
df = df.loc[start_date:end_date]

# calculate daily returns
simple_rets = df.pct_change().dropna()

# randomly generate 1000 pairs of weights, and every time we have a new pair of 
# weights, we have a new portfolio with a different mean return and volatility. 
rets = []
stds = []
wts = []
for i in range(1000):
    weights = generate_weights(2)
    rets.append(calc_portfolio_ret_avg(simple_rets.mean(), weights))
    stds.append(calc_portfolio_ret_std(simple_rets, weights))
    wts.append(weights)
    
# find the pair of weights that results in the minimum variance portfolio
minvar_wt_gmx = wts[stds.index(min(stds))][0]
minvar_wt_gns = wts[stds.index(min(stds))][1]
    
# --- plot efficient frontier and highlight the min-variance portfolio --- #

dat = pd.DataFrame({'vol': stds, 'ret': rets})

# draw main figure
fig_title = 'Efficient Frontier\n({:} ~ {:})<br><sup>Each dot is a portfolio. Avoid the bottom half of the curve.</sup>'.format(start_date, end_date)
fig = px.scatter(
    dat, x='vol', y='ret', color_discrete_sequence=['lightgray'],
    labels=dict(vol="Portfolio Volatility", ret='Portfolio Return'),
    title=fig_title
)

# all in GMX
gmx_x = simple_rets.std()['GMX']*np.sqrt(365)
gmx_y = simple_rets.mean()['GMX']*365 
# all in GNS
gns_x = simple_rets.std()['GNS']*np.sqrt(365)
gns_y = simple_rets.mean()['GNS']*365
# min-var portfolio
minvar_x = min(stds)
minvar_y = rets[stds.index(min(stds))]

# add these portfolios to figure
fig.add_trace(
    go.Scatter(name='GMX 0%, GNS 100%', x=[gns_x], y=[gns_y], mode='markers',
               marker=dict(size=12, color=[gns_green], line=dict(width=2)))
)
fig.add_trace(
    go.Scatter(name='GMX 100%, GNS 0%', x=[gmx_x], y=[gmx_y], mode='markers',
               marker=dict(size=12, color=[gmx_blue], line=dict(width=2)))
)
legend_minvar = \
    'Min-Variance: GMX {:.0%}, GNS {:.0%}'.format(minvar_wt_gmx, minvar_wt_gns)
fig.add_trace(
    go.Scatter(name=legend_minvar, x=[minvar_x], y=[minvar_y], mode='markers',
               marker=dict(size=12, color=[avax_red], line=dict(width=2)))
)

# add a dashed horizontal line across the minvar portfolio
fig.add_hline(y=minvar_y, line_dash="dash", line_color="#c4c3d0")
# add a dashed vertical line across the 100%-GMX portfolio
fig.add_vline(x=gmx_x, line_dash="dash", line_color="#c4c3d0")

# aesthetics
fig.update_layout(
    plot_bgcolor="#f8f8ff", 
    yaxis_tickformat = ',.0%',
    xaxis_tickformat = ',.0%',
    # legend=dict(orientation="h"),
    font=dict(size=18),
    autosize=False,
    width=1200,
    height=600,
)
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e3dac9')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e3dac9')

# render figure
st.plotly_chart(fig, use_container_width=True)

# Observations
st.markdown("- Given a volatility, draw a vertical line, and you want to pick the portfolio at the intersection of the vertical line and the top half of the curve.")
st.markdown("- If you want to mute volatility, the min-variance portfolio (red dot) is a good choice.")
st.markdown("- Read this [article](https://coindataschool.substack.com/p/how-to-best-weigh-gmx-and-gns-in) for more info.")

# --- analyze min-variance portfolios of different start dates --- #

# show resulting figures
st.subheader('Analysis of all min-variance portfolios, each with a different start date')
c1, c2 = st.columns(2)
with c1:
    st.image(Image.open('png/minvar_portfolios_meanrets.png'))
with c2:    
    st.image(Image.open('png/minvar_portfolios_vols.png'))
c3, c4 = st.columns(2)
with c3:
    st.image(Image.open('png/minvar_portfolios_weights_gmx.png'))
with c4:
    st.image(Image.open('png/minvar_portfolios_weights_gns.png'))

# about
st.markdown("""---""")
c1, c2 = st.columns(2)
with c1:
    st.subheader('Get data-driven insights and Learn DeFi analytics')
    st.markdown("- Subscribe to my [newsletter](https://coindataschool.substack.com/about)")
    st.markdown("- Follow me on twitter: [@coindataschool](https://twitter.com/coindataschool)")
    st.markdown("- Follow me on github: [@coindataschool](https://github.com/coindataschool)")
    st.markdown("- Find me on Dune: [@coindataschool](https://dune.com/coindataschool)")
with c2:
    st.subheader('Support my work')
    st.markdown("- Buy me a coffee with ETH: `0x783c5546c863f65481bd05fd0e3fd5f26724604e`")
    st.markdown("- [Tip me sat](https://tippin.me/@coindataschool)")