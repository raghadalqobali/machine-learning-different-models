# -*- coding: utf-8 -*-
"""MachineLearningProject.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11ow__etgzWt3mhnT80tNjP8BZBZZGvGP

# Import Libraries
"""

import pydotplus
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from sklearn.tree import export_graphviz

from sklearn import tree
from xgboost import XGBClassifier
from sklearn.impute import KNNImputer
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.preprocessing import OrdinalEncoder, LabelEncoder, StandardScaler 
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, KFold
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, VotingClassifier, StackingClassifier

from sklearn.metrics import *   
from sklearn.metrics import confusion_matrix
from sklearn.metrics import r2_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import mean_squared_error

plt.rcParams['figure.figsize'] = [15,8]
from IPython.display import Image  

import warnings
warnings.filterwarnings('ignore')

"""# 1. Data pre-processing

### Exploratory Data Analysis
"""

data = pd.read_csv('churn.csv', index_col=0)
data

"""### Data Dimensions"""

print("There are",data.shape[0]," data points and ",data.shape[1]," features in the dataset")

"""### Data Types"""

data.dtypes

data.select_dtypes(include=[np.number]).head()

data.select_dtypes(include=['object']).head()

"""### Summary Statistics"""

data.describe(include=np.number)

data.describe(include='object')

data.head()

data.info()

"""# Data Distribution 
###### Data Distribution of Features
"""

data_cat = data.drop(['referral_id','last_visit_time','avg_frequency_login_days','security_no','joining_date'], axis=1).select_dtypes(include='object')
fig,ax= plt.subplots(nrows=4,ncols=3,figsize=(20, 25)) 
for variable, subplot in zip(data_cat.columns,ax.flatten()):
    z = sns.countplot(x = data_cat[variable],ax=subplot, ) 
    z.set_xlabel(variable, fontsize = 20)
    z.set_xticklabels(z.get_xticklabels(),rotation=45)
    for p in z.patches:
      z.annotate(format(p.get_height(), '.2f'), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center',
           xytext = (0, 6), textcoords = 'offset points')
    
plt.tight_layout()

"""### Data Distribution of Target"""

plt.rcParams['figure.figsize'] = [10,10] 
ax = sns.countplot(data['churn_risk_score'])
for p in ax.patches:
    ax.annotate(format(p.get_height(), '.2f'), (p.get_x() + p.get_width() / 2. , p.get_height()), ha = 'center',
           xytext = (0, 15), textcoords = 'offset points')
plt.show()

data_num=data.drop('churn_risk_score', axis=1).select_dtypes(include=[np.number]) 
fig,ax= plt.subplots(nrows=2,ncols=3,figsize=(20,10)) 
for variable, subplot in zip(data_num.columns,ax.flatten()):
    z = sns.kdeplot(x = data_num[variable] , ax=subplot) 
    z.set_xlabel(variable, fontsize = 10)

fig.delaxes(ax[1][2])
plt.show()

dfSample = data.sample(n=1000) 
xdataSample, ydataSample = dfSample["age"], dfSample["avg_time_spent"]

sns.regplot(x=xdataSample, y=ydataSample) 
plt.show()

"""### Missing values"""

#Standard Missing Values
missing_values = pd.DataFrame({
    'missing_values':data.isnull().sum(),
    'percentage':data.isnull().sum()*100/data.shape[0]
})

missing_values.sort_values(by='missing_values', ascending=False)

#Non-Standard Missing Values
data.joined_through_referral.value_counts()

# The feature joined_through_referral has unindentified '?' values which are replaced with Nan.
data['joined_through_referral'] = data['joined_through_referral'].replace('?',np.NaN)

data.gender.value_counts()

# The feature gender has unindentified 'Unknown' values which are replaced with Nan.
data['gender'] = data['gender'].replace('Unknown',np.NaN)

data.referral_id.unique()

