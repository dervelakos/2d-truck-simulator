#!/bin/bash
source /opt/ros/jazzy/setup.bash
source env/bin/activate
#./src/Main.py --graphics --ros
#./src/Main.py --graphics --ros --comm --scenario scenarios/campain-1.yaml
./src/Main.py --graphics --comm --scenario scenarios/campain-1.yaml
