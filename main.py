import requests as re
from dateutil import parser
import pytz
import os

import pandas as pd

import config

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {config.TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28',
}

start = parser.parse(config.DATE_START).replace(tzinfo=pytz.timezone('US/Pacific'))
end = parser.parse(config.DATE_END).replace(tzinfo=pytz.timezone('US/Pacific'))

print(f"{start=}, {end=}")

def get_authors_branch(owner, repository_name, branch_name):
    print(f"Branch {branch_name}")
    url_commits = f"https://api.github.com/repos/{owner}/{repository_name}/commits?sha={branch_name}"

    r = re.get(url_commits, headers=headers)

    if r.status_code != 200:
        raise Exception(f"Error: {r.status_code}")

    obj = r.json()

    successeful_committers = set()

    for commit in obj:
        commit = commit["commit"]
        author_email = commit["author"]["email"]
        author_nikname = commit["author"]["name"]
        

        cur = parser.parse(commit['committer']['date'])
        cur = cur.astimezone(pytz.timezone('US/Pacific'))

        
        print(f"What come from API {commit['committer']['date']},\n\t What I have after conv {cur}")
        if cur >= start and cur <= end:
            successeful_committers.add((author_email, author_nikname))
            
            if commit['committer']['email'] != author_email:
                successeful_committers.add((commit['committer']['email'], commit['committer']['name']))

    return successeful_committers

def get_authors(owner, repository_name):
    """
    Get authors from single github url

    Args:
        url (str): _description_

    Raises:
        Exception: _description_

    Returns:
        set: set of tuples - (commiters email, commiters nickname)
    """
    
    url_branches = f"https://api.github.com/repos/{owner}/{repository_name}/branches"
    
    r = re.get(url_branches, headers=headers)

    if r.status_code != 200:
        raise Exception(f"Error: {r.status_code}")
    
    obj = r.json()
    committers = set()
    for branch in obj:
        successeful_committers = get_authors_branch(owner, repository_name, branch['name'])
        committers.update(successeful_committers)
    
    return committers

def create_table(filename: str):
    df = pd.DataFrame(columns=['email', 'GithubCheck Week 1'])
    df.to_csv(filename, index=False)
    
    

def update_table(committers: set, df: pd.DataFrame, period_num=1, score=5):
    
    emails = set(df["email"])
    for email, nickname in committers:
        if email not in emails:
            print(f"Commiter {email}, aka {nickname} not found in grades")
            continue
        df.loc[df["email"] == email,config.column_template.format(period_num)] = score
        # print(f"Added score for {email}")


if __name__ == "__main__":
    owner = "ucsb"
    repository_name = "CS190B-Lab2-ckrintz"

    authors = get_authors(owner, repository_name)
    
    # File have to have email column for match up
    if not os.path.exists(config.filename):
        create_table(config.filename)
    
    df = pd.read_csv(config.filename)
    update_table(authors, df)
    df.to_csv(config.filename, index=False)
    
    