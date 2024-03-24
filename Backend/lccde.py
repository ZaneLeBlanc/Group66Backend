# %% [markdown]
# # LCCDE: A Decision-Based Ensemble Framework for Intrusion Detection in The Internet of Vehicles
# This is the code for the paper entitled "**LCCDE: A Decision-Based Ensemble Framework for Intrusion Detection in The Internet of Vehicles**" accepted in 2022 IEEE Global Communications Conference (GLOBECOM).  
# Authors: Li Yang (lyang339@uwo.ca), Abdallah Shami (Abdallah.Shami@uwo.ca), Gary Stevens, and Stephen de Rusett  
# Organization: The Optimized Computing and Communications (OC2) Lab, ECE Department, Western University, Ontario, Canada; S2E Technologies, St. Jacobs, Ontario, Canada  
# 
# If you find this repository useful in your research, please cite:  
# L. Yang, A. Shami, G. Stevens, and S. DeRusett, “LCCDE: A Decision-Based Ensemble Framework for Intrusion Detection in The Internet of Vehicles," in 2022 IEEE Global Communications Conference (GLOBECOM), 2022, pp. 1-6.

# %% [markdown]
# ## Import libraries

# %%
import warnings
warnings.filterwarnings("ignore")

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score, precision_score, recall_score, f1_score
import lightgbm as lgb
import catboost as cbt
import xgboost as xgb
import time
from river import stream
from statistics import mode

# %% [markdown]
# ## Read the sampled CICIDS2017 dataset
# The CICIDS2017 dataset is publicly available at: https://www.unb.ca/cic/datasets/ids-2017.html  
# Due to the large size of this dataset, the sampled subsets of CICIDS2017 is used. The subsets are in the "data" folder.  
# If you want to use this code on other datasets (e.g., CAN-intrusion dataset), just change the dataset name and follow the same steps. The models in this code are generic models that can be used in any intrusion detection/network traffic datasets.

# %%
df = pd.read_csv("./Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km.csv")

# %%
df.Label.value_counts()

# %% [markdown]
# **Corresponding Attack Types:**  
# 0 BENIGN &emsp; 18225  
# 3 DoS        &emsp;   &emsp;   3042  
# 6 WebAttack    &emsp;      2180  
# 1 Bot        &emsp;  &emsp;      1966    
# 5 PortScan  &emsp;       1255  
# 2 BruteForce  &emsp;      96  
# 4 Infiltration  &emsp;       36  

# %% [markdown]
# ## Split train set and test set

# %%
X = df.drop(['Label'],axis=1)
y = df['Label']
X_train, X_test, y_train, y_test = train_test_split(X,y, train_size = 0.8, test_size = 0.2, random_state = 0) #shuffle=False

# %% [markdown]
# ## SMOTE to solve class-imbalance

# %%
pd.Series(y_train).value_counts()

# %%
from imblearn.over_sampling import SMOTE
smote=SMOTE(n_jobs=-1,sampling_strategy={2:1000,4:1000})

# %%
X_train, y_train = smote.fit_resample(X_train, y_train)

# %%
pd.Series(y_train).value_counts()

# %% [markdown]
# ## Machine Learning (ML) model training
# ### Training three base learners: LightGBM, XGBoost, CatBoost

# %%
# %%time
start_time = time.time()
# Train the LightGBM algorithm
start_time = time.time()
import lightgbm as lgb
lg = lgb.LGBMClassifier()
lg.fit(X_train, y_train)
y_pred = lg.predict(X_test)
print(classification_report(y_test,y_pred))
print("Accuracy of LightGBM: "+ str(accuracy_score(y_test, y_pred)))
print("Precision of LightGBM: "+ str(precision_score(y_test, y_pred, average='weighted')))
print("Recall of LightGBM: "+ str(recall_score(y_test, y_pred, average='weighted')))
print("Average F1 of LightGBM: "+ str(f1_score(y_test, y_pred, average='weighted')))
print("F1 of LightGBM for each type of attack: "+ str(f1_score(y_test, y_pred, average=None)))
lg_f1=f1_score(y_test, y_pred, average=None)

# Plot the confusion matrix
cm=confusion_matrix(y_test,y_pred)
f,ax=plt.subplots(figsize=(5,5))
sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
plt.xlabel("y_pred")
plt.ylabel("y_true")
#plt.show() #dont need rn

