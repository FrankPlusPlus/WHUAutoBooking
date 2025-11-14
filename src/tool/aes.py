import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_ac(ac_data, key_hex, iv_str):
    try:
        # 提取 Base64 部分
        encrypted_b64 = ac_data.split("#")[1]
        
        # 补全 Base64 的 '='
        padding = 4 - (len(encrypted_b64) % 4)
        encrypted_b64 += "=" * padding
        encrypted_data = base64.b64decode(encrypted_b64)
        
        # 检查长度并手动填充（如果需要）
        if len(encrypted_data) % 16 != 0:
            encrypted_data = pad(encrypted_data, AES.block_size)
        
        # 初始化 AES
        key = bytes.fromhex(key_hex)
        iv = iv_str[:16].encode("utf-8")  # 取前16字节作为 IV
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # 解密并去除填充
        decrypted = cipher.decrypt(encrypted_data)
        decrypted = unpad(decrypted, AES.block_size)
        return decrypted.decode("utf-8", errors="ignore")
    except Exception as e:
        print("解密失败:", str(e))
        return None

# 示例
ac = "5293#m8Xnj7fQ4388PJrjXX/X3Lq+M28X0Xuf+PTVWPIGsE7zJ6V04NC9sNay4hbLkE7SWNTwW6CCOAcNOh72f64cWt7xkATcJY7yODTC+62KfDvcf/cyFjX2vNutO6uUkw22vNTC41/gIw3wZY22Ih2wZrur+PTVWPIGsE7zJ6V04NC9sNay4hbLkE7SWNTwW6CCOAcNOh5K41cL+NaVFuZ/sj/dIwXVIRyoZ/QE6ROZf/7nfw49TznVT6WNTVg2ZLW2Zjn5ZL89URfNsPv/hN5ofNuwj8Xs5OzC1kplfoQYDIS1XX37m2X3h/cvhT3Xm3CEk/SsXYPMGQHrVUPR5S+wrGYmoZPcdURDQfUNVUHaQ5jLVKsa74VnXmR6MAmRUxuE4wnXOlWNHN/KZyby725Xv8XXYU8XOrrVXZrL2BSkY5UL1VIsKCQLhMQkpdpRnBxjhqUkKSyIXYkj25msI3MRin2L7Wo2HUypuPJaO53Wn8FaXX6fc73J/F2l3LwFIrfXXRyiXkVNLHk/SIAbVkh6enqeGQHto51yziEZtFB+AZzg0fppqbFNQBP/c+U12BD8qZ0KM0FTB4Kx2iDhSoNBtKzRgfRxMsH/Q4AgA+epdBdTg7PKApU0tlRjQbBbMBFmbokVNFlhb7kt0Qp9VlkUGZkzVpFaGZD7NqFRoo+pLs+/pbUztl+vq5RrAkkhpgN6xBeaSIqzEppkqghMdG+kq5eQEiHh0ZD5EUAUqg+M2qshSoJ9ApKmqI699sF6K7zNyp03o4KNAKN35O+7wiss7xj7zUp2rQBbVHUslOUEcqJsl4jttFzZKZRNzKt5teBIpZN7AqPaxbidAGzHeWteMlFZpOpCrq+69BsYKbGQeolL9HjYgx0BNpAQEslnqOzxwFGIq40eLKq+Kb+rLJtWGIzq0xpxAGqI0xpSGWLGpINLtpJ1bS+Ly+PYeoKgwKeOzkEipvN0zkEswp0fAKqXqWhV9ksDgoj2cF6m5INbds0JKgEIlOpxNkLHpozodxLMzBpJ7oFMQbUN2lFixSUMrq+/xZYxNktOlpGsKW0pdUGsKsNflKLv7IzytJwHAeKIwGe/0OjrrJ+jeQAeteeie5d2"
key = "635a429a5f66919cef86083594bdd722"
iv = "68f771b3T1EiyYPFHEkZERIgK83WSl3l7RUPMnB1"

result = decrypt_ac(ac, key, iv)
print("解密结果:", result)