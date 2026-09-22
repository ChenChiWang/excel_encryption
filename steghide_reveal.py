"""用 steghide 從 JPEG 取出密文，Fernet 解密還原 Excel。

密碼優先序：-p 參數 > 環境變數 STEGO_PASS。

用法:
    python steghide_reveal.py <stego.jpg> [輸出.xlsx] [-p 密碼]
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import common

from steghide_hide import parse_passphrase, steghide_bin


def extract_steghide(stego, passphrase):
    """呼叫 steghide 取出藏入的密文 bytes。"""
    exe = steghide_bin()
    if not exe:
        raise RuntimeError(
            "找不到 steghide，請先安裝，或設定 STEGHIDE 環境變數指向執行檔。"
        )

    fd, out_bin = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    try:
        cmd = [exe, "extract", "-sf", stego, "-xf", out_bin, "-p", passphrase, "-f"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            msg = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"steghide 取出失敗：{msg}")
        return Path(out_bin).read_bytes()
    finally:
        os.unlink(out_bin)


def main():
    passphrase, pos = parse_passphrase(sys.argv[1:])
    if not pos:
        print("用法: python steghide_reveal.py <stego.jpg> [輸出.xlsx] [-p 密碼]")
        sys.exit(1)
    if not passphrase:
        print("錯誤：請以 -p 參數或環境變數 STEGO_PASS 提供 steghide 密碼。")
        sys.exit(1)

    stego = pos[0]
    out = pos[1] if len(pos) > 1 else "revealed.xlsx"

    key = common.load_key()
    token = extract_steghide(stego, passphrase)
    common.decrypt_to_file(token, key, out)
    print(f"已取出並解密還原：{out}")


if __name__ == "__main__":
    common.run(main)
