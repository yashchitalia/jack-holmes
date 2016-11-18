#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

import random
# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "prereq_query":
        return {}
    res = makeWebhookResult(data)
    return res


def makeWebhookResult(req):
    result = req.get("result")
    parameters = result.get("parameters")
    print "Dissection:"
    course_number= parameters.get('course_number')
    course_name= parameters.get('course_name')
    print "COURSE NAME:"
    print course_name
    print "COURSE NUMBER:"
    print course_number
    if (course_number is None) and (course_number is None):
        speech = "No Course Number Specified. What course were you asking about?"
        return {
            "speech": speech,
            "displayText": speech,
            "source": "apiai-jack-holmes"
        }

    speech = 'Great Questions! No prerequisites for this class!'
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-jack-holmes"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
