# Excel 隱寫（Steganography）

把 Excel 檔先用 **Fernet 對稱式加密**，再用隱寫術藏進圖片。提供兩套技術：

| 技術 | 腳本 | 載體 → 輸出 | 特性 |
|------|------|------------|------|
| **LSB**（最低位元） | `lsb_hide.py` / `lsb_reveal.py` | 任意圖 → **PNG** | 純 Python，容量大；輸出必須無損 PNG |
| **steghide** | `steghide_hide.py` / `steghide_reveal.py` | JPEG → **JPEG** | 需外部工具，容量小，需密碼 |

共用邏輯集中在 `common.py`（金鑰管理、加解密、payload 打包、錯誤包裝）。

## 流程

```
Excel(.xlsx) --讀二進位--> Fernet 加密 --> 密文 --隱寫藏入--> 帶密圖
帶密圖 --隱寫取出--> 密文 --Fernet 解密--> 還原 Excel(.xlsx)
```

先加密再隱寫：即使有人察覺並取出藏的資料，沒有金鑰仍無法還原內容。

## 相依

```
pip install cryptography pillow numpy
```

steghide 版另需安裝 steghide 執行檔：

- Windows（系統管理員 PowerShell）：`choco install steghide -y`
- 或下載 win32 執行檔後，設環境變數 `STEGHIDE` 指向它（免動 PATH）。

## 用法

### LSB
```
python lsb_hide.py   <輸入.xlsx> [載體圖] [輸出.png]
python lsb_reveal.py <stego.png> [輸出.xlsx]
```

### steghide
```
python steghide_hide.py   <輸入.xlsx> [載體圖] [輸出.jpg] -p <密碼>
python steghide_reveal.py <stego.jpg> [輸出.xlsx]      -p <密碼>
```

密碼也可用環境變數 `STEGO_PASS` 提供；未指定載體圖時會用腳本內的預設路徑。

## 容量

- **LSB 容量** ≈ `寬 × 高 × 3 ÷ 8` bytes。
- **Fernet 加密後膨脹約 37%**（base64 編碼）：295 KB 的 Excel 加密後約 393 KB。
- **steghide 藏進 JPEG 的容量遠小於 LSB**，通常只有幾十 KB，取決於影像 DCT 係數；
  裝好後可用 `steghide info <圖>` 查實際容量。

實測（藏 295 KB Excel，加密後約 393 KB）：

| 載體圖 | 尺寸 | LSB 容量 | LSB 可行 |
|--------|------|----------|----------|
| 1024×1280 JPEG | 1024×1280 | 480 KB | 是（用掉約 82%） |
| 960×1280 JPEG | 960×1280 | 450 KB | 是（用掉約 87%，較緊） |

大檔（數百 KB）建議走 LSB；steghide 版適合小檔，或需搭配高解析無損載體（如大尺寸 BMP）。

## 注意

- **金鑰**存於 `key.key`，解密端必須用同一把；已列入 `.gitignore`，切勿外流或進 git。
- **LSB 輸出只能是 PNG**：JPEG 有損壓縮會破壞藏在最低位元的資料。
- 載體容量不足時腳本會直接報「容量不足」並中止。
