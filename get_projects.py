#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import pprint

'''
Flow of program

1. A file is created for project descriptions on Metis, and Metis project groups(pis, and members)

2. Metis projects are stored in the list `active_metis_projects` which contains dictionarys that includes the following
   -"project_title"     : Project title found in the file "metis_project_groups.txt"
   -"PI                 : PIs unique identifier
   -"group_member_count": Quantity of group members 
   -"PI_name"           : PIs name
   -"PI_department"     : PI department
   -"PI_email":         : PIs email
   -"description"       : Project description found in "metis_project_description.txt"
   
3. The file "metis_users.csv" and "metis_pis.csv" are cross referenced to get the PIs name, email, and department data

4. If when reading the file "metis_project_groups.txt" a PI has been disabled the PI is logged in the file "disabled_pis.txt"

5. The project description data is read from "metis_project_description.txt" and written to the `active_metis_projects` list


'''

def query_and_write_file(command, filename)-> str:
    '''
    query_and_write_file: Run a comand and write the results to a file

    command: Command to be executed
    filename: File to be written to
    '''
    # Execute the command on machine
    query_projects_output = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, universal_newlines=True
    )
    std_out = query_projects_output.stdout

    with open(filename, "a") as filename_description:
        filename_description.write(std_out)

    return std_out

def sort_file_contents(filename):
    '''
    sort_file_contents: Read the contents of the file and sort its contents

    filename: The file contents to be read
    '''

    # Stores all active PI's and their projects
    # active_metis_projects is a list of dictionaries
    # where each dictionary contains information for
    # - project_title
    # - PI
    # - group_member_count
    active_metis_projects = []

    # Stores all Disabled PI's and their projects
    archived_metis_projects = {
        "project_title": None,
        "PI" : None, 
        "group_member_count": None 
    }

    extracted_data = {}
    disabled_pis = []
    
    # Store a list of dictionaries for user IDs, and emails
    user_ids_and_emails = []

    print("Sorting File Contents!")
    with open(filename, "r") as file:
        for line in file:

            # Skip empty lines
            if not line:
                continue
            
            pattern_disabled_pi = r"(^#\s*Disabled\s+PI:\s+(\w+)$)"
            match_disabled_pi = re.findall(pattern_disabled_pi, line)
            for match in match_disabled_pi:
                disabled_pis.append(match[1])
            
            # Regex to gather tuples of IDs and emails
            pattern = r"([a-zA-Z0-9\-]+):\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

            # If the line matches the regex append line to matches
            matches = re.findall(pattern, line)
            for match in matches:
                # Temporary dictionary to store the current lines ID, and email matched
                user_data = {
                    "ID" : match[0],
                    "email" : match[1]
                }
                # Insert the current iterations data into the list 
                user_ids_and_emails.append(user_data)
            
            
            # Evaluate each line in the file
            # (\w+-(pi|members)) : Captures a key-like string (e.g., "user-pi" or "admin-members").
            # :                  : Matches a literal colon.
            # \s+                : Matches one or more whitespace characters.
            # (.*)               : Captures everything else in the line as a value.
            match = re.match(r"(\w+-(pi|members)):\s+(.*)", line)
            if match:
                key, _, value = match.groups() # Return a tuple of matched groups
                extracted_data[key] = value.strip()

        # Iterate through the matched lines 
        for key, value in extracted_data.items():

            # Evaluate PI lines
            if key.endswith("-pi"):
                project = {
                    "project_title": key[:-3],
                    "PI" : value, 
                    "group_member_count": None,
                    "PI_name": None,
                    "PI_department": None,
                    "PI_email": None,
                    "description": None
                }
                active_metis_projects.append(project)
            
            if key.endswith("-members"):
                project_title = key[:-8]

                member_count = len(value.split(","))
                for project in active_metis_projects:
                    if project["project_title"] == project_title:
                        project["group_member_count"] = member_count
    
    with open("../metis_users_test_code/metis_users.csv", "r") as file:
        for line in file:
            pid = ""
            pi_name = ""
            pi_department = ""
            
            # Split by commas, and check the department column
            values = line.split(",")     
            
            # Cross check our ids, anb emails list
            for user in user_ids_and_emails:
                
                # if the email matches get the name and department
                if user["email"] == values[1]:
                    
                    pi_name = values[0] 
                    pid = user["ID"]
                    pi_name = values[0]
                    pi_department = values[3] 
                    
                    for project in active_metis_projects:
                        if project["PI"] == pid:
                            
                            project["PI_email"] = values[1]
                            project["PI_name"] = pi_name
                            project["PI_department"] = pi_department
    
    with open("../metis_users_test_code/metis_pis.csv", "r") as file:
        for line in file:
            values = line.split(",")
            for data in active_metis_projects:
                if data["PI_department"] == "":
                    if(data["PI_name"] == values[0]):
                        data["PI_department"] = values[3]

    with open("./disabled_pis.txt", "w") as file:
        for element in disabled_pis:
            file.write(element + "\n")
    
    # This code is problamatic because 
    # multiple PIs can be on 1 project
    # A PI can have multiple projects
    with open("./metis_project_description.txt", "r") as file:
        content = file.read()
        
        pattern = r'description: PI=([^\n]+)(?:\n(?:description: (?!PI=).*?)*?description: DESCRIPTION=([^\n]+))?'
        matches = re.findall(pattern, content)
        
        results = {}
        for match in matches:
            pi = match[0].strip()
            description = match[1].strip() if len(match) > 1 and match[1] else "No description found"
            results[pi] = description
        
        for pi, description in results.items():
            print(f"PI: {pi} - Description: {description}")
            
            for data in active_metis_projects:
                if pi == data["PI"]:
                    data["description"] = description     

    # debug for 
    # PI
    # PI_department
    # PI_email
    # PI_name
    # description
    # group_member_count
    # project_title
    for value in active_metis_projects:
       pprint.pprint(value)
       print("")

                                        
def main():
    '''
    main: A script to get the active projects on Metis
    '''

    print("Getting Metis Projects")
    
    # Query idap for project descriptions
    print("Getting Metis Project Descriptions")
    query_projects = "ldapsearch -Z -x -H ldap://pldapms.hpc.cls | grep description"
    query_and_write_file(query_projects, "metis_project_description.txt")

    # Get all Metis groups
    print("Getting Metis Project Groups")
    metis_groups = "cat /home/admin/data/account_reports/aliases.ldap.Feb1_011701"
    query_and_write_file(metis_groups, "metis_project_groups.txt")

    # Sort the contents of the file by the following
    # Project title
    # PI (Name and Department)
    # Number of group members
    # One paragraph of project description
    # Link, if project is highlighted on the CRCD website
    sort_file_contents("./metis_project_groups.txt")

if __name__ == "__main__":
    '''
    python3 get_projects.py or ./get_projects.py
    '''
    main()