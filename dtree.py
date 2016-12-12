from collections import Counter
from math import log

import pandas as pd

class DTreeNode:
    def __init__(self, col, entropy):
        self.col = col
        self.entropy = entropy
        self.children = {}
    def pretty_print(self, depth=0):
        prefix = 2 * depth * ' '
        print(prefix + '{} ({:.2f})'.format(self.col, self.entropy))
        for val, child in sorted(self.children.items()):
            print('{}= {}'.format(prefix, val))
            if isinstance(child, str):
                print(prefix + '  {} ({:.2f})'.format(child, 0))
            else:
                child.pretty_print(depth=depth+1)

def get_entropy(df, y):
    entropy = 0
    size = df.shape[0]
    for count in Counter(df[y]).values():
        entropy -= (count / size) * log(count / size)
    return entropy

def get_attr_entropy(df, col, y):
    entropy = 0
    size = df.shape[0]
    for val in df[col].unique():
        sub_df = df[df[col] == val]
        entropy += (sub_df.shape[0] / size) * get_entropy(sub_df, y)
    return entropy

def build_dtree(df, y, depth=0):
    cur_entropy = get_entropy(df, y)
    if cur_entropy == 0:
        return df[y].iloc[0]
    columns = df.drop([y], axis=1).columns
    _, min_col = min((get_attr_entropy(df, col, y), col) for col in columns)
    root = DTreeNode(min_col, cur_entropy)
    for val in df[min_col].unique():
        child_df = df[df[min_col] == val]
        root.children[val] = build_dtree(child_df, y, depth=depth+1)
    return root

def expand_features(df):
    df['HAS_CATEGORICAL'] = (df['X1_TYPE'] == 'categorical') | (df['X2_TYPE'] == 'categorical')
    df['HAS_CATEGORICAL'] = df['HAS_CATEGORICAL'].map(lambda b: 'yes' if b else 'no')
    df['HAS_SEQUENCE'] = (df['X1_TYPE'] == 'sequence') | (df['X2_TYPE'] == 'sequence')
    df['HAS_SEQUENCE'] = df['HAS_SEQUENCE'].map(lambda b: 'yes' if b else 'no')
    df['HAS_NUMERIC'] = (df['X1_TYPE'] == 'numeric') | (df['X2_TYPE'] == 'numeric')
    df['HAS_NUMERIC'] = df['HAS_NUMERIC'].map(lambda b: 'yes' if b else 'no')
    return df

def main():
    df = pd.read_fwf('chart-types.csv')
    df = df[df['CHART_TYPE'] != 'FIXME']
    df = expand_features(df)
    dtree = build_dtree(df, 'CHART_TYPE')
    dtree.pretty_print()

if __name__ == '__main__':
    main()
