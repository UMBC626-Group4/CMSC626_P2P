import unittest
import time

from node import *

if __name__ == "__main__":
  peer1 = node("0.0.0.0", 4000)
  peer1.run()

  peer2 = node("0.0.0.0", 4001)
  peer2.run()

