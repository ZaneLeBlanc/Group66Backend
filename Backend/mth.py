# %% [markdown]
#  # MTH-IDS: A Multi-Tiered Hybrid Intrusion Detection System for Internet of Vehicles
#  This is the code for the paper entitled "[**MTH-IDS: A Multi-Tiered Hybrid Intrusion Detection System for Internet of Vehicles**](https://arxiv.org/pdf/2105.13289.pdf)" accepted in IEEE Internet of Things Journal.
#  Authors: Li Yang (liyanghart@gmail.com), Abdallah Moubayed, and Abdallah Shami
#  Organization: The Optimized Computing and Communications (OC2) Lab, ECE Department, Western University
# 
#  If you find this repository useful in your research, please cite:
#  L. Yang, A. Moubayed, and A. Shami, “MTH-IDS: A Multi-Tiered Hybrid Intrusion Detection System for Internet of Vehicles,” IEEE Internet of Things Journal, vol. 9, no. 1, pp. 616-632, Jan.1, 2022.

import time
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score,precision_recall_fscore_support
from sklearn.metrics import f1_score,roc_auc_score
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb
from xgboost import plot_importance


# %% [markdown]
#  ## Read the sampled CICIDS2017 dataset
#  The CICIDS2017 dataset is publicly available at: https://www.unb.ca/cic/datasets/ids-2017.html
#  Due to the large size of this dataset, the sampled subsets of CICIDS2017 is used. The subsets are in the "data" folder.
#  If you want to use this code on other datasets (e.g., CAN-intrusion dataset), just change the dataset name and follow the same steps. The models in this code are generic models that can be used in any intrusion detection/network traffic datasets.

# %%
#Read dataset
# df = pd.read_csv('./data/CICIDS2017.csv') 
# # The results in this code is based on the original CICIDS2017 dataset. Please go to cell [21] if you work on the sampled dataset. 

# # %%
# df

# # %%
# df.Label.value_counts()

# # %% [markdown]
# # ### Preprocessing (normalization and padding values)

# # %%
# # Z-score normalization
# features = df.dtypes[df.dtypes != 'object'].index
# df[features] = df[features].apply(
#     lambda x: (x - x.mean()) / (x.std()))
# # Fill empty values by 0
# df = df.fillna(0)

# # %% [markdown]
# # ### Data sampling
# # Due to the space limit of GitHub files and the large size of network traffic data, we sample a small-sized subset for model learning using **k-means cluster sampling**

# # %%
# labelencoder = LabelEncoder()
# df.iloc[:, -1] = labelencoder.fit_transform(df.iloc[:, -1])

# # %%
# df.Label.value_counts()

# # %%
# # retain the minority class instances and sample the majority class instances
# df_minor = df[(df['Label']==6)|(df['Label']==1)|(df['Label']==4)]
# df_major = df.drop(df_minor.index)

# # %%
# X = df_major.drop(['Label'],axis=1) 
# y = df_major.iloc[:, -1].values.reshape(-1,1)
# y=np.ravel(y)

# # %%
# # use k-means to cluster the data samples and select a proportion of data from each cluster
# from sklearn.cluster import MiniBatchKMeans
# kmeans = MiniBatchKMeans(n_clusters=1000, random_state=0).fit(X)

# # %%
# klabel=kmeans.labels_
# df_major['klabel']=klabel

# # %%
# df_major['klabel'].value_counts()

# # %%
# cols = list(df_major)
# cols.insert(78, cols.pop(cols.index('Label')))
# df_major = df_major.loc[:, cols]

# # %%
# df_major

# # %%
# def typicalSampling(group):
#     name = group.name
#     frac = 0.008
#     return group.sample(frac=frac)

# result = df_major.groupby(
#     'klabel', group_keys=False
# ).apply(typicalSampling)

# # %%
# result['Label'].value_counts()

# # %%
# result

# # %%
# result = result.drop(['klabel'],axis=1)
# result = result.append(df_minor)

# # %%
# result.to_csv('./data/CICIDS2017_sample_km.csv',index=0)


# %% [markdown]
#  ### split train set and test set


