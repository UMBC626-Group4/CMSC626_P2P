Class Node(Thread):
    Initialize:
        Set stop_event, node_host, node_port, event_callback, inbound_nodes, outbound_nodes, retry_nodes, node_id, server_socket
        Set sent_messages, received_messages, error_messages, max_peers, is_debug

    Property all_nodes:
        Return union of inbound_nodes and outbound_nodes

    Method _log_debug(msg):
        If is_debug is True:
            Print debug message with node_id and msg

    Method _create_id():
        Create unique identifier using hashlib.sha512
        Update with a random seed based on node_host, node_port, and a random integer
        Return the hexadecimal digest of the hash

    Method _initialize_server():
        Print starting message with node_port and node_id
        Set server_socket options and bind to (node_host, node_port)
        Set server_socket timeout to 10.0 seconds
        Listen for incoming connections

    Method run():
        While stop_event is not set:
            Try:
                Accept incoming connection and retrieve connection, address
                If the number of nodes is less than max_peers:
                    Log debug message about the connection
                    Create NodeConnection with self, connection, and address
                    Add NodeConnection and address to inbound_nodes
                    Start NodeConnection
            Except socket.timeout:
                Continue (do nothing)
            Except Exception as e:
                Log debug message with the error

    Method stop():
        Set stop_event

    Method broadcast(message):
        For each node in all_nodes:
            Call send(node, message)

    Method send(node, message):
        Raise NotImplementedError ("Send method not implemented yet.")

    Method connect(node_host, node_port):
        Create a new socket connection
        Connect to (node_host, node_port)
        Create NodeConnection with self, connection, and (node_host, node_port)
        Add NodeConnection and (node_host, node_port) to outbound_nodes
        Start NodeConnection

    Method __str__():
        Return a string representation of the node in the format 'node: node_host:node_port'

    Method __repr__():
        Return a string representation of the node with additional node_id in the format 'node: node_host:node_id:node_id'
