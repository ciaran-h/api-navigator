from datetime import datetime
import time
import requests
import json
from urllib.error import HTTPError

# TODO: Expired and other exceptions 

def loadHeaders(fileName):

    with open(fileName, 'r') as headers:
        return json.load(headers)

class Controller():

    _timeErrorDelta = 0.1
    _minInterval = 0.2

    # TODO: Take in filename where rates are stored
    def __init__(self, headersFileName):
        self._headers = loadHeaders(headersFileName)
        self._requestRates = {}
        self._maxRequests = -1
        self._history = []
        # TODO: Move headers out of here
    

    def registerRateLimit(self, requests, interval):
        '''
        Set max requests made over the interval in seconds
        '''
        if interval < Controller._minInterval:
            raise ValueError('"interval" must be greater ' + 
            'than {0}.'.format(Controller._minInterval))
        
        if requests < 1:
            raise ValueError('"requests" must be greater than or equal to 1')

        # Add the request rates to the dictionary and update the max requests
        # Subtract a small amount from the interval to control for time 
        # calculation errors
        self._requestRates[requests] = interval - Controller._timeErrorDelta

        if requests > self._maxRequests:
            self._maxRequests = requests

    def _registerRequest(self):

        # We only need to keep track of the history of
        # request up the the maxRequests
        # So pop any extra requests
        # This is in a loop, but if used properly, should
        # only ever pop 1 at a time
        if self._maxRequests > 0:
            self._history.insert(0, datetime.now())
            while len(self._history) > self._maxRequests:
                self._history.pop()

    def _getWaitTimeForNewRequest(self):

        currentTime = datetime.now()
        maxWaitTime = 0

        for requests, interval in self._requestRates.items():
            # Check if we have even made enough requests to even break the limit
            if len(self._history) >= requests:
                # Find the interval of time between now and the <requests>th request
                requestsInterval = (currentTime - self._history[requests - 1]).total_seconds()
                # If the this interval is less than the rate interval, then making a request
                # now would exceed the rate
                if requestsInterval <= interval:
                    waitTime = interval - requestsInterval
                    if waitTime > maxWaitTime:
                        maxWaitTime = waitTime

        return maxWaitTime

    # TODO: Support other return types (maybe?)
    def getJSON(self, url):

        # Wait until request rates will be satisfied
        waitTime = self._getWaitTimeForNewRequest()
        if waitTime != 0:
            print("A rate limit was reached. Waiting {0} seconds".format(waitTime))
            time.sleep(waitTime)

        self._registerRequest()

        # Make the get request
        response = requests.get(url, headers=self._headers)

        if not response:
            # TODO: Make sure this works
            raise HTTPError(url, response.status_code, response.text, response.headers, '')

        contentType = response.headers['content-type'].split(';')

        # Ensure the response is a JSON
        if 'application/json' not in contentType:
            raise ValueError('The "endpoint" url\'s content type ({0}) must be "application/json".'.format(contentType))

        # Load the JSON and return it
        jsonResponse = json.loads(response.text)

        return jsonResponse

    def getTimeEstimate(self, numOfRequests):
        """
        Returns the approximate ammount of time it will take to complete
        <numOfRequests> requests.
        """
        raise NotImplementedError()



if __name__ == "__main__":
    
    #controller = APIController({})
    #controller.setRateLimit(5, 1)
    #controller.setRateLimit(10, 10)
    
    '''
    for i in range(15):
        print('Making {0}th request.'.format(i))
        controller.getJSON('', {})
    '''

    pass