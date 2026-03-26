import numpy as np
import scipy.io
import pandas as pd
import os

# from func1K import *


""" for the new dataset """
## SC -- from the new dataset
def load_SC_new(nfname):
    mfold = '/SC/SC'
    subjlist = []
    bigmtx = np.zeros((1315, 100,100))
    count = 0
    for subj in range(1,1315):
        sbj = str(subj).zfill(4)
        sbjstrg = f'/sub-{sbj}/ses-1/SC/sub-{sbj}_'
        filepath = f'{pfold}{mfold}{sbjstrg}{nfname}'
        if os.path.exists(filepath):
            smtx = np.loadtxt(f'{filepath}')
            bigmtx[count] = smtx
            subjlist.append(subj)
            count+=1
    scsubj = np.array(subjlist)
    return bigmtx[:count], scsubj



## time-series -- from the new dataset
def load_timeseries_new(comfname):
    mfold = '/FC/FC'
    subjlist = []
    lts = []
    for subj in range(1,1315):
        sbj = str(subj).zfill(4)
        filepath = f'{pfold}{mfold}/sub-{sbj}/ses-1/FC/Schaefer_100_7NW/sub-{sbj}{comfname}'
        if os.path.exists(filepath):
            tseries = np.loadtxt(f'{filepath}')
            if tseries.shape[0]==296:#
                lts.append(tseries)
                # bigmtx[subj-1] = tseries
                subjlist.append(subj)
    bigmtx = np.array(lts)
    tsubj = np.array(subjlist)
    return bigmtx, tsubj


## demography -- from new dataset
def load_demography_new():
    # dem = np.loadtxt(f'{pfold}/Demographic_data.csv', delimiter=',', skiprows=1)
    dem = pd.read_csv(f'{pfold}/Demographic_data.csv', delimiter=';')
    demred = dem[['id', 'Sex', 'Age_ses-1', 'ISCED_ses-1']]
    demog = demred.dropna()
    # demog = demred[~demred.isin(['#NV']).any(axis=1)]
    dsubj = np.array([ss.split('-')[1] for ss in demog['id']]).astype(int)

    return demog, dsubj
    

# morphology -- from the new dataset
def load_morphology_new():
    mfold = 'Surface_morphology'
    fstring = 'Schaefer2018_100Parcels_17Networks_gcs'
    
    todrops = [
        ['rh_WhiteSurfArea_area',
        'BrainSegVolNotVent',
        'eTIV',
        'lh_WhiteSurfArea_area',
        'BrainSegVolNotVent.1',
        'eTIV.1'],
        ['BrainSegVolNotVent',
        'eTIV',
        'BrainSegVolNotVent.1',
        'eTIV.1'],
        ['rh_MeanThickness_thickness',
        'BrainSegVolNotVent',
        'eTIV',
        'lh_MeanThickness_thickness',
        'BrainSegVolNotVent.1',
        'eTIV.1']]
    avt = []
    avtsubj = []
    avtcnames = []
    for ix, xx in enumerate(['area', 'volume', 'thickness']):
        yy = pd.read_csv(f'{pfold}/{mfold}/{fstring}_{xx}.csv', delimiter=';')
        ysubj = np.array([ss.split('-')[1] for ss in yy['ID']]).astype(int)
        todrop = ['ID'] + todrops[ix]
        ryy = yy.drop(todrop, axis=1)
        ynames = ryy.columns
        yarr = np.array(ryy)
        
        avt.append(yarr)
        avtsubj.append(ysubj)
        avtcnames.append(ynames)
    avt = np.array(avt)
    avtsubj = np.array(avtsubj)
    avtcnames = np.array(avtcnames)    
    return avt, avtsubj, avtcnames
    

# cognition -- from the new dataset
def load_cognition_new():
    mfold = 'Cognition/V1/data'
    cog = pd.read_excel(f'{pfold}/{mfold}/1000Brains_NP_VarOI_V1_Pseudo.xlsx')
    rcog = cog.drop(['Visit', 'Age', 'Sex', 'ISCED_97'], axis=1)
    rrcogg = rcog.dropna()
    rrcog = rrcogg[(rrcogg >= 0).all(axis=1)]# removing subjects with negative scores (possibly)
    srrcog = rrcog.sort_values(by=rrcog.columns[0])
    csubj = np.array(srrcog['ID'])
    cogscore = np.array(srrcog.iloc[:,1:])
    
    cnames = srrcog.columns[1:]
    return cogscore, csubj, cnames
    




