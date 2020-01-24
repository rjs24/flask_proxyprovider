from flask import Flask
app = Flask(__name__)
import random
import os
import time
import requests
from bs4 import BeautifulSoup
import csv
import json

def generate_new_proxyfile():
    #function to request info from 'https://free-proxy-list.net/' and generate new file ./proxy_list.csv
    get_page = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(get_page.text, 'lxml')
    data_list = []
    data_table = soup.findAll('tbody')[0]
    no_proxy_list = ['Iran', "Russian Federation", "Iraq", "Cambodia", "Bangladesh", "Pakistan"]
    for row in data_table.findAll('tr'):
        row_list = []
        for cell in row.findAll('td'):
            row_list.append(cell.getText())
        data_list.append(row_list)

    final_proxy_list = []
    for rw in data_list:
        if rw[4] == 'elite proxy' and rw[3] not in no_proxy_list:
            final_proxy_list.append({'ip': rw[0], 'port': rw[1], 'country': rw[3]})
        else:
            continue
    with open('proxy_list.csv', 'w') as proxy_write:
        keys = ['ip', 'port', 'country']
        diction_writ = csv.DictWriter(proxy_write, fieldnames=keys)
        diction_writ.writeheader()
        diction_writ.writerows(final_proxy_list)
        proxy_write.close()


@app.route('/')
def server_running():
    return 'Server running'

@app.route('/proxy')
def new_proxy():
    #return new proxy from proxy list if proxy list is less than 15 mins old
    proxy_list = 'Not defined yet'
    while proxy_list == 'Not defined yet':
        try:
            with open('proxy_list.csv', 'r') as proxys:
                file_datestamp = os.path.getmtime('proxy_list.csv')
                current_time = time.time()
                if current_time - file_datestamp > 30:
                    generate_new_proxyfile()
                    time.sleep(5)
                    continue
                else:
                    return_proxy_list = []
                    proxy_list = proxys.readlines()
                    for prx in proxy_list:
                        if prx and "ip" not in prx:
                            prxy_details = prx.split(",")
                            prxy_string = "%s:%s" % (prxy_details[0], prxy_details[1])
                            return_proxy_list.append(prxy_string)
                        else:
                            continue
                    return json.dumps(return_proxy_list)
        except FileNotFoundError as no_file_here:
            generate_new_proxyfile()
    proxys.close()

if __name__ == '__main__':
    app.run(port=5000, threaded=True, host=('0.0.0.0'))