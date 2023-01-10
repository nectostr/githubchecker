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

start = parser.parse(config.DATE_START).replace(tzinfo=pytz.timezone('US/Pacific')).isoformat()
end = parser.parse(config.DATE_END).replace(tzinfo=pytz.timezone('US/Pacific')).isoformat()

def get_authors_branch(owner, repository_name, branch_name):
    print(f"Branch {branch_name}")
    url_commits = f"https://api.github.com/repos/{owner}" \
                  f"/{repository_name}/commits?sha={branch_name}&since={start}&until={end}"

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
        # if cur >= start and cur <= end:
        successeful_committers.add((author_email, author_nikname))

        if commit['committer']['email'] != author_email:
            successeful_committers.add((commit['committer']['email'], commit['committer']['name']))

    # move return in while to speed up process (then only first page will be checked)
    # (since chances that some repo will be not in 100 top of updates
    # but will be updated in last week and available for checker user
    # are not very high for now (124 repos in total for me)
    return successeful_committers

def get_authors_repo(owner, repository_name):
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

def get_authors_repos(owner:str="ucsb", repos_list:[list,None]=None):
    if not repos_list:
        repos_list = config.repos_list

    authors = set()
    for repository_name in repos_list:
        authors.update(get_authors_repo(owner, repository_name))

    return authors

def get_list_of_repos(user:str, template:str):
    repos = []
    got_repos_in_last_try = 100
    try_num = 1

    while got_repos_in_last_try == 100:
        # if you do have non-organisation, but user - use .com/users/{user}... instead
        url = f"https://api.github.com/orgs/{user}" \
              f"/repos?type=all&per_page=100&sort=updated&page={try_num}"
        try_num += 1

        r = re.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception(f"Error in getting list of repos: {r.status_code}")
        obj = r.json()
        # print(f"Try {try_num-1}, len of repos {len(obj)}")
        for repo in obj:
            if template in repo["name"].lower():
                repos.append(repo["name"])
        got_repos_in_last_try = len(obj)
    return repos

def create_table(filename: str):
    df = pd.DataFrame(columns=['email', 'GithubCheck Week 1'])
    df.to_csv(filename, index=False)


def update_table(committers: set, df: pd.DataFrame, period_num=1, score=5):
    emails = set(df["email"])
    for email, nickname in committers:
        if email not in emails:
            print(f"Commiter {email}, aka {nickname} not found in grades")
            continue
        df.loc[df["email"] == email, config.column_template.format(period_num)] = score
        # print(f"Added score for {email}")

def example_to_run():

    if not config.repos_list:
        config.repos_list = get_list_of_repos("ucsb", config.repos_template_name)

    authors = get_authors_repos()
    # File have to have email column for match up
    if not os.path.exists(config.filename):
        create_table(config.filename)

    df = pd.read_csv(config.filename)
    update_table(authors, df)
    df.to_csv(config.filename, index=False)


if __name__ == "__main__":
    do_not_check_list = ["CS190B-TestLab2"]
    repos = get_list_of_repos("ucsb", "cs190b")
    print(repos)
    repos = [i for i in repos if i not in do_not_check_list]
    print(repos)

