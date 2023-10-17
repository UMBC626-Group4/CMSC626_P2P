import threading
import socket
import json
import base64
import zlib
import bz2
import lzma

def send_data(self, data_payload, encoding_format="utf-8", compression_algorithm='none'):
	try