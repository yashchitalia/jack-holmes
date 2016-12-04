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
DICT_OF_INSTRUCTOR_QUERIES = {'university_query':1, 'quality_query':2,
                              'easiness_query':3, 'hotness_query':6,
                              'helpfulness_query':4, 'comment_query':8,
                              'wealth_query':9, 'frog_query':10}
LIST_OF_PREFERENCES = ["register-easiness", "register-gpa", 
                       "register-helpfulness", "register-hotness",
                       "register-quality", "register-specialization",
                       "frogs_affirmation_callback", "frogs_negation_callback"]
LIST_OF_CONTEXTS = ['instructor_name', 'gpa-cue', 'easiness-cue', 'helpfulness-cue', 'hotness-cue', 'quality-cue', 'specialization-cue']
PREFERENCES_SPEECH_DICT = {"register-gpa":"Thanks! I've registered your GPA successfully.\nNow, please tell me your specialization. Here are the 4 specializations the OMSCS program:\n1. Computational Perception & Robotics\n2. Computing Systems\n3. Interactive Intelligence\n4. Machine Learning",
                            "register-easiness":"Great! I registered that.\nNext, on a scale of 0-5, how much does the helpfulness of the professor matter to you?\n(0 being 'I won't interact with the professor at all, so I don't care', and 5 being 'I need my instructor to be very helpful all the time')",
                            "register-helpfulness": "Great! Next, how much, again on a scale of 0-5 does the quality of the class matter?\n(With 0 being 'I know all about these topics already, I just want it on my resume.' and 5 being 'Quality of the class is supreme!')",
                            "register-hotness":"Awesome, I have almost all your details and preferences now.\nNow for the last and final question:\nDo you like people that eat frogs?\n(Don't ask why this is relevant right now, it'll all make sense later.)",
                            "register-quality":"Great! Thanks for that!\nNow, on a scale of 0-5, how much does the hotness/cuteness of a professor matter to you?\n(With 0 being 'Doesn't matter.' to 5 being 'I want them to be very hot.')",
                            "register-specialization":"Great! I saved your specialization.\nNow, please rate on a scale of 0-5, how much the easiness of the class matters to you (with 0 being an 'Doesn't matter' to 5 being 'I like easy classes only')?", "frogs_affirmation_callback":"Great! All your preferences have been recorded. From now on, all answers will be tuned to your liking!", 
                            "frogs_negation_callback":"Great! All your preferences have been recorded. From now on, all answers will be tuned to your liking! But beware of KBAI, the professor likes eating frogs!"}

def processRequest(req):
    course_number_list = extractCourseNumber(req)
    try:
        if req.get("result").get("contexts")[0].get("name") in LIST_OF_CONTEXTS:
            context_name = req.get("result").get("contexts")[0].get("name")
        else:
            context_name = None
    except:
        context_name = None
    if (course_number_list is None) and (context_name is None):
        speech = "No Course Number Specified. Could you repeat the question with the correct course number?"
        print speech
    else:
        if req.get("result").get("action") in DICT_OF_OBJECTIVE_QUERIES.keys():
            speech = answerObjectiveQueries(course_number_list, req.get("result").get("action"))
            print speech
        elif req.get("result").get("action") in LIST_OF_NUMERIC_QUERIES:
            speech = answerNumericQueries(course_number_list, req)  
            print speech
        elif (req.get("result").get("action") in DICT_OF_INSTRUCTOR_QUERIES.keys() and 
            context_name == "instructor_name"):
            speech = answerInstructorQueries(req.get("result").get("action"))
            print speech
        elif req.get("result").get("action") in LIST_OF_PREFERENCES:
            print "Yep. Query is to add something to episodic mem"
            speech = registerEpisodicMemory(req)
            print speech
        else:
            speech = "I'm so sorry, but I don't understand your question. Can you reframe it please?" 
            print speech
    res = makeWebhookResult(speech)
    return res


