import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
import time
import threading
import sqlite3
from pytz import timezone as pytz_timezone

# Database connection
DATABASE = 'streamlitBase'

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "slashershashslinging@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "vhwa rhwt yclz vhui"  # Replace with your app password

# Function to send an email
def send_email(subject, body, to_email):
    """
    Sends an email notification.
    """
    try:
        # Create the email content
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# Function to retrieve assignments due today from the database
def get_assignments_due_today(username):
    """
    Retrieve assignments due today from the database for a given username.
    """
    today = datetime.now().date()
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Query to join users and assignments based on the username and today's date
    query = """
    SELECT assignments.assignment_name, assignments.due_date, users.email
    FROM assignments
    JOIN users ON assignments.user_id = users.id
    WHERE users.username = ? AND DATE(assignments.due_date) = ?
    """
    cursor.execute(query, (username, today))
    results = cursor.fetchall()
    connection.close()

    return results  # List of (assignment_name, due_date, email)

# Function to notify users of assignments due today
def notify_users(username):
    """
    Notify users of assignments due today.
    """
    assignments_due_today = get_assignments_due_today(username)
    if not assignments_due_today:
        print(f"No assignments due today for user {username}.")
        return

    # Send notifications for today's assignments
    for assignment_name, due_date, email in assignments_due_today:
        subject = "Today's Assignment Deadline Reminder"
        body = (f"Hello,\n\nThis is a reminder that the assignment '{assignment_name}' "
                f"is due today ({due_date}).\n\nBest regards,\nAssignment Tracker Team")
        send_email(subject, body, email)

# Scheduler to periodically check and send notifications
def start_scheduler(username, interval=3600):
    """
    Periodically check for assignments due today and send notifications.
    Runs at the specified interval (default: 3600 seconds = 1 hour).
    """
    while True:
        print("Checking for assignments due today...")
        notify_users(username)
        time.sleep(interval)  # Wait for the specified interval

# Run the scheduler in a background thread
def run_background_scheduler(username, interval=3600):
    """
    Starts the scheduler in a background thread.
    """
    scheduler_thread = threading.Thread(
        target=start_scheduler, args=(username, interval), daemon=True
    )
    scheduler_thread.start()
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
            due_date_local_adjust = due_date_local - timedelta(days=1)
                    

            # Check if the assignment is due today in the local time zone
            if due_date_local_adjust.date() == today_local:
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


# Example usage
if __name__ == "__main__":
    username = "test_user"  # Replace with a valid username
    run_background_scheduler(username, interval=3600)

    # Keep the main thread running
    while True:
        time.sleep(1)
