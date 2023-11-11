def is_k_anonymous(partition,k):
    if len(partition) < k:
        return False
    return True

def is_l_diverse(df,partition,sensitive_attr,l):
    diversity = df.loc[partition][sensitive_attr].nunique()
    return diversity >= l

def is_t_close(df,partition,sensitive_attr,global_freqs,t):
    total_count = float(len(partition))
    d_max = None
    group_counts = df.loc[partition].groupby(sensitive_attr,observed=False)[sensitive_attr].agg('count')
    for value, count in group_counts.to_dict().items():
        p = count/total_count
        d = abs(p-global_freqs[value])
        if d_max is None or d > d_max:
            d_max = d
    return d_max <= t

def frequency_set(partition,dim):
    '''
    :param partition: DataFrame
    :param dim: the column you wanna split
    :return: frequency: global_freq,for t-closeness
    '''
    frequency = {}
    total_count = float(len(partition))
    group_counts = partition.groupby(dim,observed=False)[dim].agg('count')
    for value ,count in group_counts.to_dict().items():
        fs = count/total_count
        frequency[value] = fs
    return frequency
