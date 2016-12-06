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

def main():
    df = pd.read_fwf('chart-types.csv')
    dtree = build_dtree(df, 'chart_type')
    dtree.pretty_print()

if __name__ == '__main__':
    main()
