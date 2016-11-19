from bs4 import BeautifulSoup
import re
import urllib
import pickle as pkl

sock = urllib.urlopen("https://www.omscs.gatech.edu/current-courses")
html_source = sock.read()
sock.close()

cleaned_html = BeautifulSoup(html_source)
dict_of_course_data = {}
list_of_course_links = []

def loopUntilNextHeading(text, nexth4TagSibling, nexth4Tag, firstElement):
    text.append(firstElement)
    try:
        if ((nexth4Tag == firstElement.next) or (nexth4TagSibling == firstElement.next)             
            or (nexth4Tag == firstElement.next.next) or (nexth4TagSibling == firstElement.next.next)):             
            return text
        else:
            #Using double next to skip the string nodes themselves
            return loopUntilNextHeading(text, nexth4TagSibling, nexth4Tag, firstElement.next.next)
    except AttributeError:
        return text
        
for elem in cleaned_html.findAll('a', href=re.compile('^https://www.omscs.gatech.edu/cs')):
    if elem['href'] not in list_of_course_links:
        list_of_course_links.append(elem['href'])


for course_link in list_of_course_links:
    #Let the parsing begin
    sock = urllib.urlopen(course_link)
    html_source = sock.read()
    sock.close()
    cleaned_html = BeautifulSoup(html_source)

    #Now look for course title:
    title_html = cleaned_html.find('h2', attrs={'class': 'title'})
    title = title_html.next
    #Get Course Number
    print title
    match = (re.search(r'([\w ,-]+): ([\w ,&-]+)', title))
    if match:
        course_number = match.group(1)
        course_name = match.group(2)
    else:
        corner_case = ((re.search(r'(CSE \w\w\w\w) ([\w ,&-]+)', title)) or
                        (re.search(r'(CS \w\w\w\w) ([\w ,&-]+)', title)))
        if corner_case:
            course_number = corner_case.group(1)
            course_name = corner_case.group(2)
    headings = cleaned_html.find_all('h4')
    for heading in headings:
        #Get Overview text
        match = re.search(r"Overview", heading.next)
        if match:
            nexth4TagSibling = heading.find_next_sibling('h4')
            nexth4Tag = heading.find_next('h4')
            overview_text = loopUntilNextHeading([],nexth4TagSibling, nexth4Tag, heading)
            break
    for heading in headings:
        #Get Prerequisite text
        try:
            match = re.search(r"Prerequisites", heading.next)
        except TypeError:
            continue
        if match:
            nexth4TagSibling = heading.find_next_sibling('h4')
            nexth4Tag = heading.find_next('h4')
            prereq_text = loopUntilNextHeading([],nexth4TagSibling, nexth4Tag, heading)
            break
    for heading in headings:
        #Get Instructor name text
        prof_text = []
        try:
            match = re.search(r"Creator", heading.next)
        except:
            continue
        if match:
            nextATag = heading.find_next('a') 
            prof_text.append(nextATag.next)
            break
    for heading in headings:
        #Get Grading text
        try:
            match = re.search(r"Grading", heading.next)
        except TypeError:
            continue
        if match:
            nexth4TagSibling = heading.find_next_sibling('h4')
            nexth4Tag = heading.find_next('h4')
            grading_text = loopUntilNextHeading([],nexth4TagSibling, nexth4Tag, heading)
            break
    for heading in headings:
        #Get Reading information
        try:
            match = re.search(r"Reading", heading.next)
        except TypeError:
            continue
        if match:
            nexth4TagSibling = heading.find_next_sibling('h4')
            nexth4Tag = heading.find_next('h4')
            reading_text = loopUntilNextHeading([],nexth4TagSibling, nexth4Tag, heading)
            break
    for heading in headings:
        #Get Technical Requirements 
        try:
            match = re.search(r"Technical", heading.next)
        except TypeError:
            continue
        if match:
            nexth4TagSibling = heading.find_next_sibling('h4')
            nexth4Tag = heading.find_next('h4')
            tech_req_text = loopUntilNextHeading([],nexth4TagSibling, nexth4Tag, heading)
            break

    dict_of_course_data[course_number] = {'Number': course_number,
                                          'Name': course_name,
                                          'Instructor':prof_text,
                                          'Reading':reading_text,
                                          'Prerequisites':prereq_text,
                                          'Technical': tech_req_text,
                                          'Grading': grading_text,
                                          'Overview': overview_text}


pkl.dump(dict_of_course_data, open('omscs_website_data.p', 'wb'))