def preprocessing(dataset_path, train_split):
    # Read the sampled dataset

    df = pd.read_csv(dataset_path)
    features = df.dtypes[df.dtypes != 'object'].index

    if 'CICIDS2017_sample_km.csv' in dataset_path:
        X = df.drop(['Label'],axis=1).values
        y = df.iloc[:, -1].values.reshape(-1,1)
        y=np.ravel(y)

        X_train, X_test, y_train, y_test = train_test_split(X,y, train_size = train_split, test_size = (1 - train_split), random_state = 0,stratify = y)
        
    elif 'CICIDS2017_sample.csv' in dataset_path:
        numeric_features = df.dtypes[df.dtypes != 'object'].index
        df[numeric_features] = df[numeric_features].apply(
        lambda x: (x - x.min()) / (x.max()-x.min()))

        # Fill empty values by 0
        df = df.fillna(0)

        labelencoder = LabelEncoder()
        df.iloc[:, -1] = labelencoder.fit_transform(df.iloc[:, -1])
        X = df.drop(['Label'],axis=1)
        y = df.iloc[:, -1].values.reshape(-1,1)
        y=np.ravel(y)

        X_train, X_test, y_train, y_test = train_test_split(X,y, train_size = 0.8, test_size = 0.2, random_state = 0,stratify = y)

        y_train = y_train.astype(int)
        X_train = X_train.values

#  ## Feature engineering
#  ### Feature selection by information gain
    from sklearn.feature_selection import mutual_info_classif
    importances = mutual_info_classif(X_train, y_train)

    # calculate the sum of importance scores
    f_list = sorted(zip(map(lambda x: round(x, 4), importances), features), reverse=True)
    Sum = 0
    fs = []
    for i in range(0, len(f_list)):
        Sum = Sum + f_list[i][0]
        fs.append(f_list[i][1])

    # select the important features from top to bottom until the accumulated importance reaches 90%
    f_list2 = sorted(zip(map(lambda x: round(x, 4), importances/Sum), features), reverse=True)
    Sum2 = 0
    fs = []
    for i in range(0, len(f_list2)):
        Sum2 = Sum2 + f_list2[i][0]
        fs.append(f_list2[i][1])
        if Sum2>=0.9:
            break        

    X_fs = df[fs].values
    X_fs.shape

    #  ### Feature selection by Fast Correlation Based Filter (FCBF)
    #  The module is imported from the GitHub repo: https://github.com/SantiagoEG/FCBF_module
    from FCBF_module.FCBF_module import FCBF, FCBFK, FCBFiP, get_i
    fcbf = FCBFK(k = 20)
    #fcbf.fit(X_fs, y)
    X_fss = fcbf.fit_transform(X_fs,y)
    X_fss.shape

    #  ### Re-split train & test sets after feature selection
    X_train, X_test, y_train, y_test = train_test_split(X_fss,y, train_size = train_split, test_size = (1 - train_split), random_state = 0,stratify = y)
    X_train.shape

    pd.Series(y_train).value_counts()

    from imblearn.over_sampling import SMOTE
    #  ### SMOTE to solve class-imbalance
    if 'CICIDS2017_sample_km.csv' in dataset_path:
        smote=SMOTE(n_jobs=-1,sampling_strategy={2:1000,4:1000})
    
    elif 'CICIDS2017_sample.csv' in dataset_path:
        smote=SMOTE(n_jobs=-1,sampling_strategy={4:1500})#####
        y_train = y_train.astype(int)
        y_test = y_test.astype(int)

    X_train, y_train = smote.fit_resample(X_train, y_train)

    pd.Series(y_train).value_counts()

    print('**Preprocessing Complete**')
    return X_train, X_test, y_train, y_test



