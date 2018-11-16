import sys
import time
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
            # time_slots is a dictrionary with group of days (e.g.'T,H' or 'F') as key and the [(start_time, end_time)] as value
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
        # haverford classes excluding labs and bmc classes
        hc_classes = []
        for i in range(class_line_num+2, class_line_num+total_classes+2):
            tokenizes = lines[i].split('\t')
            class_id = int(tokenizes[0])
            # TODO: this is not considering the labs
            if tokenizes[1]:
                prof_id = int(tokenizes[1])
                profs[class_id] = prof_id
                hc_classes.append(class_id)
    return profs, rooms, time_slots, hc_classes

def get_time_slot_dict(start_time, end_time, days, time_slots):
    time_slots_keys = ''
    for day in days:
        time_slots_keys += day + ','
    time_slots_keys = time_slots_keys[:-1]
    if time_slots_keys in time_slots.keys():
        time_slots[time_slots_keys].append((start_time, end_time))
    else:
        time_slots[time_slots_keys] = [(start_time, end_time)]
    return time_slots

def get_dup_time_slot_dict(time_slots):
    # take in a dictrionary of time slots and output a dictionary where key is weekdays and value is the list of list of
    # overlapping time slots.
    time_slot_grouping = {}
    time_slot_grouping["a"]:"hello"
    time_slot_no_overlapping = {}
    for days in time_slots.keys():
        # print(days)
        # sort time slots by starting time:
        sort_by_start = sorted(time_slots[days], key = lambda x: x[0])
        # print(sort_by_start)
        # sort time slots by ending time:
        #sort_by_end = sorted(time_slots[days], key = lambda x: x[1])
        same_time_list = []
        diff_time_list = []
        sublist = []
        latest_end_time = ""
        for index in range(len(sort_by_start)):
            elem = sort_by_start[index]
            if index == 0:
                #diff_time_list.append(elem)
                sublist = [elem]
                latest_end_time = elem[1]
            elif latest_end_time > elem[0]:
                sublist.append(elem)
                if latest_end_time < elem[1]:
                    latest_end_time = elem[1]
            else:
                if len(sublist) > 1:
                    same_time_list.append(sublist)
                diff_time_list.append(sublist[0])
                sublist = [elem]
                latest_end_time = elem[1]
            #print(latest_end_time)
            #print(sublist)
        time_slot_grouping[days] = same_time_list
        #print(time_slot_grouping)
        time_slot_no_overlapping[days] = diff_time_list
    return time_slot_grouping, time_slot_no_overlapping



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

def init_overlapping_schedule(overlapping_slots, rooms):
    """A function that initialize a scheduling table for overlapping time slots"""
    num_rows = 0
    for key in overlapping_slots.keys():
        num_rows += len(overlapping_slots[key])-1
    overlapping_schedule= [[0 for y in rooms] for x in range(num_rows)]
    return overlapping_schedule

def fill_schedule(schedule, room_dict, Position,classes, i, students, professors,times, room_index_dict, hc_classes, ava_rooms):
    while i < len(classes):
        class_id = classes[i][0]
        if not class_id in hc_classes:
            i += 1
            continue
        popularity = classes[i][1]
        index, t, cap = find_valid_room(schedule, popularity, room_index_dict, professors, class_id)
        if t == None:
            # Corner cases: when a specific room has very small capacity, so that the current class c cannot fit in any time of this room, and other rooms are all filled also.
            for ava_r in range(len(ava_rooms)):
                if ava_rooms[ava_r] > 0:
                    index = ava_r
            for row in range (len(schedule)):
                if schedule[row][index] == 0:
                    t = row
                    break
        if not t== None:
            ava_rooms[index] -= 1
            schedule[t][index] = class_id
            room_id = room_index_dict[index][0]
            room_dict[class_id] = (t+1,room_id)
            Position[class_id] = (t,index)
            i += 1
        else:
            return schedule, i
    return schedule, i

