#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

import random
import pickle as pkl
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

DICT_OF_OBJECTIVE_QUERIES = {"prereq_query":"Prerequisites",
                             "instructor_query":"Instructor",
                             "overview_query":"Overview"}

def processRequest(req):
    print "Trying to load data"
    course_number_list = extractCourseNumber(req)
    if course_number_list is None:
        speech = "No Course Number Specified. What course were you asking about?"
        print speech
    else:
        if req.get("result").get("action") in DICT_OF_OBJECTIVE_QUERIES.keys():
            speech = answerObjectiveQueries(course_number_list, req.get("result").get("action"))
            print speech
        else:
            speech = "I'm so sorry, but I don't understand your question. Can you reframe it please?" 
            print speech
    res = makeWebhookResult(speech)
    return res


def answerObjectiveQueries(course_number_list, query_name):
    omscs_dat = pkl.load(open('./data_collection/omscs_website/omscs_cleaned_data.p', 'rb'))
    print "Loaded data correctly"
    print course_number_list
    #Answer all the objective queries
    for course_number in course_number_list:
        if query_name in DICT_OF_OBJECTIVE_QUERIES.keys():
            print "Your query is valid"
            print DICT_OF_OBJECTIVE_QUERIES[query_name]
            print omscs_dat[course_number][DICT_OF_OBJECTIVE_QUERIES[query_name]]
            listOfResponseStrings = omscs_dat[course_number][DICT_OF_OBJECTIVE_QUERIES[query_name]]
            print listOfResponseStrings
            speech = DICT_OF_OBJECTIVE_QUERIES[query_name] + ' of ' + course_number + ':'
            print speech
            for responseString in listOfResponseStrings:
                speech = speech + ' ' + responseString
            print speech
        else:
            print "Your Query is not in my dict"
    return speech
                        

def mapCourseNameToCourseNumber(course_name):
    omscs_dat = pkl.load(open('./data_collection/omscs_website/omscs_cleaned_data.p', 'rb'))
    for course_number in omscs_dat.keys():
        if omscs_dat[course_number]['Name'] == course_name:
            return course_number
    return None

def extractCourseNumber(req):
    #Get course number from the users query
    result = req.get("result")
    parameters = result.get("parameters")
    course_number= parameters.get('course_number')
    course_name= parameters.get('course_name')
    if len(course_name) == 0:
        course_name = None
    if len(course_number) == 0:
        course_number = None
    print "COURSE NAME:" + course_name
    print "COURSE NUMBER:" + course_number
    if (course_name is None) and (course_number is None):
        return None
    elif course_name is not None:
        candidate_course_number = mapCourseNameToCourseNumber(course_name)
        if course_number is not None and course_number != candidate_course_number:
            course_number_list = [course_number, candidate_course_number]
    course_number_list = [course_number]
    return course_number_list

def makeWebhookResult(speech):
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
