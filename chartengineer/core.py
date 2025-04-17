from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.graph_objects import Scatter, Bar
import plotly.offline as pyo
import plotly.io as pio

from pandas.api.types import is_datetime64_any_dtype
import pandas as pd
import os

from chartengineer.utils import (colors, clean_values,to_percentage,normalize_to_percent)

trace_map = {
    "line": Scatter,
    "area": Scatter,
    "scatter": Scatter,
    "bar": Bar,
    "pie": go.Pie
}

def validate_textposition(kind, textposition):
    if kind == "bar":
        valid_bar_pos = ["inside", "outside", "auto", "none"]
        return textposition if textposition in valid_bar_pos else "auto"
    return textposition

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
            "annotations": False,
            "max_annotation": False,
            'tickprefix': dict(y1=None, y2=None),
            'ticksuffix': dict(y1=None,y2=None),
            'save_directory': None,
            'space_buffer': 5,
            'descending': True,
            'datetime_format': '%b. %d, %Y',
            'tickformat': dict(x=None,y1=None,y2=None),
            'normalize': False,
            'text_freq': 1,
            'textposition':'top center' 
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
    
    def build(self, df, title, axes_data=None, chart_type={"y1": "line", "y2": "line"}, options=None,
            groupby_col=None, num_col=None):
        options = options or {}
        axes_data = axes_data or {}

        merged_opts = {**self.default_options, **options}

        if merged_opts.get('normalize') == True:
            print(f'normalizing to % ...')
            df = normalize_to_percent(df=df,num_col=num_col)

        self.df = df if self.df is None else pd.concat([self.df, df]).drop_duplicates()
        self.merged_opts = merged_opts
        self.title = title
        self.save_directory = merged_opts.get('save_directory', None)
        plotted_cols = []

        space_buffer = " " * merged_opts.get('space_buffer')

        # Detect if a pie chart was requested as a string
        if isinstance(chart_type, str):
            if chart_type.lower() == "pie":
                kind = "pie"
            elif chart_type.lower() == 'heatmap':
                kind='heatmap'
            else:
                chart_type = {"y1": chart_type, "y2": chart_type}
                kind = None
        else:
            kind = None
        
        # === PIE CHART HANDLING ===
        if kind == "pie":
            if groupby_col and num_col:
                index_col = groupby_col
                sum_col = num_col
            else:
                sum_col = axes_data.get("y1", [])[0] if isinstance(axes_data.get("y1"), list) else axes_data.get("y1")
                index_col = axes_data.get("x") or df.index.name or df.index

            if not sum_col or not index_col:
                raise ValueError("For pie chart, either (groupby_col and num_col) or axes_data['x'] and ['y1'] must be provided.")

            # Extract merged options with fallbacks to the pie_chart function defaults
            colors = merged_opts.get("colors", self.colors)
            bgcolor = merged_opts.get("bgcolor", "rgba(0,0,0,0)")
            annotation_prefix = merged_opts.get("tickprefix", {}).get("y1") or ""
            annotation_suffix = merged_opts.get("ticksuffix", {}).get("y1") or ""
            annotation_font_size = merged_opts.get("annotation_font_size", 25)
            decimals = merged_opts.get("decimals", True)
            decimal_places = merged_opts.get("decimal_places", 1)
            legend_font_size = merged_opts.get("font_size", {}).get("legend", 16)
            font_size = merged_opts.get("font_size", {}).get("axes", 18)
            legend_placement = merged_opts.get("legend_placement", dict(x=0.01, y=1.1))
            margin = merged_opts.get("margin", dict(l=0, r=0, t=0, b=0))
            hole_size = merged_opts.get("hole_size", 0.6)
            line_width = merged_opts.get("line_width", 0)
            legend_orientation = merged_opts.get("legend_orientation", "v")
            itemsizing = merged_opts.get("legend_background", {}).get("itemsizing", "constant")
            dimensions = merged_opts.get("dimensions", dict(width=730, height=400))
            font_family = merged_opts.get("font_family", "Cardo")
            font_color = merged_opts.get("font_color", "black")
            textinfo = merged_opts.get("textinfo", "none")
            show_legend = merged_opts.get("show_legend", False)
            text_font_size = merged_opts.get("font_size", {}).get("textfont", 12)
            text_font_color = merged_opts.get("text_font_color", "black")
            texttemplate = merged_opts.get("texttemplate", None)
            annotation = merged_opts.get("annotations", True)
            file_type = merged_opts.get("file_type", "svg")
            directory = merged_opts.get("save_directory", "../img")

            # Calculate percentages if needed
            if textinfo == 'percent+label':
                percent=False
            else:
                percent=True
            df, total = to_percentage(df, sum_col, index_col, percent=percent)
            padded_labels = [f"{label}    " for label in df.index]

            fig = go.Figure(data=[
                go.Pie(
                    labels=padded_labels,
                    values=df[sum_col],
                    hole=hole_size,
                    textinfo=textinfo,
                    showlegend=show_legend,
                    texttemplate=texttemplate,
                    marker=dict(colors=colors, line=dict(color='white', width=line_width)),
                    textfont=dict(
                        family=font_family,
                        size=text_font_size,
                        color=text_font_color
                    ),
                )
            ])

            annote = None
            if annotation:
                annote = [dict(
                    text=f"Total: {annotation_prefix}{clean_values(total, decimals=decimals, decimal_places=decimal_places)}{annotation_suffix}",
                    x=0.5, y=0.5,
                    font=dict(size=annotation_font_size, family=font_family, color=font_color),
                    showarrow=False,
                    xref='paper', yref='paper', align='center'
                )]

            fig.update_layout(
                template="plotly_white",
                plot_bgcolor=bgcolor,
                paper_bgcolor=bgcolor,
                width=dimensions.get("width"),
                height=dimensions.get("height"),
                margin=margin,
                font=dict(size=font_size, family=font_family),
                annotations=annote,
                legend=dict(
                    yanchor="top",
                    y=legend_placement.get("y", 1.1),
                    xanchor="left",
                    x=legend_placement.get("x", 0.01),
                    orientation=legend_orientation,
                    font=dict(size=legend_font_size, family=font_family, color=font_color),
                    bgcolor='rgba(0,0,0,0)',
                    itemsizing=itemsizing
                )
            )

            self.fig = fig
            return  # Skip the rest for pie charts
        
        print(f'kind: {kind}')
        print(f'chart_type: {chart_type}')

        # === HEATMAP CHART HANDLING ===
        if kind == "heatmap":
            print(f'kind: {kind}')
            x_col = axes_data.get("x")
            y_col = axes_data.get("y1", [])[0] if isinstance(axes_data.get("y1"), list) else axes_data.get("y1")
            z_col = num_col or y_col

            if not x_col or not y_col or not z_col:
                raise ValueError("Heatmap requires axes_data['x'] and axes_data['y1'] or groupby_col + num_col.")

            color_base = merged_opts.get("heatmap_color", "#1f77b4")
            width = merged_opts.get("dimensions", {}).get("width", 800)
            height = merged_opts.get("dimensions", {}).get("height", 500)
            margins = merged_opts.get("margin", dict(t=50, b=50, l=50, r=50))
            font_size = merged_opts.get("font_size", {}).get("axes", 12)
            legend_font_size = merged_opts.get("font_size", {}).get("legend", 10)
            tick_color = merged_opts.get("font_color", "#333")
            tick_suffix = merged_opts.get("ticksuffix", {}).get("y1", "")
            bg_color = merged_opts.get("bgcolor", "#ffffff")

            print(f'font_size: {font_size}')

            colorscale = [[0, "white"], [1, color_base]]
            fig = go.Figure(data=go.Heatmap(
                z=df[z_col],
                x=df[x_col],
                y=df[y_col],
                colorscale=colorscale,
                colorbar=dict(
                    title=dict(
                        text=z_col.replace("_", " ").title(),
                        font=dict(size=legend_font_size, color=tick_color)
                    ),
                    tickfont=dict(size=legend_font_size, color=tick_color)
                )
            ))

            fig.update_layout(
                title=title,
                width=width,
                height=height,
                xaxis_title=x_col.replace("_", " ").title(),
                yaxis_title=y_col.replace("_", " ").title(),
                font=dict(size=font_size, color=tick_color),
                margin=margins,
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
            )

            fig.update_xaxes(ticksuffix=tick_suffix)

            self.fig = fig
            return  # skip rest

        # === STANDARD CHART HANDLING (line, bar, etc.) ===
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        if axes_data.get('x') is None and is_datetime64_any_dtype(df.index):
            axes_data['x'] = df.index.name if df.index.name else df.index

        if groupby_col and num_col:
            print(f'groupby and numcol passed')
            sort_list, color_map = self._prepare_grouped_series(
                df, groupby_col, num_col,
                descending=merged_opts.get('descending', True),
                cumulative_sort=merged_opts.get('cumulative_sort', True)
            )

            axis = 'y1'  # for now assume only y1 for grouped logic
            kind = chart_type.get(axis, 'bar').lower()
            trace_class = trace_map.get(kind, go.Bar)
            secondary = False  # override if needed later

            for i in sort_list:
                i_df = df[df[groupby_col] == i]
                color = color_map.get(i)
                last_val = i_df[num_col].values[-1]

                name = f'{i} ({merged_opts.get("tickprefix").get(axis) or ""}{clean_values(last_val, decimals=merged_opts["decimals"], decimal_places=merged_opts["decimal_places"])}{merged_opts.get("ticksuffix").get(axis) or ""})'

                trace_args = {
                    "name": name,
                    "showlegend": merged_opts.get("show_legend", True)
                }

                # Add text labels if enabled
                if merged_opts.get("show_text", False):
                    decimal_places = merged_opts.get("decimal_places", 1)
                    decimals = merged_opts.get("decimals", True)
                    tickprefix = merged_opts.get("tickprefix", {}).get(axis) or ''
                    ticksuffix = merged_opts.get("ticksuffix", {}).get(axis) or ''
                    text_freq = merged_opts.get("text_freq", 1)
                    textposition = merged_opts.get("textposition", "top center")
                    print(f'textposition: {textposition}')

                    # Build text values per row (or single value if bar)
                    if kind == "bar":
                        text_val = f"{tickprefix}{clean_values(last_val, decimal_places=decimal_places, decimals=decimals)}{ticksuffix}"
                        trace_args["text"] = [text_val]
                    else:
                        trace_args["text"] = [
                            f"{tickprefix}{clean_values(v, decimal_places=decimal_places, decimals=decimals)}{ticksuffix}"
                            if i % text_freq == 0 else ""
                            for i, v in enumerate(i_df[num_col])
                        ]

                    trace_args["textposition"] = validate_textposition(kind, textposition)

                if kind == 'bar':
                    textposition = merged_opts.get("textposition", "auto")
                    if not pd.api.types.is_datetime64_any_dtype(df.index):
                        trace_args.update({
                            "x": [i],
                            "y": [last_val],
                            "marker": dict(color=color),
                            "textposition": validate_textposition(kind, textposition)
                        })
                    else:
                        trace_args.update({
                            "x": i_df.index,
                            "y": i_df[num_col],
                            "marker": dict(color=color),
                            "textposition": validate_textposition(kind, textposition)
                        })
                else:
                    trace_args.update({
                        "x": i_df.index,
                        "y": i_df[num_col],
                        "mode": merged_opts.get("mode", "lines"),
                        "line": dict(color=color, width=merged_opts.get("line_width", 3))
                    })
                    if kind == 'area':
                        trace_args["stackgroup"] = 'one'

                fig.add_trace(trace_class(**trace_args), secondary_y=secondary)
                self.series.append({"col": i_df[num_col], "name": name})
        else:
            for axis in ['y1', 'y2']:
                secondary = axis == 'y2'
                for col in axes_data.get(axis, []):
                    if col not in df.columns:
                        continue
                    color = self.get_next_color()
                    kind = chart_type.get(axis, "line").lower()
                    trace_class = trace_map.get(kind, go.Scatter)

                    name = f"{col.replace('_', ' ').upper()} ({merged_opts.get('tickprefix').get(axis) or ''}{clean_values(df[col].iloc[-1], decimals=merged_opts['decimals'], decimal_places=merged_opts['decimal_places'])}{merged_opts.get('ticksuffix').get(axis) or ''}){space_buffer}"
                    # === Dynamic text annotations at a given frequency ===
                    text_bool = merged_opts.get('show_text', False)
                    text_freq = merged_opts.get('text_freq', None)
                    tickprefix = merged_opts.get("tickprefix", {}).get(axis) or ''
                    ticksuffix = merged_opts.get("ticksuffix", {}).get(axis) or ''
                    textposition = validate_textposition(kind, merged_opts.get("textposition"))

                    # Determine if text should be shown
                    if text_bool and text_freq and col in df.columns:
                        print(f'text_bool: {text_bool}')
                        text_values = [
                            f"{tickprefix}{clean_values(val, decimal_places=merged_opts.get('decimal_places', 1), decimals=merged_opts.get('decimals', True))}{ticksuffix}"
                            if i % text_freq == 0 else ""
                            for i, val in enumerate(df[col])
                        ]
                    else:
                        text_values = None
                    trace_args = {
                        "x": df.index,
                        "y": df[col],
                        "name": name,
                        "text": text_values,
                        "textposition":textposition if text_values else None,
                        "showlegend": merged_opts.get("show_legend", False)
                    }
                    print(f'trace_args: {trace_args}')

                    if kind in ['line', 'area', 'scatter']:
                        trace_args["line"] = dict(color=color, width=merged_opts.get("line_width", 3))

                        if text_values:
                            trace_args["mode"] = "lines+text"
                        else:
                            trace_args["mode"] = merged_opts.get("mode", "lines")

                        if kind == 'area':
                            trace_args["stackgroup"] = 'one'
                    elif kind == 'bar':
                        trace_args["marker"] = dict(color=color)

                    fig.add_trace(trace_class(**trace_args), secondary_y=secondary)
                    self.series.append({"col": df[col], "name": name})
                    plotted_cols.append(col)

        # Layout config
        fig.update_layout(
            xaxis_title=merged_opts.get('axes_titles').get('x', ''),
            legend=dict(
                x=merged_opts.get('legend_placement').get('x'),
                y=merged_opts.get('legend_placement').get('y'),
                orientation=merged_opts["legend_orientation"],
                xanchor=merged_opts.get('xanchor', 'left'),
                yanchor=merged_opts.get('yanchor', 'top'),
                bgcolor=merged_opts.get('legend_background').get('bgcolor'),
                bordercolor=merged_opts.get('legend_background').get('bordercolor'),
                borderwidth=merged_opts.get('legend_background').get('borderwidth'),
                traceorder=merged_opts.get('legend_background').get('traceorder'),
                font=dict(size=merged_opts["font_size"]["legend"], family=merged_opts["font_family"], color=merged_opts['font_color'])
            ),
            template='plotly_white',
            hovermode='x unified',
            width=merged_opts.get('dimensions').get('width'),
            height=merged_opts.get('dimensions').get('height'),
            margin=merged_opts["margin"],
            font=dict(color=merged_opts["font_color"], size=merged_opts["font_size"]["axes"], family=merged_opts["font_family"]),
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
            y1_title_text = merged_opts.get('axes_titles').get('y1', '')
            y2_title_text = merged_opts.get('axes_titles').get('y2', '')

        if not axes_data.get('y2'):
            merged_opts['auto_color'] = False

        y1_color = self.colors[0] if merged_opts.get('auto_color') else 'black'
        y2_color = self.colors[1] if merged_opts.get('auto_color') else 'black'

        # Determine whether to hide y-axis based on chart kind and show_text
        hide_yaxis = (
            merged_opts.get("show_text", False)
            and all(chart_type.get(axis, "").lower() == "bar" for axis in chart_type)
        )


        fig.update_yaxes(
            title_text='' if hide_yaxis else y1_title_text,
            secondary_y=False,
            color=y1_color if not hide_yaxis else 'rgba(0,0,0,0)',
            showticklabels=not hide_yaxis,
            tickprefix='' if hide_yaxis else merged_opts.get('tickprefix', {}).get('y1', ''),
            ticksuffix='' if hide_yaxis else merged_opts.get('ticksuffix', {}).get('y1', ''),
            tickformat='' if hide_yaxis else merged_opts.get('tickformat', {}).get('y1', ''),
        )
        fig.update_yaxes(
            title_text=y2_title_text, secondary_y=True, color=y2_color,
            tickprefix=merged_opts.get('tickprefix', {}).get('y2', ''),
            ticksuffix=merged_opts.get('ticksuffix', {}).get('y2', ''),
            tickformat=merged_opts.get('tickformat', {}).get('y2', ''),
        )
        fig.update_xaxes(
            tickfont=dict(color=merged_opts['font_color']),
            tickformat=merged_opts.get('tickformat', {}).get('x', '')
        )

        # === Final Y-axis buffer adjustment for bar charts with outside text ===
        try:
            if any(chart_type.get(axis, "") == "bar" for axis in chart_type):
                textposition = merged_opts.get("textposition", "")
                if merged_opts.get("show_text", False) and validate_textposition("bar", textposition) == "outside":
                    if groupby_col and num_col:
                        series = df.groupby(groupby_col)[num_col].max()
                    else:
                        series = pd.concat([
                            df[col] for axis in ['y1', 'y2']
                            for col in axes_data.get(axis, []) if col in df.columns
                        ])

                    y_max = series.max()
                    y_min = series.min()
                    y_range = y_max - y_min
                    y_buffer = y_range * 0.15  # Add 10% on both ends

                    # Only apply a buffer upward if all values are positive
                    if y_min >= 0:
                        fig.update_yaxes(range=[0, y_max + y_buffer], secondary_y=False)
                    # Only apply a buffer downward if all values are negative
                    elif y_max <= 0:
                        fig.update_yaxes(range=[y_min - y_buffer, 0], secondary_y=False)
                    # Mixed case: apply buffer on both ends
                    else:
                        fig.update_yaxes(range=[y_min - y_buffer, y_max + y_buffer], secondary_y=False)
        except Exception as e:
            print(f"Warning: could not apply Y-axis buffer: {e}")

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
            title=self.title
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
    
    def add_annotations(self, max_annotation=True, custom_annotations=None, annotation_placement=dict(x=0.5,y=0.5)):
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

        print(f'df: {df}')

        df = df.sort_index()  # Ensure consistent order

        first_idx = df.index[0]
        first_val = df.loc[first_idx, y1_col]

        last_idx = df.index[-1]
        last_val = df.loc[last_idx, y1_col]

        first_text = f'{first_idx.strftime(datetime_format) if datetime_tick else first_idx}:<br>{tickprefix}{clean_values(first_val, decimal_places=decimal_places, decimals=decimals)}{ticksuffix}'
        last_text = f'{last_idx.strftime(datetime_format) if datetime_tick else last_idx}:<br>{tickprefix}{clean_values(last_val, decimal_places=decimal_places, decimals=decimals)}{ticksuffix}'
        print(f'first_idx: {first_idx}')
        print(f'last_idx: {last_idx}')

        if isinstance(fig.data[0], go.Pie):
            total = sum(fig.data[0].values)
            annotation_prefix = opts.get("tickprefix", {}).get("y1", "")
            annotation_suffix = opts.get("ticksuffix", {}).get("y1", "")
            
            total_text = f'{annotation_prefix}{clean_values(total, decimals=decimals, decimal_places=decimal_places)}{annotation_suffix}'

            pie_annotation = dict(
                text=f"Total: {total_text}",
                x=annotation_placement['x'],
                y=annotation_placement['x'],
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
                ax=10,
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
                ax=10,
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



            
