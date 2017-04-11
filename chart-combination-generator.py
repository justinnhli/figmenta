import itertools
# import xlwt


# All possible Combination of standard Dimension, Filling and relation ship with data
def complicated_combinator(Base_dim_dic, Dimension, Filling_dic, Costomization):
    result = []
    count = -1
    for dimensions in Dimension:
        for L in range(0, len(Costomization) + 1):
            for subset in itertools.combinations(Costomization, L):
                k = [dimensions, "+", subset]
                count += 1
                result.append(k)
                nested_list = []
                for key in Base_dim_dic:
                    if dimensions == key:
                        b = Base_dim_dic.get(dimensions)
                        nested_list.append(b)
                for key in Filling_dic:
                    for i in range(len(subset)):
                        if subset[i] == key:
                            c = Filling_dic.get(subset[i])
                            nested_list.append(c)
                for subset in itertools.product(*nested_list):
                    result[count].append(subset)
    return result


# generate smaller set of combination
# fixed y dimension(fixed_y) + fixed x dimension (fixed_x) + x extra dimensions
def Combinator(fixed_x, fixed_y, x_dims, y_dims):
    x_dims_comb = []
    y_dims_comb = []
    for n in range(4):
        for subset in itertools.combinations_with_replacement(x_dims, n):
            # k = ["fixed_y:",b_y, "fied_x:",b_x, "extra dimension(s)", subset]
            x_dims_comb.append(subset)
        # for subset in itertools.combinations_with_replacement(y_dims, n):
        #     y_dims_comb.append(subset)
    # result = itertools.product(x_dims_comb, y_dims_comb)
    return x_dims_comb

# Writting in Excel
# fixme
def output(filename, sheet, list1, list2, x, y, z):
    book = xlwt.Workbook()
    sh = book.add_sheet(sheet)

    variables = [x, y, z]
    x_desc = 'Display'
    y_desc = 'Dominance'
    z_desc = 'Test'
    desc = [x_desc, y_desc, z_desc]

    col1_name = 'Stimulus Time'
    col2_name = 'Reaction Time'

    #You may need to group the variables together
    #for n, (v_desc, v) in enumerate(zip(desc, variables)):
    for n, v_desc, v in enumerate(zip(desc, variables)):
        sh.write(n, 0, v_desc)
        sh.write(n, 1, v)

    n+=1

    sh.write(n, 0, col1_name)
    sh.write(n, 1, col2_name)

    for m, e1 in enumerate(list1, n+1):
        sh.write(m, 0, e1)

    for m, e2 in enumerate(list2, n+1):
        sh.write(m, 1, e2)

    book.save(filename)



def main():
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
    compli_comb = complicated_combinator(Base_dim_dic, Dimension, Filling_dic, Costomization)

    fixed_x_dimension = ["Cata"]
    fixed_y_dimension = ["Num"]
    x_dimensions = ["Cata", "Seq", "Num"]
    y_dimensions = ["Cata", "Seq", "Num"]
    s_comb = Combinator(fixed_x_dimension,fixed_y_dimension, x_dimensions, y_dimensions)


    import csv
    with open('Chart Combination.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',', dialect='excel')
        writer.writerows(s_comb)
    f.close()

if __name__ == '__main__':
    main()




# with open('Chart Combination.txt', 'w') as fp:
#     fp.write('\n'.join('%s %s' % x for x in result))

