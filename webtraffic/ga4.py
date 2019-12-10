"""Hello Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from django.conf import settings


class Ga4Connector():

    def __init__(self, view_id, **kwargs):
        self.view_id = view_id
        if kwargs.get('caller', '' ) == 'main':
            self.KEY_FILE_LOCATION = 'XXXXXXXXXXXXXXXXXXXXX'
        else:
            self.KEY_FILE_LOCATION = settings.KEY_FILE_LOCATION
        self.SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
        self.analytics = self.__initialize_analyticsreporting()

    def __initialize_analyticsreporting(self):
        """Initializes an Analytics Reporting API V4 service object.

        Returns:
        An authorized Analytics Reporting API V4 service object.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
          self.KEY_FILE_LOCATION, self.SCOPES)

        # Build the service object.
        analytics = build('analyticsreporting', 'v4', credentials=credentials)

        return analytics


    def __get_report(self, dates_l, metrics_l, dimensions_l):

        """Queries the Analytics Reporting API V4.

        Args:
        analytics: An authorized Analytics Reporting API V4 service object.
        Returns:
        The Analytics Reporting API V4 response.
        """
        return self.analytics.reports().batchGet(
          body={
            'reportRequests': [
            {
              'viewId': self.view_id,
              'dateRanges': dates_l,
              'metrics': metrics_l,
              'dimensions': dimensions_l
            }]
          }
        ).execute()

    def __parse_response(self, response):
        """Parses and prints the Analytics Reporting API V4 response.

        Args:
        response: An Analytics Reporting API V4 response.
        """

     #    WE NEED TO UNPACK THE FOLLOWING STRUCTURE
     #
     # response = {'reports': [{
     #            'columnHeader': {
     #                'dimensions': ['ga:city', 'ga:country'],
     #                'metricHeader':{
     #                    'metricHeaderEntries': [
     #                            {'name': 'ga:sessions', 'type': 'INTEGER'},
     #                            {'name': 'ga:hits', 'type': 'INTEGER'}
     #                            ] # metric header entries
     #                        } #metric header
     #                    }, # column header
     #
     #             'data': {
     #                'rows': [
     #                    {'dimensions': ['Copenhagen', 'Denmark'], 'metrics': [{'values': ['2', '2']}]},
     #                    {'dimensions': ['Edmonton', 'Canada'], 'metrics': [{'values': ['1', '2']}]},
     #                    {'dimensions': ['Irvine', 'United States'], 'metrics': [{'values': ['1', '1']}]},
     #                    {'dimensions': ['La Crescenta-Montrose', 'United States'], 'metrics': [{'values': ['1', '3']}]}
     #                ], #rows
     #                    'totals': [{'values': ['5', '8']}],
     #                    'rowCount': 4,
     #                    'minimums': [{'values': ['1', '1']}],
     #                    'maximums': [{'values': ['2', '3']}],
     #                    'isDataGolden': True
     #                } # data
     #            }] # reports
     #        } # response


        for report in response.get('reports', []):
            columnHeader = report.get('columnHeader', {})
            dimension_headers = columnHeader.get('dimensions',[])
            metric_headers = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
            metric_headers = [ x['name'] for x in metric_headers if 'name' in x]
            headers = dimension_headers + metric_headers
            #print('THE HEADERS ARE', headers)

            data = []
            for row in report.get('data', {}).get('rows', []):
                dimension_data = row.get('dimensions', [])
                metric_data = row.get('metrics', [])
                metric_data = [ x['values'] for x in metric_data]
                metric_data = [ x for x in metric_data]
                metric_data = [ x for xx in metric_data for x in xx]
                data.append(dimension_data + metric_data)
            #print('THE DATA ARE', data)

        return {'headers': headers, 'data': data}


    def get_data(self, dates, metrics, dimensions):

        for date_pair in dates:
            if datetime.strptime(date_pair[0], '%Y-%m-%d') > datetime.strptime(date_pair[1],'%Y-%m-%d'):
                return 0, f'Please ensure that start date is before end date: date_pair[0], date_pair[1]', ''

        # google has a maximum limit of 7 dimensions and 10 metrics in any one call
        dimensions_l = [{'name': i} for i in dimensions[:7]]
        metrics_l = [{'expression': i} for i in metrics[:10]]
        dates_l = [{'startDate': d[0], 'endDate': d[1]} for d in dates[:20]]

        response = self.__get_report(dates_l, metrics_l, dimensions_l)

        if len(dimensions) > 7 or len(metrics) > 10:
            message = "Warning: Only the first 7 dimensions and first 10 metrics have been procesessed"
        else:
            message = "get_ga4 returned normally"

        return 1, message, self.__parse_response(response)

def main():
    # below are some arbitrary parametes for command line testing purposes
    view_id = '191901263'
    dates = [('2019-11-29', '2019-11-30')]
    metrics = ['ga:sessions', 'ga:hits', 'ga:users', 'ga:newUsers']
    dimensions = ['ga:city', 'ga:country', 'ga:date']
    ga4con = ga4.Ga4Connector(view_id, caller = 'main')
    status, message, result = ga4con.get_data(dates, metrics, dimensions)
    print(status, message, result)

if __name__ == '__main__':
    main()
