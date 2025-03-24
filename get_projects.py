#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import pprint
import itertools

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

class MetisProjects:
    
    def __init__(self):
        '''
        __init__: Constructor for MetisProjects
        '''
        # Stores all active PI's and their projects
        # active_metis_projects is a list of dictionaries
        # where each dictionary contains information for
        # - project_title
        # - PI
        # - group_member_count
        self.active_metis_projects = []    
        self.disabled_pis = [] 
        self.active_pis = []
        self.user_ids_and_emails = []
        
        self.pi_and_project_descriptions = {}
        
    def query_and_write_file(self, command, filename)-> str:
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

        with open(filename, "w") as filename_description:
            filename_description.write(std_out)

        return std_out

    def write_disabled_pis(self, filename="./metis_project_groups.txt")->None:
        '''
        write_disabled_pis: Write all disabled pis to disabled_pis.txt
        
        filename: The file to read the data from
        '''
        with open(filename, "r") as file:
            for line in file:

                # Skip empty lines
                if not line:
                    continue
                
                pattern_disabled_pi = r"(^#\s*Disabled\s+PI:\s+(\w+)$)"
                match_disabled_pi = re.findall(pattern_disabled_pi, line)
                for match in match_disabled_pi:
                    self.disabled_pis.append(match[1])

        with open("./disabled_pis.txt", "w") as file:
            for element in self.disabled_pis:
                file.write(element + "\n")

    def write_active_pis(self, filename="./metis_project_groups.txt"):
        '''
        write_active_pis: Write all active pis to active_pis.txt
        
        filename: The file
        '''
        extracted_data = {}
        
        with open(filename, "r") as file:
            for line in file:

                # Skip empty lines
                if not line:
                    continue
                       
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
                    self.active_pis.append(value)
                    
            with open("./active_pis.txt", "w") as file:
                for element in self.active_pis:
                    file.write(element + "\n")
            
    def extract_project_pi_and_members(self, filename="./metis_project_groups.txt")->dict:
        ''''
        project_pi_and_members: This function leverages a regex expression to read the file
            to captures the PI and group members for a project on Metis
        
        filename: The file to read from
        '''
        extracted_data = {}
        
        with open(filename, "r") as file:
            for line in file:

                # Skip empty lines
                if not line:
                    continue
    
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
                    self.user_ids_and_emails.append(user_data)
                        
                # Evaluate each line in the file
                # (\w+-(pi|members)) : Captures a key-like string (e.g., "user-pi" or "admin-members").
                # :                  : Matches a literal colon.
                # \s+                : Matches one or more whitespace characters.
                # (.*)               : Captures everything else in the line as a value.
                match = re.match(r"(\w+-(pi|members)):\s+(.*)", line)
                if match:
                    key, _, value = match.groups() # Return a tuple of matched groups
                    extracted_data[key] = value.strip()

        return extracted_data
    
    def assign_project_data(self, extracted_project_data)->None:
        ''''
        assign_project_data: Handles the extracted PI and team members 
            and appends the project data to active_metis_projects
        
        extracted_project_data: The extracted project data read from the file
        '''
        
        # Iterate through the matched lines 
        # key:   groupname-pi, or groupname-members
        # value: Either the PI name or names of the group members
        for key, value in extracted_project_data.items():

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
                self.active_metis_projects.append(project)
            
            if key.endswith("-members"):
                project_title = key[:-8]

                member_count = len(value.split(","))
                for project in self.active_metis_projects:
                    if project["project_title"] == project_title:
                        project["group_member_count"] = member_count
        
    def assign_pi_name_and_department(self):
        '''
        assign_pi_name_and_department: Cross references the PI, with data in metis_users.csv
            to assign the PIs email and department info in active_metis_projects
        '''
        with open("../metis_active_users_and_pis/metis_users.csv", "r") as file:
            for line in file:
                pid = ""
                pi_name = ""
                pi_department = ""
                
                # Split by commas, and check the department column
                values = line.split(",")     
                
                # Cross check our ids, anb emails list
                for user in self.user_ids_and_emails:
                    
                    # if the email matches get the name and department
                    if user["email"] == values[1]:
                        
                        pi_name = values[0] 
                        pid = user["ID"]
                        pi_name = values[0]
                        pi_department = values[3] 
                        
                        for project in self.active_metis_projects:
                            if project["PI"] == pid:
                                
                                project["PI_email"] = values[1]
                                project["PI_name"] = pi_name
                                project["PI_department"] = pi_department
        
        with open("../metis_active_users_and_pis/metis_pis.csv", "r") as file:
            for line in file:
                values = line.split(",")
                for data in self.active_metis_projects:
                    if data["PI_department"] == "":
                        if(data["PI_name"] == values[0]):
                            data["PI_department"] = values[3]
    
    def assign_project_descriptions(self):
        ''''
        assign_project_descriptions:
        '''
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
                # print(f"PI: {pi} - Description: {description}")
                
                for data in self.active_metis_projects:
                    if pi == data["PI"]:
                        data["description"] = description    
    
    def consecutive_pi_lines_helper(self, filename="./metis_project_description.txt")->list:
        ''''
        consecutive_pi_lines: Helper function to identify consecutive lines where 
            multiple PIs are assigned to 1 or more projects
        '''
        current_group = []         # Temp list to hold a single group of consecutive PI lines
        consecutive_pi_lines = []  # List to store groups of consecutive PI lines
        
        with open(filename, "r") as file:
            lines = file.readlines()  

            for line in lines:
                if line.startswith("description: PI="):
                    current_group.append(line[16:].strip())  # Add to the current group
                else:
                    if len(current_group) > 1:  # Only store groups with 2+ PI lines
                        consecutive_pi_lines.append(current_group)
                    current_group = []  # Reset for the next potential group

            # Check if the last group collected needs to be added
            if len(current_group) > 1:
                consecutive_pi_lines.append(current_group)
        
        return consecutive_pi_lines

    def pis_and_projects(self, filename="./metis_project_description.txt")->None:
        '''
        pis_and_projects: Retrieves the data for PIs and the projects they are working on
        '''
        
        current_pi = None

        with open(filename, "r") as file:
        
            # Skip first 2 lines
            for line in itertools.islice(file, 2, None):
                
                # Ignore this
                if "description: AFFILIATION=Hewlett-Packard" in line:
                    continue
                    
                # Append the PI
                if line.startswith('description: PI='):
                    
                    current_pi = line[len('description: PI='):].strip()
                
                    # Insert the PI 
                    if current_pi not in self.pi_and_project_descriptions:
                        
                        # Assign no description to the current PI
                        self.pi_and_project_descriptions[current_pi] = []

                # Append the description for the PI
                # If current line is a description and previous line was a PI
                elif line.startswith('description: DESCRIPTION=') and current_pi is not None:
                    description = line[len('description: DESCRIPTION='):].strip()
                    
                    # Append the description for the PI on the previous line
                    self.pi_and_project_descriptions[current_pi].append(description)
                
                # Handle scenario where a project description appears 
                elif not line.startswith('description:') and current_pi is not None and line:
                    if self.pi_and_project_descriptions[current_pi]:
                        self.pi_and_project_descriptions[current_pi][-1] += ' ' + line                        
            
    def pis_missing_description_helper(self)->None:
        ''''
        pis_missing_description_helper: Handles PIs that have missing descriptions 
            and assigns them the correct project descriptions
        '''
        pi_no_description = []
            
        consecutive_pi_lines = self.consecutive_pi_lines_helper()
            
        for element, description in self.pi_and_project_descriptions.items():
            
            # Reset after every iteration
            temporary_description = ""
                
            # If the PI doesn't have a description append it
            if not description:
                pi_no_description.append(element)
        
        for element in pi_no_description:
                
            # Iterate through consecutive PIs
            for group in consecutive_pi_lines:
                
                # Check if PI in consecutive groups
                if element in group:
                    
                        # If the PI has a missing description assign
                        # them all the projects of their last group member        
                        self.pi_and_project_descriptions[element].append(self.pi_and_project_descriptions[group[len(group) - 1]])
     
        # for pi, project_description in self.pi_and_project_descriptions.items():
        #     for project_data in self.active_metis_projects:          
        #         if pi == project_data["PI"]:
        #             project_data["description"] = project_description
                      
    def fetch_active_metis_projects(self):
        '''
        fetch_active_metis_projects: Read the contents of the file and sort its contents

        filename: The file contents to be read
        '''

        # Stores all Disabled PI's and their projects
        archived_metis_projects = {
            "project_title": None,
            "PI" : None, 
            "group_member_count": None 
        }
        
        # Extract the PI and team member names that correspond to each project
        extracted_data = self.extract_project_pi_and_members()
        
        # Initialize the project data to active_metis_projects
        self.assign_project_data(extracted_data)
        
        # Retrieve and assign the PIs email and department info to a given project
        self.assign_pi_name_and_department()
        
        # Retrieve and assign project descriptions
        self.assign_project_descriptions()
        
        # Get a list of pis and their projects descriptions
        self.pis_and_projects()
        
        # Check for any missing PI descriptions 
        self.pis_missing_description_helper()

    def debug_active_metis_users(self):
        '''
        debug: For debugging purposes
            
        PI
        PI_department
        PI_email
        PI_name
        description
        group_member_count
        project_title
        '''
        for value in self.active_metis_projects:
            pprint.pprint(value)
            print("")

    def debug_pis_and_project_descriptions(self):
        pprint.pprint(self.pi_and_project_descriptions)

                                
