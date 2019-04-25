#!/bin/bash

nohup python ants/main.py >run_console.out 2>&1 & echo $! >ant.pid
