import datetime
import pygal
from decimal import Decimal
from . import ga4, pygal
from .appsettings import AppSettings

class GeneralModel():
    def __init__(self, dates, metrics, dimensions, blanks):
        view_id=AppSettings.VIEW_ID
        ga4con = ga4.Ga4Connector(view_id)
        status, message, result = ga4con.get_data(dates, metrics, dimensions)
        self.headers = result.get('headers', [])
        self.data = result.get('data', [])
        if blanks:
            self.__fill_blanks()


    def __fill_blanks(self):

        def get_date(d):
            return datetime.date(
                            int(d[:4]),
                            int(d[4:6]),
                            int(d[6:8])
                        )

        if 'ga:date' in self.headers:
            date_i = self.headers.index('ga:date')
        else:
            return         # we only backfill if date present

        start_date = get_date(self.data[0][date_i])
        end_date = get_date(self.data[-1][date_i])
        numdays = (end_date - start_date).days + 1
        dates_all = [start_date + datetime.timedelta(days=x) for x in range(numdays)]
        list1 = [ x.strftime("%Y%m%d") for x in dates_all ]
        list2 = [ x[date_i] for x in self.data]

        # for x, y in zip(list1, list2):
        #     print(x,y)

        #zeros = [ 0 for x in range(len(self.data[0]))]

        i = 0
        while i < len(list2):
            if list2[i] != list1[i]:
                list2.insert(i, list1[i])
                #insert_list = zeros         # the commented out use of a prebuilt zeros list doesn't work!! because any update to zeros changes all the intances of zeros!
                insert_list = [ 0 for x in range(len(self.data[0]))]
                insert_list[date_i] = list1[i]
                self.data.insert(i, insert_list)
            i += 1

        self.date_x = [get_date(x) for sublist in self.data for x in sublist[0:1]]


class TrafficModel(GeneralModel):

    # dimensions=['ga:date', 'ga:month']
    # metrics=['ga:users', 'ga:newUsers', 'ga:pageViews', 'ga:pageViewsPerSession', 'ga:sessions', 'ga:sessionDuration']

    def __init__(self, date_start, date_end):
        self.plotter = pygal.PygalPlot()
        dates=[(date_start, date_end)]
        dimensions=['ga:date', 'ga:month']
        metrics=['ga:users', 'ga:newUsers', 'ga:pageViews', 'ga:pageViewsPerSession', 'ga:sessions', 'ga:sessionDuration']
        super().__init__(dates, metrics, dimensions, True)

    def __date_users_plot(self):

        text='Users and returning users are plotted as a function of time. It is difficult to see any trend in this relatively small data set, \
        although one can conclude that the majority of users are new users.'

        xy1_list=[]
        xy2_list=[]
        users = [ int(x[self.headers.index('ga:users')]) for x in self.data]
        newusers = [ int(x[self.headers.index('ga:newUsers')]) for x in self.data]
        for x, y in zip(self.date_x, users):
            xy1_list.append((x,y))
        for x, y in zip(self.date_x, users):
            xy2_list.append((x,y))

        title = 'Users and New Users versus time'
        return self.plotter.dateline_plot(
                        title,
                        self.date_x,
                        ('Returning Users', xy1_list),
                        ('New Users', xy2_list),
                        ), text

    def __date_sessions_plot(self):

        text="Sessions are plotted as a function of time. It is difficult to see any trend in this relatively small data set.\
        but peaks almost certainly correspond to facebook campaigns or other events."

        xy1_list=[]
        y1 = [ int(x[self.headers.index('ga:sessions')]) for x in self.data]
        for x, y in zip(self.date_x, y1):
            xy1_list.append((x,y))

        title = 'Sessions versus time'
        return self.plotter.dateline_plot(
                        title,
                        self.date_x,
                        ('Sessions', xy1_list),
                        ), text


    def __month_users_plot(self):

        text='Barchart of number returning and new users per month'

        date_i = self.headers.index('ga:date')
        users_i = self.headers.index('ga:users')
        newusers_i = self.headers.index('ga:newUsers')
        buckets = []
        retusers = []
        newusers = []
        for d in self.data:
            month =  d[date_i][:6]
            if month not in buckets:     # slicing date string 20190401
                buckets.append(month)
                retusers.append(0)
                newusers.append(0)
            i = buckets.index(month)
            newusers[i] += int(d[newusers_i])
            retusers[i] += int(d[users_i])-int(d[newusers_i])

        title = 'Returning Users and New Users per month'
        return self.plotter.barchart_plot(
                        title,
                        buckets,
                        ('Returning Users', retusers),
                        ('New Users',  newusers)
                        ), text

    def __pageviews_duration_plot(self):

        # dimensions=['ga:date', 'ga:month']
        # metrics=['ga:users', 'ga:newUsers', 'ga:pageViews', 'ga:pageViewsPerSession', 'ga:sessions', 'ga:sessionDuration']

        text = "Session duration is plotted as a function of average pageviews per session. One might expect these to be positively correlated. \
        if we remove the outliers at the far right of the diagram then the correlation will \
        be better - these are maybe robots?"

        duration_i = self.headers.index('ga:sessionDuration')
        vpers_i = self.headers.index('ga:pageViewsPerSession')
        xy_data = []
        for d in self.data:
            xy_data.append( (Decimal(d[duration_i]), Decimal(d[vpers_i])) )                     # tuples of (x,y)

        title = 'Session duration versus average page views per session'
        return self.plotter.xy_plot(
                        title,
                        ('All data', xy_data),
                        ), text

    def get_context(self):

        context = {}

        context['plot1'] = {
                        'plot' : self.__date_users_plot()[0],
                        'text' : self.__date_users_plot()[1],
                        }

        context['plot2'] = {
                        'plot' : self.__date_sessions_plot()[0],
                        'text' : self.__date_sessions_plot()[1],
                        }

        context['plot3'] = {
                        'plot' : self.__month_users_plot()[0],
                        'text' : self.__month_users_plot()[1],
                        }

        context['plot4'] = {
                        'plot' : self.__pageviews_duration_plot()[0],
                        'text' : self.__pageviews_duration_plot()[1],
                        }


        return context

