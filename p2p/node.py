# ############################################
# Created by: Shawn
# Date      : 2023
# Class     : CMSC 626
# Project   : P2P
# ############################################

# Summmary of file:
#
#

#import librarys
import threading
import socket
import time
import platform
import json
import sys
import ipaddress
import hashlib

import pickle
import random
from p2pnetwork.nodeconnection import NodeConnection

class node(threading.Thread):

    inbound_nodes = {}
    outbound_nodes = {}
    
    def __init__(self, node_host, node_port, node_id=None, event_callback=None, max_peers=1):

        super().__init__()
        self.stop_event = threading.Event()
        self.node_host = node_host
        self.node_port = node_port
        self.event_callback = event_callback
        self.inbound_nodes = set()
        self.outbound_nodes = set()
        self.retry_nodes = []
        self.node_id = node_id if node_id else self._create_id()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._initialize_server()
        self.sent_messages = 0
        self.received_messages = 0
        self.error_messages = 0
        self.max_peers = max_peers
        self.is_debug = False

    @property
    def all_nodes(self):
        return self.inbound_nodes | self.outbound_nodes

    def _log_debug(self, msg):
        if self.is_debug:
            print(f"DEBUG ({self.node_id}): {msg}")

    def _create_id(self):
        uid = hashlib.sha512()
        random_seed = self.node_host + str(self.node_port) + str(random.randint(1, 1e8))
        uid.update(random_seed.encode('ascii'))
        return uid.hexdigest()

    def _initialize_server(self):
        print(f"Starting the Node on port: {self.node_port} (ID: {self.node_id})")
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.node_host, self.node_port))
        self.server_socket.settimeout(10.0)
        self.server_socket.listen(1)

    def run(self):
    	while not self.stop_event.is_set():
            try:
                connection, address = self.server_socket.accept()
                if len(self.all_nodes) < self.max_peers:
                    self._log_debug(f"Connection from {address}")
                    node_connection = NodeConnection(self, connection, address)
                    node_id = node_connection.node_id  # assuming NodeConnection has a node_id attribute
                    self.inbound_nodes[node_id] = (node_connection, address)
                    node_connection.start()
            except socket.timeout:
                pass
            except Exception as e:
                self._log_debug(f"Error: {e}")

    def stop(self):
        self.stop_event.set()

    def broadcast(self, message):
        for node in self.all_nodes:
            self.send(node, message)

    def send(self, node, message):
        raise NotImplementedError("Send method not implemented yet.")

    def connect(self, node_host, node_port):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((node_host, node_port))
        node_connection = NodeConnection(self, connection, (node_host, node_port))
        node_id = node_connection.node_id  # assuming NodeConnection has a node_id attribute
        self.outbound_nodes[node_id] = (node_connection, (node_host, node_port))
        node_connection.start()

    def __str__(self):
        return f'node: {self.node_host}:{self.node_port}'

    def __repr__(self):
        return f'node: {self.node_host}:{self.node_id}:{self.node_id}'