#The feature referral_id has unindentified 'xxxxxxxx' values which are replaced with Nan.
data['referral_id'] = data['referral_id'].replace('xxxxxxxx',np.NaN)

data.medium_of_operation.value_counts()

#The feature medium_of_operation has unindentified '?' values which are replaced with Nan.
data['medium_of_operation'] = data['medium_of_operation'].replace('?',np.NaN)

data.days_since_last_login.value_counts()

#The feature days_since_last_login has unindentified '-999' values which are replaced with Nan.
data['days_since_last_login'] = data['days_since_last_login'].replace(-999,np.NaN)

len(data[data.avg_time_spent < 0]['avg_time_spent'])

#The feature avg_time_spent has negative values which are replaced with Nan
data['avg_time_spent']=data['avg_time_spent'].apply(lambda x:x if x>=0 else np.nan)

len(data[data.points_in_wallet < 0]['points_in_wallet'])

#The feature points_in_wallet has negative values which are replaced with Nan
data['points_in_wallet']=data['points_in_wallet'].apply(lambda x:x if x>=0 else np.nan)

#The feature avg_frequency_login_days has negative values as well as unidentified 'Error' values which are replaced with Nan
data['avg_frequency_login_days']=data['avg_frequency_login_days'].apply(lambda x:x if x!='Error' else -1)
data['avg_frequency_login_days']=data['avg_frequency_login_days'].astype('float')
data['avg_frequency_login_days']=data['avg_frequency_login_days'].apply(lambda x:x if x>=0 else np.nan)

missing_values = pd.DataFrame({
    'missing_values':data.isnull().sum(),
    'percentage':data.isnull().sum()*100/data.shape[0]
})

missing_values.sort_values(by='missing_values', ascending=False)

#There are 10 features that has missing values.
plt.figure(figsize=(20,10))
sns.heatmap(data.isnull(), cbar=False)
plt.show()

#Missing values imputation
df_num = data.select_dtypes(include=np.number)
df_cat = data.select_dtypes(include='object')

#Missing values treatment for categorical variable
Missing_cat = data[['gender','preferred_offer_types','region_category','joined_through_referral','medium_of_operation']]
for i,col in enumerate(Missing_cat):
    data[col].fillna(data[col].mode()[0], inplace=True)

#Missing values treatment for numerical variable
Missing_num = data[['points_in_wallet','avg_time_spent','days_since_last_login','avg_frequency_login_days']]

imputer = KNNImputer(n_neighbors=3)
imputed_value=imputer.fit_transform(Missing_num)

d1 = pd.DataFrame({
    'avg_frequency_login_days':imputed_value.T[0],
    'points_in_wallet':imputed_value.T[1],
    'days_since_last_login':imputed_value.T[2],
    'avg_time_spent':imputed_value.T[3]

})

data.drop(['avg_frequency_login_days','points_in_wallet','days_since_last_login','avg_time_spent'], axis=1, inplace=True)

data = pd.concat([data, d1], axis=1)

#Duplicate Data
data[data.duplicated()]

#Feature Engineering
data['year']=data.joining_date.apply(lambda x:2021-int(x.split('-')[0]))
data.drop(['security_no','joining_date','referral_id','last_visit_time'], axis=1, inplace=True)

#Outliers (Discovery of Outliers)
df_num=data.select_dtypes(include=[np.number])

Q1 = data.quantile(0.25) 
Q3 = data.quantile(0.75) 
IQR = Q3 - Q1 

outlier = pd.DataFrame((df_num < (Q1 - 1.5 * IQR)) | (df_num > (Q3 + 1.5 * IQR)))
for i in outlier.columns:
    print('Total number of Outliers in column',i," are" ,len(outlier[outlier[i] == True][i]))

#Removal of Outliers
data_iqr = data[~((data < (Q1 - 1.5 * IQR)) |(data > (Q3 + 1.5 * IQR))).any(axis=1)] 

data_iqr.reset_index(inplace=True)

data_iqr.drop('index',axis=1, inplace=True)

