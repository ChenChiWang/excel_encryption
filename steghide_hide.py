"""將 Excel 檔加密後，用 steghide 藏進 JPEG（外部工具）。

steghide 直接改動 JPEG 的 DCT 係數來藏資料，容量遠小於 LSB。
需先安裝 steghide 並在 PATH 上，或設環境變數 STEGHIDE 指向執行檔。
密碼優先序：-p 參數 > 環境變數 STEGO_PASS。

用法:
    python steghide_hide.py <輸入.xlsx> [載體圖] [輸出.jpg] [-p 密碼]
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import common

DEFAULT_COVER = r"C:/Users/Jelyn/Downloads/photo_2026-09-23_04-18-15.jpg"


def steghide_bin():
    """回傳 steghide 執行檔路徑，找不到回傳 None。"""
    return os.environ.get("STEGHIDE") or shutil.which("steghide")


def embed_steghide(cover, payload, out, passphrase):
    """呼叫 steghide 把 payload 藏進 cover，輸出到 out。"""
    exe = steghide_bin()
    if not exe:
        raise RuntimeError(
            "找不到 steghide，請先安裝，或設定 STEGHIDE 環境變數指向執行檔。"
        )

    fd, emb = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    try:
        Path(emb).write_bytes(payload)
        cmd = [exe, "embed", "-cf", cover, "-ef", emb,
               "-sf", out, "-p", passphrase, "-f"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            msg = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"steghide 嵌入失敗：{msg}")
    finally:
        os.unlink(emb)


def parse_passphrase(args):
    """從參數取出 -p 密碼；沒有則讀 STEGO_PASS，回傳 (passphrase, 位置參數)。"""
    passphrase = os.environ.get("STEGO_PASS")
    rest = []
    i = 0
    while i < len(args):
        if args[i] == "-p" and i + 1 < len(args):
            passphrase = args[i + 1]
            i += 2
        else:
            rest.append(args[i])
            i += 1
    return passphrase, rest


def main():
    passphrase, pos = parse_passphrase(sys.argv[1:])
    if not pos:
        print("用法: python steghide_hide.py <輸入.xlsx> [載體圖] [輸出.jpg] [-p 密碼]")
        sys.exit(1)
    if not passphrase:
        print("錯誤：請以 -p 參數或環境變數 STEGO_PASS 提供 steghide 密碼。")
        sys.exit(1)

    xlsx = pos[0]
    cover = pos[1] if len(pos) > 1 else DEFAULT_COVER
    out = pos[2] if len(pos) > 2 else "stego.jpg"

    key = common.load_or_create_key()
    token = common.encrypt_file(xlsx, key)
    embed_steghide(cover, token, out, passphrase)
    print(f"已加密並以 steghide 藏入：{out}")
    print(f"金鑰檔：{common.KEY_PATH}（解密需要，切勿外流）")
    print(f"密文大小：{len(token)} bytes")


if __name__ == "__main__":
    common.run(main)