def registerEpisodicMemory(req):
    #Answer all the objective queries
    episodic_dict = pkl.load(open('./data_collection/episodic_memory.p', 'rb'))
    speech = PREFERENCES_SPEECH_DICT[req.get("result").get("action")]
    if req.get("result").get("action") == "register-specialization":
        episodic_dict["register-specialization"]= req.get("result").get("parameters").get("specializations") 
    elif req.get("result").get("action") == "frogs_affirmation_callback":
        episodic_dict["register-frogs"] = True
    elif req.get("result").get("action") == "frogs_negation_callback":
        episodic_dict["register-frogs"] = False
    else:
        print episodic_dict
        print float(req.get("result").get("parameters").get("number"))
        try:
            episodic_dict[req.get("result").get("action")] = float(req.get("result").get("parameters").get("number"))
        except:
            speech = "Are you sure you entered a number? Please try again."
    pkl.dump(episodic_dict, open('./data_collection/episodic_memory.p', 'rb'))
    return speech
                        


def answerObjectiveQueries(course_number_list, query_name):
    #Answer all the objective queries
    for course_number in course_number_list:
        if query_name in DICT_OF_OBJECTIVE_QUERIES.keys():
            if query_name == "course_number_query":
                speech = course_number 
            else:
                omscs_dat = pkl.load(open('./data_collection/omscs_website/omscs_cleaned_data.p', 'rb'))
                speech = omscs_dat[course_number][DICT_OF_OBJECTIVE_QUERIES[query_name]]
                if query_name == "instructor_query":
                    #Save the name of the latest instructor for context
                    pkl.dump(speech, open('./data_collection/curr_prof.p', 'wb'))
        else:
            speech = "I'm afraid, I don't know the answer to that question. But maybe you can find the answer on the OMSCS website."
    return speech
                        

def answerInstructorQueries(query_name):
    #Answer all the instructor queries: Courtesy Rate My Professor
    curr_instructor = pkl.load(open('./data_collection/curr_prof.p', 'rb'))
    rmp_data = pkl.load(open('./data_collection/rate_my_professor/cleaned_rmp_data.p', 'rb'))
    instructor_names = [item[0] for item in rmp_data]
    print "Got here"
    if query_name == "hotness_query" and curr_instructor == "Ashok Goel":
        speech = "Everyone else may disagree, but I think Dr. Goel is quite cute!" 
    elif query_name == "frog_query":
        if curr_instructor == "Ashok Goel":
            speech = "Yep, I know for a fact that he likes to eat frogs. But the frogs aren't too happy about it."
        else:
            speech = "Maybe, why don't you ask " + curr_instructor + " yourself?"
    elif query_name == "wealth_query" and curr_instructor == "Ashok Goel":
        speech = "Well he's rich!\n But he wants to get richer. So he buys a gun..."
    else:
        if curr_instructor in instructor_names:
            if query_name == "university_query":
                speech = str(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES[query_name]])
            elif query_name == "comment_query":
                speech = "Here's what one student has to say:\n" + "'"+ str(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES[query_name]]) + "'"
            elif query_name in ["quality_query", "easiness_query", "helpfulness_query"]:
                if rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES[query_name]] > 4.0:
                    speech = "Very much!"
                elif rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES[query_name]] < 4.0:
                    speech = str(curr_instructor) + "'s rating is medium on this one."
                else:
                    speech = "Not good at all. :("
            elif query_name == "hotness_query":
                print "cod here"
                print instructor_names.index(curr_instructor)
                print DICT_OF_INSTRUCTOR_QUERIES[query_name]
                if rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES[query_name]] == 'new-hot':
                    speech = str(curr_instructor) + " is flamin hot!"
                else:
                    speech = str(curr_instructor) + " is as cold as Siberia in winter!"
            elif query_name == "wealth_query":
                wealth_dat = rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES[query_name]]
                if wealth_dat >= 200000:
                    speech = "Uncle Scrooge rich!"
                else:
                    speech = "Getting richer and richer!!"
            else:
                speech = "I can't seem to understand that. Brain-Freeze!"
        else:
            speech = "I don't have that data for " + str(curr_instructor) + "."
    return speech

