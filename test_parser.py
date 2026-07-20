from utils.jobs_api import fetch_live_jobs

jobs = fetch_live_jobs(query="python developer", location="India", results_count=3)

for job in jobs:
    print(job["title"], "-", job["company"])
    print(job["redirect_url"])
    print("---")