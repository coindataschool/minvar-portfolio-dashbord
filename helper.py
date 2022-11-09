import numpy as np

def calc_portfolio_ret_avg(tokens_mean_rets, weights, ndays_per_year=365):
    # Calculates the annualized average return of a portfolio. 
    #
    # tokens_mean_rets: list, numpy array, or Series
    #    Average daily returns of individual tokens in the portfolio.
    # weights: list or numpy array
    #    Proportion of each token. Sum to 1.
    # ndays_per_year: int
    #    number of trading days in a year.
    return np.dot(tokens_mean_rets, weights) * ndays_per_year

def calc_portfolio_ret_std(tokens_simple_rets, weights, ndays_per_year=365):
    # Calculates the annualized volatility of a portfolio.     
    #
    # tokens_simple_rets: data frame 
    #     Simple daily returns where each column is a token and each row is a date.
    # weights: list, numpy array, or Series
    #     Proportion of each token. Sum to 1.
    # ndays_per_year: int 
    #     number of trading days in a year.
    return np.dot(np.dot(tokens_simple_rets.cov(), weights), weights)**(1/2) * np.sqrt(ndays_per_year) 

def generate_weights(ntokens):
    # Generates portfolio weights randomly.
    #
    # ntokens: number of tokens in the portfolio
    rand = np.random.random(ntokens)
    rand /= rand.sum()
    return rand