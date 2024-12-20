import mysql.connector

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="brandonm",
        password="csit355brandon",
        database="csit355"
    )

#Prints all available commands
def show_help_prompt():
    print("Help:")
    print("L: List all available courses",
          "\nE: Enroll yourself in a course",
          "\nW: Withdraw yourself from a course",
          "\nS: Search for a course by name",
          "\nM: List your current enrollments",
          "\nP: Prerequisites for a course",
          "\nT: List all professor information",
          "\nH: List executable functions",
          "\nX: Exit application")

#Checks if the sid exists
def check_if_sid_exists(conn, sid):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM Students WHERE sid = %s", (sid,))
        result = cur.fetchone()
        return result[0] > 0

#Checks if cid exists
def check_if_cid_exists(conn, cid):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM Courses WHERE cid = %s", (cid,))
        result = cur.fetchone()
        return result[0] > 0

#Checks if a student is enrolled in a specific course
def check_if_enrollment_exists(conn, sid, cid):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM Enrolled WHERE sid = %s AND cid = %s", (sid, cid))
        result = cur.fetchone()
        return result[0] > 0

#Gets student name based on the sid
def get_student_name(conn, sid):
    with conn.cursor() as cur:
        cur.execute("SELECT sname FROM Students WHERE sid = %s", (sid,))
        result = cur.fetchone()
        return result[0] if result else None

#Creates a new student
def create_student(conn, sid, sname, age):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO Students (sid, sname, age) VALUES (%s, %s, %s)", (sid, sname, age))
        conn.commit()

#Input -1
#Accepts input from student to add into the database
def create_new_student(conn):
    try:
        sid = int(input("Enter Student ID: "))
        sname = input("Enter Student Name: ")
        age = int(input("Enter Student Age: "))
        create_student(conn, sid, sname, age)
        print(f"Student {sname} added successfully!")
    except ValueError:
        print("Invalid input. Please enter correct data types.")
    except mysql.connector.IntegrityError:
        print("A student with this ID already exists. Please try again.")

#Input L
#Prints all courses showing the cid, course name, credits, class time, and building
def select_all_courses(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.cid, c.cname, c.credits, s.class_time, s.building
            FROM Courses c
            LEFT JOIN Schedules s ON c.cid = s.cid
        """)
        courses = cur.fetchall()
        if courses:
            #Display header
            print("CID | Course Name            | Credits | Class Time | Building")
            print("----------------------------------------------------------")
            #Display rows
            for course in courses:
                cid, cname, credits, class_time, building = course
                print(f"{cid:<3} | {cname:<20} | {credits:<8} | {class_time:<10} | {building}")
        else:
            print("No records found in the Courses table.")

#Input E
#Enrolls a student with the cid input
def enroll_in_course(conn, sid):
    try:
        cid = int(input("Enter Course ID: "))
        if not check_if_cid_exists(conn, cid):
            print("Course ID does not exist.")
            return
        #Checks if the student is already enrolled in the course
        if check_if_enrollment_exists(conn, sid, cid):
            print("You are already enrolled in this course.")
            return
        #Checks if prerequisites are met
        with conn.cursor() as cur:
            cur.execute("""
                SELECT prereq_cid 
                FROM Prerequisites 
                WHERE cid = %s
            """, (cid,))
            prerequisites = cur.fetchall()
            for prereq in prerequisites:
                prereq_cid = prereq[0]
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM Enrolled 
                    WHERE sid = %s AND cid = %s
                """, (sid, prereq_cid))
                result = cur.fetchone()
                if result[0] == 0:
                    print(f"You must complete Course {prereq_cid} before enrolling in Course {cid}.")
                    return
        #Gets the class time for the course being added
        with conn.cursor() as cur:
            cur.execute("SELECT class_time FROM Schedules WHERE cid = %s", (cid,))
            course_time = cur.fetchone()
            if course_time is None:
                print("Course does not have a valid class time.")
                return
            course_time = course_time[0]
            #Checks for time conflicts with the student's existing enrollments
            cur.execute("""
                SELECT s.class_time 
                FROM Schedules s
                JOIN Enrolled e ON e.cid = s.cid
                WHERE e.sid = %s
            """, (sid,))
            enrolled_times = cur.fetchall()
            for enrolled_time in enrolled_times:
                if enrolled_time[0] == course_time:
                    print(f"Time conflict: You are already enrolled in a course at {course_time}.")
                    return
            #If no conflict and prerequisites are met, create enrollment
            cur.execute("INSERT INTO Enrolled (sid, cid) VALUES (%s, %s)", (sid, cid))
            conn.commit()
        print("You have successfully enrolled in the course.")
    except ValueError:
        print("Invalid input. Please enter a valid course ID.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")

#Input W
#Withdraws a student from a course with cid input
def withdraw_from_course(conn, sid):
    try:
        cid = int(input("Enter Course ID: "))
        if not check_if_enrollment_exists(conn, sid, cid):
            print("You are not enrolled in this course.")
            return
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Enrolled WHERE sid = %s AND cid = %s", (sid, cid))
            conn.commit()
        print("You have withdrawn from the course.")
    except ValueError:
        print("Invalid input. Please enter a valid course ID.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")

