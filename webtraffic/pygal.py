import datetime
import pygal
from decimal import Decimal
from . import ga4
from .appsettings import AppSettings

class PygalPlot():
    def __init__(self):
        self.__chart_config()

    def __chart_config(self):
        chart_config = pygal.Config()
        chart_config.legend_at_bottom = True
        chart_config.human_readable = True
        chart_config.fill = True
        chart_config.width = 300
        chart_config.height = 300
        chart_config.explicit_size = True

        self.chart_config = chart_config

        custom_style = pygal.style.Style(
          background='transparent',
          plot_background='transparent',
          foreground='#53E89B',
          foreground_strong='#53A0E8',
          foreground_subtle='#630C0D',
          opacity='.6',
          opacity_hover='.9',
          transition='400ms ease-in',
          x_label_rotation=25,
          colors=('#002080', '#4dff4d', '#00997a', '#002080', '#008000'))

        self.custom_style = custom_style

    def dateline_plot(self, title, date_x, *args):

        # see http://www.pygal.org/en/stable/documentation/types/xy.html

        dateline = pygal.DateLine(self.chart_config, style=self.custom_style)
        dateline.title = 'Users and New Users versus time'
        dateline.x_labels = [
                date_x[0],
                date_x[round((len(date_x)-1)*0.25)],
                date_x[round((len(date_x)-1)*0.5)],
                date_x[round((len(date_x)-1)*0.75)],
                date_x[round((len(date_x)-1)*1)]
        ]


        for a in args:
            dateline.add(a[0], [
                *a[1]
            ])

        mychart = dateline.render()
        mychart_str = mychart.decode('utf-8')
        return mychart_str

    def barchart_plot(self, title, buckets, *args):

        # see http://www.pygal.org/en/stable/documentation/types/bar.html

        line_chart = pygal.StackedBar(self.chart_config, style=self.custom_style)
        line_chart.title = title
        line_chart.x_labels = buckets
        for a in args:
            line_chart.add(a[0], a[1])

        mychart = line_chart.render()
        mychart_str = mychart.decode('utf-8')
        return mychart_str

    def xy_plot(self, title, *args):

        # see http://www.pygal.org/en/stable/documentation/types/bar.html

        xy_chart = pygal.XY(self.chart_config, style=self.custom_style, stroke=False)
        xy_chart.title = title

        for a in args:
            xy_chart.add(a[0], a[1])

        mychart = xy_chart.render()
        mychart_str = mychart.decode('utf-8')
        return mychart_str

    def piechart_plot(self, title, *args):

        # see http://www.pygal.org/en/stable/documentation/types/bar.html

        pie_chart = pygal.Pie(self.chart_config, style=self.custom_style)
        pie_chart.title = title

        for a in args:
            #print(a)
            for x in a:
                #print(x)
                pie_chart.add(x[0], x[1])

        mychart = pie_chart.render()
        mychart_str = mychart.decode('utf-8')
        return mychart_str
