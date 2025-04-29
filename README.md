# `chartengineer` Documentation

**chartengineer** is a lightweight Python package for building publication-ready, highly customizable Plotly charts from pandas DataFrames.

It supports a flexible API for pie charts, grouped bar charts, heatmaps, time series, and area/line plots, with robust formatting, annotations, and layout tools.

---

## Installation

```bash
pip install chartengineer
```

Or install from source:

```bash
git clone https://github.com/BrandynHamilton/chartengineer
cd chartengineer
pip install -e .
```

---

## Quickstart

```python
from chartengineer import ChartMaker

cm = ChartMaker(shuffle_colors=True)
cm.build(
    df=my_df,
    groupby_col="CHAIN",
    num_col="TOTAL_VOLUME",
    title="Bridge Volume by Chain",
    chart_type="pie",
    options={
        "tickprefix": {"y1": "$"},
        "annotations": True,
        "texttemplate": "%{label}<br>%{percent}"
    }
)
cm.add_title(subtitle="As of 2025-04-01")
cm.show_fig()
```

---

## Supported Chart Types

- `"line"` (default)
- `"bar"`
- `"area"`
- `"pie"`
- `"heatmap"`

You can use a string or dictionary:

```python
chart_type = "bar"  # applies to both y1/y2
chart_type = {"y1": "line", "y2": "bar"}  # axis-specific
```

Check the tests directory for examples for each chart type.

---

## Main Methods

### `ChartMaker.build(...)`

Build a chart.

**Arguments**

- `df`: pandas DataFrame
- `title`: Chart title
- `chart_type`: string or dict
- `groupby_col`, `num_col`: for grouped series or pie/bar
- `axes_data`: e.g. `{"x": "DATE", "y1": ["TVL"]}`
- `options`: plot style and behavior options

---

### `ChartMaker.show_fig()`

Render the current chart inline (Jupyter) or open in browser.

### `ChartMaker.save_fig(path, filetype='png')`

Save the chart as `.png`, `.svg`, or `.html`.

### `ChartMaker.add_title(title, subtitle, x, y)`

Adds a title to the chart itself, if title is None it defaults to the title name used in the build function. The X and Y parameters control the title's placement on the chart.  

### `ChartMaker.add_annotations(max_annotation=True, custom_annotations=None, annotation_placement=dict(x=0.5,y=0.5))`

If called and the chart is plotting timeseries data, this automatically adds annotations for the first and last data points.  If max_annotation is True, it dynamically calculates the max value in the dataset and annotates it.  the custom_annotation parameter expects a dictionary with date as a string and the annotation text. Note that this is meant for plotting single-series timeseries data.

If the chart is a Pie chart, the annotation_placement parameter enables moving the location of where the annotation is placed.

### `ChartMaker.add_dashed_line(date, annotation_text=None)`

Adds a dashed line and annotation at the specified date; meant for timeseries data.  If annotation_text is None, it uses the column name that contains the max value for the specified date. 

### `ChartMaker.return_df()`

Returns the dataframe used in a chart.

### `ChartMaker.return_fig()`

Returns the Plotly figure that was created from calling the build method.

---

## Customization Options

All style options can be passed via the `options` parameter when using `ChartMaker`. These options are merged with Plotly's base figure settings.

You can refer to:

- [Plotly Python Graphing Library documentation](https://plotly.com/python/reference/) for a full list of Plotly figure and layout parameters.
- [ChartMaker full list of supported options](https://www.notion.so/1e4b8f53c6b581a392ffc7d013ab71f7?v=1e4b8f53c6b58133af4f000ca0c30252&pvs=4) for available `options` and their default values.

Here’s a quick example:

```python
options = {
    "tickprefix": {"y1": "$"},
    "ticksuffix": {"y1": "%"},
    "dimensions": {"width": 800, "height": 400},
    "font_family": "Cardo",
    "font_size": {"axes": 16, "legend": 12, "textfont": 12},
    "legend_placement": {"x": 1.05, "y": 1},
    "show_text": True,
    "annotations": True,
}
```

---

## Chart Features

- Grouped bar plots with custom sort and color mapping
- Automatic annotations for first/last/max points
- Time series support with datetime formatting
- Pie chart labels, percentages, donut hole support
- Heatmaps with flexible x/y/z column mapping

---

## Contact

Email: brandynham1120@gmail.com

---

## License

MIT License © Brandyn Hamilton
