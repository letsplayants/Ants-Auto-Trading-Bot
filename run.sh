#!/bin/bash

source `pwd`/ants-env/bin/activate
nohup python `pwd`/process_monitor.py >run_console.out 2>&1 & echo $! >ant.pid
