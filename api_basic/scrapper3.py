import http.client
import mimetypes
import json
import time
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup


conn_objs = { }

def get_conn(site):
    #NSE connection settings
    if site == "nse":
        payload_nse = ''
        headers_nse = {
            'Cookie': ''
            }
        conn_objs["conn_nse"] = http.client.HTTPSConnection("www.nseindia.com")
        return conn_objs["conn_nse"],payload_nse,headers_nse
    
    #BSE connection settings
    elif site == 'bse':
        payload_bse = ''
        headers_bse = {}
        conn_objs["conn_bse"] = http.client.HTTPSConnection("api.bseindia.com")
        return conn_objs["conn_bse"],payload_bse,headers_bse


def get_nse_data(name):
    #fetching graph data from nse
    conn,payload,headers = get_conn('nse')
    conn.request("GET", "https://www.nseindia.com/api/chart-databyindex?index="+ name + "EQN", payload, headers)
    res = conn.getresponse()
    data = res.read()
    jdict = json.loads(data.decode("utf-8"))
    nse_data = jdict["grapthData"]
    if nse_data == []:
        conn.request("GET", "https://www.nseindia.com/api/chart-databyindex?index="+ name + "BEN", payload, headers)
        res = conn.getresponse()
        data = res.read()
        jdict = json.loads(data.decode("utf-8"))
        nse_data = jdict["grapthData"]
    return nse_data



def get_bse_data(scripcode):
    #fetching graph data from bse
    conn,payload,headers = get_conn('bse')
    conn.request("GET", "/BseIndiaAPI/api/StockReachGraph/w?scripcode=" + scripcode + "&flag=0&fromdate=&todate=&seriesid=", payload, headers)
    res = conn.getresponse()
    data = res.read()
    jdict = json.loads(data.decode("utf-8"))
    bse_data = json.loads(jdict["Data"])
    return bse_data
  

def getbserecord(data):
    time_str = data['dttm']
    time_obj = time.strptime(time_str, "%a %b %d %Y %H:%M:%S") 
    time_inepoch = time.mktime(time_obj)
    curr_time = (datetime.fromtimestamp(time_inepoch))
    return curr_time,data["vale1"]


def getnserecord(data):
    nse_price = data[1]
    curr_time = datetime.utcfromtimestamp(data[0]/1000)
    return curr_time,nse_price



def compute_price(name,scripcode):
   
    security = {}
    bse_data = get_bse_data(scripcode)
    nse_data = get_nse_data(name)
    i = 0
    index_counter = 0
    for bse_y in bse_data:
        bse_time,bse_price = getbserecord(bse_y)   
        for nse_x in nse_data[index_counter:]:
            nse_time,nse_price = getnserecord(nse_x)
            temp_time = bse_time.strftime("%H:%M:%S")
            if nse_time <= bse_time:
                diff_price = nse_price - float(bse_price)
                security[i] = { "timestamp": temp_time ,"nseprice" : nse_price , "bseprice" : float(bse_price) , "diffprice":round(diff_price,2) }
                index_counter+=1
            else:
                index_counter+=1
                i+=1
                break
    return security    
            

def get_securities(company_name):
    #Dictionary to maintain the symbol name and scrip codes
    # key -> symbol value --> scripcode
    securities = {}
    temp = {}
    #Fetching all securities with name containing the given string

    #fetching from bse
    bse_list = []
    conn,payload,headers = get_conn('bse')
    conn.request("GET", f"/Msource/1D/getQouteSearch.aspx?Type=EQ&text={company_name}&flag=nw", payload, headers)
    res = conn.getresponse()
    data = res.read()
    parsed_html = BeautifulSoup(data,'html.parser')
    l = parsed_html.find_all('span',attrs = {'class' : ''})
    for sym in l:
        ns = (str(sym).replace("<span>","").replace("</span>","").replace("<strong>","").replace("</strong>",""))
        symbols = re.search('^([A-Z-0-9]*)',ns).group(1)
        scripcodes = re.search('([A-Z-0-9]*)$',ns).group(1)
        bse_list.append((symbols,scripcodes))
        securities[symbols] = scripcodes
    

    #fetching from nse 
    conn,payload,headers = get_conn('nse')
    conn.request("GET", f"/api/search/autocomplete?q={company_name}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    symbols_json = json.loads(data.decode("utf-8"))
    for element in symbols_json["symbols"]:
        if element['symbol'] in securities.keys():
            temp[element['symbol']] = securities[element['symbol']]
        

    #returning only the common securities on both the exchanges
    return temp



