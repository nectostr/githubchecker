# Githubchecker
### A project to automatically check repos on updates in specific date range

## General Logic
1. *Find target*  
Find a list of target repos (upload from file or find automatically by certain pattern)
2. *Collect data*  
Work through the repos and collect active committers in the certain period of time
3. *Provide results*  
Just print committers emails (option list) or add scores of the committers to existing csv file (add option)

## Initializing on start
1. Get a token from https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token  
Provide read writes on repos/projects and users for this token  
See list in the end

2. https://github.com/settings/tokens - authorize token for UCSB organization  
TODO: check what permissions are really necessary

3. Make sure python 3.6+ installed. Also install requirements
(pandas only?)

## Usage
Essentially to options - get the arguments to run from a config file or add them as arguments in command line and environment variables

### OPTION 1. Config
** Very beginner-friendly and easy to use **
1. Go to config template file. Rename it to 'config.py'. Add the token (see step 1 of Initialization)
2. Edit the dates (see example in config)
3. Edit the name of the file with future grades
4. Edit everything else that needed to be specialized, see config_template for details
5. run `python main.py`  
Please check the config or Option 2 for advances arguments explanation.

### OPTION 2. Script-style way
**Better for docker and generally more sophisticated**
1. Add token to your environment variables with name 'GITHUB_TOKEN'
2. run `python main.py --file <filename> --start <start_date> --end <end_date>`
e.g.  
`python main.py --end=now --output-format=list --filename=test.txt`  
or  
`python main.py --start='2023-01-01 00:00:00' --end='2023-01-09 23:59:59' --filename=cs190b_grades.csv`  
**Attention:** Zero arguments will cause config-file run (see above)
Use `--help` to see all the options
```
usage: main.py [-h] [--start START] [--end END] [--user USER] [--repos-list REPOS_LIST] [--template TEMPLATE] [--output-format {add,list}] [--filename FILENAME]
               [--column-template COLUMN_TEMPLATE] [--score-for-period SCORE_FOR_PERIOD]

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start date in format YYYY-MM-DD HH:MM:SS or 'None' for minus week from $end
  --end END             End date in format YYYY-MM-DD HH:MM:SS or 'now'
  --user USER           Legal GitHub organization or user name
  --repos-list REPOS_LIST
                        Path to repos list if such created (newline-separated), or `None` for automatic collection
  --template TEMPLATE   Template for repos name (all repo names that contain this line will be targeted), e.g. 'cs190b'
  --output-format {add,list}
                        `add` for adding to existing csv file or `list` to text saving the list of committed emails
  --filename FILENAME   Filename to add scores to
  --column-template COLUMN_TEMPLATE
                        Template for column that will be used in table
  --score-for-period SCORE_FOR_PERIOD
                        Students score for doing a commit in a period

```

______________________________________________________________________________________
## Code structure
### File work
Works with pandas and adds the scores of found users to table  
TODO: Update expected  
Functions:
- update_table

### Collect repos names
One function that grabs repos by target organization/user and template  
Functions:
- get_authors_repos

### Collect commits authors
Functions that responsible for getting list of commits in all branches in target repo and parse and collect authors names  
Functions:
- get_authors_branch
- get_authors_repo
- get_authors_repos

## P.S. I am genuinely sorry for not creating logger, but I am way too lazy for that
For now it is commented out prints

## List of permissions for token
I suggest giving the full rights with the thought of a future, but some "write" rights might be revoked
Note that you and only you will have an access to this key, not me as an code author
List of provided rights:
- repo - Full control of private repositories 
- admin:repo_hook - Full control of repository hooks 
- user - Update ALL user data 
- project - Full control of projects 