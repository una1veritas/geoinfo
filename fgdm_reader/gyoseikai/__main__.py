'''
Created on 2026/09/28

@author: sin
'''

import zipfile
with zipfile.ZipFile("/Users/sin/Downloads/FG-GML-kyushu_okinawa-ALL1-20260701-Z001/FG-GML-362430-ALL-20250701.zip", 'r') as z:
    print([name for name in z.namelist() if name.endswith('.xml')])
