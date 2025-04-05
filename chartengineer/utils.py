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

def to_percentage(df, sum_col, index_col, percent=True):

    df_copy = df.copy()

    df_copy = df_copy.groupby(index_col)[sum_col].sum().reset_index()

    # Calculate total usd_revenue
    total = df[sum_col].sum()

    if percent:

        # Add a new column for percentage
        df_copy['percentage'] = (df_copy[sum_col] / total) * 100
        df_copy['legend_label'] = df_copy.apply(lambda x: f"{x[index_col]} ({x['percentage']:.1f}%)", axis=1)
        df_copy.set_index('legend_label', inplace=True)
    else:
        df_copy.set_index(index_col, inplace=True)
        print(f'df_copy: {df_copy}')
    
    df_copy.sort_values(by=sum_col, ascending=False, inplace=True)
    df_copy.drop_duplicates(inplace=True)

    return df_copy, total

def normalize_to_percent(df,num_col=None):
    print(f'num_col: {num_col}')

    if num_col == None:
    
        df_copy = df.copy()

        df_copy['total'] = df_copy.sum(axis=1)
        # Exclude the 'total_transactions' column from the percentage calculation
        chains_columns = df_copy.columns.difference(['total'])

        for col in chains_columns:
            df_copy[f'{col}_percentage'] = (df_copy[col] / df_copy['total']) * 100

        # Drop the 'total_transactions' column if you don't need it
        df_copy = df_copy.drop(columns=['total'])

        percent_cols = [col for col in df_copy.columns if '_percentage' in col]
        df_copy = df_copy[percent_cols]

        df_copy.columns = df_copy.columns.str.replace('_percentage', '', regex=False)

        print(f'percent_cols:{df_copy.columns}')
    else:
        df_copy = df.copy()
        total = df_copy.groupby(df_copy.index)[num_col].sum()
        total = total.to_frame(f'total_{num_col}')
        df_copy = df_copy.merge(total, left_index=True, right_index=True, how='inner')
        # Calculate percentage of daily active users for each app
        df_copy['percentage'] = (df_copy[num_col] / df_copy[f'total_{num_col}']) * 100

        # Drop the total_active_users column if no longer needed
        df_copy = df_copy.drop(columns=[f'total_{num_col}'])
        df_copy.drop(columns=num_col,inplace=True)

        df_copy.rename(columns={"percentage":num_col},inplace=True)

    df_copy.drop_duplicates(inplace=True)

    return df_copy