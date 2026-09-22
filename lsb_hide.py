"""將 Excel 檔加密後，用 LSB 隱寫藏進圖片，輸出無損 PNG。

LSB（最低位元）把密文一個 bit 一個 bit 寫進每個像素通道的最低位。
輸出必須是 PNG：JPEG 是有損壓縮會破壞最低位元，等同毀掉藏的資料。

用法:
    python lsb_hide.py <輸入.xlsx> [載體圖] [輸出.png]
"""
import sys

import numpy as np
from PIL import Image

import common

# 預設載體圖（可用第 2 個參數覆蓋）
DEFAULT_COVER = r"C:/Users/Jelyn/Downloads/photo_2026-09-23_04-18-15.jpg"


def embed_lsb(cover_path, payload, out_path):
    """把 payload bytes 藏進載體圖的 LSB，存成 PNG。"""
    img = Image.open(cover_path).convert("RGB")
    arr = np.array(img, dtype=np.uint8)  # 可寫副本
    shape = arr.shape
    flat = arr.reshape(-1)

    capacity = flat.size // 8  # 每個通道位元組藏 1 bit
    if len(payload) > capacity:
        raise ValueError(
            f"載體容量不足：需藏 {len(payload)} bytes，此圖最多 {capacity} bytes。"
            "請換更大／更高解析度的載體圖。"
        )

    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
    flat[:bits.size] = (flat[:bits.size] & 0xFE) | bits
    Image.fromarray(flat.reshape(shape), "RGB").save(out_path, "PNG")


def main():
    args = sys.argv[1:]
    if not args:
        print("用法: python lsb_hide.py <輸入.xlsx> [載體圖] [輸出.png]")
        sys.exit(1)

    xlsx = args[0]
    cover = args[1] if len(args) > 1 else DEFAULT_COVER
    out = args[2] if len(args) > 2 else "stego.png"

    key = common.load_or_create_key()
    token = common.encrypt_file(xlsx, key)
    payload = common.pack_payload(token)
    embed_lsb(cover, payload, out)
    print(f"已加密並以 LSB 藏入：{out}")
    print(f"金鑰檔：{common.KEY_PATH}（解密需要，切勿外流）")
    print(f"密文大小：{len(token)} bytes")


if __name__ == "__main__":
    common.run(main)
