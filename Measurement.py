import pandas as pd
import numpy as np
import scipy.stats as st
import math

class Measurement:
    def __init__(self,df,df_anony, quasi_id:list,sa:str):
        self.df =df
        self.df_anony= df_anony
        self.quasi_id =quasi_id
        self.sa = sa

    def privacy_loss(self):
        Q = self.df[self.sa].value_counts(normalize=True).sort_index()

        count_1 = self.df_anony.groupby((self.quasi_id+[str(self.sa)]),observed=False)['count'].sum()
        count_2 = self.df_anony.groupby((self.quasi_id),observed=False)['count'].sum()
        P =count_1/count_2

        series_muster = pd.Series(index=Q.index,data=0.0)
        p = []
        s=series_muster
        for i in range(P.shape[0]):
            for j in range(s.shape[0]):
                if s.index[j]==P.index[i][-1]:
                    s.iloc[j]=P.iloc[i]
                    break
            if round(s.sum(),15)==1:
               p.append(self.JS_divergence(Q,s))
               s= series_muster
        return p

    def utility_loss(self):
        count_1 = self.df_anony.groupby(self.quasi_id)['count'].sum()
        count_1 = count_1.reset_index()

        for i in count_1.columns[0:-1]:
            if self.df[i].dtype.name == "category":
                count_1[i] = count_1[i].str.split(',', expand=False)
            else:
                count_1[i] = count_1[i].str.split('-', expand=False)

        def NCP(df, series):
            sum = 0
            for i in range(len(series) - 1):
                if len(series.iloc[i]) > 1:
                    if df[series.index[i]].dtype.name == 'category':
                        sum = sum + len(series.iloc[i]) / df[series.index[i]].nunique()
                    else:
                        ncp_num = (float(series.iloc[i][1]) - float(series.iloc[i][0])) / (
                                    df[series.index[i]].max() - df[series.index[i]].min())
                        sum = sum + ncp_num
            return series.iloc[-1] * sum / (len(series) - 1)

        sum = 0
        for i in range(len(count_1)):
            sum = NCP(self.df, count_1.iloc[i]) + sum

        return sum /self.df.shape[0]

    def JS_divergence(self,p,q):
        M=(p+q)/2
        return 0.5*st.entropy(p,M,base=2)+0.5*st.entropy(q,M,base=2)

