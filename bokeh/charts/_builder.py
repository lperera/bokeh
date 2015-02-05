"""This is the Bokeh charts interface. It gives you a high level API to build
complex plot is a simple way.

This is the Builder class, a minimal prototype class to build more chart
types on top of it.
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

from .utils import cycle_colors
from ._chart import Chart
from ._data_adapter import DataAdapter
from ..models.ranges import Range
from ..properties import Any, Bool, HasProps, Instance

DEFAULT_PALETTE = ["#f22c40", "#5ab738", "#407ee7", "#df5320", "#00ad9c", "#c33ff3"]

#-----------------------------------------------------------------------------
# Classes and functions
#-----------------------------------------------------------------------------

def create_and_build(builder_class, values, **kws):
    builder_props = set(builder_class.properties())

    # create the new builder
    builder_kws = { k:v for k,v in kws.items() if k in builder_props}
    builder = builder_class(values, **builder_kws)

    # create a chart to return, since there isn't one already
    chart_kws = { k:v for k,v in kws.items() if k not in builder_props}
    chart = Chart(**chart_kws)
    chart.add_builder(builder)

    return chart


class Builder(HasProps):
    """ A prototype class to inherit each new chart Builder type.

    It provides useful methods to be used by the inherited builder classes,
    in order to automate most of the charts creation tasks and leave the
    core customization to specialized builder classes. In that pattern
    inherited builders just need to provide:

     - the following methods:
        * draw: yields the glyphs to be rendered into the plot (and
            eventually create the self._legends attribute to be used to
            create the proper legends when builder is called to build
            the glyphs on a Chart object
        * get_data(optional): Get the input data and calculates the 'data'
            attribute to be used to calculate the source data
        * get_source(optional): Push data into the self.source attribute
            (of type ColumnDataSource) and build the proper ranges
            (self.x_range and self.y_range).

    - the following attributes:
        x_range:
        y_range:
        _legends:


    so Builder can use it all to draw on a chart when called with the
    create method.

    """

    x_range = Instance(Range)
    y_range = Instance(Range)

    alette = Any

    def __init__(self, values=None, **kws):
        """Common arguments to be used by all the inherited classes.

        Args:
            values (iterable): iterable 2d representing the data series
                values matrix.
            legend (str, bool): the legend of your plot. The legend content is
                inferred from incoming input.It can be ``top_left``,
                ``top_right``, ``bottom_left``, ``bottom_right``.
                It is ``top_right`` is you set it as True.
            palette(list, optional): a list containing the colormap as hex values.


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
        super(Builder, self).__init__(**kws)
        if values is None:
            values = []

        self._values = values
        # TODO: No real reason why legends should be *private*, should be
        # legends
        self._legends = []
        self._data = {}
        self._groups = []
        self._attr = []

    def prepare_values(self):
        """Prepare the input data.

        Converts data input (self._values) to a DataAdapter and creates
        instance index if needed
        """
        if hasattr(self, 'index'):
            self._values_index, self._values = DataAdapter.get_index_and_data(
                self._values, self.index
            )
        else:
            if not isinstance(self._values, DataAdapter):
                self._values = DataAdapter(self._values, force_alias=False)

    def get_data(self):
        """Get the input data.

        It has to be implemented by any of the inherited class
        representing each different chart type. It is the place
        where we make specific calculations for each chart.
        """
        pass

    def get_source(self):
        """Push data into the ColumnDataSource and build the
        proper ranges.

        It has to be implemented by any of the inherited class
        representing each different chart type.
        """
        pass

    def draw(self):
        """ Generator that yields the glyphs to be draw on the plot

        It has to be implemented by any of the inherited class
        representing each different chart type.
        """
        pass

    def create(self, chart=None):
        self.prepare_values()
        self.get_data()
        self.get_source()
        renderers = self.draw()

        chart.add_renderers(self, renderers)

        # create chart ranges..
        if not chart.x_range:
            chart.x_range = self.x_range
        if not chart.y_range:
            chart.y_range = self.y_range

        # create the legends if needed
#         if self.legend:
#             if self.legend is True:
#                     orientation = "top_right"
#             else:
#                 orientation = self._legend
#
        # always contribute legends, let Chart sort it out
        legends = self._legends
        chart.add_legend(legends)

        return chart

    #***************************
    # Some helper methods
    #***************************

    def _set_and_get(self, data, prefix, attr, val, content):
        """Set a new attr and then get it to fill the self._data dict.

        Keep track of the attributes created.

        Args:
            data (dict): where to store the new attribute content
            attr (list): where to store the new attribute names
            val (string): name of the new attribute
            content (obj): content of the new attribute
        """
        data[prefix + val] = content
        attr.append(prefix + val)

    def set_and_get(self, prefix, val, content):
        """Set a new attr and then get it to fill the self._data dict.

        Keep track of the attributes created.

        Args:
            prefix (str): prefix of the new attribute
            val (string): name of the new attribute
            content (obj): content of the new attribute
        """
        self._set_and_get(self._data, prefix, self._attr, val, content)


