import requests as re
# TODO: add async lib to speed up process
from dateutil import parser
import pytz
import os
import sys
import argparse

import pandas as pd

import config

# The version of API and the type of header hardcoded here
# See https://docs.github.com/en/rest or README for additional info
headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {config.TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28',
}


def get_branch_committers(owner: str, start_date: str, end_date: str, repository_name: str, branch_name: str) -> set:
    """
    Get list of committers to the branch in given repo in given period
    Args:
        owner: owner of the repo
        start_date: ISO8601 date
        end_date: ISO8601 date
        repository_name: legal name of the repo
        branch_name: name of a branch in repo

    Returns:
        set of pairs (email, github_nickname) for all committers
    """
    # print(f"Branch {branch_name}")
    url_commits = f"https://api.github.com/repos/{owner}" \
                  f"/{repository_name}/commits?sha={branch_name}&since={start_date}&until={end_date}"

    r = re.get(url_commits, headers=headers)

    if r.status_code != 200:
        raise Exception(f"Error: {r.status_code}")

    obj = r.json()

    successful_committers = set()

    for commit in obj:
        commit = commit["commit"]
        author_email = commit["author"]["email"]
        author_nickname = commit["author"]["name"]

        # print(f"What come from API {commit['committer']['date']},\n\t What I have after conv {cur}")

        successful_committers.add((author_email, author_nickname))

        if commit['committer']['email'] != author_email:
            successful_committers.add((commit['committer']['email'], commit['committer']['name']))

    return successful_committers


def get_repo_committers(owner: str, start_date: str, end_date: str, repository_name: str) -> set:
    """
    Get list of committers to the repo in given period (in all branches)
    Args:
        owner: legal repo owner name
        start_date: ISO8601 date
        end_date: ISO8601 date
        repository_name: legal repo name

    Returns:
        set of pairs (email, github_nickname) for all committers
    """
    url_branches = f"https://api.github.com/repos/{owner}/{repository_name}/branches"

    r = re.get(url_branches, headers=headers)

    if r.status_code != 200:
        raise Exception(f"Error: {r.status_code}")

    obj = r.json()
    committers = set()
    for branch in obj:
        successful_committers = get_branch_committers(owner, start_date, end_date, repository_name, branch['name'])
        committers.update(successful_committers)

    return committers


def get_author_repos_committers(owner: str, start_date: str, end_date: str, repos_list: list = None) -> set:
    """
    Get list of committers to the repos from target list in given period (in all branches)
    Args:
        owner: legal repo owner name
        start_date: ISO8601 date
        end_date: ISO8601 date
        repos_list: list of repositories to check

    Returns:
        set of pairs (email, github_nickname) for all committers
    """
    authors = set()
    for repository_name in repos_list:
        authors.update(get_repo_committers(owner, start_date, end_date, repository_name))

    return authors


def get_list_of_repos(user: str, template: str) -> list:
    """
    Get list of repos from user or organisation with given template in name
    Args:
        user: legal GitHub username
        template: string template, e.g. "cs190b"

    Returns:
        list of strings - repos names
    """
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

    # move return in while to speed up process (then only first page will be checked)
    # (since chances that some repo will be not in 100 top of updates
    # but will be updated in last week and available for checker user
    # are not very high for now (124 repos in total for me)
    return repos


def update_table(committers: set, df: pd.DataFrame, period_num: int = 1, score: int = 5):
    """
    Updates score in target column for everyone who commited smth
    Mathed by email
    Args:
        committers: set of strings - emails
        df: pandas dataframe with table od scores
        period_num: Column number(of week) to update
        score: Default score to add

    Returns:
        None
    """
    raise NotImplementedError("Canvas and emails issue")
    # TODO: add period search based on empty/non existent columns with template
    emails = set(df["email"])
    for email, nickname in committers:
        # TODO: apparently canvas do not have emails, just usernames (part of ucsb emails)
        # so we need to split our results on ucsb and non-ucsb, add ucsb, manuall search for non
        # preferably force github to give ucsb emails
        if email not in emails:
            print(f"Committer {email}, aka {nickname} not found in grades")
            continue
        df.loc[df["email"] == email, config.column_template.format(period_num)] = score
        # print(f"Added score for {email}")


def run():
    """
    Main function
    """
    # Dates preprocessing
    if config.DATE_END.lower() == "now":
        end = pd.Timestamp.now(tz="US/Pacific")
    else:
        end = parser.parse(config.DATE_END).replace(tzinfo=pytz.timezone('US/Pacific'))

    if config.DATE_START is None:
        start = end - pd.Timedelta(days=7)
    else:
        start = parser.parse(config.DATE_START).replace(tzinfo=pytz.timezone('US/Pacific'))

    start = start.isoformat()
    end = end.isoformat()

    # Repos list preprocessing
    if not config.repos_list:
        config.repos_list = get_list_of_repos(config.user_name, config.repos_template_name)
    elif isinstance(config.repos_list, str):
        with open(config.repos_list, "r") as f:
            config.repos_list = f.read().splitlines()
    # Actual work, finally
    authors = get_author_repos_committers(config.user_name, start, end, config.repos_list)

    # Output
    if config.output_format == "add":
        # File have to have email column for match up
        if not os.path.exists(config.filename):
            raise FileNotFoundError(f"File {config.filename} is not there, sorry")

        df = pd.read_csv(config.filename)
        update_table(authors, df)
        df.to_csv(config.filename, index=False)
    else:
        with open(f"{config.filename}", "w") as f:
            f.writelines([f"{nick}, {email}\n" for email, nick in authors])
    print(f"File {config.filename} updated successfully")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--start", help="Start date in format YYYY-MM-DD HH:MM:SS", default=None,
                            type=str, required=False)
    arg_parser.add_argument("--end", help="End date in format YYYY-MM-DD HH:MM:SS or 'now'", default="now",
                            type=str, required=False)
    arg_parser.add_argument("--user", help="Organization or user name", default="ucsb", type=str, required=False)
    arg_parser.add_argument("--template", help="Template for repos name", default="cs190b", type=str, required=False)
    arg_parser.add_argument("--repos-list", help="Path to repos list if such created (newline-separated),"
                                                 " or `None` for automatic collection", default=None, required=False)

    arg_parser.add_argument("--output-format", help="`add` for adding to existing csv file "
                                                    "or `list` to text saving the list of committed emails",
                            choices=['add', 'list'], default="add", type=str, required=False)
    arg_parser.add_argument("--filename", help="Filename to add scores to", default="my_class_grades.csv",
                            required=False)
    arg_parser.add_argument("--column-template", help="Template for column that will be used in table",
                            default="GitHub check Week N", required=False)
    arg_parser.add_argument("--score-for-period", help="Students score for doing a commit in a period", default=5,
                            type=int, required=False)
    args = arg_parser.parse_args()

    # print(args)
    if len(sys.argv) > 2:
        config.TOKEN = os.environ.get("GITHUB_TOKEN")
        config.DATE_START = args.start
        config.DATE_END = args.end
        config.user_name = args.user
        config.repos_template_name = args.template
        config.repos_list = args.repos_list
        config.output_format = args.output_format
        config.filename = args.filename
        config.column_template = args.column_template
        config.score_for_period = args.score_for_period
    else:
        print("No arguments provided, using config file")
    run()
