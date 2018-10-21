from get_prices import valuate_holdings
import matplotlib.pyplot as plt

def main():
    prices = valuate_holdings('holdings.csv')
    Total = prices['value'].sum()
    #print(Total)
    format_total = 'Total Value '+ str(round(Total, 2))


    #pie chart of portfolio
    prices.value.groupby(prices.Type).sum().plot(kind='pie')
    plt.axis('equal')
    plt.text(-1.75, 1.0,format_total)
    plt.show()


main()