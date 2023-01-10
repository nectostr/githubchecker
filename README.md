# Githubchecker
### A project to automatically check repos on updates in specific date range

## Initializing on start
1. https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
1.1. https://github.com/settings/tokens - authorize token for UCSB organization
TODO: check what permissions are really necessary

2. Make sure python 3.6+ installed. Also install requirements
(pandas only?)

## Usage
### OPTION 1. Config
** Very beginner-friendly and easy to use **
1. Go to config template file. Rename it to 'config.py'. Add the token (see step 1 of Initialization)
2. Edit the name of the file with future grades
3. Edit the dates (see example in config)
4. run python main.py

### OPTION 2. script-style way.
**Better for docker and generally more sophisticated**
1. Add token to your environment variables with name 'GITHUB_TOKEN'
2. run `python main.py --file <filename> --start <start_date> --end <end_date>`
e.g.
`python main.py --end=now --output-format=list --filename=test.txt`
or
`python main.py --start='2023-01-01 00:00:00' --end='"2023-01-09 23:59:59"' --filename=cs190b_grades.csv`
______________________________________________________________________________________
## Code structure
### File work
Works with pandas and adds the scores of found users to table
TODO: Update expected
Functions:
- create_table
- update_table

### Collect repos names
One function that grabs repos by target organization/user and template
Functions:
- get_authors_repos

### Collect commits authors
Functions that responsible for getting list of commits in all brances in target repo and parse and collect authers names
Functions:
- get_authors_branch
- get_authors_repo
- get_authors_repos

## P.S. I am genially sorry for not creating logger, but I am way to lazy for that