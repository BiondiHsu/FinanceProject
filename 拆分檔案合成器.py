from PIL import Image
import os
from PyPDF2 import PdfMerger

# 定義來源資料夾和輸出檔案
input_folder = r"C:\Users\biond\OneDrive - 長榮大學\桌面\Sage Open\Merger"
output_pdf = os.path.join(input_folder, "Combined_output.pdf")

# 獲取資料夾內的所有圖片檔案和 PDF 檔案
image_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
pdf_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

# 確保按檔名排序
image_files.sort()
pdf_files.sort()

# 確保資料夾內有可用的檔案
if not image_files and not pdf_files:
    print("資料夾內沒有可用的圖片或 PDF 檔案，無法合併。")
else:
    # 合併圖片檔案為 PDF
    temp_image_pdf = None
    if image_files:
        try:
            with Image.open(image_files[0]) as first_image:
                # 確保圖片為 RGB 格式
                first_image = first_image.convert("RGB")

                # 開啟其餘圖片並轉換為 RGB 格式
                additional_images = []
                for file in image_files[1:]:
                    try:
                        with Image.open(file) as img:
                            additional_images.append(img.convert("RGB"))
                    except Exception as e:
                        print(f"無法處理圖片檔案：{file}，錯誤：{e}")

                # 儲存圖片為臨時 PDF
                temp_image_pdf = os.path.join(input_folder, "temp_images.pdf")
                if additional_images:
                    first_image.save(temp_image_pdf, save_all=True, append_images=additional_images)
                else:
                    first_image.save(temp_image_pdf)
                print(f"已將圖片合併為臨時 PDF：{temp_image_pdf}")
        except Exception as e:
            print(f"處理圖片檔案時發生錯誤：{e}")

    # 合併所有 PDF（包括圖片生成的臨時 PDF 和原始 PDF 檔案）
    merger = PdfMerger()
    try:
        # 合併圖片生成的臨時 PDF
        if temp_image_pdf:
            merger.append(temp_image_pdf)

        # 合併原始 PDF 檔案
        for pdf in pdf_files:
            try:
                merger.append(pdf)
            except Exception as e:
                print(f"無法合併 PDF 檔案：{pdf}，錯誤：{e}")

        # 儲存最終合併的 PDF
        merger.write(output_pdf)
        merger.close()
        print(f"已將所有檔案合併為 PDF：{output_pdf}")
    except Exception as e:
        print(f"合併 PDF 檔案時發生錯誤：{e}")
    finally:
        # 刪除臨時 PDF（如果存在）
        if temp_image_pdf and os.path.exists(temp_image_pdf):
            os.remove(temp_image_pdf)
            print(f"已刪除臨時 PDF：{temp_image_pdf}")