df_cat = data_iqr[['gender','region_category','joined_through_referral','preferred_offer_types','medium_of_operation','internet_option','used_special_discount','offer_application_preference','past_complaint']]
df_num = data_iqr.select_dtypes(include=np.number)

#Categorical Data Encoding
orderencoding_membership_category = OrdinalEncoder(categories = [["No Membership", "Basic Membership", "Silver Membership", "Gold Membership","Platinum Membership","Premium Membership"]])
data_iqr['membership_category'] = orderencoding_membership_category.fit_transform(data_iqr['membership_category'].values.reshape(-1,1))

orderencoding_complaint_status = OrdinalEncoder(categories = [["No Information Available", "Not Applicable", "Unsolved","Solved","Solved in Follow-up"]])
data_iqr['complaint_status'] = orderencoding_complaint_status.fit_transform(data_iqr['complaint_status'].values.reshape(-1,1)) 

labelencoder_feedback = LabelEncoder() 
data_iqr['feedback'] = labelencoder_feedback.fit_transform(data_iqr.feedback)

df_categorical = pd.get_dummies(df_cat, drop_first=True)
df_final = pd.concat([df_categorical,df_num,data_iqr['membership_category'],data_iqr['complaint_status'],data_iqr['feedback']], axis=1)

#Feature Scaling
col = df_final[['age','days_since_last_login','avg_time_spent','avg_transaction_value','avg_frequency_login_days','points_in_wallet']]
df_final.drop(['age','days_since_last_login','avg_time_spent','avg_transaction_value','avg_frequency_login_days','points_in_wallet'], axis=1, inplace=True)

standard_scale = StandardScaler() 
col1 = standard_scale.fit_transform(col) 
df_scaled = pd.DataFrame(col1, columns=col.columns)

df_scaled.head()

data_final = pd.concat([df_final,df_scaled], axis=1 )

# Model Evaluation (Feature Selection using Random Forest)
Features = data_final.drop(['churn_risk_score'] ,axis = 1)
Target = data_final['churn_risk_score']

X_train1, X_test1, y_train1, y_test1 = train_test_split(Features, Target, test_size=0.20, random_state=42)
print(X_train1.shape, X_test1.shape, y_train1.shape, y_test1.shape)

model =  RandomForestClassifier(random_state = 0)
model.fit(X_train1, y_train1)

important_features = pd.DataFrame({'Features': X_train1.columns, 
                                   'Importance': model.feature_importances_})

important_features = important_features.sort_values('Importance', ascending = False)

sns.barplot(x = 'Importance', y = 'Features', data = important_features)

plt.title('Feature Importance', fontsize = 15)
plt.xlabel('Importance', fontsize = 15)
plt.ylabel('Features', fontsize = 15)

plt.show()

#Important features are identified using Random Forest and dropping inconsistent features.
X = Features.drop(['region_category_Village',
                       'offer_application_preference_Yes',
                       'used_special_discount_Yes',
                       'preferred_offer_types_Gift Vouchers/Coupons',
                       'past_complaint_Yes',
                       'preferred_offer_types_Without Offers',
                       'medium_of_operation_Smartphone',
                       'medium_of_operation_Desktop',
                       'internet_option_Wi-Fi',
                       'internet_option_Mobile_Data',
                       'joined_through_referral_Yes',
                       'region_category_Town',
                      ], axis =1)
y = Target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
print(X_train1.shape, X_test1.shape, y_train1.shape, y_test1.shape)

"""# 2. Building Machine Learning Models

### Hyperparameter Tuning (Best hyperparameters are identified using Grid Search CV)
"""

def gridsearch(model , param):
    gscv = GridSearchCV(estimator = model, 
                         param_grid = param, 
                         scoring='accuracy',
                         cv = 5,
                         n_jobs = -1)
    gscv.fit(X_train , y_train)
    result = gscv.best_params_
    return result