# %%
# %%time
# Train the XGBoost algorithm
import xgboost as xgb
xg = xgb.XGBClassifier()

X_train_x = X_train.values
X_test_x = X_test.values

xg.fit(X_train_x, y_train)

y_pred = xg.predict(X_test_x)
print(classification_report(y_test,y_pred))
print("Accuracy of XGBoost: "+ str(accuracy_score(y_test, y_pred)))
print("Precision of XGBoost: "+ str(precision_score(y_test, y_pred, average='weighted')))
print("Recall of XGBoost: "+ str(recall_score(y_test, y_pred, average='weighted')))
print("Average F1 of XGBoost: "+ str(f1_score(y_test, y_pred, average='weighted')))
print("F1 of XGBoost for each type of attack: "+ str(f1_score(y_test, y_pred, average=None)))
xg_f1=f1_score(y_test, y_pred, average=None)

# Plot the confusion matrix
cm=confusion_matrix(y_test,y_pred)
f,ax=plt.subplots(figsize=(5,5))
sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
plt.xlabel("y_pred")
plt.ylabel("y_true")
#plt.show() #dont need rn

# %%
# %%time
# Train the CatBoost algorithm
import catboost as cbt
cb = cbt.CatBoostClassifier(verbose=0,boosting_type='Plain')
#cb = cbt.CatBoostClassifier()

cb.fit(X_train, y_train)
y_pred = cb.predict(X_test)
print(classification_report(y_test,y_pred))
print("Accuracy of CatBoost: "+ str(accuracy_score(y_test, y_pred)))
print("Precision of CatBoost: "+ str(precision_score(y_test, y_pred, average='weighted')))
print("Recall of CatBoost: "+ str(recall_score(y_test, y_pred, average='weighted')))
print("Average F1 of CatBoost: "+ str(f1_score(y_test, y_pred, average='weighted')))
print("F1 of CatBoost for each type of attack: "+ str(f1_score(y_test, y_pred, average=None)))
cb_f1=f1_score(y_test, y_pred, average=None)

# Plot the confusion matrix
cm=confusion_matrix(y_test,y_pred)
f,ax=plt.subplots(figsize=(5,5))
sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="red",fmt=".0f",ax=ax)
plt.xlabel("y_pred")
plt.ylabel("y_true")
#plt.show() #dont need rn

# %% [markdown]
# ## Proposed ensemble model: Leader Class and Confidence Decision Ensemble (LCCDE)

# %% [markdown]
# LCCDE aims to achieve optimal model performance by identifying the best-performing base ML model with the highest prediction confidence for each class. 

# %% [markdown]
# ### Find the best-performing (leading) model for each type of attack among the three ML models

# %%
# Leading model list for each class
model=[]
for i in range(len(lg_f1)):
    if max(lg_f1[i],xg_f1[i],cb_f1[i]) == lg_f1[i]:
        model.append(lg)
    elif max(lg_f1[i],xg_f1[i],cb_f1[i]) == xg_f1[i]:
        model.append(xg)
    else:
        model.append(cb)

# %%
model

# %% [markdown]
# **Leading Model for Each Type of Attack:**  
# 0 BENIGN: &emsp; XGBClassifier  
# 1 Bot:        &emsp;  &emsp;      XGBClassifier   
# 2 BruteForce:  &emsp;      LGBMClassifier  
# 3 DoS:        &emsp;   &emsp;   XGBClassifier  
# 4 Infiltration:  &emsp;       LGBMClassifier  
# 5 PortScan:  &emsp;       LGBMClassifier  
# 6 WebAttack:    &emsp;      XGBClassifier  

# %% [markdown]
# ## LCCDE Prediction

