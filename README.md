# Active Metis Projects

![Metis Projects Screenshot](https://github.com/user-attachments/assets/934a5723-65c5-47aa-8941-1db23f6741d7)

## Description

This project is built for the **Center for Research and Compute (CRCD)** at **NIU** to display active projects hosted on the **Metis Cluster**. Live project data is available [here](https://metis.niu.edu/pub/metis_projects/projects.php)

## Features

The script `get_projects.py` generates the following files on Metis:

- `active_pis.txt` – List of all active PIs  
- `disabled_pis.txt` – List of all disabled PIs  
- `archived_metis_projects.txt` – Projects owned by a disabled PI  
- `metis_project_description.txt` – Descriptions of all projects on Metis  
- `metis_project_groups.txt` – Raw output from IDAP, containing group data  
- `web_metis_pi_project_description.txt` – Project descriptions associated with each PI  
- `web_metis_project_data.txt` – Sorted project group data  
- `web_project_html.txt` – Project data rendered in HTML format  

## Data Format

Below is the structure of data stored in `web_metis_project_data.txt`:

```python
{
  'PI': 'The PI identifier',
  'PI_department': 'The PI\'s department',
  'PI_email': 'The PI\'s email',
  'PI_name': 'The PI\'s full name',
  'description': 'The project description',
  'group_member_count': 'Total number of group members',
  'group_members': 'List of Metis usernames in the group',
  'group_title': 'The project title',
  'pi_last_login': 'The last time the PI logged into Metis'
}
```

## Automation

This script is scheduled to run weekly using `cron`.

To edit the cron job, run:

```bash
crontab -e

# get_projects.py is run every Monday at 5:00 AM
0 5 * * 1 /path_to_this_on_metis/get_projects.py
```