knn_gs = KNeighborsClassifier()
knn_params ={'n_neighbors':[3,5,7,9,11]}
r2 = gridsearch(knn_gs , knn_params)
print("Best parameters for KNN:",r2)

rf_gs = RandomForestClassifier(random_state = 0)
rf_params = {
  'n_estimators':[200,300],
 'criterion': ( 'gini','entropy'),
 'max_depth': [2, 3 ,4],
 'min_samples_split': [2, 9],
 'max_features': ("sqrt", "log2") }
r3 = gridsearch(rf_gs , rf_params)
print("Best parameters for Random Forest:",r3)

ab_gs = AdaBoostClassifier(random_state = 0)
ab_params ={
            'n_estimators':[10,250,1000],
             'learning_rate':[0.01,0.1]
            }
r4 = gridsearch(ab_gs , ab_params)
print("Best parameters for AdaBoost :",r4)

xgb_gs =  XGBClassifier(random_state = 0, verbosity = 0)
xgb_params =  {'n_estimators':[100,300],
              'learning_rate':[0.1,0.2]} 
r5 = gridsearch(xgb_gs , xgb_params)
print("Best parameters for XGBoost :",r5)

"""# Models Evaluation"""

#Kfold Cross Validation
def kfcv(model , x , y):
    accuracies = cross_val_score(estimator = model, X = x, y = y, cv = 10, n_jobs = -1) 
    return accuracies #Accuracies for all base models

lr_kf  = LogisticRegression(random_state=0, penalty = 'l2')
knn_kf = KNeighborsClassifier(n_neighbors= 11)
nb_kf  = GaussianNB()
rf_kf  = RandomForestClassifier(max_depth=3, random_state=0 , criterion= 'gini'
                                , max_features='sqrt' , min_samples_split= 2 , n_estimators= 300)
ab_kf  = AdaBoostClassifier(n_estimators=250, learning_rate = 0.01, random_state=0)
xgb_kf = XGBClassifier(random_state= 0 , learning_rate= 0.1 , n_estimators= 100)

accuracies = kfcv(lr_kf , X , y)
print(f'Logistic Regression: \n Mean Accuracy {accuracies.mean()}\n Minimum Accuracy{accuracies.min()} \n Maximum Accuracy {accuracies.max()} \n Accuracies: {accuracies}')

accuracies1 = kfcv(nb_kf , X , y)
print(f'Naive Bayes : \n Mean Accuracy {accuracies1.mean()}\n Minimum Accuracy {accuracies1.min()} \n Maximum Accuracy {accuracies1.max()} \n Accuracies: {accuracies1}')

accuracies2 = kfcv(knn_kf , X , y) 
print(f'KNN: \n Mean Accuracy {accuracies2.mean()} \n Minimum Accuracy {accuracies2.min()} \n Maximum Accuracy {accuracies2.max()} \n Accuracies: {accuracies2}')

accuracies3 = kfcv(rf_kf , X , y)
print(f'Random Forest: \n Mean Accuracy {accuracies3.mean()} \n Minimum Accuracy {accuracies3.min()} \n Maximum Accuracy {accuracies3.max()}\n Accuracies: {accuracies3}')

accuracies4 = kfcv(ab_kf , X , y) 
print(f'AdaBoost: \n Mean Accuracy {accuracies4.mean()} \n Minimum Accuracy {accuracies4.min()}\n Maximum Accuracy {accuracies4.max()} \n Accuracies: {accuracies4}')

accuracies5 = kfcv(xgb_kf , X , y)
print(f'XGBoost: \n Mean Accuracy {accuracies5.mean()}\n Minimum Accuracy{accuracies5.min()} \n Maximum Accuracy {accuracies5.max()} \n Accuracies: {accuracies5}')

"""# Defining Functions
##### Helper Functions
"""

plt.rcParams['figure.figsize'] = [9,8]

"""#### Confusion Matrix"""

