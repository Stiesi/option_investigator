
import requests

url='https://www.boerse-frankfurt.de/en/etf/ishares-em-dividend-ucits-etf-usd-dist/price-history/historical-prices-and-volumes?currency=EUR'
response = requests.get(url)

print(response.text)
