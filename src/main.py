import csv
import random
from datetime import datetime, timedelta

# Function to round time to the nearest half hour
def round_to_nearest_half_hour(dt):
    if dt.minute >= 45:
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    elif dt.minute >= 15:
        return dt.replace(minute=30, second=0, microsecond=0)
    else:
        return dt.replace(minute=0, second=0, microsecond=0)

# Function to read the work schedule from file
def read_schedule(file_path):
    schedule = []
    with open(file_path, 'r') as file:
        for line in file:
            day_info, hours = line.strip().split(': ')
            start_time_str, end_time_str = hours.split(' - ')
            start_time = datetime.strptime(start_time_str, '%I:%M%p')
            end_time = datetime.strptime(end_time_str, '%I:%M%p')
            schedule.append({'day_info': day_info, 'start_time': start_time, 'end_time': end_time})
    return schedule

# Function to read projects with weights from file
def read_projects(file_path):
    projects = []
    weights = []
    with open(file_path, 'r') as file:
        for line in file:
            project_info = line.strip().split(',')
            project = project_info[0].strip()
            weight = int(project_info[1].strip())
            projects.append(project)
            weights.append(weight)
    return projects, weights

# Function to read meetings and mark them as 'Admin Work'
def read_meetings(file_path):
    meetings = []
    with open(file_path, 'r') as file:
        for line in file:
            day_info, hours = line.strip().split(': ')
            start_time_str, end_time_str = hours.split(' - ')
            start_time = datetime.strptime(start_time_str, '%I:%M%p')
            end_time = datetime.strptime(end_time_str, '%I:%M%p')
            meetings.append({
                'day_info': day_info,
                'start_time': start_time,
                'end_time': end_time,
                'project': 'Admin Work'  # Label for meetings
            })
    return meetings

# Function to divide work hours into blocks, integrate meetings, and assign projects based on weights
def assign_projects_to_schedule(schedule, projects, weights, meetings):
    schedule_with_projects = []
    
    for entry in schedule:
        day_info = entry['day_info']
        start_time = entry['start_time']
        end_time = entry['end_time']
        
        # Filter meetings for the current day
        daily_meetings = [m for m in meetings if m['day_info'] == day_info]
        
        # Block out meeting times as 'Admin Work'
        current_time = start_time
        for meeting in daily_meetings:
            while current_time < meeting['start_time']:
                # Assign a project up until the meeting time
                if current_time + timedelta(hours=1) <= meeting['start_time']:
                    project = random.choices(projects, weights=weights, k=1)[0]
                    schedule_with_projects.append({
                        'Day': day_info,
                        'Start Time': round_to_nearest_half_hour(current_time).strftime('%I:%M %p'),
                        'Project': project
                    })
                    current_time += timedelta(hours=1)
                else:
                    break
            
            # Add the meeting as 'Admin Work'
            schedule_with_projects.append({
                'Day': day_info,
                'Start Time': round_to_nearest_half_hour(meeting['start_time']).strftime('%I:%M %p'),
                'Project': 'Admin Work'
            })
            current_time = meeting['end_time']
        
        # Fill in remaining time with projects after meetings
        while current_time < end_time:
            project = random.choices(projects, weights=weights, k=1)[0]
            schedule_with_projects.append({
                'Day': day_info,
                'Start Time': round_to_nearest_half_hour(current_time).strftime('%I:%M %p'),
                'Project': project
            })
            current_time += timedelta(hours=1)
    
    return schedule_with_projects

# Function to write the schedule with projects to CSV
def write_schedule_to_csv(schedule_with_projects, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Day', 'Start Time', 'Project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in schedule_with_projects:
            writer.writerow(entry)

# Main function to handle the process
def main():
    schedule_file = 'schedule.txt'   # Input schedule file
    projects_file = 'projects.txt'   # Input projects file
    meetings_file = 'meetings.txt'   # Input meetings file
    output_file = 'scheduled_projects.csv'   # Output CSV file
    
    # Read schedule, projects with weights, and meetings
    schedule = read_schedule(schedule_file)
    projects, weights = read_projects(projects_file)
    meetings = read_meetings(meetings_file)
    
    # Assign projects and integrate meetings
    schedule_with_projects = assign_projects_to_schedule(schedule, projects, weights, meetings)
    
    # Write the final schedule to a CSV file
    write_schedule_to_csv(schedule_with_projects, output_file)
    print(f"Schedule with projects and meetings has been written to {output_file}")

# Run the main function
if __name__ == "__main__":
    main()
