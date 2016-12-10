from enum import Enum, unique as enum_unique

import numpy as np
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool

class Dimension:
    @enum_unique
    class Type(Enum):
        CATEGORICAL = 'CATEGORICAL'
        SEQUENCE = 'SEQUENCE'
        NUMERIC = 'NUMERIC'
    def __init__(self, df, col):
        df = df[[col, '_y']]
        self.name = col
        self.uniques = df[col].drop_duplicates()
        self.num_uniques = len(self.uniques)
        dtype = df[col].dtypes
        if dtype == np.object:
            self.datatype = Dimension.Type.CATEGORICAL
        else:
            num_deltas = self.uniques.sort_values().diff().iloc[1:].drop_duplicates().shape[0]
            if num_deltas == 1:
                self.datatype = Dimension.Type.SEQUENCE
            else:
                self.datatype = Dimension.Type.NUMERIC
        num_ys = df.groupby([col]).count()['_y'].drop_duplicates().shape[0]
        self.is_injective = (num_ys == 1)

def autovis(df, xs=None, ys=None, fig_args=None, glyph_args=None):
    # error check and fill in defaults
    if xs is None:
        xs = []
    else:
        assert isinstance(xs, list)
    if ys is None:
        ys = []
    else:
        assert isinstance(ys, list)
    if fig_args is None:
        fig_args = {}
    if glyph_args is None:
        glyph_args = {}
    # infer properties
    df = df.copy()[xs + ys]
    # FIXME better solution for NaNs
    df.dropna(inplace=True)
    df['_y'] = '\t'.join(df[y].to_string() for y in ys)
    x_dims = [Dimension(df, x) for x in xs]
    df = df.groupby(xs + ys, as_index=False).count()
    # dispatch and draw
    return dispatch_chart(df, xs, x_dims, ys, fig_args, glyph_args)

def dispatch_chart(df, xs, x_dims, ys, fig_args, glyph_args):
    x_dim = len(xs)
    y_dim = len(ys)
    if x_dims[0].datatype == Dimension.Type.CATEGORICAL:
        return bar_chart(df, xs[0], ys[0], fig_args, glyph_args)
    elif x_dims[0].datatype == Dimension.Type.SEQUENCE:
        return line_chart(df, xs[0], ys[0], fig_args, glyph_args)
    elif x_dims[0].datatype == Dimension.Type.NUMERIC:
        return scatter_plot(df, xs[0], ys[0], fig_args, glyph_args)

def bar_chart(df, x, y, fig_args, glyph_args):
    print('bar chart')
    df['_y'] = df[y] / 2
    f = figure(x_range=list(df[x]), **fig_args)
    renderer = f.rect(
            x=x,
            y='_y',
            width=1,
            height=y,
            source=ColumnDataSource(df),
            **glyph_args
    )
    f.add_tools(HoverTool(renderers=[renderer], tooltips=[
        (x, '@{}'.format(x)),
        (y, '@{}'.format(y)),
    ]))
    return f

def line_chart(df, x, y, fig_args, glyph_args):
    print('line chart')
    f = figure(**fig_args)
    renderer = f.square(
            x=x,
            y=y,
            source=ColumnDataSource(df),
            **glyph_args
    )
    f.add_tools(HoverTool(renderers=[renderer], tooltips=[
        (x, '@{}'.format(x)),
        (y, '@{}'.format(y)),
    ]))
    f.line(
            x=x,
            y=y,
            source=ColumnDataSource(df),
            **glyph_args
    )
    return f

def scatter_plot(df, x, y, fig_args, glyph_args):
    print('scatter_plot')
    f = figure(**fig_args)
    renderer = f.circle(
            x=x,
            y=y,
            source=ColumnDataSource(df),
            **glyph_args
    )
    f.add_tools(HoverTool(renderers=[renderer], tooltips=[
        (x, '@{}'.format(x)),
        (y, '@{}'.format(y)),
    ]))
    return f
