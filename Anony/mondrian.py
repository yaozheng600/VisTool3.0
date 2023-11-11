from Anony.util import is_k_anonymous, is_l_diverse, is_t_close, frequency_set
class Mondrian:
    def __init__(self,df,qusi_id,sensitive_attr=None):
        self.df = df
        self.qusi_id = qusi_id
        self.sensitive_attr = sensitive_attr
    def is_valid(self,partition,k=2,l=0,t=0.0):
        if not is_k_anonymous(partition,k):
            return False
        if l > 0 and self.sensitive_attr is not None:
            diverse =  is_l_diverse(self.df,partition,self.sensitive_attr,l)
            if not diverse:
                return False
        if t > 0.0 and self.sensitive_attr is not None:
            global_freqs = frequency_set(self.df,self.sensitive_attr)
            close = is_t_close(self.df,partition,self.sensitive_attr,global_freqs,t)
            if not close:
                return False
        return True

    def get_spans(self,partition,scale=None):
        # get normalized width
        # scale is to normalize the result
        spans = {}
        for col in self.qusi_id:
            if self.df[col].dtype.name == 'category':
                span = self.df[col][partition].nunique()
            else:
                span = self.df[col][partition].max()-self.df[col][partition].min()
            if scale is not None:
                span = span/scale[col]
            spans[col] = span
        return spans

    def split(self,col,partition):
        # find the median and then split
        dfp = self.df[col][partition]
        if dfp.dtype.name == 'category':
            # we don't need to sort the categorical column,
            # just split it into two equal part
            values = dfp.unique()
            lv = set(values[:len(values)//2])
            rv = set(values[len(values)//2:])
            return dfp.index[dfp.isin(lv)], dfp.index[dfp.isin(rv)]
        else:
            # split the numerical column from the median
            median = dfp.median()
            dfl = dfp.index[dfp<median]
            dfr = dfp.index[dfp>=median]
            return dfl,dfr

    def partition(self,k=2,l=0,t=0.0):
        # main function of the class
        scale = self.get_spans(self.df.index.values)
        result = []
        partitions = [self.df.index.values]
        while partitions:
            partition = partitions.pop(0)
            spans = self.get_spans(partition,scale)
            for col, span in sorted(spans.items(),key=lambda x:-x[1]):
                # choose the widest attribute of the quasi-identifier
                lp,rp = self.split(col,partition)
                if not self.is_valid(lp,k,l,t) or not self.is_valid(rp,k,l,t):
                    continue
                partitions.extend((lp,rp))
                break
            else:
                result.append(partition)
        return result
