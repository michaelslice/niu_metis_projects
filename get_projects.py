#!/usr/bin/env python3
import os
import sys
import subprocess
import re

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
    active_metis_projects = {
        "project_title": None,
        "PI" : None, 
        "group_member_count": None 
    }

    # Stores all Disabled PI's and their projects
    archived_metis_projects = {
        "project_title": None,
        "PI" : None, 
        "group_member_count": None 
    }

    extracted_data = {}

    print("Sorting File Contents!")
    with open(filename, "r") as file:

        for line in file:

            # Skip empty lines
            if not line:
                continue
            
            match = re.match(r"(\w+-(pi|members)):\s+(.*)", line)
            if match:
                key, _, value = match.groups()
                extracted_data[key] = value.strip()

        # Print extracted values
        for key, value in extracted_data.items():
            print(f"{key}: {value}")

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