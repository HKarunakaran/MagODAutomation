# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 20:04:14 2026

@author: Fradin Group
"""

import pandas as pd

df = pd.read_csv(r"file-name", dtype=str)

print(df.to_string())