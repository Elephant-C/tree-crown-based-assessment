import os
import sys
sys.path.append('../utils/')
import pandas as pd
from tqdm import tqdm
from Evaluation import EvaluationCrownPolygon
import multiprocessing

def ams3d_p_r_f1(seg_path: str, gt_path: str, out_path: str, cs_set: list=[1,2,3]) -> None:
    cs_suffix = ''
    for ele in cs_set:
        cs_suffix += str(ele)
    # read ground_truth:
    gt_df = pd.read_csv(gt_path, index_col=[0])
    gt_data = gt_df.drop(gt_df[gt_df['ID'] == 0].index) 
    gt_data.rename(columns={'Confidence Score': 'confiScore'}, inplace=True)
    ams3d_sepilok = EvaluationCrownPolygon(gtPts=gt_data)
    ams3d_sepilok.fitPolygonBatchwithCS(pts=gt_data, mode='gt')  
    H2CD = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    H2CH = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    predicted_tree_nums, gt_tree_nums = [], []
    TP, FP, FN = [], [], []
    Precision, Recall, F1Score = [], [], []
    for h2cd in tqdm(H2CD):
        predicted_tree_nums_row, gt_tree_nums_row = [], []
        TP_row, FP_row, FN_row = [], [], []
        precision_row, recall_row, f1_row = [], [], []
        for h2ch in tqdm(H2CH):
            name = 'h2cd_' + str(h2cd) + '_h2ch_' + str(h2ch) + '.csv'
            print(name)
            # --- read segmentation data --- #
            seg_path = os.path.join(seg_path, name)
            seg_data = pd.read_csv(seg_path, index_col=[0])
            index = list(range(1, len(seg_data) + 1))
            # --- set index colums --- #
            seg_data['Index'] = index
            # --- remove points with confidence score = 0 --- #
            seg_data = seg_data[seg_data['confiScore']!= 0]
            # --- fit polygons with labelled confidence score --- #
            print('Segmentation Polygon fitting...')
            ams3d_sepilok.fitPolygonBatchwithCS(pts=seg_data, mode='seg')
            # --- assessment --- #
            ams3d_sepilok.overlayAssessment(CS_set=cs_set)
            TP_row.append(ams3d_sepilok.TP)
            FP_row.append(ams3d_sepilok.FP)
            FN_row.append(ams3d_sepilok.FN)
            ams3d_sepilok.calPrecision()                                                                 # calculate precision
            ams3d_sepilok.calRecall()                                                                    # calculate recall
            predicted_tree_nums_row.append(ams3d_sepilok.seg_tree_nums)
            gt_tree_nums_row.append(ams3d_sepilok.gt_tree_nums)
            precision_row.append(ams3d_sepilok.precision)                                                # record precision
            recall_row.append(ams3d_sepilok.recall)                                                      # record recall
            if ams3d_sepilok.precision == 0 and ams3d_sepilok.recall==0:
                f1_row.append(0)                                                                         # calculate F1 score
            else:
                ams3d_sepilok.calF1Score()                                                               # calculate F1 score
                f1_row.append(ams3d_sepilok.f1)                                                          # record F1 score
        predicted_tree_nums.append(predicted_tree_nums_row)
        gt_tree_nums.append(gt_tree_nums_row)
        TP.append(TP_row)
        FP.append(FP_row)
        FN.append(FN_row)
        Precision.append(precision_row)
        Recall.append(recall_row)
        F1Score.append(f1_row)
        df_assess = pd.DataFrame()
        df_assess['Reference_tree_nums'] = gt_tree_nums
        df_assess['Predicted_tree_nums'] = predicted_tree_nums
        df_assess['TP'] = TP
        df_assess['FP'] = FP
        df_assess['FN'] = FN
        df_assess['Precision'] = Precision
        df_assess['Recall'] = Recall
        df_assess['F1'] = F1Score
        out_file_name = 'ams3d_cs_' + cs_suffix + '_p_r_f1.csv'
        out_path = os.path.join(out_path, out_file_name)
        df_assess.to_csv(out_path)
        print('ok')
    print('Finished..')

