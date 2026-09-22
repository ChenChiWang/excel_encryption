"""從 LSB 隱寫的 PNG 取出密文，Fernet 解密還原 Excel。

用法:
    python lsb_reveal.py <stego.png> [輸出.xlsx]
"""
import struct
import sys

import numpy as np
from PIL import Image

import common


def extract_lsb(stego_path):
    """由 PNG 的 LSB 讀回密文 bytes（依 4-byte 長度標頭定長取出）。"""
    img = Image.open(stego_path).convert("RGB")
    bits = (np.array(img, dtype=np.uint8).reshape(-1) & 1)

    # 前 32 bits = 4 byte 大端長度標頭
    header = np.packbits(bits[:32]).tobytes()
    (length,) = struct.unpack(">I", header)

    total_bits = (4 + length) * 8
    if total_bits > bits.size:
        raise ValueError("標頭長度超出影像容量，檔案可能損毀或非本工具產生。")

    blob = np.packbits(bits[:total_bits]).tobytes()
    return common.unpack_payload(blob)


def main():
    args = sys.argv[1:]
    if not args:
        print("用法: python lsb_reveal.py <stego.png> [輸出.xlsx]")
        sys.exit(1)

    stego = args[0]
    out = args[1] if len(args) > 1 else "revealed.xlsx"

    key = common.load_key()
    token = extract_lsb(stego)
    common.decrypt_to_file(token, key, out)
    print(f"已取出並解密還原：{out}")


if __name__ == "__main__":
    common.run(main)