#Input S
#Search for a course with a substring or full the name of the course
def search_for_course(conn):
    substring = input("Enter a substring to search for courses: ")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.cid, c.cname, c.credits, s.class_time, s.building
            FROM Courses c
            LEFT JOIN Schedules s ON c.cid = s.cid
            WHERE c.cname LIKE %s
        """, (f"%{substring}%",))
        courses = cur.fetchall()
        if courses:
            #Display header
            print("CID | Course Name            | Credits | Class Time | Building")
            print("----------------------------------------------------------")
            #Display rows
            for course in courses:
                cid, cname, credits, class_time, building = course
                print(f"{cid:<3} | {cname:<20} | {credits:<8} | {class_time:<10} | {building}")
        else:
            print("No matching courses found.")

#Input M
#Shows all courses a student is enrolled in
def view_my_classes(conn, sid):
    try:
        with conn.cursor() as cur:
            # Retrieve the list of classes the student is enrolled in
            cur.execute("""
                SELECT c.cid, c.cname, c.credits, s.class_time, s.building 
                FROM Enrolled e
                JOIN Courses c ON e.cid = c.cid
                JOIN Schedules s ON c.cid = s.cid
                WHERE e.sid = %s
            """, (sid,))
            enrolled_classes = cur.fetchall()
            if not enrolled_classes:
                print("You are not enrolled in any classes.")
                return
            #Display header
            print("Your enrolled classes:")
            total_credits = 0
            print(f"{'CID':<5} | {'Course Name':<20} | {'Credits':<7} | {'Class Time':<10} | {'Building':<8}")
            print("-" * 65)
            #Display rows
            for course in enrolled_classes:
                cid, cname, credits, class_time, building = course
                total_credits += credits
                print(f"{cid:<5} | {cname:<20} | {credits:<7} | {class_time:<10} | {building:<8}")
            print("-" * 65)
            print(f"Total Credits: {total_credits}")
    except mysql.connector.Error as e:
        print(f"Error: {e}")

#Input P
#Shows prerequisites for a course
def view_course_prereqs(conn, cid):
    with conn.cursor() as cur:
        cur.execute("SELECT prereq_cid FROM Prerequisites WHERE cid = %s", (cid,))
        prerequisites = cur.fetchall()
        if prerequisites:
            print(f"Prerequisites for Course {cid}:")
            for prereq in prerequisites:
                print(f"The prerequisite for {cid} is {prereq[0]}")
        else:
            print(f"No prerequisites found for Course {cid}.")

#Input T
#Prints all courses a professor is teaching, shows pid, pname, cid, class_time, credits, and total credits
def view_teaching_prof(conn):
    try:
        with conn.cursor() as cur:
            #Query to fetch professor, course details, and total credits grouped by professor
            cur.execute("""
                SELECT t.pid, p.pname, t.cid, s.class_time, c.credits,
                       SUM(c.credits) OVER (PARTITION BY t.pid) AS total_credits
                FROM Teaching t
                JOIN Professor p ON t.pid = p.pid
                JOIN Schedules s ON t.cid = s.cid
                JOIN Courses c ON t.cid = c.cid
                ORDER BY t.pid, t.cid
            """)
            rows = cur.fetchall()
            if not rows:
                print("No teaching assignments or schedules found.")
                return
            #Display header
            print(f"{'Professor ID':<15}{'Professor':<20}{'Course ID':<10}{'Class Time':<15}{'Credits':<10}{'Total Credits':<15}")
            #Display rows
            for row in rows:
                pid, pname, cid, class_time, credits, total_credits = row
                print(f"{pid:<15}{pname:<20}{cid:<10}{class_time:<15}{credits:<10}{total_credits:<15}")
    except mysql.connector.Error as e:
        print(f"Error: {e}")

#Main command interface
def start_cmd_interface(conn):
    print("Welcome to MSU Course Registration System!")
    while True:
        try:
            sid = int(input("Enter your student ID (or enter -1 to sign up): "))
            if sid == -1:
                create_new_student(conn)
            elif check_if_sid_exists(conn, sid):
                break
            else:
                print("Student ID does not exist in the database.")
        except ValueError:
            print("Student ID must be an integer.")
    print("Welcome back,", get_student_name(conn, sid),"!")
    while True:
        user_input = input("Enter a command (H for help): ").strip().upper()
        if user_input == 'L':
            select_all_courses(conn)
        elif user_input == 'E':
            enroll_in_course(conn, sid)
        elif user_input == 'W':
            withdraw_from_course(conn, sid)
        elif user_input == 'S':
            search_for_course(conn)
        elif user_input == 'M':
            view_my_classes(conn, sid)
        elif user_input == 'P':
            try:
                cid = int(input("Enter the course ID to view prerequisites: "))
                view_course_prereqs(conn, cid)
            except ValueError:
                print("Invalid course ID. Please enter an integer.")
        elif user_input == 'T':
            view_teaching_prof(conn)
        elif user_input == 'H':
            show_help_prompt()
        elif user_input == 'X':
            print("Thank you for using MSU Course Registration System!")
            break
        else:
            print("Invalid command. Enter 'H' for help.")

#Main function
def main():
    connection = connect_to_database()
    try:
        start_cmd_interface(connection)
    finally:
        connection.close()

if __name__ == '__main__':
    main()