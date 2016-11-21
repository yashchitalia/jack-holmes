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
                             "overview_query":"Overview",
                             "technical_query": "Technical",
                             "reading_query": "Reading",
                             "grading_policy_query": "Grading",
                             "course_number_query":"Number",
                             "course_name_query": "Name"}
LIST_OF_NUMERIC_QUERIES = ["grade_likelihood", "avg_gpa"]

def processRequest(req):
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
    print query_name
    #Answer all the objective queries
    for course_number in course_number_list:
        if query_name in DICT_OF_OBJECTIVE_QUERIES.keys():
            if query_name == "course_number_query":
                print "Query correctly recognized"
                speech = course_number 
            else:
                speech = omscs_dat[course_number][DICT_OF_OBJECTIVE_QUERIES[query_name]]
        else:
            speech = "I'm afraid, I don't know the answer to that question. But maybe you can find the answer on the OMSCS website."
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
    print course_name, course_number
    if (course_name is None) and (course_number is None):
        return None
    elif course_name is not None:
        candidate_course_number = mapCourseNameToCourseNumber(course_name)
        if course_number is not None and course_number != candidate_course_number:
            course_number_list = [course_number, candidate_course_number]
        else:
            course_number = candidate_course_number
    print course_number
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