def confusion_matrix_plot(model):
    ypred = model.predict(X_test)
    cm = confusion_matrix(y_test, ypred)
    cm = np.rot90(cm , 2)
    conf_matrix = pd.DataFrame(data = cm,columns = ['Predicted:1','Predicted:0'], index = ['Actual:1','Actual:0'])
    sns.heatmap(conf_matrix, annot = True, fmt = 'd', cbar = False, 
                linewidths = 0.1, annot_kws = {'size':20})
    plt.xticks(fontsize = 20)
    plt.yticks(fontsize = 20)
    plt.show()

"""##### Classification Report"""

def creport(model):
    ypred = model.predict(X_test)
    cr = classification_report(y_test, ypred)
    return cr

"""# Evaluation matrices: for classification

######  Accuracy
"""

def accuracy(y_test , ypred):
    auc = accuracy_score(y_test , ypred)
    return auc

"""##### F1 Score"""

def f1(y_test , ypred):
    f = f1_score(y_test, ypred, average='macro')
    return f

"""##### Recall"""

def recall(y_test , ypred):
    re=recall_score(y_test , ypred)
    return re

"""###### Precision"""

def precision(y_test , ypred):
    pr=precision_score(y_test, y_pred)
    return pr

"""# Evaluation matrices: For regression

######  Mean Squared Error (MSE)
"""

def MSE(y_test , y_pred):
    return mean_squared_error(y_test, y_pred)

"""###### R-Squared"""

def R_Squared(y_test , ypred):
    r2=r2_score(y_test , ypred)
    return r2

"""#  Model Building 
##### Logistic Regression 
"""

logistic_model = LogisticRegression(random_state=0, penalty = 'l2')
logistic_model.fit(X_train,y_train)

confusion_matrix_plot(logistic_model)

print(creport(logistic_model))

"""##### Linear regression"""

linear_model = LinearRegression()
linear_model.fit(X_train,y_train)
ypred=linear_model.predict(X_test)

linear_model.coef_

linear_model.intercept_

print(mean_squared_error(y_test , ypred))

R_Squared(y_test , ypred)

"""###### Naive Bayes """

gnb = GaussianNB()
gnb.fit(X_train,y_train)

confusion_matrix_plot(gnb)

print(creport(gnb))

"""#####  K nearest neighbors (KNN) """

knn = KNeighborsClassifier(n_neighbors= 11)
knn.fit(X_train, y_train)

confusion_matrix_plot(knn)

print(creport(knn))

"""###### Random Forest"""

rf = RandomForestClassifier(max_depth=3, random_state=0 , criterion= 'gini' , max_features='sqrt' , min_samples_split= 2 , n_estimators= 300)
rf.fit(X_train , y_train)

confusion_matrix_plot(rf)

print(creport(rf))

clf=tree.DecisionTreeClassifier(max_depth=2)
clf=clf.fit(X_train,y_train)
pred=clf.predict(X_test)
tree.plot_tree(clf)

"""###### AdaBoost"""

ab = AdaBoostClassifier(n_estimators=250, learning_rate = 0.01, random_state=0)
ab.fit(X_train , y_train)

confusion_matrix_plot(ab)

print(creport(ab))

"""######  XGBoost"""

xgb = XGBClassifier(random_state= 0 , learning_rate= 0.2, n_estimators= 100, verbosity = 0)
xgb.fit(X_train , y_train)

confusion_matrix_plot(xgb)

print(creport(xgb))

# Training Set Predictions
y_predtr = logistic_model.predict(X_train)
y_pred1tr = gnb.predict(X_train)
y_pred2tr = knn.predict(X_train)
y_pred3tr = rf.predict(X_train)
y_pred4tr = ab.predict(X_train)
y_pred5tr = xgb.predict(X_train)

#Test Set Predictions
y_pred = logistic_model.predict(X_test)
y_pred1 = gnb.predict(X_test)
y_pred2 = knn.predict(X_test)
y_pred3 = rf.predict(X_test)
y_pred4 = ab.predict(X_test)
y_pred5 = xgb.predict(X_test)

