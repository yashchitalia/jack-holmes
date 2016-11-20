from bs4 import BeautifulSoup
import re
import urllib
import pickle as pkl

unclean_dat = pkl.load(open('omscs_website_data.p', 'rb'))
clean_dat = {}
for course_number in unclean_dat.keys():
    curr_unclean_dat = unclean_dat[course_number]
    curr_clean_dat = {}
    for attribute in curr_unclean_dat.keys():
        if attribute == 'Instructor':
            try:
                clean_list = str(curr_unclean_dat[attribute][0])
            except:
                continue
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
            curr_clean_dat[attribute] = final_string 
            continue
    clean_dat[course_number] = curr_clean_dat


pkl.dump(clean_dat, open('omscs_cleaned_data.p', 'wb'))

