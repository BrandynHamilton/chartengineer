import pandas as pd
import matplotlib.cm as cm
from matplotlib.colors import to_hex
import colorcet as cc
import plotly.colors as pc
import random

def clean_values(x, decimals=True, decimal_places=1):
    if isinstance(x, pd.Series):
        return x.apply(clean_values, decimals=decimals, decimal_places=decimal_places)
    
    if x == 0:
        return '0'

    if decimals == True:
        if abs(x) < 1:  # Handle numbers between -1 and 1 first

            return f'{x:.2f}'  # Keep small values with two decimal points
        elif x >= 1e12 or x <= -1e12:

            return f'{x / 1e12:.{decimal_places}f}T'  # Trillion
        elif x >= 1e9 or x <= -1e9:

            return f'{x / 1e9:.{decimal_places}f}B'  # Billion
        elif x >= 1e6 or x <= -1e6:

            return f'{x / 1e6:.{decimal_places}f}M'  # Million
        elif x >= 1e3 or x <= -1e3:

            return f'{x / 1e3:.{decimal_places}f}K'  # Thousand
        elif x >= 1e2 or x <= -1e2:

            return f'{x:.{decimal_places}f}'  # Show as is for hundreds
        elif x >= 1 or x <= -1:

            return f'{x:.{decimal_places}f}'  # Show whole numbers for numbers between 1 and 100
        else:

            return f'{x:.{decimal_places}f}'  # Handle smaller numbers
    else:
        if abs(x) < 1:  # Handle numbers between -1 and 1 first
            return f'{x:.2f}'  # Keep small values with two decimal points
        elif x >= 1e12 or x <= -1e12:
            return f'{x / 1e12:.0f}t'  # Trillion
        elif x >= 1e9 or x <= -1e9:
            return f'{x / 1e9:.0f}b'  # Billion
        elif x >= 1e6 or x <= -1e6:
            return f'{x / 1e6:.0f}m'  # Million
        elif x >= 1e3 or x <= -1e3:
            return f'{x / 1e3:.0f}k'  # Thousand
        elif x >= 1e2 or x <= -1e2:
            return f'{x:.0f}'  # Show as is for hundreds
        elif x >= 1 or x <= -1:
            return f'{x:.0f}'  # Show as is for numbers between 1 and 100
        else:
            return f'{x:.0f}'  # Handle smaller numbers

def colors(shuffle=False):
    # Existing Plotly palettes
    color_palette = pc.qualitative.Plotly[::-1]
    distinct_palette = pc.qualitative.Dark24 + pc.qualitative.Set3
    
    # Add Matplotlib colors
    matplotlib_colors = [to_hex(cm.tab10(i)) for i in range(10)] + \
                        [to_hex(cm.Set1(i)) for i in range(9)]
    
    # Add Colorcet colors
    colorcet_colors = cc.palette['glasbey_dark'] + cc.palette['glasbey_light']

    # Combine all palettes
    lib_colors = distinct_palette + color_palette + matplotlib_colors + colorcet_colors

    if shuffle:
        random.shuffle(lib_colors)
    
    return lib_colors