# # #### SC file variants
# # # new dataset
# # nfname1 = 'ses-1_gibbs_eddy_clean_1p25mm_csd_tracks_act_10M_sift2_atlas-Schaefer2018_desc-100Parcels7Networks_dseg_CM.txt'
# nfname2 = 'ses-1_gibbs_eddy_clean_1p25mm_csd_tracks_act_10M_sift2_atlas-Schaefer2018_desc-100Parcels7Networks_dseg_CM_log.txt'
# # nfname3 = 'ses-1_gibbs_eddy_clean_1p25mm_csd_tracks_act_10M_atlas-Schaefer2018_desc-100Parcels7Networks_dseg_CM.txt'
# # nfname4 = 'ses-1_gibbs_eddy_clean_1p25mm_csd_tracks_act_10M_atlas-Schaefer2018_desc-100Parcels7Networks_dseg_CM_log.txt'
# # # old dataset
# # ofname1 = '1_dwi_connectome_100P_7NW_sift2_nolog.txt'
# # ofname2 = '1_dwi_connectome_100P_7NW_sift2_log10.txt'
#
#
# # parent folder for the new dataset
pfold = '/Users/sima/Documents/1Kbrains/1000BRAINSconnectomes_Jirsa'
#
# #### loading
# # loading the structural connectivity matrices of all available subjects (NEW dataset)
# bmtrx, ssubj = load_SC_new(nfname2)
# # loading demography data of all available subjects (NEW dataset)
# demog0, dsubj0 = load_demography_new()
# dsubj, dxunq = np.unique(dsubj0, return_index=True)
# demog = demog0.iloc[dxunq]
#
# # loading the timeseries of all available subjects (NEW dataset)
# comfname1 = '_ses-1_FC_TS_Schaefer_100P_7NW_V1.txt'
# tmsrs1, tsubj1 = load_timeseries_new(comfname1)
# comfname4 = '_ses-1_FC_TS_Schaefer_100P_7NW_V4.txt'
# tmsrs4, tsubj4 = load_timeseries_new(comfname1)
# print(np.array_equal(tsubj1, tsubj4))
# # loading cognitive scores of all available subjects (NEW dataset)
# cogni, csubj, cnames = load_cognition_new()
#
#
#
# # morphology
# avt0, avtsubjarr, avtcnames = load_morphology_new() ##### duplicates, we just take the first one.
# # print(np.array_equal(avtsubjarr[0], avtsubj[1]))
# # print(np.array_equal(avtsubjarr[0], avtsubj[2]))
# avtsubj0 = avtsubjarr[0]
# ## there are duplicates
# avtsubj, dxunqsubj = np.unique(avtsubj0, return_index=True)
# avt = avt0[:,dxunqsubj,:]
# # print(np.array_equal(avtsubj[0], avtsubj[1]))
# # print(np.array_equal(avtsubj[0], avtsubj[2]))
# # dxsubjs = np.where(np.in1d(avtsubj, comsubj))[0]
#
#
# from collections import Counter
# # aa = [ssubj, msubj, tsubj, dsubj, csubj]
# aa = [ssubj, tsubj1, avtsubj, dsubj, csubj]
# # bdata0 = [bmtrx, tmsrs, demog, cogni]
# typee = ['conmat', 'tseries1', 'avt', 'demog', 'cog']
#
#
# #### subjects that have sc, demog, timeseries and cognition data.
# comsubj = set(ssubj)
# for jx, jj in enumerate(aa):
#     duplicates = set([item for item, count in Counter(jj).items() if count > 1])
#     print(jx)
#     print(jj.shape)
#     print(len(duplicates)) # duplicates in demography taken care of above.
#     print('')
#     comsubj = comsubj.intersection(jj)
# comsubj = np.array(list(comsubj))
#
#
#
# idxsubjs = np.array([np.where(np.in1d(x, comsubj))[0] for x in aa])
#
# s_conns = bmtrx[idxsubjs[0]]
# t_series1 = tmsrs1[idxsubjs[1]]
# t_series4 = tmsrs4[idxsubjs[1]]
# ravt = avt[:,idxsubjs[2],:]
# cog_score = cogni[idxsubjs[4]]
#
# demography = demog.iloc[idxsubjs[3]]
# sex = demography['Sex']
# age = demography['Age_ses-1']
# edu = demography['ISCED_ses-1']
#
# sex = np.array(sex)
# age = np.array(age)
# edu = np.array(edu)
#
#
# np.savez_compressed(
#     'session1_refined.npz',
#     subjs = comsubj,
#     tseries1 = t_series1,
#     tseries4 = t_series4,
#     sconns = s_conns,
#     area = ravt[0],
#     volume=ravt[1],
#     thickness=ravt[2],
#     cogscores = cog_score,
#     cognames = cnames,
#     sex = sex,
#     age = age,
#     edu = edu,
# )
#
# np.save('ts777_v1.npy', t_series1)
# np.save('ts777_v4.npy', t_series4)



mfold = 'Cognition/V1/data'
cog = pd.read_excel(f'{pfold}/{mfold}/1000Brains_NP_VarOI_V1_Pseudo.xlsx')
rcog = cog.drop(['Visit', 'Age', 'Sex', 'ISCED_97'], axis=1)
rrcogg = rcog.dropna()
rrcog = rrcogg[(rrcogg >= 0).all(axis=1)]# removing subjects with negative scores (possibly)
srrcog = rrcog.sort_values(by=rrcog.columns[0])
csubj = np.array(srrcog['ID'])
cogscore = np.array(srrcog.iloc[:,1:])

cnames = srrcog.columns[1:]




