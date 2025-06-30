import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

#defining stock and date range
stock = 'RELIANCE.NS'
start_date = '2023-06-24'
end_date = '2025-06-29'

#download data
data = yf.download(stock, start=start_date, end=end_date, auto_adjust=True)
data.columns = data.columns.get_level_values(0)


#checking if data download was successful
if data.empty:
    print(f"Error: No data downloaded for {stock}. Check ticker or date range")
    exit()

#select close price and drop any NaN values
data = data[['Close', 'Low', 'High']].dropna()
# data.columns = ['Close']
data.reset_index(inplace=True)   #to make date an index


### some learning ###
#calculate SMAs
data['SMA20'] = data['Close'].rolling(window=20).mean()
data['SMA50'] = data['Close'].rolling(window=50).mean()

data = data.dropna(subset=['SMA20', 'SMA50']).copy()

#buy and sell signal logic
# data['Buy_Signal'] = ((data['Close'] < data['SMA20']) & (data['Close'].shift(1) >= data['SMA20'].shift(1))).astype(int)
# data['Sell_Signal'] = ((data['Close'] > data['SMA20']) & (data['Close'].shift(1) <= data['SMA20'].shift(1))).astype(int)

data['Buy_Signal'] = ((data['SMA50'] < data['SMA20']) & (data['SMA50'].shift(1) >= data['SMA20'].shift(1))).astype(int)
data['Sell_Signal'] = ((data['SMA50'] > data['SMA20']) & (data['SMA50'].shift(1) <= data['SMA20'].shift(1))).astype(int)

#backtesting logic
initial_cash = 100000
cash = initial_cash
shares = 0
position = 0
trades = []
portfolio_value = []

for i in range(len(data)):
    portfolio_value.append(cash+ shares * data['Close'].iloc[i])

    #buy signal
    if data['Buy_Signal'].iloc[i] == 1 and position == 0:
        shares = cash // data['Low'].iloc[i]

        if shares > 0:
            cost = shares * data['Close'].iloc[i]
            cash = cash - cost
            position = 1
            trades.append({
                'Date': data['Date'].iloc[i],
                'Type': 'Buy',
                'Price': data['Close'].iloc[i],
                'Shares': shares
            })
            # print(f"Buy on {data['Date'].iloc[i]} at {data['Close'].iloc[i]:.2f} INR, {shares} shares")

    elif data['Sell_Signal'].iloc[i] == 1 and position == 1:

        ### ==== does not work as expected ==== ###
        # #adding condition to sell only if the selling price is higher than the prioe with which the stock was bought
        # last_buy = next((trade for trade in reversed(trades) if trade['Type'] == 'Buy'), None)

        # if last_buy and data['Close'].iloc[i] > last_buy['Price']:
        
        cash += shares * data['High'].iloc[i]
        trades.append({
            'Date': data['Date'].iloc[i],
            'Type': 'Sell',
            'Price': data['Close'].iloc[i],
            'Shares': shares
        })
        # print(f"Sell on {data['Date'].iloc[i]} at {data['Close'].iloc[i]:.2f} INR, {shares} shares")
        position = 0
        shares = 0

#append portfolio value
# portfolio_value.append(cash + shares * data['Close'].iloc[-1])
data['Portfolio_Value'] = portfolio_value


# data = data.reset_index()
data.to_csv('data.csv')
print("Data with SMAs and signals saved to 'data.csv'")

###visualisation
plt.figure(figsize=(10, 5))
plt.plot(data['Date'], data['Close'], label='Close Price', color='blue')
plt.plot(data['Date'], data['SMA20'], label='20-day SMA', color='orange')
plt.plot(data['Date'], data['SMA50'], label='50-day SMA', color='green')

#marking buy signals on plot
buy_signals = data[data['Buy_Signal'] == 1]
plt.scatter(buy_signals['Date'], buy_signals['Close'], label='Buy Signal', color='red', marker='^', s=50)
sell_signals = data[data['Sell_Signal'] == 1]
plt.scatter(sell_signals['Date'], sell_signals['Close'], label='Sell Signal', color= '#00bfff' , marker='v', s=50)

plt.title('Reliance Stock Price with SMA20-SMA50 Crossover Signals')
plt.xlabel('Date')
plt.ylabel('Price (INR)')
plt.legend()
plt.grid(True)
# plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sma_plot.png')
# plt.show()

#portfolio value visualisation
plt.figure(figsize=(10, 5))
plt.plot(data['Date'], data['Portfolio_Value'], label='Portfolio Value', color='purple', linewidth=2)

plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value (INR)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('portfolio_growth.png')
# plt.show()

print(f"\nNumber of Buy Signals: {data['Buy_Signal'].sum()}")
print(f"Number of Sell Signals: {data['Sell_Signal'].sum()}")
# print(f"\nBacktest Summary:")
# print(f"Initial Capital: {initial_cash:.2f} INR")
# print(f"Final Portfolio Value: {portfolio_value[-1]:.2f} INR")
# print(f"Number of Trades: {len(trades) // 2}")

summary_lines = [
    f"Backtest Summary for {stock}",
    f"Date Range: {start_date} to {end_date}",
    f"Initial Capital: {initial_cash:.2f} INR",
    f"Final Portfolio Value: {portfolio_value[-1]:.2f} INR",
    f"Number of Buy Signals: {data['Buy_Signal'].sum()}",
    f"Number of Sell Signals: {data['Sell_Signal'].sum()}",
    f"Number of Completed Trades (Buy+Sell): {len(trades) // 2}",
    "",
    "Trade History:"
]

for trade in trades:
    summary_lines.append(
        f"{trade['Type']} on {trade['Date']} at {trade['Price']:.2f} INR, {trade['Shares']} shares"
    )

with open("summary.txt", "w") as f:
    f.write("\n".join(summary_lines))