# classes is a list of clsses from count_class_size(), so it should be sorted by popularity already
# rooms should also be sorted list in increasing order of capacity (room_id, cap)
# overlapping_slots is a dictrionary of overlapping time slots. e.g. {'T,H': [(1:00PM, 4:00PM), (2:30PM, 4:00PM),(12:00PM, 1:30PM)]}
# times is a dictrionary of non-overlapping time slots
def scheduling(classes, students, professors, times, rooms, hc_classes):
# def scheduling(classes, students, professors, times, rooms, hc_classes, overlapping_slots):
    # schedule for non-overlapping time slots
    Schedule = [[0 for y in rooms] for x in times]
    # overlapping_schedule = init_overlapping_schedule(overlapping_slots, rooms) # TODO: variable name
    room_index_dict = {}
    index = 0
    for room in rooms:
        room_index_dict[index] = room
        index += 1
    # Position is a dict keyed with class id
    Position = {}
    # room_dict is a dictrionary keyed with class id and (time slot,room id) in the schedule as value
    room_dict = {}
    # available rooms in the Schedule, the content of which is the number of slots that is available for the room
    ava_rooms = [len(times)]*len(rooms)
    i = 0
    Schedule, i = fill_schedule(Schedule,room_dict, Position, classes, i, students, professors, times, room_index_dict, hc_classes, ava_rooms)
    if i < len(classes):
        # there are classes still not scheduled
        # move on to overlapping_schedule
        # ava_rooms = [len(overlapping_schedule)]*len(rooms)
        # overlapping_schedule, i = fill_schedule(overlapping_schedule,room_dict, Position, classes, i, students, professors, times, room_index_dict, hc_classes, ava_rooms)
        pass
    # print("----------non_overlapping Schedule-----------")
    # print (Schedule)
    # print("-----------Position-----------")
    # print(Position)
    # print('-----------Room dict--------')
    # print(room_dict)
    return Schedule, Position, room_dict

def find_valid_room(Schedule, threshold, room_index_dict, professors, class_id):
    room_id = 0
    t = 0
    capacity = 0
    total_rooms = len(rooms)
    for index, room in room_index_dict.items():
        rid = room[0]
        cap = room[1]
        if cap >= threshold:
            room_id = rid
            capacity = cap
            t = empty_timeslot(Schedule, room_id, professors, class_id, index)
            if not t == None:
                break
    return index, t, capacity

def empty_timeslot(Schedule, room_id, professors, class_id, index):
    for row in range (len( Schedule)):
        Prof = []
        if Schedule[row][index] == 0:
            for i in range (0,index,1):
                c_id = Schedule[row][i]
                if c_id > 0:
                    Prof.append(professors[c_id])
            if not professors[class_id] in Prof:
                return row
    return None


def sort_room_cap(Class_list):
    Class_list.sort(key = lambda x: x[1])
    return Class_list

def test_result(S, Pref, Schedule, Position):
    count = 0
    total = 0
    for s in S:
        total += len(Pref[s])
        final_pick = [0] * (len(Schedule)+1)
        for c in Pref[s]:
            if c in Position:
                t = Position[c][0]
                if final_pick[t] == 0:
                    final_pick[t] = c
                    count += 1
            else:
                total -= 1
    return (float(count)/total)

start = time.time()
professors, rooms, times, hc_classes = haverford_parse_prof_rooms_times_class("../haverford/haverfordConstraints.txt")
print(times)
length = 0
for t in times.keys():
    length += len(times[t])
print(length)
time_group, time_no_dup = get_dup_time_slot_dict(times)
print(time_group)
length = 0
for t in time_group.keys():
    length += len(time_group[t])
print(length)
length = 0
for t in time_no_dup.keys():
    length += len(time_no_dup[t])
print(length)
print(time_no_dup)
times = haverford_reconstruct_time_slots(times)
pref_dict = haverford_parse_pref("../haverford/haverfordStudentPrefs.txt")
students = pref_dict.keys()
classes = count_class_size(pref_dict)
rooms = sort_room_cap(rooms)
schedule, position, room_dict = scheduling(classes, students, professors, times[:5], rooms, hc_classes)
end = time.time()
print(test_result(students, pref_dict, schedule, position))
print("runtime: {}".format(end-start))
