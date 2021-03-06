# -*- coding: utf-8 -*-
"""stats202.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14LFMBAKRp-rTOoqp93lIi69wqKMMJwGs
"""

import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

"""# Data preprocessing

"""

#load all studies
files = ['Study_A.csv','Study_B.csv','Study_C.csv','Study_D.csv','Study_E.csv']
trials = []
for file in files:
    trials.append(pd.read_csv(file))
train_data= pd.concat(trials, sort = False)

#Factorize the TxGroup (make control/Treatment to 0/1)
train_data['TxGroup'] = pd.factorize(train_data.TxGroup)[0]

#sort the data by patient and visits
train_data = train_data.sort_values(['PatientID', 'VisitDay'], ascending=[True, True]).reset_index().drop(['index'],axis=1)

#Get sum of Ps,Ns,Gs
#get sum of Ps,Ns,Gs
Ps=['P1', 'P2', 'P3', 'P4', 'P5','P6', 'P7']
Gs=['G1','G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12', 'G13', 'G14', 'G15','G16']
Ns=['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7']
train_data['Ps'] = train_data[Ps].sum(axis=1)
train_data['Gs'] = train_data[Gs].sum(axis=1)
train_data['Ns'] = train_data[Ns].sum(axis=1)

#diff of PANSS_Total
train_data['PANSS_Total_diff_1'] = train_data.groupby('PatientID')['PANSS_Total'].diff()
#(diff() function: first discrete difference of objects over the given axis)

#@title Visualize the Data : Are there missing/unexpected feature values? What kind of variables we have?
from facets_overview.generic_feature_statistics_generator import GenericFeatureStatisticsGenerator
import base64

gfsg = GenericFeatureStatisticsGenerator()
proto = gfsg.ProtoFromDataFrames([{'name': 'train', 'table': train_data}])
protostr = base64.b64encode(proto.SerializeToString()).decode("utf-8")


from IPython.core.display import display, HTML

HTML_TEMPLATE = """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/webcomponentsjs/1.3.3/webcomponents-lite.js"></script>
        <link rel="import" href="https://raw.githubusercontent.com/PAIR-code/facets/1.0.0/facets-dist/facets-jupyter.html" >
        <facets-overview id="elem"></facets-overview>
        <script>
          document.querySelector("#elem").protoInput = "{protostr}";
        </script>"""
html = HTML_TEMPLATE.format(protostr=protostr)
display(HTML(html))



"""1. We can see from reviewing the "missing" column that the following features contain missing value:

*   VisitDay
*   LeadStatus

2. Country label has some errors - need to fix it

3. Study C patient number is higher than other studies
"""

#@title Visualize the Data
# Display the Dive visualization.
from IPython.core.display import display, HTML

jsonstr = train_data.to_json(orient='records')
HTML_TEMPLATE = """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/webcomponentsjs/1.3.3/webcomponents-lite.js"></script>
        <link rel="import" href="https://raw.githubusercontent.com/PAIR-code/facets/1.0.0/facets-dist/facets-jupyter.html">
        <facets-dive id="elem" height="600"></facets-dive>
        <script>
          var data = {jsonstr};
          document.querySelector("#elem").data = data;
        </script>"""
html = HTML_TEMPLATE.format(jsonstr=jsonstr)
display(HTML(html))

"""1. In the **Binning | X-Axis** menu, select **PANSS_Total**, and in the **Color By** and  **Label By** menus, select **Country**. 

We oberved there are "other" country label --> need to know what's wrong with that data.

In higher PANSS_total (>100), argintina become the major group.  This indicates that we may have country bias on the disease score.

2. In the **Binning | X-Axis** menu, select **PANSS_Total**, and in the **Color By** and  **Label By** menus, select **Study**.

In higher PANSS_total (>100), argintina is studyA is the major group.

3. In the **Binning | X-Axis** menu, select **PANSS_Total**, and in the **Color By** and  **Label By** menus, select **LeadStatus**.

We have missing leadstatus when PANS
"""

#Original analysis

# Does the control/treament will affect the disease socre over time?

#formaula: PANSS = 

formula = "PANSS_Total_diff_1 ~ VisitDay + TxGroup + TxGroup:VisitDay"
olsModel = smf.ols(formula,data=train_data).fit()
print(olsModel.summary())

qq = sm.qqplot(olsModel.resid, line = 'r')

stdres = pd.DataFrame(olsModel.resid_pearson)
plt.plot(stdres, 'o', ls = 'None')
l = plt.axhline(y=0, color = 'r')

"""# Does different country will affect the PANSS score overtime?

# Does differemt trial (different patient population) will affect the PANSS score overtime?
"""

train_data['Study'] = pd.Categorical(train_data['Study'])

formula = "PANSS_Total_diff_1 ~ VisitDay + Study + Study*VisitDay"
olsModel = smf.ols(formula,data=train_data).fit()
print(olsModel.summary())

train_data = train_data.copy()
train_data_onehot = pd.get_dummies(train_data, columns=['Study'], prefix = ['carrier'])
train_data_onehot_txgroup0 = train_data_onehot[train_data_onehot['TxGroup'] == 0]
train_data_onehot_txgroup1 = train_data_onehot[train_data_onehot['TxGroup'] == 1]

formula = "PANSS_Total_diff_1 ~ VisitDay + TxGroup + TxGroup:VisitDay + Study + Study*VisitDay"
olsModel = smf.ols(formula,data=train_data).fit()
print(olsModel.summary())



"""1. considering mulitiple testing (studyA to studyE), we set up the alpah = 0.01
2. StudyD and StudyE have p vlaue < 0.001 --> different trials- different patint population affects the PANSS score over time.

--> Different trials (patients are from different country), may be because of different patient population lead to different PANSS over time.

Adding studD and study E into the analysis

#Adding StudyD and E variable into the analysis
"""

train_data['Study'] = pd.Categorical(train_data['Study'])

formula = "PANSS_Total_diff_1 ~ VisitDay + Study + Study*VisitDay"
olsModel = smf.ols(formula,data=train_data).fit()
print(olsModel.summary())

train_data['Country'] = pd.Categorical(train_data['Country'])

formula = "PANSS_Total_diff_1 ~ VisitDay + Country + Country*VisitDay"
olsModel = smf.ols(formula,data=train_data).fit()
print(olsModel.summary())

train_data['Country'] = pd.Categorical(train_data['Country'])

formula = "PANSS_Total_diff_1 ~ VisitDay + Country + Country*VisitDay + TxGroup + TxGroup:VisitDay"
olsModel = smf.ols(formula,data=train_data).fit()
print(olsModel.summary())