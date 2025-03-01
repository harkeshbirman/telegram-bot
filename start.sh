#!/bin/bash

python -m venv env

source env/bin/activate 

pip install -r requirements.txt 

python -u main.py 

deactivate
