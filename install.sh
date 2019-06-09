#!/bin/bash

conda create -n question-dependence pip python=3.6 -y
source activate question-dependence
pip install --ignore-installed --upgrade -r requirements.txt
