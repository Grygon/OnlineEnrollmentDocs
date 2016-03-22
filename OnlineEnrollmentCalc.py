import csv

# ID'ed by their net IDs


class Student:

    def __init__(self, eid, email, first, last,
                 pref, virt, program):
        self.eid = eid
        self.email = email
        self.first = first
        self.last = last
        self.virt = 'V' in virt
        self.prog = virt
        self.program = program
        self.pref = pref
        self.courses = []
        self.droppedCourses = []
        self.reasons = []

    def addCourse(self, course):
        if course not in self.courses:
            self.courses.append(course)

    def dropCourse(self, course):
        if course in self.courses:
            self.droppedCourses.append(course)
            self.courses.pop(course)


# ID'ed by the course number
class Course:

    def __init__(self, rdate, cid, title, credits, term, start, end):
        self.rdate = rdate
        self.cid = cid
        self.title = title
        self.credits = credits
        self.term = term
        self.start = start
        self.end = end
        self.current = False

allStudents = {}
allCourses = {}


def readEnrolls(file):
    with open(file, newline='') as csvfile:

        reader = csv.reader(csvfile)
        next(reader)
        next(reader)
        for row in reader:
            # This whole section uses magic numbers based on the CSV
            courseData = row[10:14] + row[15:16] + row[17:]
            if courseData[1] not in allCourses:
                # Just trust that it works
                allCourses[courseData[1]] = \
                    Course(courseData[0], courseData[2], courseData[3],
                           courseData[4], courseData[5], courseData[6],
                           courseData[7])
            studentData = row[0:8]
            if studentData[2] not in allStudents:
                # Yes... let the hate flow through you
                allStudents[studentData[2]] = \
                    Student(studentData[0], studentData[1], studentData[4],
                            studentData[3], studentData[5], studentData[6],
                            studentData[7])

            allStudents[studentData[2]].addCourse(allCourses[courseData[1]])


def readDrops(file):
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        next(reader)
        for row in reader:
            student = row[2]
            reason = row[13]
            cid = row[15]
            # Issue: Not all allStudents/allCourses have been enrolled before
            # being dropped. TODO
            if student in allStudents and cid in allCourses:
                allStudents[student].dropCourse(allCourses[cid])
                allStudents[student].reasons.append(reason)


# Counts number of course enrollments per term. Each student
# enrolled per course increases it by 1


def studentsPerTerm(students):
    termStudents = {}
    for student in students:
        for course in students[student].courses:
            if course.term not in termStudents:
                termStudents[course.term] = {}
            termStudents[course.term][student] = students[student]
    return termStudents


# Filters out students whose virt case is equal to virt
def virtFilter(students, virt):
    newStudents = {}
    for student in students:
        if students[student].virt is virt:
            newStudents[student] = students[student]

    return newStudents


def progFilter(students):
    prog = {}
    for key, student in students.items():
        if student.prog not in prog:
            prog[student.prog] = {}
        prog[student.prog][key] = student
    return prog


def newFilter(students):
    noobs = {}
    # TODO: Hardcoded course order. Not sure how to fix. Seasons are alphabetical...
    courseOrder = {"Summer 2015": 1, "Fall 2015": 2, "Spring 2016": 3}
    for key, student in students.items():
        firstTerm = min(student.courses, key=(lambda t: courseOrder[t.term])).term
        if firstTerm not in noobs:
            noobs[firstTerm] = {}
        noobs[firstTerm][key] = student
    return noobs


def numClassFilter(students, num):
    takers = {}
    for key, student in students.items():
        if len(student.courses) is num:
            takers[key] = student

    return takers


def overlap(firstStudents, secondStudents):
    overlappers = {}
    for key in firstStudents:
        if key in secondStudents:
            overlappers[key] = firstStudents[key]

    return overlappers


def inTerm(students, term):
    for key, student in students:
        for course in student.courses:
            if course.term is term:
                return True
    return False


def inTerms(student, term1, term2):
    for course in student.courses:
        if course.term is term1:
            for course in student.courses:
                if course.term is term2:
                    return True

    return False


def percentage(n1, n2):
    return str(round((n1/n2)*100, 2)) + "%"

    # TODO: Implement the following:
    #   num Of allStudents per-term
    #       Virt vs Non-Virt
    #       Per-Program
    #   New allStudents per-term
    #       Per-program
    #   Num of course enrollments per term
    #       V vs NV
    #       num of classes for each student

outFile = None


def registerFiles():
    print("Please enter the enrollment file:")
    while True:
        try:
            readEnrolls(input("---> "))
            break
        except:
            print(
                """Invalid enrollment file, please enter a valid file""")

    print("Please enter the drops file:")
    while True:
        try:
            read = input("---> ")
            if read is "":
                break
            readDrops(read)
            break
        except:
            print(
                """Invalid drops file, please enter a valid file
                 or press Enter to skip""")

    print("Please enter file to write to:")
    outFile = input("---> ")


def defFiles():
    readEnrolls("Enrols.csv")
    readDrops("Drops.csv")


# To execute at runtime
def runTime():
    registerFiles()
    with open(outFile, 'w', newline='') as f:
        write = lambda w: csv.writer(f).writerows(w)

        termStudents = studentsPerTerm(allStudents)
        virtStudents = virtFilter(allStudents, True)
        virtTermStudents = studentsPerTerm(virtStudents)

        # Question 1: Students virt/not per term
        print("Question 1")
        for term in termStudents:
            print("\nFor term: " + term)
            q1(termStudents[term])

        # Question 2: Students in program per term
        print("\n\n\nQuestion 2:")
        for term in termStudents:
            print("\nFor term: " + term)
            progs = progFilter(virtTermStudents[term])
            print(", ".join((str(prog) + ": " + str(len(num)) for prog, num in progs.items())))

            # TODO: Virt/non-virt (If needed)

        # Question 3:
        newStudents = newFilter(virtStudents)
        for term, students in newStudents.items():
            print("New students in term " + term)
            print(len(students))

# Testing TODO

# for student in allStudents:
#    print(allStudents[student].first)

# asdf = studentsPerTerm(allStudents)
# for term in asdf:
#    print(term, asdf[term])


# Leave this as the last call
runTime()