class GeoModel(GeneralModel):

    # dimensions=['ga:date']
    # metrics=['ga:users', 'ga:newUsers', 'ga:pageViews', 'ga:pageViewsPerSession', 'ga:sessions', 'ga:sessionDuration']

    def __init__(self, date_start, date_end):
        self.plotter = pygal.PygalPlot()
        dates=[(date_start, date_end)]
        dimensions=['ga:date', 'ga:city', 'ga:country', 'ga:continent']
        metrics=['ga:users', 'ga:newUsers', 'ga:sessions', 'ga:hits' ]
        # there are no blanks to backfill so set blanks to False in super call
        super().__init__(dates, metrics, dimensions, False)

    def __country_users_plot(self):

        text='Users from each country.'

        var_i = self.headers.index('ga:country')
        val_i = self.headers.index('ga:users')
        vars = []
        sums = []
        for d in self.data:
            if d[var_i] not in vars:
                vars.append(d[var_i])
                sums.append(0)
            i_c = vars.index(d[var_i])
            sums[i_c] += int(d[val_i])

        pie_list = []
        for v, s in zip(vars,sums):
            pie_list.append((v,s))

        title = '% of total users in each country'
        return self.plotter.piechart_plot(
                        title,
                        pie_list,
                        ), text


    def __continent_hits_plot(self):
        text='Hits from each continent. Of course this can also be plotted as a function of time'

        var_i = self.headers.index('ga:continent')
        val_i = self.headers.index('ga:hits')
        vars = []
        sums = []
        for d in self.data:
            if d[var_i] not in vars:
                vars.append(d[var_i])
                sums.append(0)
            i_c = vars.index(d[var_i])
            sums[i_c] += int(d[val_i])

        pie_list = []
        for v, s in zip(vars,sums):
            pie_list.append((v,s))

        title = '% of hits from each continent.'
        return self.plotter.piechart_plot(
                        title,
                        pie_list,
                        ), text


    def __continent_month_plot(self):

        text='Barchart of number users from each continent per month'

        date_i = self.headers.index('ga:date')
        users_i = self.headers.index('ga:users')
        cont_i = self.headers.index('ga:continent')
        buckets = []
        europe = []
        americas = []
        asia = []
        oceania = []
        for d in self.data:
            month =  d[date_i][:6]
            if month not in buckets:     # slicing date string 20190401
                buckets.append(month)
                europe.append(0)
                americas.append(0)
                asia.append(0)
                oceania.append(0)
            i = buckets.index(month)
            if d[cont_i] == 'Europe':
                europe[i] += int(d[users_i])
            elif d[cont_i] == 'Americas':
                americas[i] += int(d[users_i])
            elif d[cont_i] == 'Asia':
                asia[i] += int(d[users_i])
            elif d[cont_i] == 'Oceania':
                oceania[i] += int(d[users_i])


        title = 'Users from each continent per month'
        return self.plotter.barchart_plot(
                        title,
                        buckets,
                        ('Europe', europe),
                        ('Americas',  americas),
                        ('Asia',  asia),
                        ('Oceania',  oceania),
                        ), text

    def __cph_others_plot(self):

        text='Number of hits from Copenhagen and other cities against time.'

        date_i = self.headers.index('ga:date')
        hits_i = self.headers.index('ga:hits')
        city_i = self.headers.index('ga:city')
        days = []
        cph = []
        other = []
        for d in self.data:
            day =  d[date_i]
            #print('DAY', d)
            if day not in days:     # slicing date string 20190401
                days.append(day)
                cph.append(0)
                other.append(0)
            i = days.index(day)
            if d[city_i] == 'Copenhagen':
                cph[i] += int(d[hits_i])
            else:
                other[i] += int(d[hits_i])

        # for x,y,z in zip(days, cph, other):
        #     print(x, y, z)

        def get_date(d):
            return datetime.date(
                            int(d[:4]),
                            int(d[4:6]),
                            int(d[6:8])
                        )
        date_x = [get_date(x) for x in days]

        # for x,y,z in zip(date_x, cph, other):
        #     print(x, y, z)

        cph_list = []
        other_list = []
        for x, y in zip(date_x, cph):
            cph_list.append((x,y))
        for x, y in zip(date_x, other):
            other_list.append((x,y))

        title = 'Hits from Copenhagen versus time'
        return self.plotter.dateline_plot(
                    title,
                    date_x,
                    ('Copenhagen hits', cph_list),
                    ('All other hits', other_list),
                    ), text

    def get_context(self):

        context = {}

        context['plot1'] = {
                        'plot' : self.__country_users_plot()[0],
                        'text' : self.__country_users_plot()[1],
                        }

        context['plot2'] = {
                        'plot' : self.__continent_hits_plot()[0],
                        'text' : self.__continent_hits_plot()[1],
                        }

        context['plot3'] = {
                        'plot' : self.__continent_month_plot()[0],
                        'text' : self.__continent_month_plot()[1],
                        }

        context['plot4'] = {
                        'plot' : self.__cph_others_plot()[0],
                        'text' : self.__cph_others_plot()[1],
                        }

        return context


