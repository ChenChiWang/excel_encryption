from cryptography.fernet import Fernet
import pandas as pd

# 生成密鑰
key = Fernet.generate_key()

# 用密鑰初始化Fernet對象
fernet = Fernet(key)

# 讀取Excel文件
df = pd.read_excel('example.xlsx')

# 將Excel文件轉換為字節串
data = df.to_csv(index=False).encode()

# 使用Fernet對象加密字節串
encrypted_data = fernet.encrypt(data)

# 將加密的字節串寫入文件
with open('encrypted_data.bin', 'wb') as f:
    f.write(encrypted_data)
