from api import API
from apiutils import Controller
import json as jsonlib
from parsers import APIQuery
import parsers
from files import *
import xlsxwriter
import jsonutils
import os

if __name__ == "__main__":
    
    controller = Controller(headersFileName)
    controller.registerRateLimit(15, 1)
    controller.registerRateLimit(95, 120)

    api = API(endpointsFileName, argumentsFileName, controller)

    while True:

        queryString = input('Enter your query: ')

        try:
            values = parsers.findArgumentValues(queryString)
            skeletonQuery = parsers.parameterizeQuery(queryString)
            query = APIQuery(queryString, api)
        except Exception as e:
            print("There was an error creating the query. Error: " + str(e))

        try:
            json = query.execute(values)
        except Exception as e:
            print("There was an error executing the query. Error: " + str(e))

        if input('Print (Y/N): ') == 'Y':
            print(jsonlib.dumps(json, indent=4, sort_keys=True))
        if input('Save (Y/N): ') == 'Y':
            fileName = input('File Name: ')
            path = os.path.expanduser("~/Desktop/") + fileName + '.xlsx'
            print('Saving to: ' + path)
            try:
                workbook = xlsxwriter.Workbook(path)
                worksheet = workbook.add_worksheet('Sheet 1')
                jsonutils.writeToXLSX(worksheet, json)
                workbook.close()
            except Exception as e:
                print("There was an error saving your result. Error: " + str(e))
        #print(query._profile)

        
    #query = APIQuery('summoners{summonerName=?} -> matchlists matches[0]', api)
    #print(query.execute(['Darqk'], api))