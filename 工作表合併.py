import pandas as pd

df = pd.read_excel(r"C:\Users\biond\OneDrive - 長榮大學\桌面\Chinese Database.xlsx")


# 定義正確的 Excel 檔案路徑
file_path = r"C:\Users\biond\OneDrive - 長榮大學\桌面\Chinese Database.xlsx"

# 讀取兩個工作表
sheet_Merger = pd.read_excel(file_path, sheet_name='2018')
sheet_2019 = pd.read_excel(file_path, sheet_name='2019')

# 根據 Index 和 Year 進行合併
# 以 sheet_Merger 工作表為主表
merged_data = pd.merge(sheet_Merger, sheet_2019, on=['City-En'], how='left')

# 將合併結果寫回到 sheet_Merger 工作表中
with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='replace') as writer:
    merged_data.to_excel(writer, sheet_name='2019new', index=True)

print("合併完成，結果已寫入 Temp 工作表中。")