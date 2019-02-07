#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
# sys.path.append(".")
# print (os.getcwd())
print (sys.path)

import alogger
from arbitrage.worker import Worker


if __name__ == "__main__":
    w = Worker()
    w.run()
    pass
