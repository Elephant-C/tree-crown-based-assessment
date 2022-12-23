import os
import pandas as pd
import numpy as np
import multiprocessing

def job(index):
    cs_set_list = [[1], [1,2], [1,2,3]]
    extract(cs_set=cs_set_list[index])

def extract(cs_set):
    pwd = '/Volumes/T7/'
    cs_suffix = ''
    for ele in cs_set:
        cs_suffix += str(ele)   
    name = 'dalponte2016_ws_5_smoothing_3_cs_' + cs_suffix
    filename = name + '_p_r_f1.csv'
    inpath = os.path.join(pwd, 'Data', 'New_Sepilok', 'p_r_f1', filename)
    data = pd.read_csv(inpath, index_col=[0])
    precision_arr_str = np.asarray(data['Precision'])
    recall_arr_str = np.asarray(data['Recall'])
    f1_arr_str = np.asarray(data['F1'])
    precision_list, recall_list, f1_list = [], [], []
    for i in range(len(precision_arr_str)):
        precision_list.append(eval(precision_arr_str[i]))
        recall_list.append(eval(recall_arr_str[i]))
        f1_list.append(eval(f1_arr_str[i]))
    precision_arr = np.array(precision_list)
    precision_df = pd.DataFrame(data=precision_arr)
    recall_arr = np.array(recall_list)
    recall_df = pd.DataFrame(data=recall_arr)
    f1_arr = np.array(f1_list)
    f1_df = pd.DataFrame(data=f1_arr)
    precision_df.to_csv(os.path.join(pwd, 'Data', 'New_Sepilok', 'p_r_f1', name+'_precison.csv'))
    recall_df.to_csv(os.path.join(pwd, 'Data', 'New_Sepilok', 'p_r_f1', name+'_recall.csv'))
    f1_df.to_csv(os.path.join(pwd, 'Data', 'New_Sepilok', 'p_r_f1', name+'_f1.csv'))
    print('ok')

if __name__ == '__main__':
    pool_obj = multiprocessing.Pool(3)
    pool_obj.map(job, range(0, 3))