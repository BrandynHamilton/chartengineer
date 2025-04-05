from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.graph_objects import Scatter, Bar
import plotly.offline as pyo
import plotly.io as pio

from pandas.api.types import is_datetime64_any_dtype
import pandas as pd
import os

from chartengineer.utils import (colors, clean_values)

trace_map = {
    "line": Scatter,
    "area": Scatter,
    "scatter": Scatter,
    "bar": Bar,
    "candlestick": go.Candlestick
}

class ChartMaker:
    def __init__(self, default_options=None):
        self.colors = colors()
        self.color_index = 0
        self.fig = None
        self.merged_opts = None
        self.title = None
        self.series = []  
        self.df = None
        self.default_options = default_options or {
            "font_color": "black",
            "font_family": "Cardo",
            "orientation": "v",
            "legend_orientation": "v",
            "legend_background": dict(bgcolor='white',bordercolor='black',borderwidth=1,itemsizing='constant',buffer=5,
                                      traceorder='normal'),
            "connectgap": True,
            "barmode": "stack",
            "bgcolor": "rgba(0,0,0,0)",
            "autosize": True,
            "margin": dict(l=10, r=10, t=10, b=10),
            "dimensions": dict(width=730, height=400),
            "font_size": dict(axes=16,legend=12,textfont=12),
            "axes_titles": dict(x=None,y1=None,y2=None),
            "decimals": True,
            "decimal_places": 1,
            "show_text": False,
            "dt_format": '%b. %d, %Y',
            "auto_title": False,
            "auto_color": True,
            "normalize": False,
            "line_width": 4,
            "marker_size": 10,
            "cumulative_sort": True,
            "hole_size": 0.6,
            "annotations": True,
            'tickprefix': dict(y1=None, y2=None),
            'ticksuffix': dict(y1=None,y2=None),
            'save_directory': None,
            'space_buffer': 5,
            'descending': True
        }
        

    def get_next_color(self):
        color = self.colors[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.colors)
        return color

    def return_df(self):
        return self.df.copy()

    def save_fig(self, save_directory=None, filetype='png'):
        """Save the figure to the specified directory with the given filetype."""
        # Construct the full file path using os.path.join
        if save_directory:
            self.save_directory = save_directory

        file_path = os.path.join(self.save_directory, f'{self.title}.{filetype}')

        print(f'Saving figure to: {file_path}')

        if filetype != 'html':
            # Save as image using Kaleido engine
            self.fig.write_image(file_path, engine="kaleido")
        else:
            # Save as HTML
            self.fig.write_html(file_path)
        
    def show_fig(self,browser=False):
        if browser==False:
            pyo.iplot(self.fig)
        else: 
            pyo.plot(self.fig)

    def clear(self):
        self.fig = None
        self.series = []
        self.df = None
        self.color_index = 0

    def return_fig(self):
        return self.fig
    
    def _prepare_grouped_series(self, df, groupby_col, num_col, descending=True, cumulative_sort=False):
        """
        Groups and sorts data for multi-line plots.
        Returns: list of sorted categories, color map
        """
        sort_agg = df.groupby(groupby_col)[num_col].last().sort_values(ascending=not descending)
        sort_list = sort_agg.index.tolist()
        color_map = {
            cat: self.get_next_color() for cat in sort_list
        }
        return sort_list, color_map
    
    def build(self, df, axes_data, title, chart_type="line", options=None,
              groupby_col=None, num_col=None,):
        options = options or {}
        merged_opts = {**self.default_options, **options}

        self.df = df if self.df is None else pd.concat([self.df, df]).drop_duplicates()

        self.merged_opts = merged_opts
        self.title = title

        self.save_directory = merged_opts.get('save_directory',None)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        plotted_cols = []

        # Default X to index if datetime
        if axes_data.get('x') is None and is_datetime64_any_dtype(df.index):
            axes_data['x'] = df.index.name if df.index.name else df.index

        chart_type = chart_type.lower()
        trace_class = trace_map.get(chart_type, Scatter)

        if groupby_col and num_col:
            sort_list, color_map = self._prepare_grouped_series(
                df, groupby_col, num_col, descending = merged_opts.get('descending',True), 
                cumulative_sort = merged_opts.get('cumulative_sort',True)
            )
            # Iterate and plot each group
            for i in sort_list:
                i_df = df[df[groupby_col] == i]
                color = color_map.get(i)
                fig.add_trace(
                    go.Scatter(
                        x=i_df.index,
                        y=i_df[num_col],
                        name=f'{i} ({clean_values(i_df[num_col].iloc[-1])})',
                        line=dict(color=color, width=merged_opts.get("line_width", 3)),
                        mode=merged_opts.get("mode", "lines"),
                        showlegend=merged_opts.get("show_legend", False)
                    ),
                    secondary_y=False
                )
                self.series.append({
                    "col": df[col],
                    "name": name,
                })
        else:
            # Primary Y
            for col in axes_data.get('y1', []):
                if col not in df.columns:
                    continue
                color = self.get_next_color()
                trace_args = {
                    "x": df.index,
                    "y": df[col],
                    "name": f'{col} ({merged_opts.get('tickprefix').get('y1','')}{clean_values(df[col].iloc[-1], decimals=merged_opts['decimals'], decimal_places=merged_opts['decimal_places'])}{merged_opts.get('ticksuffix').get('y1','')}){merged_opts.get('space_buffer')}',
                    "showlegend": merged_opts.get("show_legend", False)
                }
                if chart_type in ['line', 'area', 'scatter']:
                    trace_args["line"] = dict(color=color, width=merged_opts.get("line_width", 3))
                    trace_args["mode"] = merged_opts.get("mode", "lines")
                    if chart_type == 'area':
                        trace_args["stackgroup"] = 'one'
                elif chart_type == 'bar':
                    trace_args["marker"] = dict(color=color)
                fig.add_trace(trace_class(**trace_args), secondary_y=False)
                self.series.append({
                    "col": df[col],
                    "name": name,
                })
                plotted_cols.append(col)

            # Secondary Y
            for col in axes_data.get('y2', []):
                if col not in df.columns:
                    continue
                color = self.get_next_color()
                name = f'{col} ({merged_opts.get('tickprefix').get('y2','')}{clean_values(df[col].iloc[-1], decimals=merged_opts['decimals'], decimal_places=merged_opts['decimal_places'])}{merged_opts.get('ticksuffix').get('y2','')}){merged_opts.get('space_buffer')}',
                trace_args = {
                    "x": df.index,
                    "y": df[col],
                    "name": name,
                    "showlegend": merged_opts.get("show_legend", False)
                }
                if chart_type in ['line', 'area', 'scatter']:
                    trace_args["line"] = dict(color=color, width=merged_opts.get("line_width", 3))
                    trace_args["mode"] = merged_opts.get("mode", "lines")
                    if chart_type == 'area':
                        trace_args["stackgroup"] = 'one'
                elif chart_type == 'bar':
                    trace_args["marker"] = dict(color=color)
                fig.add_trace(trace_class(**trace_args), secondary_y=True)
                plotted_cols.append(col)

            # Layout
            fig.update_layout(
                xaxis_title=merged_opts.get('axes_titles').get('x',''),
                legend=dict(
                    x=merged_opts.get('x'), y=merged_opts.get('y'), 
                    orientation=merged_opts["legend_orientation"],
                    xanchor=merged_opts.get('xanchor','left'),
                    yanchor=merged_opts.get('yanchor','top'),
                    bgcolor=merged_opts.get('legend_background').get('bgcolor'),
                    bordercolor=merged_opts.get('legend_background').get('bordercolor'),
                    borderwidth=merged_opts.get('legend_background').get('borderwidth'),
                    traceorder=merged_opts.get('legend_background').get('traceorder')
                ),
                template='plotly_white',
                hovermode='x unified',
                width=merged_opts.get('dimensions').get('width'),
                height=merged_opts.get('dimensions').get('height'),
                margin=merged_opts["margin"],
                font=dict(color=merged_opts["font_color"], family=merged_opts["font_family"]),
                autosize=merged_opts["autosize"],
                barmode=merged_opts['barmode'],

            )

            if merged_opts.get('auto_title'):
                y1_title_text = axes_data.get('y1', [''])[0].replace("_", " ").upper() if axes_data.get('y1') else None
                y2_title_text = (
                    axes_data.get('y2', [''])[0].replace("_", " ").upper() 
                    if axes_data.get('y2') and len(axes_data.get('y2')) > 0 
                    else None
                )
            else:
                y1_title_text = merged_opts.get('axes_titles').get('y1','')
                y2_title_text = merged_opts.get('axes_titles').get('y2','')

            # Auto color handling
            if not axes_data.get('y2'):  # Empty or None
                merged_opts['auto_color'] = False

            if merged_opts.get('auto_color'):
                y1_color = self.colors[0]
                y2_color = self.colors[1]
            else:
                y1_color = 'black'
                y2_color = 'black'

            # Apply y-axis titles and colors
            fig.update_yaxes(
                title_text=y1_title_text, secondary_y=False, color=y1_color,
                tickprefix=merged_opts.get('tickprefix', {}).get('y1', ''),
                ticksuffix=merged_opts.get('ticksuffix', {}).get('y1', '')
            )
            fig.update_yaxes(
                title_text=y2_title_text, secondary_y=True, color=y2_color,
                tickprefix=merged_opts.get('tickprefix', {}).get('y2', ''),
                ticksuffix=merged_opts.get('ticksuffix', {}).get('y2', '')
            )

            fig.update_xaxes(tickfont=dict(color=merged_opts['font_color']))

            self.fig = fig

            return fig

    def add_title(self,title=None,subtitle=None, x=None, y=None):
        # Add a title and subtitle
        if not hasattr(self, 'title_position') or self.title_position is None:
            self.title_position = {'x': None, 'y': None}

        # Update title position if values are provided
        if x is not None:
            self.title_position['x'] = x
        if y is not None:
            self.title_position['y'] = y

        # Update title and subtitle if provided
        # if title is not None:
        #     self.title = title
        # if subtitle is not None:
        #     self.subtitle = subtitle

        if title == None:
            title=""
        if subtitle == None:
            subtitle=""

        self.fig.update_layout(
            title={
                'text': f"<span style='color: black; font-weight: normal;'>{title}</span><br><sub style='font-size: 18px; color: black; font-weight: normal;'>{subtitle}</sub>",
                'y':1 if self.title_position['y'] == None else self.title_position['y'],
                'x':0.2 if self.title_position['x'] == None else self.title_position['x'],
                'xanchor': 'left',
                'yanchor': 'top',
                'font': {
                'color': 'black',  # Set the title color here
                'size': 27,  # You can also adjust the font size
                'family': self.font_family}
            },
        )

        
