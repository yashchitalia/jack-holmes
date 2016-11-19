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
            clean_list = str(curr_unclean_dat[attribute])
        else:
            unclean_list = curr_unclean_dat[attribute]
            clean_list = []
            if not isinstance(unclean_list, basestring):
                for item in unclean_list:
                    if isinstance(item, unicode):
                        if item == '\n':
                            unclean_list.remove(item) 
                    elif str(type(item)) == "<class 'bs4.element.Tag'>":
                        try:
                            if item.next == '\n':
                                unclean_list.remove(item) 
                            else:
                                clean_list.append(str(item.next))
                        except UnicodeEncodeError:
                            continue
                #clean_list.pop(0)
            else:
                clean_list = str(unclean_list)
        curr_clean_dat[attribute] = clean_list
    clean_dat[course_number] = curr_clean_dat


pkl.dump(clean_dat, open('omscs_cleaned_data.p', 'wb'))

