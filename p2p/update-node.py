# ############################################
# Writer    : Shawn
# Editor    : Ashish
# Date      : 2023
# Class     : CMSC 626
# Project   : P2P
# ############################################

# Summmary of file:
# Implements the functionalities of nodes/peers in a P2P environment. 
# The nodes/peers establishes connections with other nodes/peers 
# through TCP/IP. 

#import librarys
import threading
import socket
import time
import platform
import json
import sys
import ipaddress
import hashlib
import p2pnetwork

import pickle
import random
from p2pnetwork.nodeconnection import NodeConnection

class node(threading.Thread):
    
    def __init__(self, node_host, node_port, node_id=None, event_callback=None, max_peers=1):

        super().__init__()
        self.stop_event = threading.Event()
        self.node_host = node_host # ip address or hostname of the machine
        self.node_port = node_port # port used by the peer
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
                   node_connection.start()

                   node_id = node_connection.node_id  # assuming NodeConnection has a node_id attribute
                   
                   #self.inbound_nodes[node_id] = (node_connection, address)
                   self.inbound_nodes.add(node_connection)
                   #node_connection.start()
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
        self.sent_messages += 1
        node.send(message)

    def connect(self, node_host, node_port):
        print(f"I am here with node port: {node_port}")
        
        if node_host == self.node_host and node_port == self.node_port:
            print("connect_with_node: Cannot connect with yourself!!")

        for node in self.outbound_nodes:
            if self.node_host == node_host and self.node_port == node_port:
                print(f"Connected with this node {node_host.node_id} already")

        try: 
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((node_host, node_port))
            #connection = socket.create_connection((node_host, node_port))
            node_connection = NodeConnection(self, connection, (node_host, node_port))
            node_connection.start()

            #node_id = node_connection.node_id  # assuming NodeConnection has a node_id attribute
            #self.outbound_nodes[node_id] = (node_connection, (node_host, node_port))
            self.outbound_nodes.add(node_connection)
        
        except Exception as e:
            self._log_debug("Connection failed with node: " + str(e))


    def disconnect(self, node):
        if node in self.outbound_nodes:
            self._log_debug("node disconnecting: " + self.node_id)
            if self.event_callback:
                self.event_callback("disconnect")
            node.stop()
            
    def __str__(self):
        return f'node: {self.node_host}:{self.node_port}'

    def __repr__(self):
        return f'node: {self.node_host}:{self.node_id}:{self.node_id}'
    
