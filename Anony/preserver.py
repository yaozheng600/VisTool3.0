import pandas as pd

from Anony.mondrian import Mondrian

class Preserver:
    def __init__(self,df,quasi_id,sensitive_attr):
        self.mondrian = Mondrian(df,quasi_id,sensitive_attr)

    def __anonymize(self,k,l=0,t=0.0):
        partitions = self.mondrian.partition(k,l,t)
        rows= anonymize(
            self.mondrian.df,
            partitions,
            self.mondrian.qusi_id,
            self.mondrian.sensitive_attr)
        return pd.DataFrame(rows)
    def k_anonymity(self,k):
        return self.__anonymize(k)
    def l_diversity(self,k,l):
        return self.__anonymize(k,l=l)
    def t_closeness(self,k,t):
        return self.__anonymize(k,t=t)
    def __count_anonymity(self,k,l=0,t=0.0):
        partitions = self.mondrian.partition(k,l,t)
        return count_anonymity(
            self.mondrian.df,
            partitions,
            self.mondrian.qusi_id,
            self.mondrian.sensitive_attr,
        )
    def count_k_anonymity(self,k):
        return self.__count_anonymity(k)
    def count_l_diversity(self,k,l):
        return self.__count_anonymity(k,l=l)
    def count_t_closeness(self,k,t):
        return self.__count_anonymity(k,t=t)
def anonymize(df,partitions,quasi_id,sensitive_attr,max_partions=None):
    generalizations = {}
    for col in quasi_id:
        if df[col].dtype.name == 'category':
            generalizations[col] = generalize_categorical
        else:
            generalizations[col] = generalize_numerical
    rows = []
    for i, partition in enumerate(partitions):
        if max_partions is not None and i > max_partions:
            break
        grouped_cols = df.loc[partition].agg(generalizations,squeeze=False)
        sensitive_counts = df.loc[partition].groupby(sensitive_attr,observed=False).agg({sensitive_attr:'count'})
        values = list_to_str(grouped_cols).to_dict()
        for sensitive_value, count in sensitive_counts[sensitive_attr].items():
            if count == 0:
                continue
            values.update(
                {
                    sensitive_attr: sensitive_value,
                    'count': count,
                }
            )
            rows.append(values.copy())
    return rows
def generalize_numerical(series):
    min = series.min()
    max = series.max()
    if max == min:
        string = str(max)
    else:
        string = f'{min}-{max}'
    return [string]
def generalize_categorical(series):
    l = [str(n) for n in set(series)]
    return [','.join(l)]
def list_to_str(df):
    for i in range(df.shape[0]):
        df.iloc[i] = ''.join(df.iloc[i])
    return df
def count_anonymity(df,partitions,quasi_id,sensitive_attr,max_partitions=None):
    generalizations = {}
    for col in quasi_id:
        if df[col].dtype.name == 'category':
            generalizations[col] = generalize_categorical
        else:
            generalizations[col] = generalize_numerical
        generalizations[sensitive_attr] = 'count'
        rows = []
        for i, partition in enumerate(partitions):
            if max_partitions is not None and i > max_partitions:
                break
            grouped_cols = df.loc[partition].agg(generalizations, squeeze= False)
            values = grouped_cols.to_dict()
            rows.append(values.copy())
    return rows
