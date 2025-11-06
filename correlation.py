import pandas as pd

df = pd.read_csv("./dataset/A.csv")


corr = df[['Close', 'Adj Close']].corr(method='pearson')
print(corr)