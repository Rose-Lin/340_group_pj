import sys
import operator

def parse_classTimes(file):    
    with open (file) as f:
        raw_content = f.read()
        lines = raw_content.splitlines(True)[2:6]
        teachers_lines = raw_content.splitlines(True)[8:]
        total_classes = raw_content.splitlines(True)[6]
        total = int(total_classes.split('\t')[1])
        total_rooms = int(raw_content.splitlines(True)[1].split('\t')[1])
    # a list of professors indexed by the class id
    professors = [0]*total
    classes = [0]*total
    rooms = []
    for line in lines:
        tokens = line.split('\t')
        class_time = int(tokens[0])
        room = int(tokens[1])
        room_id = int(tokens[0])
        #print("class_time: {}---room:{}".format(class_time, room))
        rooms.append((room_id, room))
    for line in teachers_lines:
        tokens = line.split('\t')
        class_num = int(tokens[0])
        teachers = int(tokens[1])
        # print("class_num: {}---teachers: {}".format(class_num, teachers))
        classes [class_num-1] = class_num
        professors[class_num-1] = teachers
    return professors, rooms

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
    # n is the sorted classes list according to popularity
    # content in n: (class id, popularity)
    n = sorted(sizes.items(), key=operator.itemgetter(1))
    n.reverse()
    print(n)
    return n

# classes is a list of clsses from count_class_size(), so it should be sorted by popularity already
# rooms should also be sorted list in increasing order of capacity (room_id, cap)
def scheduling(classes, students, professors, times, rooms):
    #sort room #TODO
    Schedule = [[0 for y in rooms] for x in times]
    # a list of indecis of classes in the Schedule
    Position = [0]*len(classes)
    for pair in  classes:
        class_id = pair[0]
        popularity = pair[1]
        room_id = 0
        room_id, t, cap = find_valid_room(popularity, rooms)
        Prof = []
        for i in range (0,room_id-1,1):
            if room_id > 1:
                Prof.append(professors[Schedule[t][i]])
        if professors[class_id] in Prof:
            room_id, t, cap = find_valid_room(cap+1, rooms)
        Schedule[t][room_id-1] = class_id
        Position[class_id-1] = (t,room_id-1)
    print (Schedule)
    print(Position)
    return Schedule

def find_valid_room(threshold, rooms):
    room_id = 0
    t = 0
    capacity = 0
    for rid, cap in rooms:
        if cap >= threshold:
            room_id = rid
            capacity = cap
            t = empty_timeslot() 
            if not t == None:
                break
    return room_id, t, capacity 

def empty_timeslot(Schedule, room_id):
    for row in Schedule:
        if Schedule[row][room_id-1] == 0:
            return row
    return None
    
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
    # print(n)
    # print(len(weight))
    return weight

parse_classTimes("./demo_constraints.txt")
dict = parse_pref("./demo_studentprefs.txt")
count_class_size(parse_pref("./demo_studentprefs.txt"))
#edgeWeights(dict)
