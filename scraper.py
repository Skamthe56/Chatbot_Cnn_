import requests, json
from bs4 import BeautifulSoup
import traceback
import datetime
from datetime import datetime

class scraper(object):
    url=str('http://ojp.nationalrail.co.uk/service/timesandfares/')
    @staticmethod
    def scrape_tickets(user_input):
        isReturn=False
        returndate= None
        updated_url= scraper.url + user_input['fromLocat'] + '/' + user_input['toLocat']+ '/' + user_input['travelDate'] + '/' + user_input['travelTime'] + '/dep'
        print("single url:",updated_url)
        if ('returnDate' in user_input):
            isReturn=True
            returndate= user_input['returnDate']
            updated_url= updated_url+'/'+ user_input['returnDate'] + '/' + user_input['returnTime'] + '/dep'
            print("return url:",updated_url)
        page=scraper.getPage(updated_url)
        print("page from main",page)
        get_cheapest= scraper.getCheapestticket(page, isReturn, user_input['travelDate'], returndate,updated_url)
        return get_cheapest
    #getPage
    @staticmethod
    def getPage(url):
        req = requests.get(url)
        return BeautifulSoup(req.text, 'html.parser')
    
    #get cheapest ticket 
    @staticmethod
    def getCheapestticket(page, isReturn, departDate, returnDate,url_new):
        try:
            script_tag= page.find('script', {'type':'application/json'})
            #print("script tag",script_tag)
            info = json.loads(script_tag.contents[0])
            #info = json.loads(page_contents.find('script', {'type':'application/json'}).text)
            #print("WS:after change",info)
            ticket = {}
            ticket['url'] = url_new
            ticket['isReturn'] = isReturn
            ticket['departDate'] = scraper.custom_to_date(departDate, '%d-%b-%Y')
            ticket['departureStationName'] = str(info['jsonJourneyBreakdown']['departureStationName'])
            ticket['arrivalStationName'] = str(info['jsonJourneyBreakdown']['arrivalStationName'])
            ticket['departureTime'] = str(info['jsonJourneyBreakdown']['departureTime'])
            ticket['arrivalTime'] = str(info['jsonJourneyBreakdown']['arrivalTime'])
            durationHours = str(info['jsonJourneyBreakdown']['durationHours'])
            durationMinutes = str(info['jsonJourneyBreakdown']['durationMinutes'])
            ticket['duration'] = (durationHours + 'h ' + durationMinutes + 'm')
            ticket['changes'] = str(info['jsonJourneyBreakdown']['changes'])
            #print("WS: ticket", ticket)

            if isReturn:
                ticket['returnDate'] = scraper.custom_to_date(returnDate, '%d-%b-%Y')
                ticket['fareProvider'] = info['returnJsonFareBreakdowns'][0]['fareProvider']
                ticket['returnTicketType'] = info['returnJsonFareBreakdowns'][0]['ticketType']
                ticket['ticketPrice'] = info['returnJsonFareBreakdowns'][0]['ticketPrice']
                print("ticket",ticket)
            else:
                ticket['fareProvider'] = info['singleJsonFareBreakdowns'][0]['fareProvider']
                ticket['ticketPrice'] = info['singleJsonFareBreakdowns'][0]['ticketPrice']
                print("ticket",ticket)

            return ticket
        except Exception as e:
            print("WS:except: line 69", traceback.format_exc())
            return False
    #@staticmethod
    #def get_strptime(string):
        #return datetime.strptime(string, '%d%m%y')
    @staticmethod
    def custom_to_date(string, type_format):
        return str(datetime.strftime(datetime.strptime(string, '%d%m%y'), type_format))
    




# dict: {'fromLocat': 'london', 'toLocat': 'paris', 'travelDate': '301221', 'travelTime': '1800', 'returnDate': '010122', 'returnTime': '1800'}
