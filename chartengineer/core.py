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
    def __init__(self, default_options=None, shuffle_colors=False):
        self.colors = colors(shuffle_colors)
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
            "legend_background": dict(bgcolor="rgba(0,0,0,0)",bordercolor="rgba(0,0,0,0)",
                                    borderwidth=1,itemsizing='constant',buffer=5,
                                      traceorder='normal'),
            'legend_placement': dict(x=0.01,y=1.1),
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
            'descending': True,
            'datetime_format': '%b. %d, %Y'
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
    
    def build(self, df, axes_data, title, chart_type={"y1":"line","y2":"line"}, options=None,
            groupby_col=None, num_col=None,):
        options = options or {}
        merged_opts = {**self.default_options, **options}

        self.df = df if self.df is None else pd.concat([self.df, df]).drop_duplicates()

        self.merged_opts = merged_opts
        self.title = title

        self.save_directory = merged_opts.get('save_directory',None)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        plotted_cols = []

        space_buffer = " " * merged_opts.get('space_buffer')

        # Default X to index if datetime
        if axes_data.get('x') is None and is_datetime64_any_dtype(df.index):
            axes_data['x'] = df.index.name if df.index.name else df.index

        # Normalize chart_type to support dict input
        if isinstance(chart_type, str):
            chart_type = {"y1": chart_type, "y2": chart_type}

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
                kind = chart_type.get("y1", "line").lower()
                trace_class = trace_map.get(kind, Scatter)

                name = f"{col.replace('_', ' ').upper()} ({merged_opts.get('tickprefix').get('y1') or ''}{clean_values(df[col].iloc[-1], decimals=merged_opts['decimals'], decimal_places=merged_opts['decimal_places'])}{merged_opts.get('ticksuffix').get('y1')or ''}){space_buffer}"
                trace_args = {
                    "x": df.index,
                    "y": df[col],
                    "name": name,
                    "showlegend": merged_opts.get("show_legend", False)
                }
                if kind in ['line', 'area', 'scatter']:
                    trace_args["line"] = dict(color=color, width=merged_opts.get("line_width", 3))
                    trace_args["mode"] = merged_opts.get("mode", "lines")
                    if kind == 'area':
                        trace_args["stackgroup"] = 'one'
                elif kind == 'bar':
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
                kind = chart_type.get("y2", "line").lower()
                trace_class = trace_map.get(kind, Scatter)

                name = f"{col.replace('_', ' ').upper()} ({merged_opts.get('tickprefix').get('y2') or ''}{clean_values(df[col].iloc[-1], decimals=merged_opts['decimals'], decimal_places=merged_opts['decimal_places'])}{merged_opts.get('ticksuffix').get('y2') or ''}){space_buffer}"
                trace_args = {
                    "x": df.index,
                    "y": df[col],
                    "name": name,
                    "showlegend": merged_opts.get("show_legend", False)
                }
                if kind in ['line', 'area', 'scatter']:
                    trace_args["line"] = dict(color=color, width=merged_opts.get("line_width", 3))
                    trace_args["mode"] = merged_opts.get("mode", "lines")
                    if kind == 'area':
                        trace_args["stackgroup"] = 'one'
                elif kind == 'bar':
                    trace_args["marker"] = dict(color=color)

                fig.add_trace(trace_class(**trace_args), secondary_y=True)
                self.series.append({
                    "col": df[col],
                    "name": name,
                })
                plotted_cols.append(col)

            # Layout
            fig.update_layout(
                xaxis_title=merged_opts.get('axes_titles').get('x',''),
                legend=dict(
                    x=merged_opts.get('legend_placement').get('x'), 
                    y=merged_opts.get('legend_placement').get('y'), 
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


    def add_title(self,title=None,subtitle=None, x=0.25, y=0.9):
        # Add a title and subtitle
        if not hasattr(self, 'title_position') or title_position is None:
            title_position = {'x': None, 'y': None}

        # Update title position if values are provided
        if x is not None:
            title_position['x'] = x
        if y is not None:
            title_position['y'] = y

        if title == None:
            title=""
        if subtitle == None:
            subtitle=""

        self.fig.update_layout(
            title={
                'text': f"<span style='color: black; font-weight: normal;'>{title}</span><br><sub style='font-size: 18px; color: black; font-weight: normal;'>{subtitle}</sub>",
                'y':1 if title_position['y'] == None else title_position['y'],
                'x':0.2 if title_position['x'] == None else title_position['x'],
                'xanchor': 'left',
                'yanchor': 'top',
                'font': {
                'color': 'black',  # Set the title color here
                'size': 27,  # You can also adjust the font size
                'family': self.merged_opts['font_family']}
            },
        )
    
    def add_annotations(self, max_annotation=True, custom_annotations=None):
        if self.df is None or self.fig is None:
            return  # Cannot annotate without a figure and data

        opts = self.merged_opts
        fig = self.fig
        df = self.df

        font_color = opts.get("font_color", "black")
        font_family = opts.get("font_family", "Cardo")
        text_font_size = opts.get("font_size", {}).get("textfont", 12)
        datetime_format = opts.get("datetime_format", "%b. %d, %Y")
        decimal_places = opts.get("decimal_places", 1)
        decimals = opts.get("decimals", True)
        tickprefix = opts.get("tickprefix", {}).get("y1") or ''
        ticksuffix = opts.get("ticksuffix", {}).get("y1") or ''
        annotations = opts.get("annotations", True)
        max_annotation_bool = opts.get("max_annotation", max_annotation)

        # Determine which column was plotted
        y1_cols = self.merged_opts.get("axes_titles", {}).get("y1", [])
        y2_cols = self.merged_opts.get("axes_titles", {}).get("y2", [])
        plotted_cols = self.series

        if len(plotted_cols) != 1:
            return  # Only annotate if exactly one series was plotted

        y1_col = plotted_cols[0]["col"].name

        # Determine if index is datetime
        datetime_tick = pd.api.types.is_datetime64_any_dtype(df.index)

        # Last value annotation
        last_val = df[y1_col].iloc[0]
        last_idx = df.index[0]
        last_text = f'{last_idx.strftime(datetime_format) if datetime_tick else last_idx}:<br>{tickprefix}{clean_values(last_val, decimal_places=decimal_places, decimals=decimals)}{ticksuffix}'

        print(f'last_text: {last_text}')

        # First value annotation
        first_val = df[y1_col].iloc[-1]
        first_idx = df.index[-1]
        first_text = f'{first_idx.strftime(datetime_format) if datetime_tick else first_idx}:<br>{tickprefix}{clean_values(first_val, decimal_places=decimal_places, decimals=decimals)}{ticksuffix}'

        if isinstance(fig.data[0], go.Pie):
            total = sum(fig.data[0].values)
            annotation_prefix = opts.get("tickprefix", {}).get("y1", "")
            annotation_suffix = opts.get("ticksuffix", {}).get("y1", "")
            
            total_text = f'{annotation_prefix}{clean_values(total, decimals=decimals, decimal_places=decimal_places)}{annotation_suffix}'

            pie_annotation = dict(
                text=f"Total: {total_text}",
                x=0.5,
                y=0.5,
                font=dict(
                    size=text_font_size,
                    family=font_family,
                    color=font_color
                ),
                showarrow=False,
                xref='paper',
                yref='paper',
                align='center'
            )
            fig.update_layout(annotations=[pie_annotation])

        if annotations:
            # Add last annotation
            fig.add_annotation(dict(
                x=last_idx,
                y=last_val,
                text=last_text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=1.5,
                ax=-100,
                ay=-50,
                font=dict(size=text_font_size, family=font_family, color=font_color),
                xref='x',
                yref='y',
                arrowcolor='black'
            ))

            # Add first annotation
            fig.add_annotation(dict(
                x=first_idx,
                y=first_val,
                text=first_text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=1.5,
                ax=50,
                ay=-50,
                font=dict(size=text_font_size, family=font_family, color=font_color),
                xref='x',
                yref='y',
                arrowcolor='black'
            ))

        if max_annotation_bool:
            max_val = df[y1_col].max()
            max_idx = df[df[y1_col] == max_val].index[0]
            max_text = f'{max_idx.strftime(datetime_format) if datetime_tick else max_idx}:<br>{tickprefix}{clean_values(max_val, decimal_places=decimal_places, decimals=decimals)}{ticksuffix} (ATH)'

            if max_idx not in [first_idx, last_idx]:
                fig.add_annotation(dict(
                    x=max_idx,
                    y=max_val,
                    text=max_text,
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=1.5,
                    ax=-10,
                    ay=-50,
                    font=dict(size=text_font_size, family=font_family, color=font_color),
                    xref='x',
                    yref='y',
                    arrowcolor='black'
                ))

            # Custom annotations
            if custom_annotations:
                for date, label in custom_annotations.items():
                    if date in df.index:
                        y_val = df.loc[date, y1_col]
                        fig.add_annotation(dict(
                            x=date,
                            y=y_val,
                            text=label,
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1.5,
                            arrowwidth=1.5,
                            ax=-10,
                            ay=-50,
                            font=dict(size=text_font_size, family=font_family, color=font_color),
                            xref='x',
                            yref='y',
                            arrowcolor='black'
                        ))

    def add_dashed_line(self, date, annotation_text=None):
        if self.df is None or self.fig is None:
            print("Error: DataFrame or figure not initialized.")
            return

        opts = self.merged_opts
        df = self.df
        fig = self.fig

        font_family = opts.get("font_family", "Cardo")
        font_color = opts.get("font_color", "black")
        text_font_size = opts.get("font_size", {}).get("textfont", 12)
        datetime_format = opts.get("datetime_format", "%b. %d, %Y")
        line_color = opts.get("dashed_line_color", "black")
        line_width = opts.get("dashed_line_width", 3)
        line_factor = opts.get("dashed_line_factor", 1.0)  # Optional y-scaling
        cols_to_plot = [s["col"].name for s in self.series] if self.series else df.columns.tolist()

        # Coerce to timestamp if datetime index
        if pd.api.types.is_datetime64_any_dtype(df.index):
            date = pd.to_datetime(date)

        if date not in df.index:
            print(f"Error: {date} is not in the DataFrame index.")
            return

        # Pick column for y-value (first plotted or max column at date)
        if len(cols_to_plot) == 1:
            col = cols_to_plot[0]
        else:
            col = df.loc[date, cols_to_plot].idxmax()
        
        y_value = df.loc[date, col]

        if pd.isna(y_value):
            print(f"Warning: Missing value at {date} for {col}.")
            return

        # Dashed vertical line
        fig.add_shape(
            type="line",
            x0=date,
            y0=0,
            x1=date,
            y1=y_value * line_factor,
            line=dict(color=line_color, width=line_width, dash="dot"),
        )

        if annotation_text is None:
            annotation_text = f"{col}: {clean_values(y_value)}"

        fig.add_annotation(
            x=date,
            y=y_value * line_factor,
            text=f"{annotation_text}<br>{pd.to_datetime(date).strftime(datetime_format)}",
            showarrow=False,
            font=dict(size=text_font_size, family=font_family, color=font_color),
        )



            