class TechModel(GeneralModel):

    def __init__(self, date_start, date_end):
        self.plotter = pygal.PygalPlot()
        dates=[(date_start, date_end)]
        dimensions=['ga:browser', 'ga:language', 'ga:operatingSystem', 'ga:continent']
        metrics=['ga:hits', 'ga:sessions']
        # there are no blanks to backfill so set blanks to False in super call
        super().__init__(dates, metrics, dimensions, False)

    def __browser_sessions_plot(self):

        text='Sessions by browser type.'

        var_i = self.headers.index('ga:browser')
        val_i = self.headers.index('ga:sessions')
        vars = []
        sums = []
        for d in self.data:
            if d[var_i] not in vars:
                vars.append(d[var_i])
                sums.append(0)
            i_c = vars.index(d[var_i])
            sums[i_c] += int(d[val_i])

        pie_list = []
        for v, s in zip(vars,sums):
            pie_list.append((v,s))

        title = 'Total sessions per browser type'
        return self.plotter.piechart_plot(
                        title,
                        pie_list,
                        ), text


    def __lang_sessions_plot(self):
        text='Sessions by language. This is the language setting in the browser, i.e. probably \
        hints at the users native language.'

        var_i = self.headers.index('ga:language')
        val_i = self.headers.index('ga:sessions')
        vars = []
        sums = []
        for d in self.data:
            if d[var_i] not in vars:
                vars.append(d[var_i])
                sums.append(0)
            i_c = vars.index(d[var_i])
            sums[i_c] += int(d[val_i])

        pie_list = []
        for v, s in zip(vars,sums):
            pie_list.append((v,s))

        title = 'Total sessions by language.'
        return self.plotter.piechart_plot(
                        title,
                        pie_list,
                        ), text


    def __continent_browser_plot(self):

        text='Barchart of continents represented for each browser'

        br_i = self.headers.index('ga:browser')
        cont_i = self.headers.index('ga:continent')
        sessions_i = self.headers.index('ga:sessions')
        buckets = []
        europe = []
        americas = []
        asia = []
        oceania = []
        for d in self.data:
            browser =  d[br_i]
            if browser not in buckets:     # slicing date string 20190401
                buckets.append(browser)
                europe.append(0)
                americas.append(0)
                asia.append(0)
                oceania.append(0)
            i = buckets.index(browser)
            if d[cont_i] == 'Europe':
                europe[i] += int(d[sessions_i])
            elif d[cont_i] == 'Americas':
                americas[i] += int(d[sessions_i])
            elif d[cont_i] == 'Asia':
                asia[i] += int(d[sessions_i])
            elif d[cont_i] == 'Oceania':
                oceania[i] += int(d[sessions_i])

        title = 'Continents for each browser'
        return self.plotter.barchart_plot(
                        title,
                        buckets,
                        ('Europe', europe),
                        ('Americas',  americas),
                        ('Asia',  asia),
                        ('Oceania',  oceania),
                        ), text

    def __continent_os_plot(self):

        text='Barchart of continents represented for each operating system'

        os_i = self.headers.index('ga:operatingSystem')
        cont_i = self.headers.index('ga:continent')
        sessions_i = self.headers.index('ga:sessions')
        buckets = []
        europe = []
        americas = []
        asia = []
        oceania = []
        for d in self.data:
            os =  d[os_i]
            if os not in buckets:     # slicing date string 20190401
                buckets.append(os)
                europe.append(0)
                americas.append(0)
                asia.append(0)
                oceania.append(0)
            i = buckets.index(os)
            if d[cont_i] == 'Europe':
                europe[i] += int(d[sessions_i])
            elif d[cont_i] == 'Americas':
                americas[i] += int(d[sessions_i])
            elif d[cont_i] == 'Asia':
                asia[i] += int(d[sessions_i])
            elif d[cont_i] == 'Oceania':
                oceania[i] += int(d[sessions_i])

        title = 'Barchart of continents represented for each operating system'
        return self.plotter.barchart_plot(
                        title,
                        buckets,
                        ('Europe', europe),
                        ('Americas',  americas),
                        ('Asia',  asia),
                        ('Oceania',  oceania),
                        ), text

    def get_context(self):

        context = {}

        context['plot1'] = {
                        'plot' : self.__browser_sessions_plot()[0],
                        'text' : self.__browser_sessions_plot()[1],
                        }

        context['plot2'] = {
                        'plot' : self.__lang_sessions_plot()[0],
                        'text' : self.__lang_sessions_plot()[1],
                        }

        context['plot3'] = {
                        'plot' : self.__continent_browser_plot()[0],
                        'text' : self.__continent_browser_plot()[1],
                        }

        context['plot4'] = {
                        'plot' : self.__continent_os_plot()[0],
                        'text' : self.__continent_os_plot()[1],
                        }

        return context


