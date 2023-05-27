from cryptography.fernet import Fernet
import pandas as pd

# 從文件中讀取加密的字節串
with open('encrypted_data.bin', 'rb') as f:
    encrypted_data = f.read()

# 生成密鑰
key = b'your_key_here'

# 用密鑰初始化Fernet對象
fernet = Fernet(key)

# 使用Fernet對象解密字節串
decrypted_data = fernet.decrypt(encrypted_data)

# 將解密的字節串轉換回Excel數據
df = pd.read_csv(io.BytesIO(decrypted_data))

# 將Excel數據寫入文件
df.to_excel('example_decrypted.xlsx', index=False)
