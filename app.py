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

LIST_OF_COMPARISON_QUERIES = ["comparison_better_query", "comparison_ease_query"]
LIST_OF_EXPLANATION_QUERIES = ["inference_request", "analysis_request"]
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
    try:
        if req.get("result").get("contexts")[0].get("name") in LIST_OF_CONTEXTS:
            context_name = req.get("result").get("contexts")[0].get("name")
        else:
            context_name = None
    except:
        context_name = None
    if req.get("result").get("action") in LIST_OF_PREFERENCES:
        speech = registerEpisodicMemory(req)
        print speech
    elif req.get("result").get("action") in LIST_OF_COMPARISON_QUERIES:
        course_number_list = extractMultipleCourseNumbers(req)
        speech = answerProductionRules(course_number_list, req.get("result").get("action"))
        print speech
    elif req.get("result").get("action") in LIST_OF_EXPLANATION_QUERIES:
        speech = answerExplanationTypeQueries(req.get("result").get("action"))
        print speech
    elif req.get("result").get("action") == "plan_query":
        speech = generateCoursePlan()
        print speech
    else:
        course_number_list = extractCourseNumber(req)
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
            else:
                speech = "I'm so sorry, but I don't understand your question. Can you reframe it please?" 
                print speech
    res = makeWebhookResult(speech)
    return res


def answerExplanationTypeQueries(query_name):
    #Pull last answer from the pickle file and return, lol
    if query_name == 'inference_request':
        explanation = pkl.load(open('./data_collection/explanation.p', 'rb'))
        return explanation
    else:
        analysis = pkl.load(open('./data_collection/analysis.p', 'rb'))
        return analysis

def generateProductionRuleExplanation(course_number_list):
    #Generate a textual explanation for answering the reasoning behind
    # Production Rule type questions
    explanation = ""
    episodic_dict = pkl.load(open('./data_collection/episodic_memory.p', 'rb'))
    specializations_dict = pkl.load(open('./data_collection/specializations/specializations_course_list.p', 'rb'))
    specialization_preference = episodic_dict["register-specialization"]
    easiness_preference = episodic_dict["register-easiness"]
    helpfulness_preference = episodic_dict["register-helpfulness"]
    quality_preference = episodic_dict["register-quality"]
    if easiness_preference >= 4.0 or helpfulness_preference >= 4.0 or quality_preference >= 4.0:
        explanation += "So you gave a high preference to "
        if easiness_preference >= 4.0:
            explanation += "Easiness of the class,"
        if helpfulness_preference>= 4.0:
            explanation += " Helpfulness of the professor,"
        if quality_preference>= 4.0:
            explanation += " Quality of teaching,"
    explanation += " So I scored the courses, by weighting them according to your preferences, and the ratings given by other students."
    if ((course_number_list[0] in specializations_dict[specialization_preference] and
        course_number_list[1] not in specializations_dict[specialization_preference])):
        explanation += "Also, "+course_number_list[0]+" is in your selected major, but "+course_number_list[1]+" is not."
        explanation += " So I weighed that in too."
    elif ((course_number_list[1] in specializations_dict[specialization_preference] and
        course_number_list[0] not in specializations_dict[specialization_preference])):
        explanation += "Also, "+course_number_list[1]+" is in your selected major, but "+course_number_list[0]+" is not."
        explanation += " So I weighed that in too."
    return explanation

