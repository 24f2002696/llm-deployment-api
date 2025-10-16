from github import Github
import os
import time

def deploy_to_github(task, files, email, round_num):
    """Deploy files to a GitHub repo (create new for round 1, update for round 2+)"""
    
    github_token = os.environ.get('GITHUB_TOKEN')
    g = Github(github_token)
    user = g.get_user()
    
    # Create repo name (without round number - same repo for all rounds)
    repo_name = f"{task}".replace('/', '-').replace(' ', '-')
    
    if round_num == 1:
        # Round 1: Create new repo
        print(f"Round 1: Creating new repo: {repo_name}")
        
        # Check if repo exists and delete if it does (for testing)
        try:
            existing_repo = user.get_repo(repo_name)
            print(f"Repo {repo_name} exists, deleting...")
            existing_repo.delete()
            time.sleep(2)
        except:
            pass
        
        # Create new public repo
        repo = user.create_repo(
            repo_name,
            description=f"Auto-generated app for {task}",
            private=False,
            auto_init=False
        )
        
        # Add files to repo
        print(f"Adding files to repo...")
        for filename, content in files.items():
            repo.create_file(
                filename,
                f"Add {filename}",
                content,
                branch="main"
            )
    else:
        # Round 2+: Update existing repo
        print(f"Round {round_num}: Updating existing repo: {repo_name}")
        
        try:
            # Try to get repo without round number first
            repo = user.get_repo(repo_name)
        except:
            # If not found, try with round 1 suffix (for backwards compatibility)
            try:
                round1_name = f"{task}-round1".replace('/', '-').replace(' ', '-')
                print(f"Repo {repo_name} not found, trying {round1_name}")
                repo = user.get_repo(round1_name)
                # Update the repo name variable for later use
                repo_name = round1_name
            except Exception as e:
                print(f"Error fetching repo: {e}")
                raise
        
        # Update files in repo
        print(f"Updating files in repo...")
        for filename, content in files.items():
            try:
                # Try to get existing file
                existing_file = repo.get_contents(filename, ref="main")
                # Update existing file
                repo.update_file(
                    filename,
                    f"Update {filename} for round {round_num}",
                    content,
                    existing_file.sha,
                    branch="main"
                )
                print(f"Updated {filename}")
            except:
                # File doesn't exist, create it
                repo.create_file(
                    filename,
                    f"Add {filename}",
                    content,
                    branch="main"
                )
                print(f"Created {filename}")
    
    # Get commit SHA
    commits = repo.get_commits()
    commit_sha = list(commits)[0].sha
    
    # Enable GitHub Pages via REST API (only needed for round 1)
    if round_num == 1:
        print(f"Enabling GitHub Pages...")
        try:
            url = f"{repo.url}/pages"
            headers = {"Accept": "application/vnd.github.v3+json"}
            payload = {"source": {"branch": "main", "path": "/"}}
            
            repo._requester.requestJsonAndCheck("POST", url, input=payload, headers=headers)
            print("GitHub Pages enabled successfully")
            time.sleep(3)
        except Exception as e:
            print(f"GitHub Pages may already be enabled or error occurred: {e}")
    
    # Construct URLs
    repo_url = repo.html_url
    pages_url = f"https://{user.login}.github.io/{repo_name}/"
    
    print(f"Deployment complete!")
    print(f"Repo: {repo_url}")
    print(f"Pages: {pages_url}")
    
    return repo_url, commit_sha, pages_url