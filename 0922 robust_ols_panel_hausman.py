# PanelOLS 完整版：含排除城市、交乘項、小數精度處理 + 小數精度檢查工具 + 選擇性 Quantile Regression + Robust SE 輸出
import os
import pandas as pd
import numpy as np
from statsmodels.api import add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor
from linearmodels.panel import PanelOLS
import warnings
warnings.filterwarnings("ignore")
import os

# ====== 設定檔案路徑 ======
file_path = r"E:\VS Code\0915 Finance\0922 local environ budget.xlsx"
output_path = r"E:\VS Code\0915 Finance\0922 panel_ols_results.xlsx"

# ====== 讀取 Excel ======
if not os.path.exists(file_path):
    raise FileNotFoundError(f"⚠️ Excel 檔案不存在: {file_path}")
else:
    df = pd.read_excel(file_path)

df.columns = df.columns.str.strip()
df.replace(['-', '...'], np.nan, inplace=True)

# 轉換數字欄位
for col in df.columns:
    if df[col].dtype == object:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ====== 篩選年份 ======
df['Year'] = df['Year'].astype(int)
df = df[(df['Year'] >= 2011) & (df['Year'] <= 2024)]

# ====== 排除特定城市 ======
exclude_codes = [22]
df = df[~df['Code'].isin(exclude_codes)]
print(f"資料筆數：{len(df)}, 年份範圍：{df['Year'].min()}-{df['Year'].max()}")

# ====== 設定自變數與因變數 ======
dependent_var = "EnvironBudget%_lead"
pollutants = ["AA", "A35", "A43", "A5322t", "A63"]
controls = ["Green_Area", "EnvironBudget%"]
selected_vars = pollutants + controls

# ====== 建立 Panel Data ======
panel_data = df.copy()
panel_data = panel_data.set_index(['Code', 'Year'])

# 避免固定效果吸收問題：移除在 group 內不變的變數
var_keep = []
for col in selected_vars:
    if panel_data.groupby(level='Code')[col].nunique().min() > 1:
        var_keep.append(col)
selected_vars = var_keep
print(f"保留自變數（避免被固定效果吸收）: {selected_vars}")

# ====== 建立 X 與 y ======
X_base = panel_data[selected_vars]
X = add_constant(X_base).astype(float)
y = panel_data[dependent_var].astype(float)

# ====== 清理 NaN ======
XY = pd.concat([X, y], axis=1).dropna()
X = XY.drop(columns=[y.name])
y = XY[y.name]

# ====== 建立 PanelOLS 模型（固定效果） ======
model_fe = PanelOLS(y, X, entity_effects=True, time_effects=True)

# cluster 轉成 2D DataFrame
clusters = XY.index.get_level_values('Code').to_frame()
results_fe = model_fe.fit(cov_type='clustered', clusters=clusters)
results_fe_robust = model_fe.fit(cov_type='robust')

# clusters 必須是 array-like
clusters = XY.index.get_level_values('Code').to_numpy()  
results_fe = model_fe.fit(cov_type='clustered', clusters=clusters)
results_fe_robust = model_fe.fit(cov_type='robust')

# ====== VIF ======
X_for_vif = X_base.copy().astype(float)
vif_df = pd.DataFrame({
    "Variable": X_for_vif.columns,
    "VIF": [variance_inflation_factor(X_for_vif.values, i) for i in range(X_for_vif.shape[1])]
})
print("\n===== 自變數 VIF =====")
print(vif_df)

# ====== 儲存結果至 Excel ======
with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    results_fe.summary.tables[1].to_excel(writer, sheet_name='Panel_FE_Clustered')
    results_fe_robust.summary.tables[1].to_excel(writer, sheet_name='Panel_FE_Robust')
    vif_df.to_excel(writer, sheet_name='VIF')

print(f"\n✅ PanelOLS 結果已輸出至 {output_path}")
