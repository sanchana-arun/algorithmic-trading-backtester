import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

stock = 'RELIANCE.NS'
data = yf.download(stock, start='2024-06-24', end='2025-06-24')

data = data[['Close']].dropna()

#calculate SMAs
data['SMA20'] = data['Close'].rolling(window=20).mean()
data['SMA50'] = data['Close'].rolling(window=50).mean()

data = data.reset_index()
data.to_csv('data.csv')

#visualisation
plt.figure(figsize=(10, 5))
plt.plot(data['Date'], data['Close'], label='Close Price', color='blue')
plt.plot(data['Date'], data['SMA20'], label='20-day SMA', color='orange')
plt.plot(data['Date'], data['SMA50'], label='50-day SMA', color='green')
plt.title('Reliance Stock Price with 20-day SMA')
plt.xlabel('Date')
plt.ylabel('Price (INR)')
plt.legend()
plt.grid(True)
# plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sma_plot.png')
# plt.show()