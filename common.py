"""共用工具：Fernet 金鑰管理、Excel 加解密、LSB payload 打包。

兩套隱寫（LSB / steghide）都先用 Fernet 對稱式加密 Excel 二進位，
再交給各自的隱寫模組藏進圖片。金鑰存成 key.key（已列入 .gitignore）。
"""
import struct
from pathlib import Path

from cryptography.fernet import Fernet

# 預設金鑰檔路徑
KEY_PATH = Path("key.key")


def load_or_create_key(path=KEY_PATH):
    """讀取金鑰；不存在則產生新金鑰並寫檔（加密端用）。"""
    path = Path(path)
    if path.exists():
        return path.read_bytes()
    key = Fernet.generate_key()
    path.write_bytes(key)
    return key


def load_key(path=KEY_PATH):
    """讀取既有金鑰；不存在直接報錯（解密端用）。"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"找不到金鑰檔 {path}，無法解密")
    return path.read_bytes()


def encrypt_file(xlsx_path, key):
    """讀取 Excel 二進位並以 Fernet 加密，回傳密文 bytes。"""
    data = Path(xlsx_path).read_bytes()
    return Fernet(key).encrypt(data)


def decrypt_to_file(token, key, out_path):
    """以 Fernet 解密 token 並寫回 Excel 檔。"""
    data = Fernet(key).decrypt(token)
    Path(out_path).write_bytes(data)


def pack_payload(token):
    """在密文前加 4-byte 大端長度標頭，供 LSB 端定長取回。"""
    return struct.pack(">I", len(token)) + token


def unpack_payload(blob):
    """由 blob 前 4 bytes 讀出長度並回傳對應密文（LSB 端用）。"""
    (length,) = struct.unpack(">I", blob[:4])
    return blob[4:4 + length]


def run(main):
    """執行 main，將預期錯誤轉為簡潔訊息與非零離開碼（非預期錯誤仍拋出）。"""
    import sys

    from cryptography.fernet import InvalidToken

    try:
        main()
    except (RuntimeError, ValueError, FileNotFoundError, InvalidToken) as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        sys.exit(1)
