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

def sort_room_cap(Class_list):
    Class_list.sort(key = lambda x: x[1])
    Class_list.reverse()
    print (Class_list)
    return Class_list
    
def test_result(S, Pref, Schedule, Position):
    count = 0
    total = 0
    for s in S:
        total += len(Pref[c])
        final_pick = [0] * (len(Schedule)+1)
        for c in Pref[s]:
            t = Position[c+1][0]
            if final_pick[t] == 0:
                final_pick[t] = c
                count += 1
    return (count/total)

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
sort_room_cap([(1,40),(2,50),(3,20),(4,30)])
#edgeWeights(dict)
