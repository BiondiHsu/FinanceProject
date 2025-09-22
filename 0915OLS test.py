import numpy as np
import statsmodels.api as sm

# 模擬數據
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])

X = sm.add_constant(x)  # 加上常數項
model = sm.OLS(y, X).fit()
print(model.summary())
