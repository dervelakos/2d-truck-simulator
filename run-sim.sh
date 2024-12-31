#!/bin/bash
source /opt/ros/jazzy/setup.bash
source env/bin/activate
#./src/Main.py --graphics --ros
./src/Main.py --graphics --ros --scenario scenarios/campain-1.yaml
