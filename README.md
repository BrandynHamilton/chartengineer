# 📊 `chartengineer` Documentation

**chartengineer** is a lightweight Python package for building publication-ready, highly customizable Plotly charts from pandas DataFrames.

It supports a flexible API for pie charts, grouped bar charts, heatmaps, time series, and area/line plots, with robust formatting, annotations, and layout tools.

---

## Installation

```bash
pip install chartengineer
```

Or install from source:

```bash
git clone https://github.com/your-org/chartengineer
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
- `"scatter"`
- `"pie"`
- `"heatmap"`
- `"candlestick"`

You can use a string or dictionary:

```python
chart_type = "bar"  # applies to both y1/y2
chart_type = {"y1": "line", "y2": "bar"}  # axis-specific
```

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

---

## Customization Options

All style options can be passed via the `options` parameter.

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

## Project Structure

```
chartengineer/
├── __init__.py
├── core.py         # ChartMaker class
├── utils.py        # Plotting utils, formatting
```

---

## License

MIT License © Brandyn Hamilton
