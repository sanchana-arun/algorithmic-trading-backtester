import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

stock = 'RELIANCE.NS'
data = yf.download(stock, start='2024-06-24', end='2025-06-24', auto_adjust = True)

data = data[['Close']].dropna()
data.columns = ['Close']
data.reset_index(inplace=True)

#calculate SMAs
data['SMA20'] = data['Close'].rolling(window=20).mean()
data['SMA50'] = data['Close'].rolling(window=50).mean()

data = data.dropna(subset=['SMA20', 'SMA50']).copy()

#buy when close is lesser than sma20
data.loc[:, 'Buy_Signal'] = (data['Close'] < data['SMA20']).astype(int)

# data = data.reset_index()
data.to_csv('data.csv')

###visualisation
plt.figure(figsize=(10, 5))
plt.plot(data['Date'], data['Close'], label='Close Price', color='blue')
plt.plot(data['Date'], data['SMA20'], label='20-day SMA', color='orange')
plt.plot(data['Date'], data['SMA50'], label='50-day SMA', color='green')

#marking buy signals on plot
buy_signals = data[data['Buy_Signal'] == 1]
plt.scatter(buy_signals['Date'], buy_signals['Close'], label='Buy Signal', color='black', marker='.', s=50)

plt.title('Reliance Stock Price with 20-day SMA')
plt.xlabel('Date')
plt.ylabel('Price (INR)')
plt.legend()
plt.grid(True)
# plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sma_plot.png')
plt.show()