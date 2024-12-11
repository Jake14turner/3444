import streamlit as st
import json
from database import retrieve_time_estimates_from_db, retrieveDaysAvailableFromDB
from datetime import datetime, timedelta
from user import Class


class Assignment:
    def __init__(self, name, dueDate, timeToComplete):
        self.name = name
        self.dueDate = dueDate
        self.timeToComplete = timeToComplete

class Week:
    def __init__(self, week_number, days_available):
        self.week_number = week_number #this is a unique week number
        self.days_available = days_available #this is the number of days that there is at least a 0 for time available
        self.schedule = {i: [] for i in range(len(days_available))} #this creates a dictionary where the indices are the days of the week 0 - 6 and each one has a list of assignemtns to create. 

    def add_assignment(self, assignment):
        time_needed = assignment.timeToComplete
        for day_index, hours in enumerate(self.days_available):
            if hours > 0 and time_needed > 0:
                allocated_time = min(time_needed, hours)
                self.schedule[day_index].append({"name": assignment.name, "time": allocated_time})
                self.days_available[day_index] -= allocated_time
                time_needed -= allocated_time

            if time_needed == 0:
                break

        return time_needed  #this will return the time that is left over if one of the assignemnts is at the edge between two days. 

    def display(self):
        schedule_output = {}
        for day, tasks in self.schedule.items():
            schedule_output[day] = [{"name": task["name"], "time": task["time"]} for task in tasks]
        return schedule_output




def generate_weeks_schedule(username):
    listOfDaysAvailable = retrieveDaysAvailableFromDB(username)
    saved_estimates = retrieve_time_estimates_from_db(username)
    allAssignmentsWithTime = []

    weeks = [Week(week_number=1, days_available=listOfDaysAvailable.copy())]


    if saved_estimates:
        st.subheader("Stored Time Estimates from Database")
#create a new list that has all of the assignments with their respective time to complete values
        for class_info in st.session_state.info:
            for assignment in class_info.assignmentList:
                key = f"{class_info.name}_{assignment.name}_time_estimate"
                stored_time = saved_estimates.get(key, "No estimate")
                newOne = Assignment(assignment.name, assignment.dueDate, stored_time)
                allAssignmentsWithTime.append(newOne)

#sort all of the assignments according to the time format
    allAssignmentsWithTime.sort(key=lambda x: datetime.strptime(x.dueDate, "%Y-%m-%dT%H:%M:%SZ") if x.dueDate else datetime.min)



    for assignment in allAssignmentsWithTime:
        time_needed = assignment.timeToComplete

        for week in weeks:
            if time_needed > 0:
                time_needed = week.add_assignment(assignment)

        if time_needed > 0:
            new_week = Week(week_number=len(weeks) + 1, days_available=listOfDaysAvailable.copy())
            weeks.append(new_week)
            new_week.add_assignment(assignment)

    return weeks
    
#function to sort all of the assignments a user has by only the ones that are still needing to be submitted. 
def filterAssignments(studentInfo):
    newList = []
    today = datetime.utcnow() 
    for i in studentInfo:
        assignmentList = []
        className = Class(i.name, assignmentList)
        newList.append(className)
        for j in i.assignmentList:
            if j.dueDate:
                dueDate = datetime.strptime(j.dueDate, "%Y-%m-%dT%H:%M:%SZ")
                
                #make sure the date of the assignment is after the current date. 
                if dueDate > today:
                    assignmentList.append(j)


    return newList


