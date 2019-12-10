import datetime
import pygal
from decimal import Decimal
import numpy as np
import pandas as pd
from . import ga4, pygal
from .appsettings import AppSettings

class GeneralPanda():
    def __init__(self, dates, metrics, dimensions):
        view_id=AppSettings.VIEW_ID
        ga4con = ga4.Ga4Connector(view_id)
        status, message, result = ga4con.get_data(dates, metrics, dimensions)
        self.headers = result.get('headers', [])
        self.data = result.get('data', [])
        self.df = pd.DataFrame(
            self.data,
            index = [x for x in range(len(self.data))],
            columns = self.headers,
        )
        self.df['ga:users'] = self.df['ga:users'].astype(int)
        self.df['ga:newUsers'] = self.df['ga:newUsers'].astype(int)
        self.df['ga:sessions'] = self.df['ga:sessions'].astype(int)
        self.df['ga:hits'] = self.df['ga:hits'].astype(int)
        print(self.df)
        print(self.df.dtypes)
        print(self.df.index)
        print(self.df.columns)
        print(self.df.values)
        print(self.df.describe())



class GeoPanda(GeneralPanda):
    def __init__(self, date_start, date_end):
        self.plotter = pygal.PygalPlot()
        dates=[(date_start, date_end)]
        dimensions=['ga:date', 'ga:city', 'ga:country', 'ga:continent']
        metrics=['ga:users', 'ga:newUsers', 'ga:sessions', 'ga:hits' ]
        # there are no blanks to backfill so set blanks to False in super call
        super().__init__(dates, metrics, dimensions)
