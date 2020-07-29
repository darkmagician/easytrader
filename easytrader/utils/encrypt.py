
import base64
from Crypto.Cipher import AES
cipher = None


def init_cipher(key):
    global cipher
    while len(key) % 16 != 0:
        key += '\0'
    key = key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)


def encrypt(data):
    bs = AES.block_size

    def pad(s): return (s + (bs - len(s) % bs) * '\0').encode('utf-8')
    encrypt_data = cipher.encrypt(pad(data))
    return base64.b64encode(encrypt_data)


def decrypt(encrypt_data):
    result2 = base64.b64decode(encrypt_data)
    decrypted = cipher.decrypt(result2)
    #print(decrypted)
    return decrypted.decode('utf-8','ignore').rstrip('\0')


if __name__ == '__main__':
    init_cipher('abc')
    encrypted = encrypt('daizzz')
    print(f'encrypted {encrypted}')
    data = decrypt(encrypted)
    print(f'decrypted {data}')