def generateCoursePlan():
    #Retrieves data of the user's preferences and generates a course-plan for the user
    course_critique_dat = pkl.load(open('./data_collection/course_critique/cleaned_course_critique_data.p', 'rb'))
    episodic_dict = pkl.load(open('./data_collection/episodic_memory.p', 'rb'))
    rmp_data = pkl.load(open('./data_collection/rate_my_professor/cleaned_rmp_data.p', 'rb'))
    omscs_dat = pkl.load(open('./data_collection/omscs_website/omscs_cleaned_data.p', 'rb'))
    specializations_dict = pkl.load(open('./data_collection/specializations/specializations_course_combos.p', 'rb'))
    #This is a dict, where the key is each specialization and the value is a list
    #The list has a number of sub-lists. Each sub-list has tuples of combos in it.
    instructor_names = [item[0] for item in rmp_data]
    #Extract User Preferences
    specialization_preference = episodic_dict["register-specialization"]
    easiness_preference = episodic_dict["register-easiness"]
    helpfulness_preference = episodic_dict["register-helpfulness"]
    quality_preference = episodic_dict["register-quality"]
    #Threshold values
    if easiness_preference > 5.0:
        easiness_preference = 5.0 
    if easiness_preference < 0.0:
        easiness_preference = 0.0 
    if helpfulness_preference> 5.0:
        helpfulness_preference= 5.0 
    if helpfulness_preference< 0.0:
        helpfulness_preference= 0.0 
    if quality_preference> 5.0:
        quality_preference= 5.0 
    if quality_preference< 0.0:
        quality_preference= 0.0 
    final_course_plan = []
    for course_list_of_combos in specializations_dict[specialization_preference]:
        max_score = 0
        best_tuple = (None, None)
        print course_list_of_combos
        for course_number_tuple in course_list_of_combos:
            print course_number_tuple
            if type(course_number_tuple) is not tuple:
                #Singleton cases
                course_number = str(course_number_tuple)
                print "Course number"+ course_number
                #Extract Instructor Data for this course
                curr_instructor = omscs_dat[course_number]["Instructor"]
                easiness_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["easiness_query"]]) 
                helpfulness_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["helpfulness_query"]]) 
                quality_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["quality_query"]]) 
                curr_score = (easiness_rating*easiness_preference +
                              helpfulness_rating*helpfulness_preference +
                              quality_rating*quality_preference)
                print curr_score
                if curr_score > max_score:
                    max_score = curr_score
                    best_tuple = [str(course_number_tuple)]
                print best_tuple
            else:
                curr_score = 0
                for course_number in course_number_tuple:
                    #Extract Instructor Data for this course
                    print course_number
                    curr_instructor = omscs_dat[course_number]["Instructor"]
                    print curr_instructor
                    easiness_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["easiness_query"]]) 
                    helpfulness_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["helpfulness_query"]]) 
                    quality_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["quality_query"]]) 
                    curr_score += (easiness_rating*easiness_preference +
                                  helpfulness_rating*helpfulness_preference +
                                  quality_rating*quality_preference)
                    print curr_score
                if curr_score > max_score:
                    max_score = curr_score
                    best_tuple = course_number_tuple
        final_course_plan += list(best_tuple)
        print final_course_plan
    speech = "First Semester: " + final_course_plan[0] + ", " + final_course_plan[1] + ".\n"
    speech += "Second Semester: " + final_course_plan[2] + ", " + final_course_plan[3] + ".\n"
    if len(final_course_plan) > 4:
        speech += "Finally, you can take "
        for item in final_course_plan[4:]:
            speech += item + ", "
        speech += ", at your own pace."
    else:
        speech += "And that's it! You're ready to graduate in two semesters!"
    return speech

