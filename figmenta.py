from copy import copy
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
        df = df[[col, '_y']]             # add an extra col to deal with unique(injective) and difference
        self.name = col
        self.uniques = df[col].drop_duplicates()
        self.num_uniques = len(self.uniques)
        dtype = df[col].dtypes
        if dtype == np.object:
            self.datatype = Dimension.Type.CATEGORICAL
        else:
            num_deltas = self.uniques.sort_values().diff().iloc[1:].drop_duplicates().shape[0] # the number of difference
            if num_deltas == 1:
                self.datatype = Dimension.Type.SEQUENCE # arithmetic sequence;
            else:
                self.datatype = Dimension.Type.NUMERIC
        num_ys = df.groupby([col]).count()['_y'].drop_duplicates().shape[0] # the number of unique ys
        self.is_injective = (num_ys == 1)

def autovis(df, xs=None, ys=None, fig_args=None, glyph_args=None):
    # error check and fill in defaults (what is the defaults?)
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
    else:
        fig_args = copy(fig_args)
    if glyph_args is None:
        glyph_args = {}
    else:
        glyph_args = copy(glyph_args)
    # copy the dataframe
    df = df.copy()[xs + ys]
    # FIXME better solution for NaNs
    df.dropna(inplace=True)
    df['_y'] = '\t'.join(df[y].to_string() for y in ys)
    # infer properties
    x_dims = [Dimension(df, x) for x in xs]
    df = df.groupby(xs + ys, sort=False, as_index=False).count()
    # dispatch and draw
    return dispatch_chart(df, x_dims, ys, fig_args, glyph_args)

def dispatch_chart(df, x_dims, ys, fig_args, glyph_args):
    x_dim = len(x_dims)
    y_dim = len(ys)
    if x_dim == 0 and y_dim == 1:
        return # box_plot
    elif x_dim == 1 and y_dim == 1:
        if x_dims[0].datatype == Dimension.Type.CATEGORICAL:
            return bar_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args) # except many cata
        elif x_dims[0].datatype == Dimension.Type.SEQUENCE:
            return line_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args)
        elif x_dims[0].datatype == Dimension.Type.NUMERIC:
            return scatter_plot(df, x_dims[0].name, ys[0], fig_args, glyph_args)
    elif x_dim == 2 and y_dim == 1:
        if x_dims[0].datatype == Dimension.Type.CATEGORICAL:
            if x_dim < 13:  # arbitrary # for x_dim
                if x_dims[1].datatype ==Dimension.Type.CATEGORICAL and y_dim < 13: ##### the branch of it bigger than 13
                   return bar_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args) # with group bar chart
                elif x_dims[1].datatype == Dimension.Type.SEQUENCE:
                    return line_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args) # with color cata respect to xs
                elif x_dims[1].datatype == Dimension.Type.NUMERIC:
                    return scatter_plot(df, x_dims[0].name, ys[0], fig_args, glyph_args) # with color cata by respect to xs
            elif x_dim >= 13:
                if x_dims[1].datatype ==Dimension.Type.CATEGORICAL:
                   return #  heat map
                elif x_dims[1].datatype == Dimension.Type.SEQUENCE:
                    return line_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args) # with color cata respect to xs
                elif x_dims[1].datatype == Dimension.Type.NUMERIC:
                    return scatter_plot(df, x_dims[0].name, ys[0], fig_args, glyph_args)
        elif x_dims[0].datatype == Dimension.Type.SEQUENCE:
            if x_dims[1].datatype == Dimension.Type.CATEGORICAL:
                return # heat map




def bar_chart(df, x, y, fig_args, glyph_args):
    df['_y'] = df[y] / 2
    fig_args.setdefault('x_range', list(df[x])) # what is list(df[x])
    fig_args.setdefault('x_axis_label', x.title())
    if min(df[y]) >= 0:
        fig_args.setdefault('y_range', [0, 1.1 * max(df[y])])
    elif max(df[y]) <= 0:
        fig_args.setdefault('y_range', [1.1 * min(df[y]), 0])
    else:
        fig_args.setdefault('y_range', [1.1 * min(df[y]), 1.1 * max(df[y])])
    fig_args.setdefault('y_axis_label', y.title())

    f = figure(**fig_args)
    renderer = f.rect(
            x=x,
            y='_y',
            width=0.9,
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
    fig_args.setdefault('x_axis_label', x.title())
    fig_args.setdefault('y_axis_label', y.title())
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
    fig_args.setdefault('x_axis_label', x.title())
    fig_args.setdefault('y_axis_label', y.title())
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
