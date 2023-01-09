import requests as re
import datetime

import config

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {config.TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28',
}

format = "%Y-%m-%dT%H:%M:%SZ"
start = datetime.datetime.strptime(config.DATE_START, format)
end = datetime.datetime.strptime(config.DATE_END, format)


def get_authors(url):
    """
    Get authors from single github url

    Args:
        url (str): _description_

    Raises:
        Exception: _description_

    Returns:
        set: set of tuples - (commiters email, commiters nickname)
    """
    r = re.get(url, headers=headers)

    if r.status_code != 200:
        raise Exception(f"Error: {r.status_code}")

    obj = r.json()

    successeful_committers = set()

    for commit in obj:
        commit = commit["commit"]
        author_email = commit["author"]["email"]
        author_nikname = commit["author"]["name"]
        

        cur = datetime.datetime.strptime(commit['committer']['date'], format)
        
        if cur >= start and cur <= end:
            successeful_committers.add((author_email, author_nikname))
            
            if commit['committer']['email'] != author_email:
                successeful_committers.append((commit['committer']['email'], commit['committer']['name']))

    return successeful_committers


if __name__ == "__main__":
    owner = "nectostr"
    repository_name = "githubchecker"
    url = f"https://api.github.com/repos/{owner}/{repository_name}/commits"

    print(get_authors(url))