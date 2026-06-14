# imports required for the analysis and visualisation of the data and stork market
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm

#using seaborn for visualisation of graph in more clear manner

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")

# installing the real world data of the the stock market 

tickers = [
    
    'AAPL', 'MSFT', 'GOOGL','AMZN', 'NVDA','META','AMD','INTC','IBM','CSCO', # tech
    'JPM', 'BAC', 'WFC','GS','MS','BLK','AXP','C','USB','SCHW',   # financials
    'JNJ', 'PFE', 'UNH','MRK','ABBV','LLY','BMY','AMGN','GILD','MDT',  # healthcare
    'XOM', 'CVX','COP','SLB','CAT','DE','GE','BA','HON','ETN',   # energy
    'WMT', 'COST', 'TGT','KMB',  # consumer
    'MCD', 'NKE', 'SBUX','WMT','COST','PG','KO','PEP','CL','GIS','HSY', # consumer discretionary
    'BA', 'CAT', 'GE',  # industrials
    'VZ', 'T', 'TMUS',  # telecom
    'PLD', 'SPG'       # real estate

] # 63 company data

#adding the market index

tickers.append('SPY')

# download the data for the period of 3 year over the s&r for 500

data = yf.download(tickers , 
                   period = '3y' , 
                   interval = '1d'
                  
)['Close']

print(data.head()) # for check 

# Data cleanning

data = data.dropna(axis=1, thresh=len(data)*0.8) 

# calculate the daly returns

daily_returns = data.pct_change().dropna()

#geting annual volatility which is equal to volatility*(252)^(1/2)
# volatility explain about the amount of fluctuation or in simple words risk
annual_volatility = daily_returns.std()*np.sqrt(252)

#annual return
annual_returns = (1 + daily_returns.mean())**(252)-1

stock_stats = pd.DataFrame({
    'Volatility': annual_volatility,
    'Return': annual_returns
})
#save SPY values
spy_vol = annual_volatility['SPY']
spy_ret = annual_returns['SPY']
#removing spy from stock_stats
stock_stats = stock_stats.drop('SPY')


#grouping the stock according to volatility

#sort by volitility
stock_stats_sorted = stock_stats.sort_values('Volatility')

#split it into three groups 

n_stocks = len(stock_stats_sorted)

low_vol = stock_stats_sorted.iloc[:n_stocks//3]

mid_vol = stock_stats_sorted.iloc[n_stocks//3:2*n_stocks//3]

high_vol = stock_stats_sorted.iloc[2*n_stocks//3:]



print(f"\n Groups:")
print(f"Low volatility: {len(low_vol)} stocks")
print(f"  - Companies: {list(low_vol.index)}")
print(f"  - Vol range: {low_vol['Volatility'].min():.3f} - {low_vol['Volatility'].max():.3f}")
print(f"  - Avg return: {low_vol['Return'].mean():.2%}")


print(f"\nMid volatility: {len(mid_vol)} stocks")
print(f"  - Companies: {list(mid_vol.index)}")
print(f"  - Avg return: {mid_vol['Return'].mean():.2%}")


print(f"\nHigh volatility: {len(high_vol)} stocks")
print(f"  - Companies: {list(high_vol.index)}")
print(f"  - Vol range: {high_vol['Volatility'].min():.3f} - {high_vol['Volatility'].max():.3f}")
print(f"  - Avg return: {high_vol['Return'].mean():.2%}")


print(f"\n📊 Market (SPY):")
print(f"  - Volatility: {spy_vol:.3f}")
print(f"  - Return: {spy_ret:.2%}")

#scatter plot for - volatility vs return
fig1, ax1 = plt.subplots(figsize=(10, 6))

ax1.scatter(low_vol['Volatility'], low_vol['Return'], 
            color='green', label='Low Vol', s=100, alpha=0.7)
ax1.scatter(mid_vol['Volatility'], mid_vol['Return'], 
            color='orange', label='Mid Vol', s=100, alpha=0.7)
ax1.scatter(high_vol['Volatility'], high_vol['Return'], 
            color='red', label='High Vol', s=100, alpha=0.7)
ax1.scatter(spy_vol, spy_ret, color='blue', marker='*', 
            s=300, label='Market (SPY)', edgecolors='black')

# Add trend line
z = np.polyfit(stock_stats['Volatility'], stock_stats['Return'], 1)
p = np.poly1d(z)
x_line = np.array([stock_stats['Volatility'].min(), stock_stats['Volatility'].max()])
ax1.plot(x_line, p(x_line), "k--", alpha=0.5, 
         label=f'Trend: slope = {z[0]:.4f}')

ax1.set_xlabel('Annualized Volatility (Risk)', fontsize=12)
ax1.set_ylabel('Annualized Return', fontsize=12)
ax1.set_title('Tech Stocks: Low Volatility Anomaly', fontsize=14)
ax1.legend()
ax1.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

fig2, ax2 = plt.subplots(figsize=(8, 6))

group_returns = [
    low_vol['Return'].mean(),
    mid_vol['Return'].mean(),
    high_vol['Return'].mean(),
    spy_ret
]
group_names = ['Low Vol', 'Mid Vol', 'High Vol', 'Market (SPY)']
colors_bar = ['green', 'orange', 'red', 'blue']

bars = ax2.bar(group_names, group_returns, color=colors_bar, edgecolor='black')
ax2.set_ylabel('Average Annual Return', fontsize=12)
ax2.set_title('Low Volatility Portfolio Outperforms High Volatility', fontsize=14)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

for bar, value in zip(bars, group_returns):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{value:.2%}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()

#correlation analysis of the volatility vs risk

correlation = stock_stats['Volatility'].corr(stock_stats['Return'])

print("\n"+'-'*50)
print("correlation analysis ")
print('-'*50)
print(f"Correlation between Volatility and Return: {correlation:.4f}")

if correlation < 0:
    print(" NEGATIVE correlation: Higher risk → Lower returns (The Anomaly exists!)")
else:
    print(" POSITIVE correlation: Higher risk → Higher returns (Efficient market)")

# Linear Regression: Return vs Volatility

# X = independent variable (Volatility)
X = stock_stats['Volatility']

# Y = dependent variable (Return)
Y = stock_stats['Return']

# Add constant term (β0)
X = sm.add_constant(X)

# Build regression model
model = sm.OLS(Y, X).fit()

# Print regression summary
print(model.summary())

# Scatter plot with regression line

plt.figure(figsize=(10,6))

sns.regplot(
    x='Volatility',
    y='Return',
    data=stock_stats,
)

plt.title('Return vs Volatility Regression')
plt.xlabel('Annual Volatility')
plt.ylabel('Annual Return')

plt.show()