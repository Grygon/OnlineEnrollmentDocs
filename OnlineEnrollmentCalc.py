import csv

# ID'ed by their net IDs


class Student:

    def __init__(self, eid, email, first, last,
                 pref):
        self.email = email
        self.first = first
        self.last = last
        # TODO: Students can change partway through. fuck
        self.progs = {}
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

    def addProg(self, program, term):
        if term not in self.progs:
            self.progs[term] = program


# ID'ed by the course number
class Course:

    def __init__(self, cid, title, credits, term, start, end):
        self.cid = cid
        self.title = title
        self.credits = credits
        self.term = term
        self.current = False

allStudents = {}
allCourses = {}
programs = []
virtPrograms = []


def readEnrolls(file):
    with open(file, newline='') as csvfile:

        reader = csv.reader(csvfile)
        next(reader)
        next(reader)
        for row in reader:
            # This whole section uses magic numbers based on the CSV
            courseData = row[10:13] + row[14]
            # Uses Class num as identifier 
            if courseData[0] not in allCourses:
                # Just trust that it works
                allCourses[courseData[0]] = \
                    Course(courseData[1], courseData[2], 
                      courseData[3], row[1])
            studentData = row[0:8]
            # TODO: Fix this. Just appending term to ID so changed terms work. This breaks
            # a LOT of statistics tracking (anything w/ previous-term)
            if studentData[2] not in allStudents:
                # Yes... let the hate flow through you
                allStudents[studentData[2]] = \
                    Student(studentData[0], studentData[1], studentData[4],
                            studentData[3], studentData[5])

            allStudents[studentData[2]].addCourse(allCourses[courseData[1]])
            for course in allStudents[studentData[2]].courses:
                allStudents[studentData[2]].addProg(
                    studentData[6], course.term)


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

        # TODO: Implement new prog listing for drops.


# Counts number of course enrollments per term. Each student
# enrolled per course increases it by 1


def studentsPerTerm(students):
    termStudents = {}
    for key, student in students.items():
        for prog in student.progs:
            if prog not in termStudents:
                termStudents[prog] = {}
            termStudents[prog][key] = student
    return termStudents


# Filters out students who are virt in the given term
def virtFilter(students, virt, term):
    virtStudents = {}
    for key, student in students.items():
        for t, prog in student.progs.items():
            if ('V' in prog) == virt and t == term:
                virtStudents[key] = student

    return virtStudents


# Filters for students in the given program in the given term
def progFilter(students, program, term):
    filtered = {}
    for key, student in students.items():
        if term in student.progs and student.progs[term] == program:
            filtered[key] = student
    return filtered


# Gets a dict of enrolled programs for the given term
def progGet(students):
    prog = {}
    for key, student in students.items():
        if student.progs[term] not in prog:
            prog[student.progs[term]] = {}
        prog[student.progs[term]][key] = student
    return prog


# Returns a dict of terms and noobs for the respective term
# TODO: Optimize for new progs
def newFilter(students):
    noobs = {}
    for key, student in students.items():
        firstTerm = min(student.courses, key=(lambda t: keyTerm(t.term))).term
        if firstTerm not in noobs:
            noobs[firstTerm] = {}
        noobs[firstTerm][key] = student
    return noobs


# Returns a dict of students taking the number of classes in the term
def numClassFilter(students, num, term):
    takers = {}
    for key, student in students.items():
        numTermCourses = 0
        for course in student.courses:
            if course.term == term:
                numTermCourses += 1
        if numTermCourses is num:
            takers[key] = student

    return takers


# Returns the intersection of two students
def overlap(firstStudents, secondStudents):
    overlappers = {}
    for key in firstStudents:
        if key in secondStudents:
            overlappers[key] = firstStudents[key]

    return overlappers


# Finds if there is a student in the given term
def inTerm(students, term):
    for key, student in students:
        for pTerm in student.progs:
            if pTerm == term:
                return True
    return False


# Finds if a student is in both terms
def inTerms(student, term1, term2):
    for term in student.progs:
        if term is term1 and term is term2:
            return True

    return False


def percentage(n1, n2):
    if n2 is 0:
        return "N/A"
    return str(round((n1 / n2) * 100, 2)) + "%"