#  ## Machine learning model training
#  ### Training four base learners: decision tree, random forest, extra trees, XGBoost
#  #### Apply XGBoost
def train_models(X_train, X_test, y_train, y_test, max_features, hpo_max_evals):
    #time models
    global start_time
    start_time = time.time()

    xg = xgb.XGBClassifier(n_estimators = 10)
    xg.fit(X_train,y_train)
    xg_score=xg.score(X_test,y_test)
    y_predict=xg.predict(X_test)
    y_true=y_test
    print('Accuracy of XGBoost: '+ str(xg_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of XGBoost: '+(str(precision)))
    print('Recall of XGBoost: '+(str(recall)))
    print('F1-score of XGBoost: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()



    #  #### Hyperparameter optimization (HPO) of XGBoost using Bayesian optimization with tree-based Parzen estimator (BO-TPE)
    #  Based on the GitHub repo for HPO: https://github.com/LiYangHart/Hyperparameter-Optimization-of-Machine-Learning-Algorithms


    from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    def objective(params):
        params = {
            'n_estimators': int(params['n_estimators']), 
            'max_depth': int(params['max_depth']),
            'learning_rate':  abs(float(params['learning_rate'])),

        }
        clf = xgb.XGBClassifier( **params)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        score = accuracy_score(y_test, y_pred)

        return {'loss':-score, 'status': STATUS_OK }

    space = {
        'n_estimators': hp.quniform('n_estimators', 10, 100, 5),
        'max_depth': hp.quniform('max_depth', 4, 100, 1),
        'learning_rate': hp.normal('learning_rate', 0.01, 0.9),
    }

    best = fmin(fn=objective,
                space=space,
                algo=tpe.suggest,
                max_evals=hpo_max_evals)
    print("XGBoost: Hyperopt estimated optimum {}".format(best))

    best['n_estimators'] = int(best['n_estimators'])
    best['max_depth'] = int(best['max_depth'])
    best['learning_rate'] = abs(best['learning_rate'])

    #xg = xgb.XGBClassifier(learning_rate= 0.7340229699980686, n_estimators = 70, max_depth = 14)
    xg = xgb.XGBClassifier(**best)
    xg.fit(X_train,y_train)
    xg_score=xg.score(X_test,y_test)
    y_predict=xg.predict(X_test)
    y_true=y_test
    print('Accuracy of XGBoost: '+ str(xg_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of XGBoost: '+(str(precision)))
    print('Recall of XGBoost: '+(str(recall)))
    print('F1-score of XGBoost: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()



    xg_train=xg.predict(X_train)
    xg_test=xg.predict(X_test)



    #  #### Apply RF


    rf = RandomForestClassifier(random_state = 0)
    rf.fit(X_train,y_train) 
    rf_score=rf.score(X_test,y_test)
    y_predict=rf.predict(X_test)
    y_true=y_test
    print('Accuracy of RF: '+ str(rf_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of RF: '+(str(precision)))
    print('Recall of RF: '+(str(recall)))
    print('F1-score of RF: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()



    #  #### Hyperparameter optimization (HPO) of random forest using Bayesian optimization with tree-based Parzen estimator (BO-TPE)
    #  Based on the GitHub repo for HPO: https://github.com/LiYangHart/Hyperparameter-Optimization-of-Machine-Learning-Algorithms


    # Hyperparameter optimization of random forest
    from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    # Define the objective function
    def objective(params):
        params = {
            'n_estimators': int(params['n_estimators']), 
            'max_depth': int(params['max_depth']),
            'max_features': int(params['max_features']),
            "min_samples_split":int(params['min_samples_split']),
            "min_samples_leaf":int(params['min_samples_leaf']),
            "criterion":str(params['criterion'])
        }
        clf = RandomForestClassifier( **params)
        clf.fit(X_train,y_train)
        score=clf.score(X_test,y_test)

        return {'loss':-score, 'status': STATUS_OK }
    # Define the hyperparameter configuration space
    space = {
        'n_estimators': hp.quniform('n_estimators', 10, 200, 1),
        'max_depth': hp.quniform('max_depth', 5, 50, 1),
        "max_features":hp.quniform('max_features', 1, max_features, 1),
        "min_samples_split":hp.quniform('min_samples_split',2,11,1),
        "min_samples_leaf":hp.quniform('min_samples_leaf',1,11,1),
        "criterion":hp.choice('criterion',['gini','entropy'])
    }

    best = fmin(fn=objective,
                space=space,
                algo=tpe.suggest,
                max_evals=hpo_max_evals)
    print("Random Forest: Hyperopt estimated optimum {}".format(best))

    best['n_estimators'] = int(best['n_estimators'])
    best['max_depth'] = int(best['max_depth'])
    best['max_features'] = int(best['max_features'])
    best['min_samples_split'] = int(best['min_samples_split'])
    best['min_samples_leaf'] = int(best['min_samples_leaf'])
    best['criterion'] = 'gini' if best['criterion'] == 0 else 'entropy'

    #rf_hpo = RandomForestClassifier(n_estimators = 71, min_samples_leaf = 1, max_depth = 46, min_samples_split = 9, max_features = 20, criterion = 'entropy')
    rf_hpo = RandomForestClassifier(**best)
    rf_hpo.fit(X_train,y_train)
    rf_score=rf_hpo.score(X_test,y_test)
    y_predict=rf_hpo.predict(X_test)
    y_true=y_test
    print('Accuracy of RF: '+ str(rf_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of RF: '+(str(precision)))
    print('Recall of RF: '+(str(recall)))
    print('F1-score of RF: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()



    rf_train=rf_hpo.predict(X_train)
    rf_test=rf_hpo.predict(X_test)



    #  #### Apply DT


    dt = DecisionTreeClassifier(random_state = 0)
    dt.fit(X_train,y_train) 
    dt_score=dt.score(X_test,y_test)
    y_predict=dt.predict(X_test)
    y_true=y_test
    print('Accuracy of DT: '+ str(dt_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of DT: '+(str(precision)))
    print('Recall of DT: '+(str(recall)))
    print('F1-score of DT: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()



    #  #### Hyperparameter optimization (HPO) of decision tree using Bayesian optimization with tree-based Parzen estimator (BO-TPE)
    #  Based on the GitHub repo for HPO: https://github.com/LiYangHart/Hyperparameter-Optimization-of-Machine-Learning-Algorithms


    # Hyperparameter optimization of decision tree
    from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    # Define the objective function
    def objective(params):
        params = {
            'max_depth': int(params['max_depth']),
            'max_features': int(params['max_features']),
            "min_samples_split":int(params['min_samples_split']),
            "min_samples_leaf":int(params['min_samples_leaf']),
            "criterion":str(params['criterion'])
        }
        clf = DecisionTreeClassifier( **params)
        clf.fit(X_train,y_train)
        score=clf.score(X_test,y_test)

        return {'loss':-score, 'status': STATUS_OK }
    # Define the hyperparameter configuration space
    space = {
        'max_depth': hp.quniform('max_depth', 5, 50, 1),
        "max_features":hp.quniform('max_features', 1, max_features, 1),
        "min_samples_split":hp.quniform('min_samples_split',2,11,1),
        "min_samples_leaf":hp.quniform('min_samples_leaf',1,11,1),
        "criterion":hp.choice('criterion',['gini','entropy'])
    }

    best = fmin(fn=objective,
                space=space,
                algo=tpe.suggest,
                max_evals=hpo_max_evals)
    print("Decision tree: Hyperopt estimated optimum {}".format(best))

    best['max_depth'] = int(best['max_depth'])
    best['max_features'] = int(best['max_features'])
    best['min_samples_split'] = int(best['min_samples_split'])
    best['min_samples_leaf'] = int(best['min_samples_leaf'])
    best['criterion'] = 'gini' if best['criterion'] == 0 else 'entropy'

    #dt_hpo = DecisionTreeClassifier(min_samples_leaf = 2, max_depth = 47, min_samples_split = 3, max_features = 19, criterion = 'gini')
    dt_hpo = DecisionTreeClassifier(**best)
    dt_hpo.fit(X_train,y_train)
    dt_score=dt_hpo.score(X_test,y_test)
    y_predict=dt_hpo.predict(X_test)
    y_true=y_test
    print('Accuracy of DT: '+ str(dt_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of DT: '+(str(precision)))
    print('Recall of DT: '+(str(recall)))
    print('F1-score of DT: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()



    dt_train=dt_hpo.predict(X_train)
    dt_test=dt_hpo.predict(X_test)



    #  #### Apply ET


    et = ExtraTreesClassifier(random_state = 0)
    et.fit(X_train,y_train) 
    et_score=et.score(X_test,y_test)
    y_predict=et.predict(X_test)
    y_true=y_test
    print('Accuracy of ET: '+ str(et_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of ET: '+(str(precision)))
    print('Recall of ET: '+(str(recall)))
    print('F1-score of ET: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()



    #  #### Hyperparameter optimization (HPO) of extra trees using Bayesian optimization with tree-based Parzen estimator (BO-TPE)
    #  Based on the GitHub repo for HPO: https://github.com/LiYangHart/Hyperparameter-Optimization-of-Machine-Learning-Algorithms


    # Hyperparameter optimization of extra trees
    from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    # Define the objective function
    def objective(params):
        params = {
            'n_estimators': int(params['n_estimators']), 
            'max_depth': int(params['max_depth']),
            'max_features': int(params['max_features']),
            "min_samples_split":int(params['min_samples_split']),
            "min_samples_leaf":int(params['min_samples_leaf']),
            "criterion":str(params['criterion'])
        }
        clf = ExtraTreesClassifier( **params)
        clf.fit(X_train,y_train)
        score=clf.score(X_test,y_test)

        return {'loss':-score, 'status': STATUS_OK }
    # Define the hyperparameter configuration space
    space = {
        'n_estimators': hp.quniform('n_estimators', 10, 200, 1),
        'max_depth': hp.quniform('max_depth', 5, 50, 1),
        "max_features":hp.quniform('max_features', 1, max_features, 1),
        "min_samples_split":hp.quniform('min_samples_split',2,11,1),
        "min_samples_leaf":hp.quniform('min_samples_leaf',1,11,1),
        "criterion":hp.choice('criterion',['gini','entropy'])
    }

    best = fmin(fn=objective,
                space=space,
                algo=tpe.suggest,
                max_evals=hpo_max_evals)
    print("Random Forest: Hyperopt estimated optimum {}".format(best))

    best['n_estimators'] = int(best['n_estimators'])
    best['max_depth'] = int(best['max_depth'])
    best['max_features'] = int(best['max_features'])
    best['min_samples_split'] = int(best['min_samples_split'])
    best['min_samples_leaf'] = int(best['min_samples_leaf'])
    best['criterion'] = 'gini' if best['criterion'] == 0 else 'entropy'

    #et_hpo = ExtraTreesClassifier(n_estimators = 53, min_samples_leaf = 1, max_depth = 31, min_samples_split = 5, max_features = 20, criterion = 'entropy')
    et_hpo = ExtraTreesClassifier(**best)
    et_hpo.fit(X_train,y_train) 
    et_score=et_hpo.score(X_test,y_test)
    y_predict=et_hpo.predict(X_test)
    y_true=y_test
    print('Accuracy of ET: '+ str(et_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of ET: '+(str(precision)))
    print('Recall of ET: '+(str(recall)))
    print('F1-score of ET: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()



    et_train=et_hpo.predict(X_train)
    et_test=et_hpo.predict(X_test)



    #  ### Apply Stacking
    #  The ensemble model that combines the four ML models (DT, RF, ET, XGBoost)


    base_predictions_train = pd.DataFrame( {
        'DecisionTree': dt_train.ravel(),
            'RandomForest': rf_train.ravel(),
        'ExtraTrees': et_train.ravel(),
        'XgBoost': xg_train.ravel(),
        })
    base_predictions_train.head(5)


    dt_train=dt_train.reshape(-1, 1)
    et_train=et_train.reshape(-1, 1)
    rf_train=rf_train.reshape(-1, 1)
    xg_train=xg_train.reshape(-1, 1)
    dt_test=dt_test.reshape(-1, 1)
    et_test=et_test.reshape(-1, 1)
    rf_test=rf_test.reshape(-1, 1)
    xg_test=xg_test.reshape(-1, 1)


    dt_train.shape

    x_train = np.concatenate(( dt_train, et_train, rf_train, xg_train), axis=1)
    x_test = np.concatenate(( dt_test, et_test, rf_test, xg_test), axis=1)

    stk = xgb.XGBClassifier().fit(x_train, y_train)
    y_predict=stk.predict(x_test)
    y_true=y_test
    stk_score=accuracy_score(y_true,y_predict)
    print('Accuracy of Stacking: '+ str(stk_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of Stacking: '+(str(precision)))
    print('Recall of Stacking: '+(str(recall)))
    print('F1-score of Stacking: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()

    #  #### Hyperparameter optimization (HPO) of the stacking ensemble model (XGBoost) using Bayesian optimization with tree-based Parzen estimator (BO-TPE)
    #  Based on the GitHub repo for HPO: https://github.com/LiYangHart/Hyperparameter-Optimization-of-Machine-Learning-Algorithms

    # 
    from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    def objective(params):
        params = {
            'n_estimators': int(params['n_estimators']), 
            'max_depth': int(params['max_depth']),
            'learning_rate':  abs(float(params['learning_rate'])),

        }
        clf = xgb.XGBClassifier( **params)
        clf.fit(x_train, y_train)
        y_pred = clf.predict(x_test)
        score = accuracy_score(y_test, y_pred)

        return {'loss':-score, 'status': STATUS_OK }

    space = {
        'n_estimators': hp.quniform('n_estimators', 10, 100, 5),
        'max_depth': hp.quniform('max_depth', 4, 100, 1),
        'learning_rate': hp.normal('learning_rate', 0.01, 0.9),
    }

    best = fmin(fn=objective,
                space=space,
                algo=tpe.suggest,
                max_evals=hpo_max_evals)
    print("XGBoost: Hyperopt estimated optimum {}".format(best))

    best['n_estimators'] = int(best['n_estimators'])
    best['max_depth'] = int(best['max_depth'])
    best['learning_rate'] = abs(best['learning_rate'])

    # final stacked
    #xg = xgb.XGBClassifier(learning_rate= 0.19229249758051492, n_estimators = 30, max_depth = 36)
    xg = xgb.XGBClassifier(**best)
    xg.fit(x_train,y_train)
    xg_score=xg.score(x_test,y_test)
    y_predict=xg.predict(x_test)
    y_true=y_test
    print('Accuracy of XGBoost: '+ str(xg_score))
    precision,recall,fscore,none= precision_recall_fscore_support(y_true, y_predict, average='weighted') 
    print('Precision of XGBoost: '+(str(precision)))
    print('Recall of XGBoost: '+(str(recall)))
    print('F1-score of XGBoost: '+(str(fscore)))
    print(classification_report(y_true,y_predict))
    cm=confusion_matrix(y_true,y_predict)
    f,ax=plt.subplots(figsize=(5,5))
    sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
    plt.xlabel("y_pred")
    plt.ylabel("y_true")
    #plt.show()

    return str(xg_score), str(precision), str(recall), str(fscore), cm


# %% [markdown]
#  ## Anomaly-based IDS

# %% [markdown]
#  ### Generate the port-scan datasets for unknown attack detection

# %%
def anomaly_based():
    df=pd.read_csv('./Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km.csv')
    df.Label.value_counts()

    df1 = df[df['Label'] != 5]
    df1['Label'][df1['Label'] > 0] = 1
    df1.to_csv('./Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km_without_portscan.csv',index=0)

    df2 = df[df['Label'] == 5]
    df2['Label'][df2['Label'] == 5] = 1
    df2.to_csv('./Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km_portscan.csv',index=0)

    #  ### Read the generated datasets for unknown attack detection
    df1 = pd.read_csv('./Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km_without_portscan.csv')
    df2 = pd.read_csv('./Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km_portscan.csv')

    features = df1.drop(['Label'],axis=1).dtypes[df1.dtypes != 'object'].index
    df1[features] = df1[features].apply(
        lambda x: (x - x.mean()) / (x.std()))
    df2[features] = df2[features].apply(
        lambda x: (x - x.mean()) / (x.std()))
    df1 = df1.fillna(0)
    df2 = df2.fillna(0)

    df1.Label.value_counts()
    df2.Label.value_counts()

    df2p=df1[df1['Label']==0]
    df2pp=df2p.sample(n=None, frac=1255/18225, replace=False, weights=None, random_state=None, axis=0)
    df2=pd.concat([df2, df2pp])

    df2.Label.value_counts()

    df = df1._append(df2)

    X = df.drop(['Label'],axis=1) .values
    y = df.iloc[:, -1].values.reshape(-1,1)
    y=np.ravel(y)
    pd.Series(y).value_counts()


    #  ### Feature engineering (IG, FCBF, and KPCA)
    #  #### Feature selection by information gain (IG)

    from sklearn.feature_selection import mutual_info_classif
    importances = mutual_info_classif(X, y)

    # calculate the sum of importance scores
    f_list = sorted(zip(map(lambda x: round(x, 4), importances), features), reverse=True)
    Sum = 0
    fs = []
    for i in range(0, len(f_list)):
        Sum = Sum + f_list[i][0]
        fs.append(f_list[i][1])

    # select the important features from top to bottom until the accumulated importance reaches 90%
    f_list2 = sorted(zip(map(lambda x: round(x, 4), importances/Sum), features), reverse=True)
    Sum2 = 0
    fs = []
    for i in range(0, len(f_list2)):
        Sum2 = Sum2 + f_list2[i][0]
        fs.append(f_list2[i][1])
        if Sum2>=0.9:
            break        

    X_fs = df[fs].values
    X_fs.shape
    X_fs

    #  #### Feature selection by Fast Correlation Based Filter (FCBF)
    # 
    #  The module is imported from the GitHub repo: https://github.com/SantiagoEG/FCBF_module

    from FCBF_module.FCBF_module import FCBF, FCBFK, FCBFiP, get_i
    fcbf = FCBFK(k = 20)
    #fcbf.fit(X_fs, y)

    X_fss = fcbf.fit_transform(X_fs,y)
    X_fss.shape
    X_fss

    #  ####  kernel principal component analysis (KPCA)
    #from sklearn.decomposition import KernelPCA
    #kpca = KernelPCA(n_components = 10, kernel = 'rbf')
    #kpca.fit(X_fss, y)
    #X_kpca = kpca.transform(X_fss)

    from sklearn.decomposition import PCA
    kpca = PCA(n_components = 10)
    kpca.fit(X_fss, y)
    X_kpca = kpca.transform(X_fss)

    #  ### Train-test split after feature selection

    X_train = X_kpca[:len(df1)]
    y_train = y[:len(df1)]
    X_test = X_kpca[len(df1):]
    y_test = y[len(df1):]

    #  ### Solve class-imbalance by SMOTE

    pd.Series(y_train).value_counts()


    from imblearn.over_sampling import SMOTE
    smote=SMOTE(n_jobs=-1,sampling_strategy={1:18225})
    X_train, y_train = smote.fit_resample(X_train, y_train)

    pd.Series(y_train).value_counts()
    pd.Series(y_test).value_counts()


    #  ### Apply the cluster labeling (CL) k-means method

    from sklearn.cluster import KMeans
    from sklearn.cluster import DBSCAN,MeanShift
    from sklearn.cluster import SpectralClustering,AgglomerativeClustering,AffinityPropagation,Birch,MiniBatchKMeans,MeanShift 
    from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
    from sklearn.metrics import classification_report
    from sklearn import metrics

    def CL_kmeans(X_train, X_test, y_train, y_test,n,b=100):
        km_cluster = MiniBatchKMeans(n_clusters=n,batch_size=b)
        result = km_cluster.fit_predict(X_train)
        result2 = km_cluster.predict(X_test)

        count=0
        a=np.zeros(n)
        b=np.zeros(n)
        for v in range(0,n):
            for i in range(0,len(y_train)):
                if result[i]==v:
                    if y_train[i]==1:
                        a[v]=a[v]+1
                    else:
                        b[v]=b[v]+1
        list1=[]
        list2=[]
        for v in range(0,n):
            if a[v]<=b[v]:
                list1.append(v)
            else: 
                list2.append(v)
        for v in range(0,len(y_test)):
            if result2[v] in list1:
                result2[v]=0
            elif result2[v] in list2:
                result2[v]=1
            else:
                print("-1")
        print(classification_report(y_test, result2))
        cm=confusion_matrix(y_test,result2)
        acc=metrics.accuracy_score(y_test,result2)
        print(str(acc))
        print(cm)


    CL_kmeans(X_train, X_test, y_train, y_test, 8)

    #  ### Hyperparameter optimization of CL-k-means
    #  Tune "k"

    #Hyperparameter optimization by BO-GP
    from skopt.space import Real, Integer
    from skopt.utils import use_named_args
    from sklearn import metrics

    space  = [Integer(2, 50, name='n_clusters')]
    @use_named_args(space)
    def objective(**params):
        km_cluster = MiniBatchKMeans(batch_size=100, **params)
        n=params['n_clusters']
        
        result = km_cluster.fit_predict(X_train)
        result2 = km_cluster.predict(X_test)

        count=0
        a=np.zeros(n)
        b=np.zeros(n)
        for v in range(0,n):
            for i in range(0,len(y_train)):
                if result[i]==v:
                    if y_train[i]==1:
                        a[v]=a[v]+1
                    else:
                        b[v]=b[v]+1
        list1=[]
        list2=[]
        for v in range(0,n):
            if a[v]<=b[v]:
                list1.append(v)
            else: 
                list2.append(v)
        for v in range(0,len(y_test)):
            if result2[v] in list1:
                result2[v]=0
            elif result2[v] in list2:
                result2[v]=1
            else:
                print("-1")
        cm=metrics.accuracy_score(y_test,result2)
        print(str(n)+" "+str(cm))
        return (1-cm)
    from skopt import gp_minimize
    import time
    t1=time.time()
    res_gp = gp_minimize(objective, space, n_calls=20, random_state=0)
    t2=time.time()
    print(t2-t1)
    print("Best score=%.4f" % (1-res_gp.fun))
    print("""Best parameters: n_clusters=%d""" % (res_gp.x[0]))

    #Hyperparameter optimization by BO-TPE
    from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.cluster import MiniBatchKMeans
    from sklearn import metrics

    def objective(params):
        params = {
            'n_clusters': int(params['n_clusters']), 
        }
        km_cluster = MiniBatchKMeans(batch_size=100, **params)
        n=params['n_clusters']
        
        result = km_cluster.fit_predict(X_train)
        result2 = km_cluster.predict(X_test)

        count=0
        a=np.zeros(n)
        b=np.zeros(n)
        for v in range(0,n):
            for i in range(0,len(y_train)):
                if result[i]==v:
                    if y_train[i]==1:
                        a[v]=a[v]+1
                    else:
                        b[v]=b[v]+1
        list1=[]
        list2=[]
        for v in range(0,n):
            if a[v]<=b[v]:
                list1.append(v)
            else: 
                list2.append(v)
        for v in range(0,len(y_test)):
            if result2[v] in list1:
                result2[v]=0
            elif result2[v] in list2:
                result2[v]=1
            else:
                print("-1")
        score=metrics.accuracy_score(y_test,result2)
        print(str(params['n_clusters'])+" "+str(score))
        return {'loss':1-score, 'status': STATUS_OK }
    space = {
        'n_clusters': hp.quniform('n_clusters', 2, 50, 1),
    }

    best = fmin(fn=objective,
                space=space,
                algo=tpe.suggest,
                max_evals=20)
    print("Random Forest: Hyperopt estimated optimum {}".format(best))


    CL_kmeans(X_train, X_test, y_train, y_test, 16)


#  ### Apply the CL-k-means model with biased classifiers

# Only a sample code to show the logic. It needs to work on the entire dataset to generate sufficient training samples for biased classifiers
def Anomaly_IDS(X_train, X_test, y_train, y_test,n,b=100):
    # CL-kmeans
    km_cluster = MiniBatchKMeans(n_clusters=n,batch_size=b)
    result = km_cluster.fit_predict(X_train)
    result2 = km_cluster.predict(X_test)

    count=0
    a=np.zeros(n)
    b=np.zeros(n)
    for v in range(0,n):
        for i in range(0,len(y_train)):
            if result[i]==v:
                if y_train[i]==1:
                    a[v]=a[v]+1
                else:
                    b[v]=b[v]+1
    list1=[]
    list2=[]
    for v in range(0,n):
        if a[v]<=b[v]:
            list1.append(v)
        else: 
            list2.append(v)
    for v in range(0,len(y_test)):
        if result2[v] in list1:
            result2[v]=0
        elif result2[v] in list2:
            result2[v]=1
        else:
            print("-1")
    print(classification_report(y_test, result2))
    cm=confusion_matrix(y_test,result2)
    #y2 replaced with y_test
    acc=metrics.accuracy_score(y2,result2)
    print(str(acc))
    print(cm)
    
    #Biased classifier construction
    count=0
    print(len(y))
    a=np.zeros(n)
    b=np.zeros(n)
    FNL=[]
    FPL=[]
    for v in range(0,n):
        al=[]
        bl=[]
        for i in range(0,len(y)):   
            if result[i]==v:        
                if y[i]==1:        #label 1
                    a[v]=a[v]+1
                    al.append(i)
                else:             #label 0
                    b[v]=b[v]+1
                    bl.append(i)
        if a[v]<=b[v]:
            FNL.extend(al)
        else:
            FPL.extend(bl)
        #print(str(v)+"="+str(a[v]/(a[v]+b[v])))
        
    dffp=df.iloc[FPL, :]
    dffn=df.iloc[FNL, :]
    dfva0=df[df['Label']==0]
    dfva1=df[df['Label']==1]
    
    dffpp=dfva1.sample(n=None, frac=len(FPL)/dfva1.shape[0], replace=False, weights=None, random_state=None, axis=0)
    dffnp=dfva0.sample(n=None, frac=len(FNL)/dfva0.shape[0], replace=False, weights=None, random_state=None, axis=0)
    
    dffp_f=pd.concat([dffp, dffpp])
    dffn_f=pd.concat([dffn, dffnp])
    
    Xp = dffp_f.drop(['Label'],axis=1)  
    yp = dffp_f.iloc[:, -1].values.reshape(-1,1)
    yp=np.ravel(yp)

    Xn = dffn_f.drop(['Label'],axis=1)  
    yn = dffn_f.iloc[:, -1].values.reshape(-1,1)
    yn=np.ravel(yn)
    
    rfp = RandomForestClassifier(random_state = 0)
    rfp.fit(Xp,yp)
    rfn = RandomForestClassifier(random_state = 0)
    rfn.fit(Xn,yn)

    dffnn_f=pd.concat([dffn, dffnp])
    
    Xnn = dffn_f.drop(['Label'],axis=1)  
    ynn = dffn_f.iloc[:, -1].values.reshape(-1,1)
    ynn=np.ravel(ynn)

    rfnn = RandomForestClassifier(random_state = 0)
    rfnn.fit(Xnn,ynn)

    X2p = df2.drop(['Label'],axis=1) 
    y2p = df2.iloc[:, -1].values.reshape(-1,1)
    y2p=np.ravel(y2p)

    result2 = km_cluster.predict(X2p)

    count=0
    a=np.zeros(n)
    b=np.zeros(n)
    for v in range(0,n):
        for i in range(0,len(y)):
            if result[i]==v:
                if y[i]==1:
                    a[v]=a[v]+1
                else:
                    b[v]=b[v]+1
    list1=[]
    list2=[]
    l1=[]
    l0=[]
    for v in range(0,n):
        if a[v]<=b[v]:
            list1.append(v)
        else: 
            list2.append(v)
    for v in range(0,len(y2p)):
        if result2[v] in list1:
            result2[v]=0
            l0.append(v)
        elif result2[v] in list2:
            result2[v]=1
            l1.append(v)
        else:
            print("-1")
    print(classification_report(y2p, result2))
    cm=confusion_matrix(y2p,result2)
    print(cm)


# %% [markdown]
#  95% of the code has been shared, and the remaining 5% is retained for future extension.
#  Thank you for your interest and more details are in the paper.

def run_model(dataset_path, train_split, max_features, hpo_max_evals):
    X_train, X_test, y_train, y_test = preprocessing(dataset_path, train_split)
    acc, prec, recall, f1_score, cm = train_models(X_train, X_test, y_train, y_test, max_features, hpo_max_evals)
    end_time = time.time()
    run_model_time = end_time - start_time
    return (str(run_model_time), acc, prec, recall, f1_score, str(cm.tolist()))

#run_model()