def answerProductionRules(course_number_list, query_name):
    #Answer comparison type questions
    course_critique_dat = pkl.load(open('./data_collection/course_critique/cleaned_course_critique_data.p', 'rb'))
    course_number_list = course_number_list[:2]
    if query_name == "comparison_better_query":
        score_dict = {}
        episodic_dict = pkl.load(open('./data_collection/episodic_memory.p', 'rb'))
        rmp_data = pkl.load(open('./data_collection/rate_my_professor/cleaned_rmp_data.p', 'rb'))
        omscs_dat = pkl.load(open('./data_collection/omscs_website/omscs_cleaned_data.p', 'rb'))
        specializations_dict = pkl.load(open('./data_collection/specializations/specializations_course_list.p', 'rb'))
        instructor_names = [item[0] for item in rmp_data]
        #Extract User Preferences
        specialization_preference = episodic_dict["register-specialization"]
        easiness_preference = episodic_dict["register-easiness"]
        helpfulness_preference = episodic_dict["register-helpfulness"]
        quality_preference = episodic_dict["register-quality"]
        #Threshold values
        if easiness_preference > 5.0:
            easiness_preference = 5.0 
        if easiness_preference < 0.0:
            easiness_preference = 0.0 
        if helpfulness_preference> 5.0:
            helpfulness_preference= 5.0 
        if helpfulness_preference< 0.0:
            helpfulness_preference= 0.0 
        if quality_preference> 5.0:
            quality_preference= 5.0 
        if quality_preference< 0.0:
            quality_preference= 0.0 
        for course_number in course_number_list:
            #Extract Instructor Data for this course
            curr_instructor = omscs_dat[course_number]["Instructor"]
            easiness_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["easiness_query"]]) 
            helpfulness_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["helpfulness_query"]]) 
            quality_rating=float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES["quality_query"]]) 
            curr_score = (easiness_rating*easiness_preference +
                          helpfulness_rating*helpfulness_preference +
                          quality_rating*quality_preference)
            if course_number in specializations_dict[specialization_preference]:
                curr_score += 20.0
            print course_number, curr_score
            score_dict[course_number] = curr_score
        better_course = str(max(score_dict, key=score_dict.get))
        worse_course = str(min(score_dict, key=score_dict.get))
        speech = "So, it looks like "+better_course+" is better for you than "+worse_course+"."
        explanation = generateProductionRuleExplanation(course_number_list)
        explanation += "\n So that's why I picked "+better_course+" over "+worse_course+"."
        explanation += "\n But if you think my choices are wrong, you can tweak your preferences by saying 'change preferences'."
        analysis = "curr_score = (easiness_rating*easiness_preference + helpfulness_rating*helpfulness_preference + quality_rating*quality_preference) \n"
        analysis += "if course_number in specializations_dict[specialization_preference]:\n curr_score += 20.0"
        pkl.dump(analysis, open('./data_collection/analysis.p', 'wb'))
        pkl.dump(explanation, open('./data_collection/explanation.p', 'wb'))
    elif query_name == "comparison_ease_query":
        explanation = ""
        ease_dict = {}
        episodic_dict = pkl.load(open('./data_collection/episodic_memory.p', 'rb'))
        curr_gpa = float(episodic_dict["register-gpa"])
        if curr_gpa >=3.75:
            explanation+="So I thought your GPA was high enough, to assume, that when you say 'easy' you mean 'easy to get an A in'. So I just summed up all percentages of A grades for each of these classes, "
        elif curr_gpa < 3.75 and curr_gpa >= 3.00:
            explanation+="So I thought your GPA was high enough, to assume, that when you say 'easy' you mean 'easy to get an A  or B in'. So I just summed up all percentages of A and B grades in each year this class was taught, "
        else:
            explanation+="Since your GPA is quite low, I just computed the percentage of students that pass these classes and compared the two,"
        for course_number in course_number_list:
            percentage = []
            grade_dict = {'A':3, 'B':4, 'C':5, 'D':6}

            try:
                course_matrix = course_critique_dat[course_number]
                print course_matrix
            except:
                return "I don't have that data for " + course_number +". So sorry, I can't say much!"
            if curr_gpa >= 3.75:
                for row in course_matrix:
                    sum_row = 0.0
                    for num in grade_dict.keys():
                        sum_row = sum_row + row[grade_dict[num]]
                    percentage.append(row[grade_dict['A']]*100.0/sum_row)
                avg_pass_percentage = (1.0*sum(percentage))/len(percentage)
            elif curr_gpa >= 3.00 and curr_gpa < 3.75:
                for row in course_matrix:
                    sum_row = 0.0
                    for num in grade_dict.keys():
                        sum_row = sum_row + row[grade_dict[num]]
                    percentage.append(row[grade_dict['A']]+row[grade_dict['B']]*100.0/sum_row)
                avg_pass_percentage = (1.0*sum(percentage))/len(percentage)
            else:
                for row in course_matrix:
                    sum_row = 0.0
                    for num in grade_dict.keys():
                        sum_row = sum_row + row[grade_dict[num]]
                    percentage.append((sum_row-row[grade_dict['D']])*100.0/sum_row)
                avg_pass_percentage = (1.0*sum(percentage))/len(percentage)
            ease_dict[course_number] = avg_pass_percentage
        easiest_course = str(min(ease_dict, key=ease_dict.get))
        harder_course = str(max(ease_dict, key=ease_dict.get))
        speech = "So, it looks like "+easiest_course+" is easier than "+harder_course+"."
        explanation += " and it looked like "+easiest_course+" scores are better than "+harder_course+"."
        explanation += "\n But if you want to change your GPA, you can do so by changing your preferences by saying 'change preferences'."
        analysis = "if(gpa > 3.75) {average all A grade percentages}\nif(gpa is between 3.00, 3.75) {average all A, B grade percentages}"
        analysis += "\n if(gpa < 3.00) {average all passing percentages}"
        pkl.dump(analysis, open('./data_collection/analysis.p', 'wb'))
        pkl.dump(explanation, open('./data_collection/explanation.p', 'wb'))
        print explanation
    return speech
                        

