# ############################################
# Created by: Josh Li
# Date      : 2023
# Class     : CMSC 626
# Project   : P2P
# ############################################

from cryptography.fernet import Fernet
from nodeconnection import node_connection

class node_connection_encryption(node_connection):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def encrypt_data(self, data):
        try:
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data)
            return encrypted_data
        except Exception as e:
            self.parent_node.debug_message(f"Encryption error: {e}")
            return None

    def decrypt_data(self, encrypted_data):
        try:
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data
        except Exception as e:
            self.parent_node.debug_message(f"Decryption error: {e}")
            return None
