# portfolio-tracking
This project uses the Alpha-vantage API and CoinMarketCap API to find the realtime value of a portfolio made up of stocks and cryptos.

Add all assets to the "portfolio.csv" file in the following format:
Assets,Quantity,Type

Type is either 'crypto' or 'stock'

and a df is returned with the most recent price, along with the sum of all quantity*prices.
