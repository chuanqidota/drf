from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.hashes import SHA256
import os


class Signer:
    """
    用来加密,解密,和基于时间戳的方式验证token
    """

    def __init__(self, key=None):
        """
            初始化
        :param key: 盐
        """
        self.fnt = Fernet(key)

    @staticmethod
    def make_key():
        """
            生成一个随机字符串
        """
        return Fernet.generate_key().decode("utf-8")

    @staticmethod
    def generate_key():
        """
            生成随机key
        """
        return base64.urlsafe_b64encode(os.urandom(32))

    def encrypt(self, dat):
        """
        加密
        :param dat: bytes or string
        :return: string
        """
        if isinstance(dat, str):
            dat = dat.encode('utf-8')
        assert isinstance(dat, bytes), 'The argument `dat` must be a bytes or a string.'
        return self.fnt.encrypt(dat).decode('utf-8')

    def decrypt(self, dat):
        """
        解密
        若dat非encrypt加密的数据，会抛出异常：
            cryptography.fernet.InvalidToken
        :param dat: bytes or string
        :return: string
        """
        if isinstance(dat, str):
            dat = dat.encode('utf-8')
        assert isinstance(dat, bytes), 'The argument `dat` must be a bytes or a string.'
        return self.fnt.decrypt(dat).decode('utf-8')


class Signer2:
    """
        通过公钥私钥来解密数据
        以及签名
    """

    @staticmethod
    def make_private_and_public_key():
        """
            生成密钥对
        :return:
            私钥 用于解密数据
            公钥 用于加密数据
        """
        private_key = generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # 将私钥转换为PEM格式的字符串
        pem_private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        # 将公钥转换为PEM格式的字符串
        pem_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        return pem_private_key, pem_public_key

    @staticmethod
    def encrypt_from_pem(plaintext, pem_public_key):
        """
            使用PEM格式的公钥加密数据
        :param plaintext: 明文数据
        :param pem_public_key: PEM格式的公钥字符串
        :return: 加密后的数据
        """
        public_key = serialization.load_pem_public_key(
            pem_public_key.encode('utf-8'),
            backend=default_backend()
        )
        encrypted_data = public_key.encrypt(
            plaintext.encode("utf-8"),
            OAEP(
                mgf=MGF1(SHA256()),
                algorithm=SHA256(),
                label=None
            )
        )
        return encrypted_data

    @staticmethod
    def decrypt_from_pem(ciphertext, pem_private_key):
        """
            使用PEM格式的私钥解密数据
        :param ciphertext: 加密后的数据
        :param pem_private_key: PEM格式的私钥字符串
        :return: 解密后的数据
        """
        private_key = serialization.load_pem_private_key(
            pem_private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        decrypted_data = private_key.decrypt(
            ciphertext,
            OAEP(
                mgf=MGF1(SHA256()),
                algorithm=SHA256(),
                label=None
            )
        )
        return decrypted_data.decode()

    @staticmethod
    def sign_data(message, pem_private_key):
        """
            使用PEM格式的私钥对给定消息进行签名
        :param message: 需要签名的消息
        :param pem_private_key: PEM格式的私钥
        :return:
        """
        # 加载PEM格式的私钥
        private_key = serialization.load_pem_private_key(
            pem_private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        # 使用私钥、PSS填充方式和SHA256散列函数对消息进行签名
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    @staticmethod
    def verify_signature(message, signature, pem_public_key):
        """
            验证给定消息的数字签名是否由对应的私钥生成
        :param message: 需要验证签名的原始消息字符串
        :param signature: 消息对应的数字签名
        :param pem_public_key: 公钥，用于验证签名，格式为PEM
        :return:
        """
        public_key = serialization.load_pem_public_key(
            pem_public_key.encode('utf-8'),
            backend=default_backend()
        )
        try:
            public_key.verify(
                signature,
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False


if __name__ == '__main__':
    # 对称加密
    _key = Signer.make_key()
    _dat = "1a!晋"
    print("加密后:", Signer(_key).encrypt(_dat))
    print("解密后:", Signer(_key).decrypt(Signer(_key).encrypt(_dat)))

    # 非对称加密
    _private_key, _public_key = Signer2.make_private_and_public_key()
    print("私钥:", _private_key)
    print("公钥:", _public_key)
    _encrypted_data = Signer2.encrypt_from_pem(_dat, _public_key)
    print("加密后的数据:", _encrypted_data)
    print("解密后的数据:", Signer2.decrypt_from_pem(_encrypted_data, _private_key))

    # 签名
    message = "This is a test message."
    pem_private_key, pem_public_key = Signer2.make_private_and_public_key()
    signature = Signer2.sign_data(message, pem_private_key)
    print("签名:", signature)
    # 假设你有一个签名，你想验证它
    is_valid = Signer2.verify_signature(message, signature, pem_public_key)
    print(f"Signature is valid: {is_valid}")
