import unittest
import time

from node import *

if __name__ == "__main__":
    
    # Test to see connection between two nodes
    node1 = node("0.0.0.0", 4000)
    node2 = node("0.0.0.0", 4001)
    
    node1.start()
    node2.start()
    time.sleep(3)

    # Checking same nodes cannot connect with each other
    node1.connect("0.0.0.0", 4000)
    time.sleep(1)

    node1.connect("0.0.0.0", 4001)
    time.sleep(2)

    node1.stop()
    node2.stop()

    node1.join()
    node2.join()
