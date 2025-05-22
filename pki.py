"""
"""


import os
from crypto.symmetric import SKE
from crypto.asymmetric import AKE


KEY_DIR = "keys"


PRIV_FILE = "priv.key"


PUB_FILE = "pub.key"


# Encrypted ZIP file format:
# ==========================
# first 4 bytes -- specifies length of following PKI-encrypted one-time symmetic key
# next N bytes  -- encrypted symmetric key
# next M bytes  -- encrypted data (using symmetric key)


def setup():
    """
    """

    pki_cipher = AKE()

    with open(os.path.join(KEY_DIR, PRIV_FILE), "wb") as f:
        f.write(pki_cipher.private_key)
    
    with open(os.path.join(KEY_DIR, PUB_FILE), "wb") as f:
        f.write(pki_cipher.public_key)
    

def encrypt(zip_file, public_key = None):
    """
    """

    if public_key is None:
        with open(os.path.join(KEY_DIR, PUB_FILE), "rb") as f:
            public_key = f.read()

    pki_cipher = AKE(public_key=public_key)
    ske_cipher = SKE()

    with open(zip_file, "rb") as f:
        plaintext_data = f.read()

    encrypted_data = ske_cipher.encrypt(plaintext_data, byte_output=True)
    # encrypt file data using symmetric key

    encrypted_sym_key = pki_cipher.encrypt(ske_cipher.key, byte_output=True)
    # encrypt symmetric key using supplied public key

    with open(zip_file + ".enc", "wb") as f:
        f.write(len(encrypted_sym_key).to_bytes(4, "big"))
        f.write(encrypted_sym_key)
        f.write(encrypted_data)
        # write data to encrypted zip file
    
    
def decrypt(enc_file: str):
    """
    """

    with open(os.path.join(KEY_DIR, PRIV_FILE), "rb") as f:
        private_key = f.read()

    pki_cipher = AKE(private_key=private_key)

    with open(enc_file, "rb") as f:
        length_bytes = f.read(4)
        sym_key_len = int.from_bytes(length_bytes, "big")
        # read first 4 bytes to get length of encrypted symmetric key

        encrypted_sym_key = f.read(sym_key_len)
        # read encrypted symmetric key

        encrypted_data = f.read()
        # read the rest as encrypted data

    symmetric_key = pki_cipher.decrypt(encrypted_sym_key, byte_output=True)
    # decrypt the symmetric key using the private key

    ske_cipher = SKE(key=symmetric_key, iv=b"0" * 16)
    plaintext_data = ske_cipher.decrypt(encrypted_data, byte_output=True)
    # extract original file data

    zip_file = enc_file.rsplit(".", 1)[0]

    with open(zip_file, "wb") as f:
        f.write(plaintext_data)
        # write decrypted zip file


#setup()
#encrypt("test.zip")
#decrypt("test.zip.enc")