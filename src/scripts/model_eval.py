import pandas as pd
import matplotlib.pyplot as plt
from src.modules.patient import Patient
import os.path as path
import argparse
import yaml

def parse_args():
    parser = argparse.ArgumentParser(description='Pull YAML file entries.')
    parser.add_argument('-c', '--config', required=True, help='Enter location '
                        ' of config file.')
    return parser.parse_args()

def load_config(path):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    args = parse_args()
    config = load_config(args.config)

    script_dir = path.dirname(path.abspath(__file__))
    src_dir = path.dirname(script_dir)
    project_dir = path.dirname(src_dir)


if __name__ == '__main__':
    main()
