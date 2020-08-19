#!/usr/bin/python
# -*- coding: UTF-8 -*-
import argparse
import sys
import configobj

parser = argparse.ArgumentParser()
parser.add_argument('cfg')
args = parser.parse_args()
if not args.cfg:
    print("config file is not provided")
    sys.exit(2)
_config = configobj.ConfigObj(args.cfg, interpolation=False)
root = _config['General']['root']
sys.path.append(root)

