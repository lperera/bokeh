"""This is the Bokeh charts interface. It gives you a high level API to build
complex plot is a simple way.

This is the Line class which lets you build your Line charts just
passing the arguments to the Chart class and calling the proper functions.
"""
#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2014, Continuum Analytics, Inc. All rights reserved.
#
# Powered by the Bokeh Development Team.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from six import string_types
import numpy as np

from ..utils import cycle_colors
from .._builder import Builder, create_and_build
from ...models import ColumnDataSource, DataRange1d, GlyphRenderer, Range1d
from ...models.glyphs import Line as LineGlyph
from ...properties import Any

#-----------------------------------------------------------------------------
# Classes and functions
#-----------------------------------------------------------------------------


def Line(values, index=None, **kws):
    return create_and_build(LineBuilder, values, index=index, **kws)


class LineBuilder(Builder):
    """This is the Line class and it is in charge of plotting
    Line charts in an easy and intuitive way.
    Essentially, we provide a way to ingest the data, make the proper
    calculations and push the references into a source object.
    We additionally make calculations for the ranges.
    And finally add the needed lines taking the references from the source.
    """

    index = Any

    def __init__(self, values, index=None, legend=False, palette=None, **kws):
        """
        Args:
            values (iterable): iterable 2d representing the data series
                values matrix.
            index (str|1d iterable, optional): can be used to specify a
                common custom index for all data series as follows:
                    - As a 1d iterable of any sort that will be used as
                        series common index
                    - As a string that corresponds to the key of the
                        mapping to be used as index (and not as data
                        series) if area.values is a mapping (like a dict,
                        an OrderedDict or a pandas DataFrame)
            legend (str, optional): the legend of your chart. The legend
                content is inferred from incoming input.It can be
                ``top_left``, ``top_right``, ``bottom_left``,
                ``bottom_right``. ``top_right`` is set if you set it
                 as True. Defaults to None.
            palette(list, optional): a list containing the colormap as
                hex values.

        Attributes:
            source (obj): datasource object for your plot,
                initialized as a dummy None.
            x_range (obj): x-associated datarange object for you plot,
                initialized as a dummy None.
            y_range (obj): y-associated datarange object for you plot,
                initialized as a dummy None.
            groups (list): to be filled with the incoming groups of data.
                Useful for legend construction.
            data (dict): to be filled with the incoming data and be passed
                to the ColumnDataSource in each chart inherited class.
                Needed for _set_And_get method.
            attr (list): to be filled with the new attributes created after
                loading the data dict.
                Needed for _set_And_get method.
        """
        super(LineBuilder, self).__init__(values, **kws)
        self._source = None

    def get_data(self):
        """Calculate the chart properties accordingly from line.values.
        Then build a dict containing references to all the points to be
        used by the line glyph inside the ``draw`` method.
        """
        self._data = dict()
        # list to save all the attributes we are going to create
        self._attr = []
        xs = self._values_index
        self.set_and_get("x", "", np.array(xs))
        for col in self._values.keys():
            if isinstance(self.index, string_types) and col == self.index:
                continue

            # save every new group we find
            self._groups.append(col)
            values = [self._values[col][x] for x in xs]
            self.set_and_get("y_", col, values)

    def get_source(self):
        """
        Push the Line data into the ColumnDataSource and calculate the
        proper ranges.
        """
        self._source = ColumnDataSource(self._data)
        self.x_range = DataRange1d(sources=[self._source.columns("x")])

        y_names = self._attr[1:]
        endy = max(max(self._data[i]) for i in y_names)
        starty = min(min(self._data[i]) for i in y_names)
        self.y_range = Range1d(
            start=starty - 0.1 * (endy - starty),
            end=endy + 0.1 * (endy - starty)
        )

    def draw(self):
        """Use the line glyphs to connect the xy points in the Line.
        Takes reference points from the data loaded at the ColumnDataSource.
        """
        colors = cycle_colors(self._attr)
        for i, duplet in enumerate(self._attr[1:], start=1):
            glyph = LineGlyph(x='x', y=duplet, line_color=colors[i - 1])
            renderer = GlyphRenderer(data_source=self._source, glyph=glyph)
            self._legends.append((self._groups[i-1], [renderer]))
            yield renderer