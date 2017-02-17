import itertools

Dimension = ["BD1", "BD2", "BD3", "BD4"]
Costomization = ["Colo", "Satu", "Size", "Shap", "Orie", "Text"]
Plot = ["Scatter Plot", "Bar Chart", "Box Plot", "Line Chart", "Violin Chart"]

# Fillings' relation with Data
Filling_dic = {
    "Colo" : ["CN", "DN", "C"],
    "Satu" : ["CN", "*DN", "*C"],
    "Size" : ["*CN", "DN (population)", "*C"],
    "Shap" : ["DN", "*C"],
    "Orie" : ["*CN", "*DN", "*C"],
    "Text" : ["C", "*DN"]
}

# Base Dimension(s)'s relation with Data
Base_dim_dic = {
    "BD1" : ["CN"],
    "BD2" : ["CN + CN"],
    "BD3" : ["CN + CN + CN"],
    "BD4" : ["CN + CN + CN + CN"]
}

# All possible Combination of standard Dimension, Filling and relation ship with data

result = []
count = -1
for a in Dimension:
    for L in range(0, len(Costomization) + 1):
        for subset in itertools.combinations(Costomization, L):
            k = [a, "+", subset]
            count += 1
            result.append(k)
            nested_list = []
            for key in Base_dim_dic:
                if a == key:
                    b = Base_dim_dic.get(a)
                    nested_list.append(b)
            for key in Filling_dic:
                for i in range(len(subset)):
                    if subset[i] == key:
                        c = Filling_dic.get(subset[i])
                        nested_list.append(c)
            for subset in itertools.product(*nested_list):
                result[count].append(subset)
print(result)


# with open('Chart Combination.txt', 'w') as fp:
#     fp.write('\n'.join('%s %s' % x for x in result))
import csv
with open('Chart Combination.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(result)
    # FIXME
