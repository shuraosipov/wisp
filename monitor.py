import requests
import urlparse
import datetime
import json
from flask import Flask, render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = True

with open("inventory.json") as data_file:
    inventory = json.load(data_file)


@app.route('/')
def healh_check():
    results = {}
    health = []

    for service in inventory:
        url = inventory[service]['url']

        try:
            gl_req = requests.get(url, verify=False, timeout=5)
            gl_status = gl_req.status_code
            health.append(str(gl_status))
            gl_elapsed = gl_req.elapsed.total_seconds()
            results[service] = {'url': url, 'status': gl_status, 'elapsed': gl_elapsed}
            results[service]['nodes'] = []

        except requests.exceptions.ConnectionError:
            results[service] = {'url': url, 'status': "ConnectionError", 'elapsed': "-"}
            results[service]['nodes'] = []
            pass

        for node in inventory[service]['nodes']:
            try:
                nd_req = requests.get(node, verify=False, timeout=5)
                nd_status = nd_req.status_code
                nd_elapsed = nd_req.elapsed.total_seconds()
                h = urlparse.urlparse(node)
                nd_nodename = h.hostname
                results[service]['nodes'].append({nd_nodename: {'status': nd_status, 'elapsed': nd_elapsed}})

            except requests.exceptions.ConnectionError:
                h = urlparse.urlparse(node)
                nd_nodename = h.hostname
                results[service]['nodes'].append({nd_nodename: {'status': "ConnectionError", 'elapsed': "-"}})
                pass

    now = datetime.datetime.now()
    date = now.ctime()
    month = now.strftime("%B")
    day = now.strftime("%d")
    year = now.year

    return render_template('index.html', results=results, date=date, month=month, day=day, year=year, health=health)
