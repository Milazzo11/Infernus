"""
Configuration file parser.

:author: Max Milazzo
"""


import yaml


with open("config.yaml", "r") as f:
  CONFIG = yaml.safe_load(f)