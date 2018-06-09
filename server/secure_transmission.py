from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
import socket

class AESmessage:
    def __init__(self,password):
        #key必须是16(24,32)的倍数,这里16足够
        self.key=password[:16]

    def AESEncript(self,msg):
        #return a string
        iv=Random.new().read(AES.block_size)
        cipher=AES.new(self.key,AES.MODE_CFB,iv)
        data=iv+cipher.encrypt(msg)
        return data

    def AESDecrypt(self,msg):
        #msg必须是16的倍数
        #return a string
        iv=msg[:16]
        cipher=AES.new(self.key, AES.MODE_CFB,iv)
        return (cipher.decrypt(msg[16:])).decode()
    

class RSAmessage:
    def __init__(self,newKey=True,pubKey=''):
        if newKey==True:
            #伪随机数生成器
            self.random_generator=Random.new().read
            #rsa算法生成实例
            rsa=RSA.generate(1024,self.random_generator)
            #密钥对生成
            self.priKey=rsa.exportKey()
            self.pubKey=rsa.publickey().exportKey()
        else:
            self.pubKey=pubKey

    def RSAEncrypt(self,msg):
        #公钥加密
        #return a bytes
        rsaKey=RSA.importKey(self.pubKey)
        cipher=Cipher_pkcs1_v1_5.new(rsaKey)
        data=base64.b64encode(cipher.encrypt(msg.encode('utf-8')))
        return data

    def RSADecrypt(self,msg):
        #私钥解密：
        #return a bytes
        rsaKey=RSA.importKey(self.priKey)
        cipher=Cipher_pkcs1_v1_5.new(rsaKey)
        data=cipher.decrypt(base64.b64decode(msg),self.random_generator)
        return data

# 服务器生成RSA公钥、私钥
# 客户端连接后服务端发送公钥到客户端
# 客户端生成DES密钥
# 客户端用RSA公钥加密DES密钥后发送到服务端
# 服务端用RSA私钥解密DES
# 开始用DES密钥加密通信

  
