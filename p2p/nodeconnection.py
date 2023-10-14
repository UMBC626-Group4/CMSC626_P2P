# ############################################
# Created by: Shawn
# Date      : Tue 2023
# Class     : CMSC 626
# Project   : P2P
# ############################################

# Summmary of file:
#
#


import threading
import socket
import json
import base64
import zlib
import bz2
import lzma

class node_connection(threading.Thread):
    def __init__(self, parent_node, connection_socket, node_id, parent_host, parent_port):
        self.parent_host = parent_host
        self.parent_port = parent_port
        self.parent_node = parent_node
        self.connection_socket = connection_socket
        self.terminate_event = threading.Event()
        self.connected_node_id = str(node_id)
        self.END_OF_TRANSMISSION = 0x04.to_bytes(1, 'big')
        self.COMPRESSION_INDICATOR = 0x02.to_bytes(1, 'big')
        self.additional_info = {}
        self.connection_socket.settimeout(10.0)

        self.parent_node.debug_message(
            f"node_connection: Started with client ({self.connected_node_id}) '{self.parent_host}:{self.parent_port}'")
        super(node_connection, self).__init__()

    def apply_compression(self, data_payload, compression_algorithm):
        compressed_data = data_payload

        try:
            if compression_algorithm == 'zlib':
                compressed_data = base64.b64encode(zlib.compress(data_payload, 6) + b'zlib')
            elif compression_algorithm == 'bzip2':
                compressed_data = base64.b64encode(bz2.compress(data_payload) + b'bzip2')
            elif compression_algorithm == 'lzma':
                compressed_data = base64.b64encode(lzma.compress(data_payload) + b'lzma')
            else:
                self.parent_node.debug_message(f"{self.connected_node_id}: Unknown compression algorithm")
                return None
        except Exception as error:
            self.parent_node.debug_message(f"Compression error: {error}")

        return compressed_data

    def apply_decompression(self, compressed_payload):
        decompressed_data = base64.b64decode(compressed_payload)
        try:
            if decompressed_data[-4:] == b'zlib':
                decompressed_data = zlib.decompress(decompressed_data[:-4])
            elif decompressed_data[-5:] == b'bzip2':
                decompressed_data = bz2.decompress(decompressed_data[:-5])
            elif decompressed_data[-4:] == b'lzma':
                decompressed_data = lzma.decompress(decompressed_data[:-4])
        except Exception as error:
            print(f"Decompression error: {error}")

        return decompressed_data

    def send_data(self, data_payload, encoding_format='utf-8', compression_algorithm='none'):
        try:
            if isinstance(data_payload, str):
                data_payload = data_payload.encode(encoding_format)
            elif isinstance(data_payload, dict):
                data_payload = json.dumps(data_payload).encode(encoding_format)
            elif not isinstance(data_payload, bytes):
                self.parent_node.debug_message('Invalid data type, please use str, dict or bytes')
                return

            if compression_algorithm != 'none':
                compressed_data = self.apply_compression(data_payload, compression_algorithm)
                if compressed_data:
                    self.connection_socket.sendall(compressed_data + self.COMPRESSION_INDICATOR + self.END_OF_TRANSMISSION)
            else:
                self.connection_socket.sendall(data_payload + self.END_OF_TRANSMISSION)
        except Exception as e:
            self.parent_node.debug_message(f"Send data error: {e}")
            self.terminate_connection()

    def terminate_connection(self):
        self.terminate_event.set()

    def interpret_received_packet(self, packet_payload):
        if packet_payload.endswith(self.COMPRESSION_INDICATOR):
            packet_payload = self.apply_decompression(packet_payload[:-1])

        try:
            packet_payload_decoded = packet_payload.decode('utf-8')
            return json.loads(packet_payload_decoded)
        except (UnicodeDecodeError, json.decoder.JSONDecodeError):
            return packet_payload

    def run(self):
        data_buffer = b''
        while not self.terminate_event.is_set():
            try:
                received_chunk = self.connection_socket.recv(4096)
                if received_chunk:
                    data_buffer += received_chunk
                    end_pos = data_buffer.find(self.END_OF_TRANSMISSION)
                    while end_pos > 0:
                        packet = data_buffer[:end_pos]
                        data_buffer = data_buffer[end_pos + 1:]
                        self.parent_node.message_count_recv += 1
                        self.parent_node.process_received_message(self, self.interpret_received_packet(packet))
                        end_pos = data_buffer.find(self.END_OF_TRANSMISSION)
            except (socket.timeout, Exception) as e:
                self.terminate_event.set()
                self.parent_node.debug_message(f"Error in connection thread: {e}")

        self.connection_socket.close()
        self.parent_node.notify_disconnected_node(self)
        self.parent_node.debug_message("node_connection: Stopped")
        
    def set_additional_info(self, key, value):
    	set.additional_info[key] = value
    	
    def get_additonal_info(self, key):
        return self.additional_info.get(key, None)
        
    def get_connection_string(self):
        return (f'node_connection: {self.main_node_address}:{self.main_node_port} <-> '
            f'{self.connected_host}:{self.connected_port} (Node ID: {self.connected_node_id})')

    def get_detailed_representation(self):
        return (f'<node_connection: Main Node {self.main_node_address}:{self.main_node_port} <-> '
            f'Connected Node {self.connected_host}:{self.connected_port}>')

    def generate_hash_from_node_ids(self):
        return hash(f'{self.main_node_id}{self.connected_node_id}')

    def are_nodes_equal(self, other_node):
        return self.main_node == other_node.main_node and self.connected_node_id == other_node.connected_node_id
