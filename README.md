# webtraffic
A Django application for interacting with Google Analytics

The application is an interface to the Google Analytics Reporting API version 4

Here are some links to the Google documentation:
https://developers.google.com/analytics/devguides/reporting/core/v4/samples?hl=en_US
https://developers.google.com/analytics/devguides/reporting/core/v4/basics

The dimensions and metrics explorer is available here:
https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/?hl=en_US#ga:socialInteractionAction


Currently the application:

1) Connect and communicate to Google:
ga4.py

2) Creates various models based on grouping types of request together:
ga4models.py

3) Provides various generic plot functions based on Pygal:
pygal.py

4) Standard Django database and presentation logic:
models.py
views.py
urls.py

Prerequisites:

Describe here the authentication and authorisation process at Google
