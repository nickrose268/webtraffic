from django.core.management.base import BaseCommand
import datetime
import re
from webtraffic import models

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('infile', type=str, help='file for import')
        parser.add_argument('action', type=str, help='putm|putd')

    def handle(self, *args, **kwargs):
        file_name = kwargs['infile']
        action = kwargs['action']

        if action == 'putm':
            self.put(file_name, 'putm')
            self.stdout.write(self.style.SUCCESS('Metrics inserted successfully'))
        elif action == 'putd':
            self.put(file_name, 'putd')
            self.stdout.write(self.style.SUCCESS('Dimensions inserted successfully'))
        else:
            self.stdout.write('Command line error: should be putm or putd')

    # def get_data(self, file_name):
    #     file_name = file_name
    #     myfile = open(file_name, "a+")
    #     list = fda.search_food("+description:raw", get_page = '4')
    #
    #     for f in list:
    #         myfile.write(f'Y : {f[0]} : {f[1]}\n')
    #
    #     myfile.close()

    def put(self, file_name, action):
        file_name = file_name

        myfile = open(file_name, "r")

        hits = []
        for line in myfile.readlines():
            result =  re.findall("ga:\w+", line)
            if result:
                hits = hits + result

        if action == 'putm':
            for i in hits:
                models.GaMetric.objects.create(name=i)
        elif action == 'putd':
            for i in hits:
                models.GaDimension.objects.create(name=i)
        else:
            print("Unknown action")

        myfile.close()
