#!/usr/bin/env python3
import os
import sys
import subprocess

def query_and_write_file(command, filename):
    '''
    query_and_write_file: Run a comand and write the results to a file

    command: Command to be executed
    filename: File to be written to
    '''
    # Execute the command on machine
    query_projects_output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    std_out = query_projects_output.stdout

    # Debug code
    # for line in std_out.splitlines():
    #     print(line)

    # Write the results to the file
    with open(filename, "a") as filename_description:
        filename_description.write(std_out)

    return std_out

def main():
    '''
    main: A script to get the active projects on Metis
    '''

    print("Getting Metis Projects")
    
    # Query idap for project descriptions
    # ldapsearch -Z -x -H ldap://pldapms.hpc.cls
    print("Getting Metis Project Descriptions")
    query_projects = "ldapsearch -Z -x -H ldap://pldapms.hpc.cls | grep description"
    query_and_write_file(query_projects, "metis_project_description.txt")

    # Get all Metis groups
    print("Getting Metis Project Groups")
    metis_groups = "cat /home/admin/data/account_reports/aliases.ldap.Feb1_011701"
    query_and_write_file(metis_groups, "metis_project_groups.txt")

if __name__ == "__main__":
    '''
    python3 get_projects.py or ./get_projects.py
    '''
    main()