outFile = None


def registerFiles():
    global outFile
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


def testFiles():
    global outFile
    readEnrolls("Enrols.csv")
    readDrops("Drops.csv")
    outFile = "test.csv"


def createPrograms():
    for key, student in allStudents.items():
        for term, prog in student.progs.items():
            if prog not in programs:
                if 'V' in prog:
                    virtPrograms.append(prog)
                programs.append(prog)

    virtPrograms.sort()
    programs.sort()


def keyTerm(t):
    seasonComp = {"Spring": 1, "Summer": 2, "Fall": 3}
    return t[-4:] + str(seasonComp[t[:-5]])


# To execute at runtime
def runTime():
    registerFiles()
    # testFiles()
    createPrograms()
    with open(outFile, 'w', newline='') as f:
        write = lambda w: csv.writer(f).writerow(w)

        termStudents = studentsPerTerm(allStudents)
        virtStudents = {}
        for term in termStudents:
            virtStudents[term] = virtFilter(allStudents, True, term)

        # Question 1: Students virt/not per term
        print("Question 1")
        write(["# and % of students on/off campus"])
        numPercent = lambda x: [str(x), percentage(x, len(termStudents[term]))]
        write(["", "# On", "% On", "# Off", "% Off"])
        for term in sorted(termStudents, key=keyTerm):
            write([term] +
                  numPercent(len(virtFilter(termStudents[term], False, term))) +
                  numPercent(len(virtStudents[term])))

        write([""])

        # Question 2: Students in program per term
        print("\nQuestion 2")
        write(["# of students in each online program"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            write([term] + [len(progFilter(termStudents[term], program, term))
                            for program in virtPrograms] +
                  [len(virtFilter(termStudents[term], True, term))])

        write([""])

        # Question 3:
        print("\nQuestion 3")
        write(["# of new students in each online program"])
        write([""] + virtPrograms + ["Total"])
        noobs = newFilter(allStudents)
        for term in sorted(termStudents, key=keyTerm):
            write([term] + [len(progFilter(noobs[term], program, term))
                            for program in virtPrograms] +
                  [len(virtFilter(noobs[term], True, term))])

        write([""])

        # Question 4:
        print("\nQuestion 4")
        write(["% of students in each online program taking 1 class"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            write([term] +
                  [percentage(len(numClassFilter(progFilter(termStudents[term], program, term), 1, term)),
                              len(progFilter(termStudents[term], program, term)))
                   for program in virtPrograms] +
                  [percentage(len(numClassFilter(termStudents[term], 1, term)),
                              len(termStudents[term]))])

        write([""])

        # Question 5:
        print("\nQuestion 5")
        write(["% of students in each online program taking 2 classes"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            write([term] +
                  [percentage(len(numClassFilter(progFilter(termStudents[term], program, term), 2, term)),
                              len(progFilter(termStudents[term], program, term)))
                   for program in virtPrograms] +
                  [percentage(len(numClassFilter(termStudents[term], 2, term)),
                              len(termStudents[term]))])

        write([""])

        # Question 6:
        print("\nQuestion 6a")
        write(["# of students in each online program taking 1 class"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            write([term] +
                  [len(numClassFilter(progFilter(termStudents[term], program, term), 1, term))
                   for program in virtPrograms] +
                  [len(numClassFilter(virtStudents[term], 1, term))])

        write([""])

        # Question 6:
        print("\nQuestion 6b")
        write(["% of students in each online program taking 1 class"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            write([term] +
                  [percentage(len(numClassFilter(progFilter(termStudents[term], program, term), 1, term)),
                              len(progFilter(termStudents[term], program, term)))
                   for program in virtPrograms] +
                  [percentage(len(numClassFilter(virtStudents[term], 1, term)),
                              len(virtStudents[term]))])

        write([""])

        # Question 7:
        print("\nQuestion 7a")
        write(["# of students in each online program taking 2 classes"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            write([term] +
                  [len(numClassFilter(progFilter(termStudents[term], program, term), 2, term))
                   for program in virtPrograms] +
                  [len(numClassFilter(virtStudents[term], 2, term))])

        write([""])

        # Question 7:
        print("\nQuestion 7b")
        write(["% of students in each online program taking 2 classes"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            write([term] +
                  [percentage(len(numClassFilter(progFilter(termStudents[term], program, term), 2, term)),
                              len(progFilter(termStudents[term], program, term)))
                   for program in virtPrograms] +
                  [percentage(len(numClassFilter(virtStudents[term], 2, term)),
                              len(virtStudents[term]))])

        write([""])

        terms = sorted(termStudents, key=keyTerm)

        # Question 8:
        print("\nQuestion 8a")
        write(
            ["# of students in each online program who took 1 last term, now 2 classes"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [len(overlap(
                      # In theory I don't need an overlap here,
                      # but I don't want to mess with it...
                      # Students who took 1 last term
                      numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          1, terms[nowTerm - 1]),
                      # Students taking 2 now
                      numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          2, terms[nowTerm])))
                   for program in virtPrograms] +
                  # Is this right? Depends what we're looking for
                  [len(overlap(
                      # Students who took 1 last term
                      numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          1, terms[nowTerm - 1]),
                      # Students taking 2 now
                      numClassFilter(
                          virtStudents[term],
                          2, terms[nowTerm])))])

        write([""])

        # Question 8:
        print("\nQuestion 8b")
        write(
            ["% of students in each online program who took 1 last term, now 2 classes"])
        # Comparing % for num who took 1
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [percentage(len(overlap(
                      # In theory I don't need an overlap here,
                      # but I don't want to mess with it...
                      # Students who took 1 last term
                      numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          1, terms[nowTerm - 1]),
                      # Students taking 2 now
                      numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          2, terms[nowTerm]))),
                      len(numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          1, terms[nowTerm - 1])))
                   for program in virtPrograms] +
                  # Is this right? Depends what we're looking for
                  [percentage(len(overlap(
                      # Students who took 1 last term
                      numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          1, terms[nowTerm - 1]),
                      # Students taking 2 now
                      numClassFilter(
                          virtStudents[term],
                          2, terms[nowTerm]))),
                      len(numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          1, terms[nowTerm - 1])))])

        write([""])

        # Question 9:
        print("\nQuestion 9a")
        write(
            ["# of students in each online program who took 1 last term, now 1 class"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [len(overlap(
                      # Students who took 1 last term
                      numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          1, terms[nowTerm - 1]),
                      # Students taking 1 now
                      numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          1, terms[nowTerm])))
                   for program in virtPrograms] +
                  # Is this right? Depends what we're looking for
                  [len(overlap(
                      # Students who took 1 last term
                      numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          1, terms[nowTerm - 1]),
                      # Students taking 1 now
                      numClassFilter(
                          virtStudents[term],
                          1, terms[nowTerm])))])

        write([""])

        # Question 9:
        print("\nQuestion 9b")
        write(
            ["% of students in each online program who took 1 last term, now 1 class"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [percentage(len(overlap(
                      # Students who took 1 last term
                      numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          1, terms[nowTerm - 1]),
                      # Students taking 1 now
                      numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          1, terms[nowTerm]))),
                      len(numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          1, terms[nowTerm])))
                   for program in virtPrograms] +
                  # Is this right? Depends what we're looking for
                  [percentage(len(overlap(
                      # Students who took 1 last term
                      numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          1, terms[nowTerm - 1]),
                      # Students taking 1 now
                      numClassFilter(
                          virtStudents[term],
                          1, terms[nowTerm]))),
                      len(numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          1, terms[nowTerm - 1])))])

        write([""])

        # Question 10:
        print("\nQuestion 10a")
        write(
            ["# of students in each online program who took 2 last term, now 2 classes"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [len(overlap(
                      # Students who took 2 last term
                      numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          2, terms[nowTerm - 1]),
                      # Students taking 2 now
                      numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          2, terms[nowTerm])))
                   for program in virtPrograms] +
                  # Is this right? Depends what we're looking for
                  [len(overlap(
                      # Students who took 2 last term
                      numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          2, terms[nowTerm - 1]),
                      # Students taking 2 now
                      numClassFilter(
                          virtStudents[term],
                          2, terms[nowTerm])))])

        write([""])

        # Question 10:
        print("\nQuestion 10b")
        write(
            ["% of students in each online program who took 2 last term, now 2 classes"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [percentage(len(overlap(
                      # Students who took 2 last term
                      numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          2, terms[nowTerm - 1]),
                      # Students taking 2 now
                      numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          2, terms[nowTerm]))),
                      len(numClassFilter(progFilter(
                          virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          2, terms[nowTerm - 1])))
                   for program in virtPrograms] +
                  # Is this right? Depends what we're looking for
                  [percentage(len(overlap(
                      # Students who took 2 last term
                      numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          2, terms[nowTerm - 1]),
                      # Students taking 2 now
                      numClassFilter(
                          virtStudents[term],
                          2, terms[nowTerm]))),
                      len(numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          2, terms[nowTerm - 1])))])

        write([""])

        # Question 11:
        print("\nQuestion 11a")
        write(
            ["# of students in each online program who took 2 last term, now 1 class"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [len(overlap(
                      # Students who took 2 last term
                      numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          2, terms[nowTerm - 1]),
                      # Students taking 1 now
                      numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          1, terms[nowTerm])))
                   for program in virtPrograms] +
                  # Is this right? Depends what we're looking for
                  [len(overlap(
                      # Students who took 2 last term
                      numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          2, terms[nowTerm - 1]),
                      # Students taking 1 now
                      numClassFilter(
                          virtStudents[term],
                          1, terms[nowTerm])))])

        write([""])

        # Question 11:
        print("\nQuestion 11b")
        write(
            ["% of students in each online program who took 2 last term, now 1 class"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [percentage(len(overlap(
                      # Students who took 2 last term
                      numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          2, terms[nowTerm - 1]),
                      # Students taking 1 now
                      numClassFilter(
                          progFilter(virtStudents[term], program, term),
                          1, terms[nowTerm]))),
                      len(numClassFilter(
                          progFilter(
                              virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                          2, terms[nowTerm - 1])))

                   for program in virtPrograms] +
                  # Is this right? Depends what we're looking for
                  [percentage(len(overlap(
                      # Students who took 2 last term
                      numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          2, terms[nowTerm - 1]),
                      # Students taking 1 now
                      numClassFilter(
                          virtStudents[term],
                          1, terms[nowTerm]))),
                      len(numClassFilter(
                          virtStudents[terms[nowTerm - 1]],
                          2, terms[nowTerm - 1])))])

        write([""])

        # Question 12:
        print("\nQuestion 12a")
        write(
            ["# of students in each online program who were in last and current semester"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            terms = sorted(termStudents, key=keyTerm)
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [len(overlap(
                      # Students in last term
                      progFilter(
                          virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                      # Students now
                      progFilter(virtStudents[term], program, term)))
                   for program in virtPrograms] +
                  [len(overlap(
                      # Students in last term
                      virtStudents[terms[nowTerm - 1]],
                      # Students  now
                      virtStudents[term]))])

        write([""])

        # Question 12:
        print("\nQuestion 12b")
        write(
            ["% of students in each online program in last semester also in current semester"])
        write([""] + virtPrograms + ["Total"])
        for term in sorted(termStudents, key=keyTerm):
            terms = sorted(termStudents, key=keyTerm)
            nowTerm = terms.index(term)
            if nowTerm == 0:
                continue
            write([term] +
                  [percentage(len(overlap(
                      # Students in last term
                      progFilter(
                          virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1]),
                      # Students now
                      progFilter(virtStudents[term], program, term))),
                      len(progFilter(
                          virtStudents[terms[nowTerm - 1]], program, terms[nowTerm - 1])))
                   for program in virtPrograms] +
                  [percentage(len(overlap(
                      # Students in last term
                      virtStudents[terms[nowTerm - 1]],
                      # Students  now
                      virtStudents[term])),
                      len(virtStudents[terms[nowTerm - 1]]))])

            # TODO: Missing Spring EBVMS student...

            # Testing

            # for student in allStudents:
            #    print(allStudents[student].first)

            # asdf = studentsPerTerm(allStudents)
            # for term in asdf:
            #    print(term, asdf[term])

            # Leave this as the last call
runTime()