def dalponte2016_p_r_f1(seg_path: str, gt_path: str, out_path: str, cs_set: list=[1,2,3]) -> None:
    print('input cs is:' + str(cs_set))
    cs_suffix = ''
    for ele in cs_set:
        cs_suffix += str(ele)
    WS = [5] # [5, 10, 15, 20, 25] 
    for ws in tqdm(WS):
        # read ground_truth:
        gt_df = pd.read_csv(gt_path, index_col=[0])
        gt_data = gt_df.drop(gt_df[gt_df['ID'] == 0].index)  #把真值里面的未标记点云去除
        gt_data.rename(columns={'Confidence Score': 'confiScore'}, inplace=True)
        dalponte2016_sepilok = EvaluationCrownPolygon(gtPts=gt_data)
        dalponte2016_sepilok.fitPolygonBatchwithCS(pts=gt_data, mode='gt')
        smoothing = [1,3,5,7]
        th_seed = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        th_cr = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        for smoothing_i in tqdm(smoothing):
            print('smoothing size is:', smoothing_i)
            predicted_tree_nums, gt_tree_nums = [], []
            TP, FP, FN = [], [], []
            Precision, Recall, F1Score = [], [], []
            for th_seed_i in tqdm(th_seed):
                predicted_tree_nums_row, gt_tree_nums_row = [], []
                TP_row, FP_row, FN_row = [], [], []
                precision_row, recall_row, f1_row = [], [], []
                for th_cr_i in th_cr:
                    name = 'ws_' + str(ws) + '_smoothing_' + str(smoothing_i) + '_thcr_' + str(th_cr_i) + '_thseed_' + str(th_seed_i) + '.csv'
                    print(name)
                    # --- read segmentation data --- #
                    seg_path = os.path.join(seg_path, name)
                    seg_data = pd.read_csv(seg_path, index_col=[0])
                    index = list(range(1, len(seg_data) + 1))
                    # --- set index column --- #
                    seg_data['Index'] = index
                    # --- remove points with confidence score = 0 --- #
                    seg_data = seg_data[seg_data['confiScore']!= 0]
                    # --- fit polygons with labelled confidence score --- #
                    print('Segmentation Polygon fitting...')
                    dalponte2016_sepilok.fitPolygonBatchwithCS(pts=seg_data, mode='seg')
                    # --- assessment --- #
                    dalponte2016_sepilok.overlayAssessment(CS_set=cs_set)
                    TP_row.append(dalponte2016_sepilok.TP)
                    FP_row.append(dalponte2016_sepilok.FP)
                    FN_row.append(dalponte2016_sepilok.FN)
                    dalponte2016_sepilok.calPrecision()                                                                 # calculate precision
                    dalponte2016_sepilok.calRecall()                                                                    # calculate recall
                    predicted_tree_nums_row.append(dalponte2016_sepilok.seg_tree_nums)                                  # calculate number of predicted tree
                    gt_tree_nums_row.append(dalponte2016_sepilok.gt_tree_nums)
                    precision_row.append(dalponte2016_sepilok.precision)                                                # record precision
                    recall_row.append(dalponte2016_sepilok.recall)                                                      # record recall
                    if dalponte2016_sepilok.precision == 0 and dalponte2016_sepilok.recall==0:
                        f1_row.append(0)                                                                                # calculate F1 score
                    else:
                        dalponte2016_sepilok.calF1Score()                                                               # calculate F1 score
                        f1_row.append(dalponte2016_sepilok.f1)                                                          # record F1 score
                predicted_tree_nums.append(predicted_tree_nums_row)                                                     # total number of trees in prediction
                gt_tree_nums.append(gt_tree_nums_row)
                TP.append(TP_row)                                                                                       # TP
                FP.append(FP_row)                                                                                       # FP
                FN.append(FN_row) 
                Precision.append(precision_row)
                Recall.append(recall_row)
                F1Score.append(f1_row)
            df_assess = pd.DataFrame()
            df_assess['Reference_tree_nums'] = gt_tree_nums
            df_assess['Predicted_tree_nums'] = predicted_tree_nums
            df_assess['TP'] = TP
            df_assess['FP'] = FP
            df_assess['FN'] = FN
            df_assess['Precision'] = Precision
            df_assess['Recall'] = Recall
            df_assess['F1'] = F1Score
            out_file_name = 'dalponte2016_ws_' + str(ws) + '_smoothing_' + str(smoothing_i) + '_cs_' + cs_suffix + '_p_r_f1.csv'
            out_path = os.path.join(outpath, out_file_name)
            print(out_path)
            df_assess.to_csv(out_path)
            print('ok')
    print('Finished..')

