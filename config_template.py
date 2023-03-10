TOKEN = "YOUR-SECRET-TOKEN"
# See readme for creation link

user_name = "ucsb"  # Add user or organisation name here

DATE_START = "2023-01-01 00:00:00"  # ISO8601 date or 'None' for minus exactly week from end
DATE_END = "2023-01-09 23:59:59"  # ISO8601 date or 'now'

repos_list = None  # None for automatic repos collection,
# or create list manually (or read from file - newline-separated)
# repos_list = ['repo1', 'repo2', 'repo3']
# repos_list = 'repos.txt'
'''
repo1
repo2
repo3
'''

repos_template_name = "cs190b"  # for automatic repos collection
# (string that has to be part of repo name)

output_format = "add"  # "add" for adding to existing csv file, "list" to text saving the list of committed emails
column_template = "GitHub check Week {}"
filename = "cs190b_grades.csv"

score_per_period = 5  # For the automatic score update if that option picked