def sortKey(self, item):                                                    
    return item[1]                                                          


def registerEpisodicMemory(req):
    #Register Users Preferences
    episodic_dict = pkl.load(open('./data_collection/episodic_memory.p', 'rb'))
    speech = PREFERENCES_SPEECH_DICT[req.get("result").get("action")]
    if req.get("result").get("action") == "register-specialization":
        episodic_dict["register-specialization"]= req.get("result").get("parameters").get("specializations") 
    elif req.get("result").get("action") == "frogs_affirmation_callback":
        episodic_dict["register-frogs"] = True
    elif req.get("result").get("action") == "frogs_negation_callback":
        episodic_dict["register-frogs"] = False
    else:
        try:
            episodic_dict[req.get("result").get("action")] = float(req.get("result").get("parameters").get("number"))
        except:
            speech = "Are you sure you entered a number? Please try again."
    print episodic_dict
    pkl.dump(episodic_dict, open('./data_collection/episodic_memory.p', 'wb'))
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
                if float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES[query_name]]) > 4.0:
                    speech = "Very much!"
                elif float(rmp_data[instructor_names.index(curr_instructor)][DICT_OF_INSTRUCTOR_QUERIES[query_name]]) < 4.0:
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

def extractMultipleCourseNumbers(req):
    #Get course number from the users query
    result = req.get("result")
    course_number_list = []
    course_name_list = []
    parameters = result.get("parameters")
    if type(parameters.get('course_number')) is list:
        course_number_list.append(parameters.get('course_number')[0])
    else: 
        course_number_list.append(parameters.get('course_number'))
    if type(parameters.get('course_number1')) is list:
        course_number_list.append(parameters.get('course_number1')[0])
    else:
        course_number_list.append(parameters.get('course_number1'))

    if type(parameters.get('course_name')) is list:
        course_name_list.append(parameters.get('course_name')[0])
    else:
        course_name_list.append(parameters.get('course_name'))

    if type(parameters.get('course_name1')) is list:
        course_name_list.append(parameters.get('course_name1')[0])
    else:
        course_name_list.append(parameters.get('course_name1'))
    print course_name_list
    final_list = []
    for course_number in course_number_list:
        try:
            if len(course_number) == 0:
                course_number = None
        except:
            course_number = None

        if (course_number is None):
            continue
        else:
            final_list.append(course_number)

    for course_name in course_name_list:
        try:
            if len(course_name) == 0:
                course_name = None
        except:
            course_name = None
        if course_name is not None:
            candidate_course_number = mapCourseNameToCourseNumber(course_name)
            if candidate_course_number is None:
                continue
            else:
                final_list.append(candidate_course_number)
        else:
            continue
    return final_list 



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