def dalponte2016plus_p_r_f1(seg_path: str, gt_path: str, out_path: str, cs_set: list=[1,2,3]) -> None:
    print('input cs is:' + str(cs_set))
    cs_suffix = ''
    for ele in cs_set:
        cs_suffix += str(ele)
    # read ground_truth:
    gt_df = pd.read_csv(gt_path, index_col=[0])
    gt_data = gt_df.drop(gt_df[gt_df['ID'] == 0].index)                                                  #把真值里面的未标记点云去除
    gt_data.rename(columns={'Confidence Score': 'confiScore'}, inplace=True)
    daplonte2016plus_sepilok = EvaluationCrownPolygon(gtPts=gt_data)
    daplonte2016plus_sepilok.fitPolygonBatchwithCS(pts=gt_data, mode='gt')   
    TAU = [10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
    THSEED = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    THCR = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    for tau in tqdm(TAU):
        predicted_tree_nums, gt_tree_nums = [], []
        TP, FP, FN = [], [], []
        Precision, Recall, F1Score = [], [], []
        for thseed in THSEED:
            predicted_tree_nums_row, gt_tree_nums_row = [], []
            TP_row, FP_row, FN_row = [], [], []
            precision_row, recall_row, f1_row = [], [], []
            for thcr in THCR:
                name = 'tau_' + str(tau) + '_THSEED_' + str(thseed) + '_THCR_' + str(thcr) + '_cw_1.csv'
                # --- read segmentation data --- #
                seg_path = os.path.join(seg_path, name)
                seg_data = pd.read_csv(seg_path, index_col=[0])
                # --- set index column --- #
                index = list(range(1, len(seg_data) + 1))
                seg_data['Index'] = index   
                # --- remove points with confidence score = 0 --- #
                seg_data = seg_data[seg_data['confiScore']!= 0]     
                # --- fit polygons with labelled confidence score --- #        
                print('Segmentation Polygon fitting...')
                daplonte2016plus_sepilok.fitPolygonBatchwithCS(pts=seg_data, mode='seg')   
                # --- assessment --- #
                daplonte2016plus_sepilok.overlayAssessment(CS_set=cs_set)
                TP_row.append(daplonte2016plus_sepilok.TP)
                FP_row.append(daplonte2016plus_sepilok.FP)
                FN_row.append(daplonte2016plus_sepilok.FN)
                daplonte2016plus_sepilok.calPrecision()                                                                 # calculate precision
                daplonte2016plus_sepilok.calRecall()       
                predicted_tree_nums_row.append(daplonte2016plus_sepilok.seg_tree_nums)
                gt_tree_nums_row.append(daplonte2016plus_sepilok.gt_tree_nums)
                precision_row.append(daplonte2016plus_sepilok.precision)                                                # record precision
                recall_row.append(daplonte2016plus_sepilok.recall)                                                      # record recall
                if daplonte2016plus_sepilok.precision == 0 and daplonte2016plus_sepilok.recall==0:
                    f1_row.append(0)                                                                                    # calculate F1 score
                else:
                    daplonte2016plus_sepilok.calF1Score()                                                               # calculate F1 score
                    f1_row.append(daplonte2016plus_sepilok.f1)                                                          # record F1 score
            predicted_tree_nums.append(predicted_tree_nums_row)
            gt_tree_nums.append(gt_tree_nums_row)
            TP.append(TP_row)
            FP.append(FP_row)
            FN.append(FN_row)
            Precision.append(precision_row)
            Recall.append(recall_row)
            F1Score.append(f1_row)
        df_assess = pd.DataFrame()
        df_assess['Reference_tree_nums'] = gt_tree_nums
        df_assess['Predicted_tree_nums'] = predicted_tree_nums
        df_assess['TP'] = TP
        df_assess['FP'] = FP
        df_assess['FN'] = FN
        df_assess['Precision'] = Precision
        df_assess['Recall'] = Recall
        df_assess['F1'] = F1Score
        out_file_name =  'dalponte2016+_tau_' + str(tau) + '_cs_' + cs_suffix + '_p_r_f1.csv'
        out_path = os.path.join(out_path, out_file_name)
        print(out_path)
        df_assess.to_csv(out_path)
        print('ok')
    print('Finished..')            
    
def li2012_p_r_f1(cs_set: list=[1,2,3]) -> None:
    print('input cs is:' + str(cs_set))
    pwd = '/home/yc547/Sepilok/'
    in_root_path = os.path.join(pwd, 'Seg_res', 'seg_pts', 'li2012')
    gt_root_path = os.path.join(pwd, 'Ground_truth')
    gt_path = os.path.join(gt_root_path, 'ground_truth.csv')
    cs_suffix = ''
    for ele in cs_set:
        cs_suffix += str(ele)
    gt_df = pd.read_csv(gt_path, index_col=[0])
    gt_data = gt_df.drop(gt_df[gt_df['ID'] == 0].index)                                                  #把真值里面的未标记点云去除
    gt_data.rename(columns={'Confidence Score': 'confiScore'}, inplace=True)
    li2012_sepilok = EvaluationCrownPolygon(gtPts=gt_data)
    li2012_sepilok.fitPolygonBatchwithCS(pts=gt_data ,mode='gt')                                         # fit ground truth polygon
    DT1 = [1,2,3,4,5,6,7,8,9,10]
    DT2 = [1,2,3,4,5,6,7,8,9,10]
    predicted_tree_nums, gt_tree_nums = [], []
    TP, FP, FN = [], [], []
    Precision, Recall, F1Score = [], [], []
    for dt1 in tqdm(DT1):
        predicted_tree_nums_row, gt_tree_nums_row = [], []
        TP_row, FP_row, FN_row = [], [], []
        precision_row, recall_row, f1_row = [], [], []
        for dt2 in tqdm(DT2):
            # --- read segmentation data --- #
            name = 'sepilok_R_1_dt1_' + str(dt1) + '_dt2_' + str(dt2) + '.csv'
            print(name)
            seg_path = os.path.join(in_root_path, name)
            seg_df = pd.read_csv(seg_path, index_col=[0])
            seg_data = seg_df.drop(seg_df[seg_df['ID'] == 10000].index)
            # --- set index column --- # 
            index = list(range(1, len(seg_data) + 1))
            seg_data['Index'] = index
            # --- remove points with confidence score = 0 --- #
            seg_data = seg_data[seg_data['confiScore']!= 0]
            # --- fit polygons with labelled confidence score --- #
            print('Segmentation Polygon fitting...')
            li2012_sepilok.fitPolygonBatchwithCS(pts=seg_data, mode='seg')                                # fit segmentation polygon
            # --- assessment --- #
            li2012_sepilok.overlayAssessment(CS_set=cs_set)
            TP_row.append(li2012_sepilok.TP)
            FP_row.append(li2012_sepilok.FP)
            FN_row.append(li2012_sepilok.FN)
            li2012_sepilok.calPrecision()                                                                 # calculate precision
            li2012_sepilok.calRecall() 
            predicted_tree_nums_row.append(li2012_sepilok.seg_tree_nums)
            gt_tree_nums_row.append(li2012_sepilok.gt_tree_nums)
            precision_row.append(li2012_sepilok.precision)                                                # record precision
            recall_row.append(li2012_sepilok.recall)                                                      # record recall
            if li2012_sepilok.precision == 0 and li2012_sepilok.recall==0:
                f1_row.append(0)                                                                          # calculate F1 score
            else:
                li2012_sepilok.calF1Score()                                                               # calculate F1 score
                f1_row.append(li2012_sepilok.f1)                                                          # record F1 score
        predicted_tree_nums.append(predicted_tree_nums_row)                                               # total number of trees in prediction
        gt_tree_nums.append(gt_tree_nums_row)
        TP.append(TP_row)                                                                                 # TP
        FP.append(FP_row)                                                                                 # FP
        FN.append(FN_row)                                                                                 # FN
        Precision.append(precision_row)
        Recall.append(recall_row)
        F1Score.append(f1_row)
    df_assess = pd.DataFrame()
    df_assess['Reference_tree_nums'] = gt_tree_nums
    df_assess['Predicted_tree_nums'] = predicted_tree_nums
    df_assess['TP'] = TP
    df_assess['FP'] = FP
    df_assess['FN'] = FN
    df_assess['Precision'] = Precision
    df_assess['Recall'] = Recall
    df_assess['F1'] = F1Score
    out_file_name =  'li2012_R_1_dt1_' + str(dt1) + '_dt2_' + str(dt2) + '_cs_' + cs_suffix + '_p_r_f1.csv'
    out_path = os.path.join(pwd, 'Seg_res', 'seg_pts', out_file_name)
    print(out_path)
    df_assess.to_csv(out_path)
    print('ok')
    print('Finished..')

def job(seg_path: str, gt_path: str, out_path: str, index: int, method: str=None) -> None: 
    cs_set_list = [[1], [1,2], [1,2,3]]
    if method == 'dalponte2016':
        dalponte2016_p_r_f1(seg_path=seg_path, gt_path=gt_path, out_path=out_path, cs_set=cs_set_list[index]) 
    elif method == 'dalponte2016plus':
        dalponte2016plus_p_r_f1(seg_path=seg_path, gt_path=gt_path, out_path=out_path, cs_set=cs_set_list[index])
    elif method == 'ams3d':
        ams3d_p_r_f1(seg_path=seg_path, gt_path=gt_path, out_path=out_path, cs_set=cs_set_list[index])
    elif method == 'li2012':
        li2012_p_r_f1(seg_path=seg_path, gt_path=gt_path, out_path=out_path, cs_set=cs_set_list[index])
    else:
        print('Please choose a method: dalponte2016/dalponte2016plus/ams3d/li2012')

if __name__ == '__main__':
    segmentation_res_path = None
    groundtruth_path = None
    output_path = None
    # job(1) # test single confidence score set
    pool_obj = multiprocessing.Pool(3)
    pool_obj.map(job(seg_path=segmentation_res_path, gt_path=groundtruth_path, out_path=output_path, method='dalponte2016'), range(0, 3))
