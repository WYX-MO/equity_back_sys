import hashlib
import os
import binascii

def hash_numeric_password(password: str) -> str:
    """
    对数字密码进行简单哈希加密
    适用于对安全性要求不高的场景
    """
    # 确保输入是纯数字
    if not password.isdigit():
        raise ValueError("密码必须是纯数字")
    
    # 使用SHA-256进行哈希
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

def salted_hash_password(password: str) -> tuple:
    """
    带盐值的数字密码加密（更安全）
    返回加密后的哈希值和盐值
    """
    if not password.isdigit():
        raise ValueError("密码必须是纯数字")
    
    # 生成随机盐值（16字节）
    salt = os.urandom(16)
    
    # 结合盐值进行哈希
    sha256 = hashlib.sha256()
    sha256.update(salt + password.encode('utf-8'))
    hashed = sha256.digest()
    
    # 将盐值和哈希值转换为十六进制字符串返回
    return (binascii.hexlify(hashed).decode('utf-8'), 
            binascii.hexlify(salt).decode('utf-8'))

def verify_salted_password(password: str, hashed: str, salt: str) -> bool:
    """验证带盐值加密的密码"""
    if not password.isdigit():
        return False
    
    # 将盐值从十六进制转回字节
    salt_bytes = binascii.unhexlify(salt)
    
    # 重新计算哈希
    sha256 = hashlib.sha256()
    sha256.update(salt_bytes + password.encode('utf-8'))
    new_hash = binascii.hexlify(sha256.digest()).decode('utf-8')
    
    # 比较哈希值
    return new_hash == hashed

# 示例用法
if __name__ == "__main__":
    # 原始数字密码
    numeric_password = "123456"
    
    # 简单哈希加密
    simple_hash = hash_numeric_password(numeric_password)
    print(f"简单哈希加密结果: {simple_hash}")
    
    # 带盐值加密
    hashed_pwd, salt = salted_hash_password(numeric_password)
    print(f"带盐值加密结果: {hashed_pwd}")
    print(f"盐值: {salt}")
    
    # 验证密码
    is_valid = verify_salted_password("123456", hashed_pwd, salt)
    print(f"密码验证结果（正确密码）: {is_valid}")
    
    is_valid_wrong = verify_salted_password("654321", hashed_pwd, salt)
    print(f"密码验证结果（错误密码）: {is_valid_wrong}")
    