import pandas as pd
import numpy as np
import xlrd
import pickle as pkl

list_of_classes = [u'CS 6035', u'CS 6210', u'CSE 6220', u'CSE 6242', u'CS 6250', u'CS 6262', u'CS 6290', u'CS 6300', u'CS 6310', u'CS 6340', u'CS 6400', u'CS 6440', u'CS 6460', u'CS 6475', u'CS 4495', u'CS 6505', u'CS 6601', u'CS 7637', u'CS 7641', u'CS 7646', u'CSE 8803 Special Topics', u'CS 8803']
course_grades_dict = {}
for classname in list_of_classes:
    try:
        class_data = pd.read_excel(open('course_critique_tables.xlsx', 'rb'), sheetname = classname)
    except xlrd.biffh.XLRDError:
        course_grades_dict[classname] = None 
        pass
    class_matrix = class_data.as_matrix()
    course_grades_dict[classname] = class_matrix
    
    pkl.dump(course_grades_dict, open( "course_critique_data.p", "wb" ) )
