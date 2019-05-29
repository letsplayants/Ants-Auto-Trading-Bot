#!/bin/bash

nohup python `pwd`/ants/main.py >run_console.out 2>&1 & echo $! >ant.pid
