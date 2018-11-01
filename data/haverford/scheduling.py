import sys
import operator

def haverford_parse_prof_rooms_times_class(file):
    """" A function used on haverford data, returns professors list, rooms list and time slots list"""
    with open(file) as f:
        raw_content =  f.read().strip()
        lines = raw_content.split('\n')
        total_time_slots = int(lines[0].split('\t')[1])
        time_slots = {}
        for i in range(1, total_time_slots+1):
            times = lines[i].split('\t')[1].split()
            start_time = times[0]+times[1]
            end_time = times[2]+times[3]
            days = times[4:]
            # time_slots is a dictrionary with each day of the week as key and the [(start_time, end_time)] as value
            time_slots = get_time_slot_dict(start_time, end_time, days, time_slots)
        # room_line_num is the line of which the information about rooms starts
        room_line_num = 1+total_time_slots
        total_rooms = int(lines[room_line_num].split('\t')[1])
        # rooms is a list of tuples [(room_name, cap)]
        rooms = []
        for i in range(1+room_line_num, 1+room_line_num+total_rooms):
            room_name = lines[i].split('\t')[0]
            cap = int(lines[i].split('\t')[1])
            rooms.append((room_name, cap))
        # class_line_num is the line of which the information about classes and teachers starts
        class_line_num = 1+room_line_num+total_rooms
        total_classes = int(lines[class_line_num].split('\t')[1])
        total_teachers = int(lines[class_line_num+1].split('\t')[1])
        # profs is a dictrionary, with keys as class id and professors id as value
        profs = {}
        for i in range(class_line_num+2, class_line_num+total_classes+2):
            tokenizes = lines[i].split('\t')
            class_id = int(tokenizes[0])
            # TODO: this is not considering the labs
            if tokenizes[1]:
                prof_id = int(tokenizes[1])
                profs[class_id] = prof_id
    return profs, rooms, time_slots

def get_time_slot_dict(start_time, end_time, days, time_slots):
    for day in days:
        if day in time_slots.keys():
            if (start_time, end_time) not in time_slots[day]:
                time_slots[day].append((start_time, end_time))
        else:
            time_slots[day] = [(start_time, end_time)]
    return time_slots


def haverford_reconstruct_time_slots(time_slots):
    """ A function reconstruct a dictrionary of time_slots to a list, so that it is ready to be passed into scheduling function"""
    times = []
    for day, periods in time_slots.items():
        for slot in periods:
            times.append((day, slot))
    return times

def haverford_parse_pref(file):
    """" A function used on haverford data, returns professors students pref dict"""
    pref_dict = {}
    with open(file) as f:
        raw_content = f.read().strip()
        lines = raw_content.split('\n')
        total_student_num = int(lines[0].split('\t')[1])
        for i in range(1, 1+total_student_num):
            student_id = int(lines[i].split('\t')[0])
            pref_list_line = lines[i].split('\t')[1]
            pref_dict[student_id] = [int(x) for x in pref_list_line.split()]
    return pref_dict

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

# classes is a list of clsses from count_class_size(), so it should be sorted by popularity already
# rooms should also be sorted list in increasing order of capacity (room_id, cap)
def scheduling(classes, students, professors, times, rooms):
    print(rooms)
    Schedule = [[0 for y in rooms] for x in times]
    room_index_dict = {}
    index = 0
    for room in rooms:
        room_index_dict[index] = room
        index += 1
    print(room_index_dict)
    # Position is a dict keyed with class id
    Position = {}
    # room_dict is a dictrionary keyed with class id and (time slot,room id) in the schedule as value
    room_dict = {}
    # available rooms
    ava_rooms = [len(times)]*len(rooms)
    for pair in  classes:
        class_id = pair[0]
        popularity = pair[1]
        # room_id = 0
        index, t, cap = find_valid_room(Schedule, popularity, room_index_dict, professors, class_id)
        # room_id, t, cap = find_valid_room(Schedule, popularity, rooms, professors, class_id)
        if t == None:
            # Corner cases: when a specific room has very small capacity, so that the current class c cannot fit in any time of this room, and other rooms are all filled also.
            for ava_r in range(len(ava_rooms)):
                if ava_rooms[ava_r] > 0:
                    index = ava_r
            for row in range (len(Schedule)):
                if Schedule[row][index] == 0:
                    t = row
                    break
        ava_rooms[index] -= 1
        Schedule[t][index] = class_id
        room_id = room_index_dict[index][0]
        room_dict[class_id] = (t+1,room_id)
        Position[class_id] = (t,index)
    print("----------Schedule-----------")
    print (Schedule)
    print("-----------Position-----------")
    print(Position)
    print('-----------Room dict--------')
    print(room_dict)
    return Schedule, Position, room_dict

def find_valid_room(Schedule, threshold, room_index_dict, professors, class_id):
    room_id = 0
    t = 0
    capacity = 0
    total_rooms = len(rooms)
    # for rid, cap in room_index_dict:
    for index, room in room_index_dict.items():
        rid = room[0]
        cap = room[1]
        if cap >= threshold:
            room_id = rid
            capacity = cap
            t = empty_timeslot(Schedule, room_id, professors, class_id, index)
            if not t == None:
                break
    #print(t, room_id)
    return index, t, capacity

def empty_timeslot(Schedule, room_id, professors, class_id, index):
    for row in range (len( Schedule)):
        Prof = []
        if Schedule[row][index] == 0:
            for i in range (0,index,1):
                c_id = Schedule[row][i]
                if c_id > 0:
                    Prof.append(professors[c_id])
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

professors, rooms, times = haverford_parse_prof_rooms_times_class("../haverford/haverfordConstraints.txt")
print(professors)
times = haverford_reconstruct_time_slots(times)
pref_dict = haverford_parse_pref("../haverford/haverfordStudentPrefs.txt")
students = pref_dict.keys()
classes = count_class_size(pref_dict)
# print (classes)
rooms = sort_room_cap(rooms)
schedule, position = scheduling(classes, students, professors, times, rooms)
print(test_result(students, dict, schedule, position))
