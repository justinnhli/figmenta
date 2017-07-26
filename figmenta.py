from copy import copy
from enum import Enum, unique as enum_unique

import numpy as np
import pandas as pd
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.palettes import Pastel1_9, Category10_10

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
            return bar_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args) # except many data
        elif x_dims[0].datatype == Dimension.Type.SEQUENCE:
            return line_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args)
        elif x_dims[0].datatype == Dimension.Type.NUMERIC:
            return scatter_plot(df, x_dims[0].name, ys[0], fig_args, glyph_args)
    elif x_dim == 2 and y_dim == 1:
        if x_dims[0].datatype == Dimension.Type.CATEGORICAL:
            if x_dims[1].num_uniques < 13:  # arbitrary # for x_dim
                if x_dims[1].datatype == Dimension.Type.CATEGORICAL and y_dim < 13: ##### the branch of it bigger than 13
                   return bar_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args,
                           groupby=x_dims[1].name) # with group bar chart
                elif x_dims[1].datatype == Dimension.Type.SEQUENCE:
                    return line_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args) # with color data respect to x[0]
                elif x_dims[1].datatype == Dimension.Type.NUMERIC:
                    return scatter_plot(df, x_dims[1].name, ys[0], fig_args, glyph_args, groupby=x_dims[0].name) # with color data by respect to x[0]
            else:
                if x_dims[1].datatype ==Dimension.Type.CATEGORICAL:
                   return #  heat map
                elif x_dims[1].datatype == Dimension.Type.SEQUENCE:
                    return line_chart(df, x_dims[0].name, ys[0], fig_args, glyph_args) # with color data respect to xs
                elif x_dims[1].datatype == Dimension.Type.NUMERIC:
                    return scatter_plot(df, x_dims[0].name, ys[0], fig_args, glyph_args)
        elif x_dims[0].datatype == Dimension.Type.SEQUENCE:
            if x_dims[1].datatype == Dimension.Type.CATEGORICAL:
                if x_dims[1].num_uniques < 13:  # arbitrary # for x_dim
                    return None # FIXME colored line plot
                else:
                    return # heat map
        elif x_dims[0].datatype == Dimension.Type.NUMERIC:
            if x_dims[1].datatype == Dimension.Type.CATEGORICAL:
                return scatter_plot(df, x_dims[0].name, ys[0], fig_args, glyph_args, groupby=x_dims[1].name)

def bar_chart(df, x, y, fig_args, glyph_args, groupby=None):
    if groupby is None:
        df['_groupby'] = pd.Series(df.shape[0] * [''])
        groupby = '_groupby'
    x_values = list(df[x].unique())
    x_locs = dict((x, i) for i, x in enumerate(x_values))
    fig_args.setdefault('x_range', x_values)
    fig_args.setdefault('x_axis_label', x.title())
    set_y_range(fig_args, df[y])
    fig_args.setdefault('y_axis_label', y.title())

    num_groups = len(list(df[groupby].unique()))
    glyph_args['x'] = '_x'
    glyph_args['y'] = '_y'
    glyph_args['width'] = 1 / (num_groups + 1)
    glyph_args['height'] = y
    f = figure(**fig_args)
    for i, group in enumerate(df[groupby].unique()):
        plot_df = df[df[groupby] == group].copy().reset_index()
        plot_df['_x'] = plot_df[x].map(lambda x: x_locs[x] + (2 * i + num_groups + 3) / (2 * num_groups + 2))
        plot_df['_y'] = plot_df[y] / 2
        tooltips = [
            (fig_args['x_axis_label'], '@{}'.format(x)),
            (fig_args['y_axis_label'], '@{}'.format(y)),
        ]
        if num_groups > 1:
            tooltips.append(tuple([groupby.title(), '@{}'.format(groupby)]))
        renderer = f.rect(
                legend=group.title(),
                color=Pastel1_9[i],
                source=ColumnDataSource(plot_df),
                **glyph_args)
        f.add_tools(HoverTool(renderers=[renderer], tooltips=tooltips))
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

def scatter_plot(df, x, y, fig_args, glyph_args, groupby=None):
    if groupby is None:
        df['_groupby'] = pd.Series(df.shape[0] * [''])
        groupby = '_groupby'
    fig_args.setdefault('x_axis_label', x.title())
    fig_args.setdefault('y_axis_label', y.title())
    set_y_range(fig_args, df[y])

    num_groups = len(list(df[groupby].unique()))
    glyph_args['x'] = '_x'
    glyph_args['y'] = '_y'
    glyph_args.setdefault('size', 5)
    f = figure(**fig_args)
    for i, group in enumerate(df[groupby].unique()):
        plot_df = df[df[groupby] == group].copy().reset_index()
        plot_df['_x'] = plot_df[x]
        plot_df['_y'] = plot_df[y]
        tooltips = [
            (fig_args['x_axis_label'], '@{}'.format(x)),
            (fig_args['y_axis_label'], '@{}'.format(y)),
        ]
        if num_groups > 1:
            tooltips.append(tuple([groupby.title(), '@{}'.format(groupby)]))
        renderer = f.circle(
                legend=group.title(),
                color=Category10_10[i],
                source=ColumnDataSource(plot_df),
                **glyph_args
        )
        f.add_tools(HoverTool(renderers=[renderer], tooltips=tooltips))
    return f

def set_y_range(fig_args, values):
    minimum = min(values)
    maximum = max(values)
    if minimum >= 0:
        fig_args.setdefault('y_range', [0, 1.1 * maximum])
    elif maximum <= 0:
        fig_args.setdefault('y_range', [1.1 * minimum, 0])
    else:
        fig_args.setdefault('y_range', [1.1 * minimum, 1.1 * maximum])
