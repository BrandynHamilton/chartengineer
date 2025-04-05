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
            print(f'x < 1:{x}')
            return f'{x:.2f}'  # Keep small values with two decimal points
        elif x >= 1e12 or x <= -1e12:
            print(f'x:{x}T')
            return f'{x / 1e12:.{decimal_places}f}T'  # Trillion
        elif x >= 1e9 or x <= -1e9:
            print(f'x:{x}B')
            return f'{x / 1e9:.{decimal_places}f}B'  # Billion
        elif x >= 1e6 or x <= -1e6:
            print(f'x:{x}M')
            return f'{x / 1e6:.{decimal_places}f}M'  # Million
        elif x >= 1e3 or x <= -1e3:
            print(f'x:{x}k')
            return f'{x / 1e3:.{decimal_places}f}K'  # Thousand
        elif x >= 1e2 or x <= -1e2:
            print(f'x:{x}')
            return f'{x:.{decimal_places}f}'  # Show as is for hundreds
        elif x >= 1 or x <= -1:
            print(f'x:{x}')
            return f'{x:.{decimal_places}f}'  # Show whole numbers for numbers between 1 and 100
        else:
            print(f'x:{x}')
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

# def add_annotations(self, custom_annotations=None):
#     if datetime_tick:
#         last_text = f'{df.index[-1].strftime(datetime_format)}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
#     else:
#         last_text = f'{df.index[-1]}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

#     # Handling the first value annotation
#     if datetime_tick:
#         first_text = f'{df.index[0].strftime(datetime_format)}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[0], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
#     else:
#         first_text = f'{df.index[0]}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[0], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

#     # Adding annotations for first and last value
#     if annotations:
#         # Last value annotation
#         fig.add_annotation(dict(
#             x=df.index[-1],
#             y=df[y1_col].iloc[-1],
#             text=last_text,
#             showarrow=True,
#             arrowhead=2,
#             arrowsize=1.5,
#             arrowwidth=1.5,
#             ax=-100,
#             ay=-50,
#             font=dict(size=text_font_size, family=font_family, color=font_color),
#             xref='x',
#             yref='y',
#             arrowcolor='black'
#         ))

#         # First value annotation
#         fig.add_annotation(dict(
#             x=df.index[0],
#             y=df[y1_col].iloc[0],
#             text=first_text,
#             showarrow=True,
#             arrowhead=2,
#             arrowsize=1.5,
#             arrowwidth=1.5,
#             ax=100,
#             ay=-50,
#             font=dict(size=text_font_size, family=font_family, color=font_color),
#             xref='x',
#             yref='y',
#             arrowcolor='black'
#         ))

#     # Handling the maximum value annotation
#     if max_annotation:
#         max_value = df[y1_col].max()
#         max_index = df[df[y1_col] == max_value].index[0]  # Get the index where the maximum value occurs

#         if datetime_tick:
#             max_text = f'{max_index.strftime(datetime_format)}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(max_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""} (ATH)'
#         else:
#             max_text = f'{max_index}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(max_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

#         fig.add_annotation(dict(
#             x=max_index,
#             y=max_value,
#             text=max_text,
#             showarrow=True,
#             arrowhead=2,
#             arrowsize=1.5,
#             arrowwidth=1.5,
#             ax=-10,
#             ay=-50,
#             font=dict(size=text_font_size, family=font_family, color=font_color),
#             xref='x',
#             yref='y',
#             arrowcolor='black'
#         ))

#     if custom_annotation:
#         for date in custom_annotation:
#             if date in df.index:
#                 y_value = df.loc[date, y1_col]
#                 annotation_text = f'{date}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(y_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

#                 fig.add_annotation(dict(
#                     x=date,
#                     y=y_value,
#                     text=annotation_text,
#                     showarrow=True,
#                     arrowhead=2,
#                     arrowsize=1.5,
#                     arrowwidth=1.5,
#                     ax=-10,
#                     ay=-50,
#                     font=dict(size=text_font_size, family=font_family, color=font_color),
#                     xref='x',
#                     yref='y',
#                     arrowcolor='black'  # Customize arrow color if needed
#                 ))