def main():
    '''
    main: A script to get the active projects on Metis
    '''

    print("Getting Metis Projects")
    metis_projects = MetisProjects()
    
    # Query idap for project descriptions
    print("Getting Metis Project Descriptions")
    query_projects = "ldapsearch -Z -x -H ldap://pldapms.hpc.cls | grep description"
    metis_projects.query_and_write_file(query_projects, "metis_project_description.txt")

    # Get all Metis groups
    print("Getting Metis Project Groups")
    metis_groups = "cat /home/admin/data/account_reports/aliases.ldap.Feb1_011701"
    metis_projects.query_and_write_file(metis_groups, "metis_project_groups.txt")

    # Write all disabled pis to disabled_pis.txt
    metis_projects.write_disabled_pis()

    # Write all active pis to active_pis.txt
    metis_projects.write_active_pis()

    # Retrieving and writing all Metis Projects
    metis_projects.fetch_active_metis_projects()
    
    # Get PIs and their projects
    metis_projects.pis_and_projects(filename="./metis_project_description.txt")

    # View all active projects on Metis
    metis_projects.debug_active_metis_users()
    
    # View all PIs and their project descriptions
    # metis_projects.debug_pis_and_project_descriptions()
    


if __name__ == "__main__":
    '''
    python3 get_projects.py or ./get_projects.py
    '''
    main()