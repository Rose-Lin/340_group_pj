import sys

def parse_classTimes(file):
    with open (file) as f:
        raw_content = f.read()
        lines = raw_content.splitlines(True)[2:6]
        teachers_lines = raw_content.splitlines(True)[8:]
    for line in lines:
        tokens = line.split('\t')
        class_time = tokens[0]
        room = tokens[1]
        print("class_time: {}---room:{}".format(class_time, room))
    for line in teachers_lines:
        tokens = line.split('\t')
        class_num = tokens[0]
        teachers = tokens[1]
        print("class_num: {}---teachers: {}".format(class_num, teachers))

def parse_pref(file):
    pass

parse_classTimes("./demo_constraints.txt")
