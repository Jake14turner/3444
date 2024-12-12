import requests
import streamlit as st
import json
from database import retreiveKey, insertUserTokenIntoDatabase, registerUser, loginUser, save_time_estimates_to_db, saveGradesToDB
from datetime import datetime
import time
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import json
from database import (
    retreiveKey,
    insertUserTokenIntoDatabase,
    registerUser,
    loginUser,
    save_assignment,
    create_assignments_table,
)
from datetime import datetime, timezone, timedelta
from notifications import send_email
import time
import threading
import sqlite3
from pytz import timezone as pytz_timezone 


class Assignment:
    def __init__(self, name, dueDate, pointsPossible):
        self.name = name
        self.dueDate = dueDate
        self.pointsPossible = pointsPossible
        #self.timeToComplete = timeToComplete

class Class:
    def __init__(self, name, assignmentList):
        self.name = name
        self.assignmentList = assignmentList


class gradeGetter:
    def __init__(self, classID, assignmentIDList):
        self.classID = classID
        self.assignmentIDList = assignmentIDList

# Retrieve user email
def getUserEmail(username):
    connection = sqlite3.connect("streamlitBase")
    cursor = connection.cursor()

    cursor.execute("SELECT email FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    connection.close()

    if result:
        return result[0]
    return None




# Store assignments in the database
def store_assignments(data, user_id):
    """
    Stores assignments from the Canvas API in the database.
    
    Args:
        data (dict): The JSON data containing courses and assignments.
        user_id (int): The ID of the user associated with the assignments.
    """
    for course in data["courses"]:
        for assignment in course["assignments"]:
            assignment_name = assignment["name"]
            due_date = assignment.get("due_date", None)
            
            if due_date:
                try:
                    # Normalize the due_date to ISO 8601 UTC format
                    if due_date.endswith("Z"):
                        due_date = due_date.replace("Z", "+00:00")
                    parsed_date = datetime.fromisoformat(due_date)

                    # Optionally adjust due_date (if needed)
                    adjusted_date = parsed_date - timedelta(days=1)  # Adjust by -1 day if needed
                    adjusted_due_date_str = adjusted_date.isoformat().replace("+00:00", "Z")
                    
                    # Save the assignment to the database
                    save_assignment(user_id, assignment_name, adjusted_due_date_str)
                except ValueError as e:
                    print(f"Error parsing date for assignment '{assignment_name}': {e}")
                except Exception as e:
                    print(f"Error saving assignment '{assignment_name}': {e}")





def loadGrades(username):
    testToken = retreiveKey(username)
    scoreList = []
    gradeInformation = []

    headers = {
    'Authorization': f'Bearer {testToken}'
    }

    #first get the user ID
    response = requests.get(f"https://canvas.instructure.com/api/v1/users/self", headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        userID = user_data.get("id")

    IDList = st.session_state.gradeInformation 
    i = 0
    for course in IDList:
        i = i + 1

    totalIts = i
    stepVal = 100 // i
    current = 0

    progressBar = st.progress(0)
    for course in IDList:
        progressBar.progress(current + stepVal, f"Loading grades for course id: {course.classID}")
        current = current + stepVal
        courseID = course.classID
        for assignment in course.assignmentIDList:
            link = f'https://canvas.instructure.com/api/v1/courses/{courseID}/assignments/{assignment}/submissions/{userID}'

            response = requests.get(link, headers=headers)

            if response.status_code == 200:
                 grades = response.json()
                 individ = grades.get('score')
                 scoreList.append(individ)
    progressBar.progress(100)

    studentInfo = st.session_state.studentInfo

    i = 0
    for course in studentInfo:
        courseName = course.name
        for assignment in course.assignmentList:
            assignmentName = assignment.name
            pointsPossible = assignment.pointsPossible
            score = scoreList[i]
            i = i + 1
            gradeInformation.append({
                    "class_name": courseName,
                    "assignment_name": assignmentName,
                    "score": score,
                    "points_possible": pointsPossible
                 })
            
    return gradeInformation





    






#####     This function is to access the users assignments and return them to UI in JSON form     #####
def initializeUserInfoJSON(username):
    #courseIDList, courseNameList, studentInfo, username
    courseIDList = []
    courseNameList =  []
    studentInfo = []
    progressBar = st.progress(0.0, "Loading data from canvas, please dont leave this page until completion")
    progressValue = 0
    courseIDWithNames = []


    gradeInformation = []
    assignmentList = []

   #This is the database component's responsiblity: We need to retreive the key from the database
    testToken = retreiveKey(username)

    #define the link for the api
    apiLink = 'https://canvas.instructure.com/api/v1'

    #define headers for authentication
    headers = {
    'Authorization': f'Bearer {testToken}'
    }

  

    data = {"courses": []}

    #now generate the actual link to access the api endpoint we want, right here we are accesing courses
    #just append the endpointe "courses" to the root link
    link = f'{apiLink}/courses'


    courseCount = 0
    tempLink = link
    while tempLink:
        response = requests.get(tempLink, headers=headers)
        if response.status_code == 200:
            courses = response.json()
            courseCount += len(courses)
            tempLink = response.links.get('next', {}).get('url')
        else:
            st.text("Failed to fetch courses.")
            break

    if courseCount == 0:
        st.text("No courses found. Exiting.")
        return data

    progressIncrement = 1.0 / courseCount 



    #now print out all courses
    while link:
        #define the response using the requests tool
        response = requests.get(link, headers=headers)
        #check if the request receives an approriate response
        if response.status_code == 200:
            #take in the response in json form and put it into the var courses. 
            courses = response.json()
            #loop through each course in the response json var
            for course in courses:
                #checking for name, because if we dont some courses that are random garbage without names or other defining characteristics will be included
                if 'name' in course:
                    #st.text(f"Course name: {course['name']}, Course ID: {course['id']}")
                    #append each courses id into the course id list. This makes them more easily accesable for other functions in the future
                    courseIDList.append(course['id'])
                    courseID = course['id']
                    courseNameList.append(course['name'])
                    courseName = course['name']

                    #each course will have a name, id, and list of assignemts
                    course_data = {
                        "course_name": course['name'],
                        "course_id": course['id'],
                        "assignments": []
                    }

                    #for each class there will be a new link to the assignemtns
                    assignments_link = f"{apiLink}/courses/{course['id']}/assignments"
                    while assignments_link:
                        #get the json response of the assignemtns for a particular course
                        assignments_response = requests.get(assignments_link, headers=headers)
                        #if we successfully get a response
                        if assignments_response.status_code == 200:
                            #put the response into json type variable assignemtns
                            assignments = assignments_response.json()
                            #for eveery assignemt
                            for assignment in assignments:
                                
                                #append the assignment name and due date to the list of assignments
                                course_data["assignments"].append({
                                    "id": assignment.get('id'),
                                    "name": assignment.get('name'),
                                    "due_date": assignment.get('due_at', 'N/A'),
                                    "points_possible": assignment.get('points_possible', 'N/A')
                                })
                                assignmentName = assignment.get('name')
                                assignmentID = assignment.get('id')
                                pointsPossible = assignment.get('points_possible', 'N/A')
                                assignmentList.append(assignmentID)



                            assignments_link = assignments_response.links.get('next', {}).get('url')
                        else:
                            st.text(f"Failed to fetch assignments for Course ID {course['id']}")
                            break
                    #append the course as a whole to the json
                    gradeInformation.append(gradeGetter(courseID, assignmentList))
                    #clear the list for the next class
                    assignmentList = []
                    data["courses"].append(course_data)
                    
                progressValue = min(progressValue + progressIncrement, 1.0)
                progressBar.progress(progressValue, "Loading data from canvas, please dont leave this page until completion")

                link = response.links.get('next', {}).get('url')
                




                    #check if there is a next page, otherwise end.
                
    st.session_state.gradeInformation = gradeInformation

    progressBar.progress(100) 
    return data


#####   this function will take the data returned by the previous function and sort it into a list of class objects and assignment objects so we can easily use them   #####
def sortUserDataIntoList(data):
    i = 0
    studentInfo = []
    for course in data['courses']:

        assignmentList = []
        className = Class(course['course_name'], assignmentList)
        studentInfo.append(className)
        
        for assignment in course['assignments']:
            thisOne = Assignment(assignment['name'], assignment['due_date'], assignment['points_possible'])
            studentInfo[i].assignmentList.append(thisOne)
        i = i + 1

    return studentInfo






#####   this function is to check if a user has a key already with us   #####
def checkForUserKey(username):

    if 'hasKey' not in st.session_state:
        st.session_state.hasKey = False
   
    #This is the database component's responsiblity: We need to retreive the key from the database
    testToken = retreiveKey(username)

    
    
    #if the user does not have a key do this
    if testToken is None:
        placeholder = st.empty()
        with placeholder.container():

                #the first thing we need to do is make the user enter their key and then write that to their name in the database
            st.text("Lets start off by connecting your canvas account. Please input your canvas token:")
                #put the users token into token
            token = ""
            token = st.text_input("Please enter your token")
            testToken = ""

                
            if st.button("Submit token"):

                if token and username:
                            
                        #this is the database components respoonsibility:  we need to insert informatin into the database, so we will have the database component take care of it and not user.
                        testToken = insertUserTokenIntoDatabase(token, username)
                        st.session_state.hasKey = True

                        if testToken == token:
                            st.success(f"Token saved for {username}.")
                            st.session_state.hasToken = True
                            st.session_state.token_saved = True
                            return
                        else:
                            st.error(f"Failed to save or retrieve the token for user {username}.")
                            placeholder.empty()
                            st.experimental_rerun()
    #if the user already has a key, return
    else:
        st.session_state.hasKey = True
        return
    

#####   This function is to register a user   #####
def register():
   
    words = "Submit"
    text = "Already have an account? Press here to log in."
    can = False

    if 'show_text' not in st.session_state:
        st.session_state.show_text = True
    if 'can_show_homepage' not in st.session_state:
        st.session_state.can_show_homepage = False


    if st.session_state.show_text:

        username = st.text_input("Please enter a username")
        password = st.text_input("Please choose a password", type="password")
        email = st.text_input("Please enter your email")
        key = st.text_input("Please enter in a canvas access token")

        if st.button(words):
            if username and password and email and key:
                if "@" not in email or "." not in email:
                    st.error("Invalid email address.")
                    return                

                #This is the responsibiliyt of the database component: We need to take the entered username and password, check if they are already taken, and if not they can create an account
                success = registerUser(username, password, key, email)
                if success:
                    st.success("User registered successfully!")
                    st.session_state.show_text = False
                    st.session_state.can_show_homepage = True
                    can = True
                    st.session_state.registered = True
                    login = st.button("Log in")
                    if login:
                        st.switch_page("loginPage.py")



                     # Send a welcome email
                    subject = "Welcome to the Assignment Tracker!"
                    body = f"Hi {username},\n\nThank you for registering. You can now log in and start tracking your assignments.\n\nBest regards,\nAssignment Tracker Team"
                    try:
                        send_email(subject, body, email)
                        st.success("A welcome email has been sent to your email address.")
                    except Exception as e:
                        st.warning(f"Registration successful, but failed to send the email: {e}")

                else:
                    st.error("Registration failed. The username or email might already exist.")                                          
            else:
                    st.error("Please fill in both fields before submitting.")
        if st.button(text):
            st.switch_page("loginPage.py")
    if st.session_state.can_show_homepage:
        st.text("Thanks for registering, You can now login to your account")
        time.sleep(1)
        st.switch_page("loginPage.py")


#####   this functinon is for a user to log into their account   #####
def login():
    username = st.text_input("Please enter your username")
    password = st.text_input("Please enter your password", type="password")

    if st.button("Log in"):

        if username and password:  # Check if both fields are filled
            

            #This is the responsibility of the Database component: we need to take a username and password then check if they are in the databse
            user = loginUser(username, password)
            
            if user:
                st.success(f"Welcome {username}!")
              # st.session_state.isLoggedIn = True
                st.session_state.username = username
                return True
            else:
                st.error("Invalid username or password")
                return False
        else:
            st.error("Please fill in both fields before submitting.")


# Send daily reminders for assignments
def send_daily_reminders():
    """
    Fetch assignments due today (adjusted for the local time zone) and send email reminders.
    """
    # Set your local time zone (e.g., "US/Central")
    local_tz = pytz_timezone("US/Central")
    
    # Get today's date in the local time zone
    today_local = datetime.now(local_tz).date()

    connection = sqlite3.connect("streamlitBase")
    cursor = connection.cursor()

    # Fetch assignments along with user emails and usernames
    query = '''
        SELECT users.username, users.email, assignments.assignment_name, assignments.due_date
        FROM assignments
        JOIN users ON assignments.user_id = users.id
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()

    # Process each assignment and send an email
    for username, email, assignment_name, due_date_str in results:
        try:
            # Parse the due_date from string to UTC datetime
            due_date_utc = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
            
            # Convert the UTC due_date to the local time zone
            due_date_local = due_date_utc.astimezone(local_tz)

            # Check if the assignment is due today in the local time zone
            if due_date_local.date() == today_local:
                subject = "Assignment Due Reminder"
                body = (
                    f"Hi {username},\n\n"
                    f"This is a reminder that your assignment '{assignment_name}' "
                    f"is due today ({due_date_local.strftime('%Y-%m-%d %I:%M %p %Z')}).\n\n"
                    "Best regards,\nAssignment Tracker Team"
                )
                send_email(subject, body, email)
                print(f"Email sent to {email} for assignment: {assignment_name}")
            else:
                print(f"Assignment '{assignment_name}' is not due today.")
        except ValueError as e:
            print(f"Error parsing due_date for assignment '{assignment_name}': {e}")
        except Exception as e:
            print(f"Failed to send email to {email} for assignment '{assignment_name}': {e}")


# Start the reminder system
def start_reminder_system():
    """
    Start a scheduled system to check for assignments due today and send reminders.
    """
    try:
        print("Starting reminder system...")
        while True:
            send_daily_reminders()
            # Sleep for 24 hours before running again
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Reminder system stopped.")


# Run reminder system in a background thread
def run_reminder_in_background():
    """
    Run the reminder system in a background thread.
    """
    thread = threading.Thread(target=start_reminder_system, daemon=True)
    thread.start()


def initialize_user_assignments(username):
    """
    Fetch assignments for the user from the Canvas API and store them in the database.
    """
    # Get the user's API key from the database
    api_key = retreiveKey(username)
    if not api_key:
        st.error("No API key found for this user. Please register or update your key.")
        return

    # Fetch assignments using the `initializeUserInfoJSON` function
    st.info("Fetching assignments from Canvas...")
    user_data = initializeUserInfoJSON(username) # Fetch courses and assignments

    if not user_data or "courses" not in user_data:
        st.error("Failed to fetch assignments. Please check your API key.")
        return

    # Save assignments to the database
    st.info("Saving assignments to the database...")
    for course in user_data["courses"]:
        for assignment in course["assignments"]:
            assignment_name = assignment["name"]
            due_date = assignment.get("due_date")
            if due_date:
                try:
                    save_assignment(
                        user_id=st.session_state.username,
                        assignment_name=assignment_name,
                        due_date=due_date,
                    )
                except Exception as e:
                    st.error(f"Error saving assignment '{assignment_name}': {e}")
                    continue

    st.success("Assignments have been initialized and stored in the database.")


# Display user dashboard
def display_user_dashboard(username):
    """
    Display the user's assignments on their dashboard.
    """
    st.title(f"Welcome, {username}!")
    connection = sqlite3.connect("streamlitBase")
    cursor = connection.cursor()

    # Fetch assignments for the user
    query = '''
        SELECT assignments.assignment_name, assignments.due_date
        FROM assignments
        JOIN users ON assignments.user_id = users.id
        WHERE users.username = ?
        ORDER BY assignments.due_date
    '''
    cursor.execute(query, (username,))
    assignments = cursor.fetchall()
    connection.close()

    # Display assignments
    if assignments:
        st.subheader("Your Upcoming Assignments:")
        for assignment_name, due_date in assignments:
            due_date_obj = datetime.fromisoformat(due_date)
            formatted_date = due_date_obj.strftime("%Y-%m-%d %H:%M:%S")
            st.write(f"- {assignment_name}: Due on {formatted_date}")
    else:
        st.info("No assignments found. Please fetch your Canvas assignments.")

    # Option to fetch assignments
    if st.button("Fetch Canvas Assignments"):
        initialize_user_assignments(username)











#####   this functinon is for a user to log out of their account   #####
def logout():
    st.session_state.logged_in = False
    st.switch_page("logoutPage.py")




def refresh_grades():
    grades = loadGrades(st.session_state.username)
    st.session_state.gradeInformation = grades
    saveGradesToDB(grades, st.session_state.username)
    st.rerun()


def displayProgressBar(total_score, total_possible):
    if total_possible > 0:
        progress = total_score / total_possible
        color = (
            "green" if progress > 0.9 else
            "yellow" if progress > 0.7 else
            "red"
        )
        st.progress(progress, text=f"{progress * 100:.2f}% Completed")
        st.markdown(f"<div style='color: {color}; font-size: 1.2em; font-weight: bold;'>Class Progress: {progress * 100:.2f}%</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: gray; font-size: 1.2em; font-weight: bold;'>No graded assignments to calculate progress</div>", unsafe_allow_html=True)



def displayAssignmentsWithAverageNoText(assignments):
    total_score = 0
    total_possible = 0

    assignment_table = []
    for assignment in assignments:
        if assignment["score"] is not None and assignment["points_possible"] > 0:
            score_percentage = (assignment["score"] / assignment["points_possible"] * 100)
            score_display = f"{score_percentage:.2f}%"
            total_score += assignment["score"]
            total_possible += assignment["points_possible"]
        elif assignment["points_possible"] == 0:
            score_display = "Points not available"
        else:
            score_display = "Not graded"

        assignment_table.append([
            assignment["assignment_name"],
            score_display
        ])

    if total_possible > 0:
        average_percentage = (total_score / total_possible) * 100
    else:
        average_percentage = None

    return average_percentage, total_score, total_possible



def displayPieChart(class_name, grade_information):
    completed = sum(1 for grade in grade_information if grade["score"] is not None)
    not_completed = len(grade_information) - completed

    pie_data = pd.DataFrame({
        "Status": ["Completed", "Not Completed"],
        "Count": [completed, not_completed]
    })

  
    fig = px.pie(
        pie_data,
        values="Count",
        names="Status",
        title=f"{class_name} Assignment Completion Status",
        color_discrete_sequence=["green", "red"]
    )

    st.plotly_chart(fig, use_container_width=True)




def displayAssignmentsWithAverage(assignments):
    total_score = 0
    total_possible = 0

    assignment_table = []
    for assignment in assignments:
        if assignment["score"] is not None and assignment["points_possible"] > 0:
            score_percentage = (assignment["score"] / assignment["points_possible"] * 100)
            score_display = f"{score_percentage:.2f}%"
            total_score += assignment["score"]
            total_possible += assignment["points_possible"]
        elif assignment["points_possible"] == 0:
            score_display = "Points not available"
        else:
            score_display = "Not graded"

        assignment_table.append([
            assignment["assignment_name"],
            score_display
        ])

    st.table(
        pd.DataFrame(
            assignment_table,
            columns=["Assignment Name", "Score"]
        )
    )

    if total_possible > 0:
        average_percentage = (total_score / total_possible) * 100
    else:
        average_percentage = None

    return average_percentage, total_score, total_possible


def convertToDictionary(grade_information):
    if grade_information and isinstance(grade_information[0], dict):
        return grade_information 

    grade_dicts = []
    for grade in grade_information:
        grade_dicts.append({
            "class_name": grade.classID,  
            "assignment_name": grade.assignmentIDList, 
            "score": None,  
            "points_possible": None  
        })
    return grade_dicts


def displayNextThreeAssignments(upcoming_assignments):
    if upcoming_assignments:
        for assignment in upcoming_assignments:
            due_date_str = assignment.dueDate
            if due_date_str:
                try:
                    due_date = parseDueDate(due_date_str)
                    due_date_display = due_date.strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    due_date_display = "Invalid date format"
            else:
                due_date_display = "No due date available"

          
            st.write(f"**Assignment Name**: {assignment.name}")
            st.write(f"**Due Date**: {due_date_display}")
            st.write(f"**Points Possible**: {assignment.pointsPossible}")
            st.write("---")
    else:
        st.write("No upcoming assignments.")


def parseDueDate(due_date):
    if due_date is None:
        return None  

    try:
        if isinstance(due_date, str):
            return datetime.strptime(due_date.rstrip('Z'), '%Y-%m-%dT%H:%M:%S')
        elif isinstance(due_date, datetime):
            return due_date
        else:
            raise ValueError(f"Invalid dueDate format: {due_date}")
    except ValueError as e:

        print(f"Error parsing due date: {e} for due_date: {due_date}")
        return None 

def getNextThreeAssignments(course):
    valid_assignments = [assignment for assignment in course.assignmentList if assignment.dueDate]
    

    sorted_assignments = sorted(
        valid_assignments,
        key=lambda x: parseDueDate(x.dueDate) if parseDueDate(x.dueDate) else datetime.max
    )


    return [assignment for assignment in sorted_assignments if parseDueDate(assignment.dueDate) > datetime.now()][:3]




