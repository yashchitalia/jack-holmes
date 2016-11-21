from bs4 import BeautifulSoup
import re
import urllib
import pickle as pkl

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleanr_still = re.compile('\\xa0')
    cleanertext = re.sub(cleanr_still, '', cleantext)
    cleanr_even = re.compile('\\u2019s')
    cleanesttext= re.sub(cleanr_even, '', cleanertext)
    cleanr_more = re.compile('\\u2019ll')
    cleanest_even = re.sub(cleanr_more, ' ', cleanesttext)
    cleanest_even_more = cleanest_even.replace('\\xa0', ' ')
    cleanest_even_more = cleanest_even_more.replace('\\u2014', ' ')
    cleanest_even_more = cleanest_even_more.replace('\\u201c', ' ')
    cleanest_even_more = cleanest_even_more.replace('\\u201d', ' ')
    cleanest_even_more = cleanest_even_more.replace('\\u2013', ' ')
    return cleanest_even_more

unclean_dat = pkl.load(open('omscs_website_data.p', 'rb'))
clean_dat = {}
for course_number in unclean_dat.keys():
    curr_unclean_dat = unclean_dat[course_number]
    curr_clean_dat = {}
    for attribute in curr_unclean_dat.keys():
        if attribute == 'Instructor':
            try:
                instructor_name = str(curr_unclean_dat[attribute][0])
            except:
                continue
            curr_clean_dat[attribute] = instructor_name
        elif attribute == 'Name':
            try:
                class_name = str(curr_unclean_dat[attribute])
            except:
                continue
            curr_clean_dat[attribute] = class_name 

        elif attribute in ['Overview', 'Prerequisites', 'Grading', 'Technical', 'Reading']:
            final_string= ''
            unclean_list = curr_unclean_dat[attribute]
            unclean_list.pop(0)
            for item in unclean_list:
                try:
                    if str(type(item)) == "<class 'bs4.element.NavigableString'>":
                        item = item.encode('ascii', errors='backslashreplace')
                        if str(item) == '\n':
                            continue
                        final_string = final_string+ ' ' + str(item)
                    elif str(type(item)) == "<class 'bs4.element.Tag'>":
                        if item.next == '\n':
                            continue 
                        final_string = final_string+ ' '+ str(item.next)
                except UnicodeEncodeError:
                    item = item.encode('ascii', errors='backslashreplace')
                    if str(item) == '\n':
                        continue
                    final_string = final_string+ ' ' + str(item)
            html_cleaned_string = cleanhtml(final_string)
            curr_clean_dat[attribute] = html_cleaned_string 
            continue

    clean_dat[course_number] = curr_clean_dat


pkl.dump(clean_dat, open('omscs_cleaned_data.p', 'wb'))

