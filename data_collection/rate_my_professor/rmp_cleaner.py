import pickle as pkl
import csv

final_list = []

with open('rmp_data.csv', 'rU') as f:
    #reader  = csv.reader(f, dialect=csv.excel_tab)
    final_list = list(list(rec) for rec in csv.reader(f, delimiter=',')) 
pkl.dump(final_list, open('cleaned_rmp_data.p', 'wb'))
