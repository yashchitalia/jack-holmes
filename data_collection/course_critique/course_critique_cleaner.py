import pickle as pkl
import numpy as np


raw_dat = pkl.load(open('./course_critique_data.p' , 'rb'))
cleaned_dat = {}
for key_name in raw_dat.keys():
    cleaned_dat[str(key_name)] = raw_dat[key_name]

pkl.dump(cleaned_dat, open('./cleaned_course_critique_data.p', 'wb'))
