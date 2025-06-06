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
   -"group_title"       : Group title found in the file "metis_project_groups.txt"
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
        Constructor for MetisProjects
        '''
        
        # Stores all active PI's and their projects
        self.active_metis_projects = []    
        self.disabled_pis = [] 
        self.active_pis = []
        self.user_ids_and_emails = []
        self.missing_pi_department = {
            "piot" : "Physics",
            "yyin" : "Chemistry & Biochemistry",
            "hedin" : "Physics"
        }
        self.updated_project_descriptions = {
            "AML" : "The AML project is for research in machine learning, federated learning and optimization.",
            "ATLAS" : "The ATLAS group searches for new particles beyond the Standard Model, focusing on final states with multiple heavy quarks.",
            "AVLAB" : "Analyzing large spatial datasets to understand the factors affecting US Hospitals' success requires considering a very detailed spatial context for each health facility.",
            "AVLAB2" : "The study of how participants of a federated fine-tuning regime can achieve an equilibrium, where every member is sufficiently incentivized to participate.",
            "LINLAB" : "LINLAB is a NIU research team that works on the quadruped robots as guide dogs for the visually impaired population.",
            "PCT" : "The pcT (proton computed Tomography) project focuses on reconstructing 3D tomographic medical images using protons. These high-resolution images are used to support post-diagnosis, proton-based cancer treatment by improving the accuracy of proton dose delivery. Innovations from the pcT project have led to four U.S. patents and five international patents.",
            "PRAD" : "The PRAD (Proton Radiography) project is dedicated to reconstructing 2D radiographic medical images using protons. These images play a vital role in post-diagnosis, proton-based cancer treatment by enhancing treatment planning and verification. Innovations from the PRAD project have contributed to four U.S. patents and five international patents.",
            "REDCAP" : "REDCap is a secure web platform for building and managing online databases and surveys. It is available to NIU faculty, staff, and students for use in research projects.",
            "ZWLAB" : "Developing iGAIT a smartphone-based tool that uses machine learning and video gait analysis to help detect early signs of autism in children."
        }
        self.archived_metis_projects = [
            "chem600s2017",
            "aard",
            "cmodel",
            "fast",
            "hedin",
            "jahreda",
            "npohlman",
            "piot",
            "ritelab",
            "syphers",
            "resx",
            "bios641"
        ]
        self.pi_and_project_descriptions = {}
        self.black_list_projects = []
        
    def query_and_write_file(self, command, filename)-> str:
        '''
        Run a comand and write the results to a file

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
        Write all disabled pis to disabled_pis.txt
        
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

    def write_archived_metis_projects(self, filename="./metis_project_groups.txt") -> None:
        ''''
        Store and write all archived metis projects
        '''
        with open(filename, "r") as file:
            for line in file:
                
                # Temp dict to store archived project data
                metis_projects = {
                    "group_title": None,
                    "PI" : None, 
                    "group_member_count": None 
                }

                for pi in self.disabled_pis:
                    if line.startswith(pi):             
                        line = line.replace(pi + "-members:", "")
                        line = line.replace(" ", "")
                        members = line.strip().split(",")

                        metis_projects = {
                            "group_title": pi,
                            "PI" : pi, 
                            "group_member_count": len(members)  
                        }

                        self.archived_metis_projects.append(metis_projects)

        with open("archived_metis_projects.txt", "w") as file:
            for value in self.archived_metis_projects:
                formatted_value = pprint.pformat(value)  
                file.write(formatted_value + "\n") 
                file.write("" + "\n")  
        
    def write_active_pis(self, filename="./metis_project_groups.txt")->None:
        '''
        Write all active pis to active_pis.txt
        
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
        This function leverages a regex expression to read the file
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
        Handles the extracted PI and team members 
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
                    "group_title": key[:-3],
                    "PI" : value, 
                    "group_member_count": None,
                    "PI_name": None,
                    "PI_department": None,
                    "PI_email": None,
                    "description": None,
                    "group_members": None,
                    "pi_last_login":  None
                }
                self.active_metis_projects.append(project)
                        
            if key.endswith("-members"):
                group_title = key[:-8]
                group_members = value
                member_count = len(value.split(","))
                
                for project in self.active_metis_projects:
                    if project["group_title"] == group_title:
                        project["group_member_count"] = member_count
                        project["group_members"] = group_members

    def assign_pi_name_and_department(self)->None:
        '''
        Cross references the PI, with data in metis_users.csv
        to assign the PIs email and department info in active_metis_projects
        '''
        with open("/opt/metis/el8/contrib/accounting/metis_active_users_and_pis/metis_users.csv", "r") as file:
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
        
        with open("/opt/metis/el8/contrib/accounting/metis_active_users_and_pis/metis_pis.csv", "r") as file:
            for line in file:
                values = line.split(",")
                for data in self.active_metis_projects:
                    if data["PI_department"] == "":
                        if(data["PI_name"] == values[0]):
                            data["PI_department"] = values[3]
    
    def get_pi_last_log(self, pi_email, filename="/opt/metis/el8/contrib/accounting/metis_active_users_and_pis/metis_pi_lastlog.csv")->str:
        '''
        Iterate through metis_pi_lastlog.csv, and return the PIs last login date
        '''
        with open(filename, "r") as file:
            for line in file:                
                line = line.split(",")
                
                if str(pi_email).strip() == str(line[1]).strip():
                    last_login = line[2] 
                    return last_login.strip()  
    
    def assign_pi_last_log(self)->None:
        '''
        Add the PIs last log to the PIs group
        '''
        for project in self.active_metis_projects:
            if project["PI"] in self.active_pis:
                pi_last_log = self.get_pi_last_log(pi_email=project["PI_email"])
                project["pi_last_login"] = pi_last_log
    
    def assign_project_descriptions(self)->None:
        ''''
        Assign the group their project description
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
        Helper function to identify consecutive lines where 
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

    def pis_and_projects(self, filename="./metis_project_description.txt") -> None:
        '''
        Retrieves the data for PIs and the projects they are working on
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
                    
                    # Ensure PI is in the dictionary
                    if current_pi not in self.pi_and_project_descriptions:
                        self.pi_and_project_descriptions[current_pi] = []

                # Append the description for the PI
                elif line.startswith('description: DESCRIPTION=') and current_pi is not None:
                    description = line[len('description: DESCRIPTION='):].strip()
                    
                    # Only add the description if it's not already in the list
                    if description not in self.pi_and_project_descriptions[current_pi]:
                        self.pi_and_project_descriptions[current_pi].append(description)
                
                # Handle scenario where a project description appears on a new line
                elif not line.startswith('description:') and current_pi is not None and line.strip():
                    if self.pi_and_project_descriptions[current_pi]:
                        last_description = self.pi_and_project_descriptions[current_pi][-1]

                        # Avoid adding duplicates caused by multi-line descriptions
                        updated_description = last_description + ' ' + line.strip()
                        
                        # Update last description if it hasn't changed, otherwise append
                        if updated_description not in self.pi_and_project_descriptions[current_pi]:
                            self.pi_and_project_descriptions[current_pi][-1] = updated_description

    def pis_missing_description_helper(self)->None:
        ''''
        Handles PIs that have missing descriptions 
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
                
    def resolve_pi_department_discrepancy(self)->None:
        ''''
        In the data we are working with some PIs
        department data is not found, this function resolves this problme
        '''
        for project in self.active_metis_projects:
            if project["PI"] in self.missing_pi_department:
                project_pi = project["PI"]
                project["PI_department"] = self.missing_pi_department[project_pi]
                
    def fetch_active_metis_projects(self)->None:
        '''
        Read the contents of the file and sort its contents

        filename: The file contents to be read
        '''

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
        
        # Resolve PI missing department problem
        self.resolve_pi_department_discrepancy()
        
        # Write all archived metis projects
        self.write_archived_metis_projects()
        
        # Get the PIs last login
        self.assign_pi_last_log()

    def write_active_metis_projects(self, data, filename)->None:
        ''''
        Write the active metis project data to filename
        ''' 
        with open(filename, "w") as file:
            for value in data:
                formatted_value = pprint.pformat(value)  
                file.write(formatted_value + "\n") 
                file.write("" + "\n")  
           
    def write_pis_and_project_descriptions(self, data, filename)->None:
        ''''
        Write the pis and their project descriptions to filename
        '''
        with open(filename, "w") as file:
            for pi, descriptions in data.items():
                formatted_data = f"{pi}:\n{pprint.pformat(descriptions, indent=4)}\n\n"
                file.write(formatted_data)
    
    def valid_project_count(self)->int:
        '''
        Return the number of projects without 'None' entries
        
        '''
        project_count: int = 0
        
        for group in self.active_metis_projects:
            if group['PI_name'] is None or \
                group['PI_department'] is None or \
                group['PI_department'] == "" or \
                group["group_member_count"] is None or \
                group['description'] == "No description found" or \
                group["group_title"] in self.archived_metis_projects or \
                group["group_title"] in self.archived_metis_projects:
            
                # If any None entries, it is considered a "black list" project
                self.black_list_projects.append(group)
                continue
            else:  
                project_count += 1
            
        return project_count
    
    def update_project_descriptions(self)->None:
        '''
        Iterate through active_metis_projects, and update all projects with their most recent description
        '''
        for group in self.active_metis_projects:
            group_title = str(group["group_title"]).upper()

            if group_title in self.updated_project_descriptions:
                group["description"] = self.updated_project_descriptions[group_title]

    def write_web_metis_project_data(self, filename="web_project_html.txt")->None:
        '''
        write_web_metis_project_data: Iterate through the project data and format as html data
        ''' 
        with open(filename, "w") as file:
            
            file.write(f"""
                <div class="top-text">
                    <h1 class="header-text">CRCD Supported Research Projects</h1>
                    <h2 class="header-text">Total Number of Active Research Projects: {self.valid_project_count()}</h2>
                </div>   
                <div class="inner-body">               
            """)
            
            for group in self.active_metis_projects:
                
                if group['PI_name'] is None or \
                   group['PI_department'] is None or \
                    group['PI_department'] == "" or \
                   group["group_member_count"] is None or \
                   group['description'] == "No description found" or \
                   group["group_title"] in self.archived_metis_projects:
                    continue
                
                else:    
                    # Capitalize first letter of group title
                    group_title = str(group['group_title']).upper()
                    
                    # Embed the project data within html
                    group_as_html = f""" 
                        <div class="project">
                            <h2> { group_title } </h2> 
                            <p>  { group['PI_name'] } ({ group['PI_department'] })</p>
                            <p><i>{ group['description'] }</i></p>
                            <p>  Group Members: { group['group_member_count'] } </p>
                        </div>
                    """
                    # Write the html formatted data
                    file.write(group_as_html)
        
            file.write("</div>")
        # Copy the formatted html to the public directory
        copy_html_to_public = subprocess.run(
            ["cp", "./web_project_html.txt", "/var/www/html/pub/metis_projects"]
        )   
                                     
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

    # Write the active metis projects data
    metis_projects.write_active_metis_projects(metis_projects.active_metis_projects, "./web_metis_project_data.txt")
    
    # Write the PIs and their project descriptions
    metis_projects.write_pis_and_project_descriptions(metis_projects.pi_and_project_descriptions, "./web_metis_pi_project_descriptions.txt")
    
    # Update Metis projects with the most recent project descriptions
    metis_projects.update_project_descriptions()

    # Write the project data as html data
    metis_projects.write_web_metis_project_data()

if __name__ == "__main__":
    '''
    python3 get_projects.py or ./get_projects.py
    '''
    main()