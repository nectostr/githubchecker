import requests as re
from datetime import datetime, timezone
from dateutil import parser

import pytz

import config

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {config.TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28',
}

format = "%Y-%m-%dT%H:%M:%SZ"
start = datetime.strptime(config.DATE_START, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('US/Pacific'))
end = datetime.strptime(config.DATE_END, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('US/Pacific'))

print(f"{start=}, {end=}")

def get_authors_branch(owner, repository_name, branch_name):
    print(f"Branch {branch_name}")
    url_commits = f"https://api.github.com/repos/{owner}/{repository_name}/commits/{branch_name}"

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
        # cur = cur.replace(tzinfo=timezone.utc)
        cur = cur.astimezone(pytz.timezone('US/Pacific'))

        
        print(f"What come from API {commit['committer']['date']},\n\t What I have after conv {cur}")
        if cur >= start and cur <= end:
            successeful_committers.add((author_email, author_nikname))
            
            if commit['committer']['email'] != author_email:
                successeful_committers.append((commit['committer']['email'], commit['committer']['name']))

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
    
    
    
    
 


if __name__ == "__main__":
    owner = "nectostr"
    repository_name = "githubchecker"

    print(get_authors(owner, repository_name))