def answerNumericQueries(course_number_list, req):
    #Answer all quantitative queries
    query_name = req.get("result").get("action")
    course_critique_dat = pkl.load(open('./data_collection/course_critique/cleaned_course_critique_data.p', 'rb'))
    for course_number in course_number_list:
        try:
            course_matrix = course_critique_dat[course_number]
        except:
            return "I don't have that data for " + course_number +"."
        if query_name == "grade_likelihood":
            print "Identified Query correctly"
            grade_req = req.get("result").get("parameters").get("grade")
            print grade_req
            grade_dict = {'A':3, 'B':4, 'C':5, 'D':6}
            percentage = []
            if grade_req in grade_dict.keys():
                print "Grade found in dict"
                for row in course_matrix:
                    sum_row = 0.0
                    for num in grade_dict.keys():
                        sum_row = sum_row + row[grade_dict[num]]
                    percentage.append(row[grade_dict[grade_req]]*100.0/sum_row)
                print percentage
                avg_percentage = (1.0*sum(percentage))/len(percentage)
                speech = "Average percentage of "+grade_req+"'s in "+course_number+" is "+ str(avg_percentage)
                print speech
                return speech
            elif grade_req == 'pass' or grade_req == 'fail':
                fail_percentage = []
                for row in course_matrix:
                    sum_row = 0.0
                    for num in grade_dict.keys():
                        sum_row = sum_row + row[grade_dict[num]]
                    percentage.append((sum_row-row[grade_dict['D']])*100.0/sum_row)
                    fail_percentage.append((row[grade_dict['D']])*100.0/sum_row)
                avg_pass_percentage = (1.0*sum(percentage))/len(percentage)
                avg_fail_percentage = (1.0*sum(fail_percentage))/len(fail_percentage)
                if avg_pass_percentage >= 90.0:
                    speech = "Average passing percentage is "+ str(avg_pass_percentage) + " and averge failing percentage is "+ str(avg_fail_percentage) + ". Yay. Lot's of people seem to pass this one. Go for it!"
                else:
                    speech = "Average passing percentage is "+ str(avg_pass_percentage) + " and averge failing percentage is "+ str(avg_fail_percentage) + ". Oh, notice, that lot's of people seem to flunk this one. Tread carefully..."
                return speech
            else:
                speech = ''
                for grade in grade_dict.keys():
                    for row in course_matrix:
                        sum_row = 0.0
                        for num in grade_dict.keys():
                            sum_row = sum_row + row[grade_dict[num]]
                        percentage.append(row[grade_dict[grade]]*100.0/sum_row)
                    avg_percentage = (1.0*sum(percentage))/len(percentage)
                    speech = speech + "Average percentage of "+grade+"'s is "+ str(avg_percentage) +"."
                return speech
        elif query_name == "avg_gpa":
            print "Starting computation..."
            gpa_arr = []
            for row in course_matrix:
                print row
                gpa_arr.append(row[2])
            avg_gpa = (1.0*sum(gpa_arr))/len(gpa_arr)
            return str(avg_gpa)
            
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
    try:
        if len(course_name) == 0:
            course_name = None
    except:
        course_name = None
    try:
        if len(course_number) == 0:
            course_number = None
    except:
        course_number = None

    if (course_name is None) and (course_number is None):
        return None
    elif course_name is not None:
        candidate_course_number = mapCourseNameToCourseNumber(course_name)
        if candidate_course_number is None:
            return None
        if course_number is not None and course_number != candidate_course_number:
            course_number_list = [course_number, candidate_course_number]
        else:
            course_number = candidate_course_number
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
