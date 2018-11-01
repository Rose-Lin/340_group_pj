import sys
import operator

def parse_classTimes(file):
    """" A function used on basic data, returns professors list, rooms list and time slots list"""
    with open (file) as f:
        raw_content = f.read().strip()
        table = raw_content.split('\n')
        total_time_slots = int(table[0].split('\t')[1])
        total_rooms = int(table[1].split('\t')[1])
        # class_line is the line number of the start of the classes
        class_line = total_rooms
        total_classes = table[2+class_line]
        # total is the total number of classes
        total = int(total_classes.split('\t')[1])
        teachers_classes_lines = table[4+class_line:]
        rooms_times_lines = table[2:2+class_line]
    # a list of professors indexed by the class id, class id starts from 0
    professors = [0]*total
    classes = [0]*total
    # 1 indexing, room id starts from 1
    rooms = []
    # 0 indexing, time slot id starts from 0
    time_slots = []
    for line in rooms_times_lines:
        tokens = line.split('\t')
        class_time = int(tokens[0])
        room = int(tokens[1])
        room_id = int(tokens[0])
        #print("class_time: {}---room:{}".format(class_time, room))
        time_slots.append(class_time-1)
        rooms.append((room_id, room))
    for line in teachers_classes_lines:
        tokens = line.split('\t')
        class_num = int(tokens[0])
        teachers = int(tokens[1])
        # print("class_num: {}---teachers: {}".format(class_num, teachers))
        classes [class_num-1] = class_num
        professors[class_num-1] = teachers
    return professors, rooms, time_slots

def parse_pref(file):
    """" A function used on basic data, returns student's pre dict, with student id as keys and pref list as value."""
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
    # print(n)
    return n

def get_students_in_class(pref_dict, room_dict):
    students = {}
    for s in pref_dict:
        times = []
        for c in pref_dict[s]:
            if room_dict[c][0] not in times:
                times.append(room_dict[c][0])
                if c in students:
                    students[c].append(s)
                else:
                    students[c] = [s]
    return students

# classes is a list of clsses from count_class_size(), so it should be sorted by popularity already
# rooms should also be sorted list in increasing order of capacity (room_id, cap)
def scheduling(classes, students, professors, times, rooms):
    Schedule = [[0 for y in rooms] for x in times]
    # a list of indecis of classes in the Schedule
    Position = [0]*len(classes)
    room_dict = {}
    ava_rooms = [len(times)]*len(rooms)
    for pair in  classes:
        class_id = pair[0]
        popularity = pair[1]
        room_id = 0
        room_id, t, cap = find_valid_room(Schedule, popularity, rooms, professors, class_id)
        if t == None:
            # Corner cases: when a specific room has very small capacity, so that the current class c cannot fit in any time of this room, and other rooms are all filled also.
            for ava_r in range(len( ava_rooms)):
                if ava_rooms[ava_r] > 0:
                    room_id = ava_r + 1
            print(room_id)
            for row in range (len(Schedule)):
                if Schedule[row][room_id-1] == 0:
                    t = row
                    break
        ava_rooms[room_id-1] -= 1
        Schedule[t][room_id-1] = class_id
        room_dict[class_id] = (t+1,room_id)
        Position[class_id-1] = (t,room_id-1)
    print("----------Schedule-----------")
    print (Schedule)
    print("-----------Position-----------")
    print(Position)
    return Schedule, Position, room_dict

def find_valid_room(Schedule, threshold, rooms, professors, class_id):
    room_id = 0
    t = 0
    capacity = 0
    for rid, cap in rooms:
        if cap >= threshold:
            room_id = rid
            capacity = cap
            t = empty_timeslot(Schedule, room_id, professors, class_id)
            if not t == None:
                break
    #print(t, room_id)
    return room_id, t, capacity

def empty_timeslot(Schedule, room_id, professors, class_id):
    for row in range (len( Schedule)):
        Prof = []
        if Schedule[row][room_id-1] == 0:
            for i in range (0,room_id-1,1):
                Prof.append(professors[Schedule[row][i]-1])
            if not professors[class_id-1] in Prof:
                return row
    return None

def sort_room_cap(Class_list):
    Class_list.sort(key = lambda x: x[1])
    # Class_list.reverse()
    #print (Class_list)
    return Class_list

def test_result(S, Pref, Schedule, Position):
    count = 0
    total = 0
    for s in S:
        total += len(Pref[s])
        final_pick = [0] * (len(Schedule)+1)
        for c in Pref[s]:
            t = Position[c-1][0]
            if final_pick[t] == 0:
                final_pick[t] = c
                count += 1
    return (float(count)/total)

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

def write_schedule_to_file(s_in_c, prof, room_dict, schedule, file):
    f = open(file, 'w')
    f.write("Course\tRoom\tTeacher\tTime\tStudents\n")
    for c in s_in_c:
        print(c)
        f.write(str(c)+ "\t")
        #f.write("\t")
        f.write(str(room_dict[c][1]) + "\t")
        #print(room_dict[c])
        f.write(str(prof[c-1]) + "\t")
        f.write(str(room_dict[c][0]) + "\t")
        f.write(''.join(str(e) + " " for e in s_in_c[c]))
        #print(s_in_c[c])
        f.write("\n")
    f.close()

professors, rooms, times = parse_classTimes("./demo_constraints.txt")
dict = parse_pref("./demo_studentprefs.txt")
students = dict.keys()
classes = count_class_size(parse_pref("./demo_studentprefs.txt"))
print (classes)
rooms = sort_room_cap(rooms)
schedule, position, room_dict = scheduling(classes, students, professors, times, rooms)
s_in_c = get_students_in_class(dict, room_dict)
#print(room_dict)
write_schedule_to_file(s_in_c, professors, room_dict, schedule, sys.argv[1])
print(test_result(students, dict, schedule, position))
