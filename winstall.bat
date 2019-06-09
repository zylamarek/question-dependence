@echo off
PATH = %PATH%;%USERPROFILE%\Miniconda3\Scripts
conda create -n question-dependence pip python=3.6 -y
call activate question-dependence
pip install --ignore-installed --upgrade -r requirements.txt