# %%
def LCCDE(X_test, y_test, m1, m2, m3):
    i = 0
    t = []
    m = []
    yt = []
    yp = []
    l = []
    pred_l = []
    pro_l = []

    # For each class (normal or a type of attack), find the leader model
    for xi, yi in stream.iter_pandas(X_test, y_test):

        xi2=np.array(list(xi.values()))
        y_pred1 = m1.predict(xi2.reshape(1, -1))      # model 1 (LightGBM) makes a prediction on text sample xi
        y_pred1 = int(y_pred1[0])
        y_pred2 = m2.predict(xi2.reshape(1, -1))      # model 2 (XGBoost) makes a prediction on text sample xi
        y_pred2 = int(y_pred2[0])
        y_pred3 = m3.predict(xi2.reshape(1, -1))      # model 3 (Catboost) makes a prediction on text sample xi
        y_pred3 = int(y_pred3[0])

        p1 = m1.predict_proba(xi2.reshape(1, -1))     # The prediction probability (confidence) list of model 1 
        p2 = m2.predict_proba(xi2.reshape(1, -1))     # The prediction probability (confidence) list of model 2  
        p3 = m3.predict_proba(xi2.reshape(1, -1))     # The prediction probability (confidence) list of model 3  

        # Find the highest prediction probability among all classes for each ML model
        y_pred_p1 = np.max(p1)
        y_pred_p2 = np.max(p2)
        y_pred_p3 = np.max(p3)

        if y_pred1 == y_pred2 == y_pred3: # If the predicted classes of all the three models are the same
            y_pred = y_pred1 # Use this predicted class as the final predicted class

        elif y_pred1 != y_pred2 != y_pred3: # If the predicted classes of all the three models are different
            # For each prediction model, check if the predicted class’s original ML model is the same as its leader model
            if model[y_pred1]==m1: # If they are the same and the leading model is model 1 (LightGBM)
                l.append(m1)
                pred_l.append(y_pred1) # Save the predicted class
                pro_l.append(y_pred_p1) # Save the confidence

            if model[y_pred2]==m2: # If they are the same and the leading model is model 2 (XGBoost)
                l.append(m2)
                pred_l.append(y_pred2)
                pro_l.append(y_pred_p2)

            if model[y_pred3]==m3: # If they are the same and the leading model is model 3 (CatBoost)
                l.append(m3)
                pred_l.append(y_pred3)
                pro_l.append(y_pred_p3)

            if len(l)==0: # Avoid empty probability list
                pro_l=[y_pred_p1,y_pred_p2,y_pred_p3]

            elif len(l)==1: # If only one pair of the original model and the leader model for each predicted class is the same
                y_pred=pred_l[0] # Use the predicted class of the leader model as the final prediction class

            else: # If no pair or multiple pairs of the original prediction model and the leader model for each predicted class are the same
                max_p = max(pro_l) # Find the highest confidence
                
                # Use the predicted class with the highest confidence as the final prediction class
                if max_p == y_pred_p1:
                    y_pred = y_pred1
                elif max_p == y_pred_p2:
                    y_pred = y_pred2
                else:
                    y_pred = y_pred3  
        
        else: # If two predicted classes are the same and the other one is different
            n = mode([y_pred1,y_pred2,y_pred3]) # Find the predicted class with the majority vote
            y_pred = model[n].predict(xi2.reshape(1, -1)) # Use the predicted class of the leader model as the final prediction class
            y_pred = int(y_pred[0]) 

        yt.append(yi)
        yp.append(y_pred) # Save the predicted classes for all tested samples
    return yt, yp

# %%
# %%time
# Implementing LCCDE
def run_model():
    yt, yp = LCCDE(X_test, y_test, m1 = lg, m2 = xg, m3 = cb)
    end_time = time.time()
    run_model_time = end_time - start_time
    # %%
    # The performance of the proposed lCCDE model
    print("Accuracy of LCCDE: "+ str(accuracy_score(yt, yp)))
    print("Precision of LCCDE: "+ str(precision_score(yt, yp, average='weighted')))
    print("Recall of LCCDE: "+ str(recall_score(yt, yp, average='weighted')))
    print("Average F1 of LCCDE: "+ str(f1_score(yt, yp, average='weighted')))
    print("F1 of LCCDE for each type of attack: "+ str(f1_score(yt, yp, average=None)))

    # %%
    # Comparison: The F1-scores for each base model
    print("F1 of LightGBM for each type of attack: "+ str(lg_f1))
    print("F1 of XGBoost for each type of attack: "+ str(xg_f1))
    print("F1 of CatBoost for each type of attack: "+ str(cb_f1))

    #format time, accuracy, prec, recall, f1
    return (str(run_model_time), str(accuracy_score(yt, yp)), str(precision_score(yt, yp, average='weighted')), str(recall_score(yt, yp, average='weighted')), str(f1_score(yt, yp, average='weighted')))

# %% [markdown]
# **Conclusion**: The performance (F1-score) of the proposed LCCDE ensemble model on each type of attack detection is higher than any base ML model.

# %%


