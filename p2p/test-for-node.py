import unittest
import time

from update_node import *

if __name__ == "__main__":
    
    # Test to see connection between two nodes
    node1 = node("localhost", 4000)
    node2 = node("localhost", 4001)
    
    node1.start()
    node2.start()
    time.sleep(3)

    total_inbound_nodes_1 = len(node1.inbound_nodes)
    total_outbound_nodes_1 = len(node1.outbound_nodes)
    print(total_inbound_nodes_1)
    print(total_outbound_nodes_1)

    # Checking same nodes cannot connect with each other
    node1.connect("localhost", 4000)
    time.sleep(1)

    node1.connect("localhost", 4001)
    time.sleep(2)

    total_inbound_nodes_2_ = len(node2.inbound_nodes)
    total_outbound_nodes_2_ = len(node2.outbound_nodes)
    print(total_inbound_nodes_2_)
    print(total_outbound_nodes_2_)

    node1.stop()
    node2.stop()

    node1.join()
    node2.join()
