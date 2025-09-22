import pandas as pd
import numpy as np
from statsmodels.api import add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor
from linearmodels.panel import PanelOLS
import warnings
warnings.filterwarnings("ignore")
import os

# ====== 檔案設定 ======
file_path = r"E:\VS Code\0915 Finance\0922 local environ budget.xlsx"
output_path = r"E:\VS Code\0915 Finance\0922 panel_ols_results.xlsx"

# ====== 讀取 Excel ======
if not os.path.exists(file_path):
    raise FileNotFoundError(f"⚠️ Excel 檔案不存在: {file_path}")
df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()
df.replace(['-', '...'], np.nan, inplace=True)

# ====== 將物件型態轉為數字 ======
for col in df.columns:
    if df[col].dtype == object:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ====== 篩選年份 2011-2024 ======
df['Year'] = df['Year'].astype(int)
df = df[(df['Year'] >= 2011) & (df['Year'] <= 2024)]

# ====== 排除特定城市 ======
exclude_codes = [22]
df = df[~df['Code'].isin(exclude_codes)]
print(f"資料筆數：{len(df)}, 年份範圍：{df['Year'].min()}-{df['Year'].max()}")

# ====== 自變數與因變數 ======
dependent_var = "EnvironBudget%_lead"
pollutants = ["AA", "A35", "A43", "A5322t", "A63"]
controls = ["Green_Area", "EnvironBudget%"]
selected_vars = pollutants + controls

# ====== 建立 Panel Data ======
panel_data = df.copy()
panel_data = panel_data.set_index(['Code', 'Year'])

# ====== 移除固定效果吸收的變數 ======
var_keep = [col for col in selected_vars if panel_data.groupby(level='Code')[col].nunique().min() > 1]
selected_vars = var_keep
print(f"保留自變數（避免固定效果吸收）: {selected_vars}")

# ====== 建立 X 與 y ======
X_base = panel_data[selected_vars]
X = add_constant(X_base).astype(float)
y = panel_data[dependent_var].astype(float)

# ====== 清理 NaN ======
XY = pd.concat([X, y], axis=1).dropna()
X = XY.drop(columns=[y.name])
y = XY[y.name]

# ====== Cluster 用 Series，檢查對齊 ======
clusters = pd.Series(XY.index.get_level_values('Code'), index=XY.index)
if len(clusters) != len(y):
    raise ValueError(f"❌ Cluster 長度 {len(clusters)} 與 y 長度 {len(y)} 不一致，請檢查資料對齊")

# ====== 建立 PanelOLS 模型 ======
model_fe = PanelOLS(y, X, entity_effects=True, time_effects=True)

# --- Clustered SE ---
results_fe_clustered = model_fe.fit(cov_type='clustered', clusters=clusters)

# --- Robust SE ---
results_fe_robust = model_fe.fit(cov_type='robust')

# ====== VIF ======
X_for_vif = X_base.loc[XY.index].copy().astype(float)
vif_df = pd.DataFrame({    "Variable": X_for_vif.columns,
    "Variable": X_for_vif.columns,
    "VIF": [variance_inflation_factor(X_for_vif.values, i) for i in range(X_for_vif.shape[1])]
})
print("\n===== 自變數 VIF =====")
print(vif_df)

# ====== 顯示回歸結果 ======
print("\n===== PanelOLS Fixed Effects (Clustered SE) =====")
print(results_fe_clustered.summary)

print("\n===== PanelOLS Fixed Effects (Robust SE) =====")
print(results_fe_robust.summary)

# ====== 輸出 APA 樣式表 ======
def summary_to_apa_panel(results):
    df = results.params.to_frame(name='B')
    df['SE'] = results.std_errors
    df['t'] = results.tstats
    df['p'] = results.pvalues
    df = df.reset_index().rename(columns={'index':'Variable'})
    # 加顯著性標記
    df['Signif'] = df['p'].apply(lambda x: '***' if x<0.01 else '**' if x<0.05 else '*' if x<0.1 else '')
    return df[['Variable','B','SE','t','p','Signif']]

# 生成 APA 表格
apa_clustered = summary_to_apa_panel(results_fe_clustered)
apa_robust = summary_to_apa_panel(results_fe_robust)

print("\n===== APA 樣式表（Clustered SE） =====")
print(apa_clustered)

print("\n===== APA 樣式表（Robust SE） =====")
print(apa_robust)

# ====== 儲存至 Excel ======
with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    apa_clustered.to_excel(writer, sheet_name='APA_Clustered', index=False)
    apa_robust.to_excel(writer, sheet_name='APA_Robust', index=False)
    vif_df.to_excel(writer, sheet_name='VIF')

