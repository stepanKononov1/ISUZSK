from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

# Генерация приватного ключа
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=1024
)

# Экспорт приватного ключа в PEM-формате
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Кодирование приватного ключа в Base64
private_pem_b64 = base64.b64encode(private_pem).decode()

# Генерация публичного ключа
public_key = private_key.public_key()

# Экспорт публичного ключа в PEM-формате
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Кодирование публичного ключа в Base64
public_pem_b64 = base64.b64encode(public_pem).decode()

# Сохранение ключей в файлы (опционально)
with open("private_key.pem", "wb") as private_file:
    private_file.write(private_pem)

with open("public_key.pem", "wb") as public_file:
    public_file.write(public_pem)
