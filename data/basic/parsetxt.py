import sys
import operator

def parse_classTimes(file):
    with open (file) as f:
        raw_content = f.read()
        lines = raw_content.splitlines(True)[2:6]
        teachers_lines = raw_content.splitlines(True)[8:]
    for line in lines:
        tokens = line.split('\t')
        class_time = int(tokens[0])
        room = int(tokens[1])
        # print("class_time: {}---room:{}".format(class_time, room))
    for line in teachers_lines:
        tokens = line.split('\t')
        class_num = int(tokens[0])
        teachers = int(tokens[1])
        # print("class_num: {}---teachers: {}".format(class_num, teachers))

def parse_pref(file):
    dict = {}
    with open(file) as f:
        raw_content = f.read()
        lines = raw_content.splitlines(True)[1:]
        for line in lines:
            student_id = int(line.split('\t')[0])
            pref_list_line = line.split('\t')[1]
            pref_list = [int(x) for x in pref_list_line.split()]
            dict[student_id] = pref_list
    return dict


def count_class_size(pref_dict):
    sizes = {}
    for x in pref_dict:
        for index in pref_dict[x]:
            if index in sizes.keys():
                sizes[index] += 1
            else:
                sizes[index] = 1
    n = sorted(sizes.items(), key=operator.itemgetter(1))
    n.reverse()
    # print(n)

def edgeWeights(dict):
    weight = {}
    for student in dict.keys():
        for i in range(len(dict[student])):
            for j in range (i+1, len(dict[student])):
                key1 = dict[student][i]
                key2 =dict[student][j]
                keyMin = min(key1,key2)
                keyMax = max(key1, key2)
                key = (keyMin, keyMax)
                if not weight.get(key) == None:
                    weight[key] += 1
                else:
                    weight[key] = 1
    # print(weight)
    n = sorted(weight.items(), key=operator.itemgetter(1))
    n.reverse()
    print(n)
    print(len(weight))
    return weight

parse_classTimes("./demo_constraints.txt")
dict = parse_pref("./demo_studentprefs.txt")
count_class_size(parse_pref("./demo_studentprefs.txt"))
edgeWeights(dict)