class SiteModel(GeneralModel):

    def __init__(self, date_start, date_end):
        self.plotter = pygal.PygalPlot()
        dates=[(date_start, date_end)]
        dimensions=['ga:pagePath', 'ga:fullReferrer', 'ga:landingPagePath', 'ga:exitPagePath']
        metrics=['ga:hits', 'ga:sessions']
        # there are no blanks to backfill so set blanks to False in super call
        super().__init__(dates, metrics, dimensions, False)

    def __hits_page_plot(self):

        text='This show which pages get the most hits. All the plots in this page can be expressed versus\
        time, I have just picked pie charts to save time'

        var_i = self.headers.index('ga:pagePath')
        val_i = self.headers.index('ga:hits')
        vars = ['post', 'kontakt', 'faq', 'about-brigitte', 'test-depression', 'english-psychotherapy', '/ ', 'Other']
        sums = [0,0,0,0,0,0,0]
        for d in self.data:
            for v in vars:
                if v in d[var_i]:
                    i = vars.index(v)
                    sums[i] += int(d[val_i])
                else:
                    sums[-1] += int(d[val_i])

        pie_list = []
        for v, s in zip(vars,sums):
            pie_list.append((v,s))

        title = 'Hits per page'
        return self.plotter.piechart_plot(
                        title,
                        pie_list,
                        ), text


    def __sessions_entry_plot(self):

        text='This shows entry pages (landing page) for the site'

        var_i = self.headers.index('ga:landingPagePath')
        val_i = self.headers.index('ga:sessions')
        vars = ['post', 'fbclid', 'kontakt', 'faq', 'about-brigitte', 'test-depression', 'english-psychotherapy', '/ ', 'Other']
        sums = [0,0,0,0,0,0,0]
        for d in self.data:
            for v in vars:
                if v in d[var_i]:
                    i = vars.index(v)
                    sums[i] += int(d[val_i])
                else:
                    sums[-1] += int(d[val_i])

        pie_list = []
        for v, s in zip(vars,sums):
            pie_list.append((v,s))

        title = 'Entry pages'
        return self.plotter.piechart_plot(
                        title,
                        pie_list,
                        ), text



    def __sessions_exit_plot(self):

        text='This shows exit pages for the site. This is the læast page the user was on before leaving.'

        var_i = self.headers.index('ga:exitPagePath')
        val_i = self.headers.index('ga:hits')
        vars = ['post', 'kontakt', 'faq', 'about-brigitte', 'test-depression', 'english-psychotherapy', '/ ', 'Other']
        sums = [0,0,0,0,0,0,0]
        for d in self.data:
            for v in vars:
                if v in d[var_i]:
                    i = vars.index(v)
                    sums[i] += int(d[val_i])
                else:
                    sums[-1] += int(d[val_i])

        pie_list = []
        for v, s in zip(vars,sums):
            pie_list.append((v,s))

        title = 'Exit pages'
        return self.plotter.piechart_plot(
                        title,
                        pie_list,
                        ), text

    def __sessions_referrer_plot(self):

        text='This the referrer. I.e. when someone has clicked on a link from another site.'

        var_i = self.headers.index('ga:fullReferrer')
        val_i = self.headers.index('ga:sessions')
        vars = ['google', 'facebook', 'linked-in', 'Other']
        sums = [0,0,0,0,0,0,0]
        for d in self.data:
            for v in vars:
                if v in d[var_i]:
                    i = vars.index(v)
                    sums[i] += int(d[val_i])
                else:
                    sums[-1] += int(d[val_i])

        pie_list = []
        for v, s in zip(vars,sums):
            pie_list.append((v,s))

        title = 'Referring sites'
        return self.plotter.piechart_plot(
                        title,
                        pie_list,
                        ), text


    def get_context(self):

        context = {}

        context['plot1'] = {
                        'plot' : self.__hits_page_plot()[0],
                        'text' : self.__hits_page_plot()[1],
                        }

        context['plot2'] = {
                        'plot' : self.__sessions_entry_plot()[0],
                        'text' : self.__sessions_entry_plot()[1],
                        }

        context['plot3'] = {
                        'plot' : self.__sessions_exit_plot()[0],
                        'text' : self.__sessions_exit_plot()[1],
                        }

        context['plot4'] = {
                        'plot' : self.__sessions_referrer_plot()[0],
                        'text' : self.__sessions_referrer_plot()[1],
                        }

        return context