print(precision(y_test,y_pred6))

# Comparison of Different Models per Performance Metrics

comp = pd.DataFrame({'Model':['Logistic Regression','Naive Bayes','KNN','Random Forest','AdaBoost','XGBoost'],
                    'Train Accuracy':[accuracy(y_train,y_predtr), accuracy(y_train,y_pred1tr), accuracy(y_train,y_pred2tr), accuracy(y_train,y_pred3tr),
                                      accuracy(y_train,y_pred4tr), accuracy(y_train,y_pred5tr)],
                    'Test Accuracy':[accuracy(y_test,y_pred), accuracy(y_test,y_pred1), accuracy(y_test,y_pred2), accuracy(y_test,y_pred3),
                                      accuracy(y_test,y_pred4), accuracy(y_test,y_pred5)],
                    'Test f1-Score':[f1(y_test,y_pred), f1(y_test,y_pred1), f1(y_test,y_pred2), f1(y_test,y_pred3),
                                      f1(y_test,y_pred4), f1(y_test,y_pred5)],
                    'Test precision':[precision(y_test,y_pred), precision(y_test,y_pred1), precision(y_test,y_pred2), precision(y_test,y_pred3),
                                      precision(y_test,y_pred4), precision(y_test,y_pred5)],
                    'Test recall':[recall(y_test,y_pred), recall(y_test,y_pred1), recall(y_test,y_pred2), recall(y_test,y_pred3),
                                      recall(y_test,y_pred4), recall(y_test,y_pred5)]}
                    )

print(comp)

names = ['Logistic Regression','Naive Bayes','KNN','Random Forest','AdaBoost','XGBoost']
values = [f1(y_test,y_pred), f1(y_test,y_pred1), f1(y_test,y_pred2), f1(y_test,y_pred3), f1(y_test,y_pred4), f1(y_test,y_pred5)]

plt.figure(figsize=(30, 3))

plt.subplot(131)
plt.bar(names, values)
plt.subplot(132)
plt.scatter(names, values)
plt.subplot(133)
plt.plot(names, values)
plt.suptitle('Comparison of Different Models')
plt.show()

"""# Model Ensembling"""

#Voting Classifier 
clf1 = KNeighborsClassifier(n_neighbors= 11)
clf2 = RandomForestClassifier(max_depth=4, random_state=0 , criterion= 'entropy' , max_features='sqrt' , min_samples_split= 2 , n_estimators= 300)
clf3 = AdaBoostClassifier(n_estimators=250, learning_rate = 0.01,random_state=0)
vclf = VotingClassifier(estimators=[('KNN', clf1), ('Random_Forest', clf2), ('AdaBoost' , clf3)],
                                   voting='soft')

# Stacking Classifier
estimators = [('Voting Classifier' , vclf),
              ('XGBoost', XGBClassifier(random_state= 0 , learning_rate= 0.2 , n_estimators= 100, verbosity = 0) )]

stackclf = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression(random_state= 0))

stackclf.fit(X_train ,y_train)

confusion_matrix_plot(stackclf)

y_pred6tr = stackclf.predict(X_train)
y_pred6 = stackclf.predict(X_test)

"""# Use Voting Classifier to improve the performance of our ML models"""

comp1 = pd.DataFrame({'Model':['Final Model'],
                      'Train Accuracy':[accuracy(y_train,y_pred6tr)],
                      'Test Accuracy':[accuracy(y_test,y_pred6)],
                      'Test f1-Score':[f1(y_test , y_pred6)],
                      'Test recall':[recall(y_test , y_pred6)],
                      'Test precision':[precision(y_test , y_pred6)]})
final_comp = pd.concat([comp, comp1], axis = 0)

final_comp.reset_index(drop=True, inplace=True)

final_comp.style.highlight_max(color = 'lightblue', subset = 'Test Accuracy')