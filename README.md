# Rewwwind

App development project

### Team Members

- Benny
- Nelson
- Ryan
- Femina

### Prerequisites

- Above python 3.10 should do

### How to run

**IMPORTANT: Run the project in virutal environment when testing, and please read "How to commit changes" before making any changes.**
1. Clone this repository: `git clone https://github.com/bennygdev/rewwwind.git`
2. Open this project: cd into the directory and do `code .`
3. Install dependencies: Run `pip install -r requirements.txt` in project **virtual environment**. To access virutal environment, create a virtual environment (if you do not have a venv folder) by running `python -m venv .venv` then activate venv by running `.venv\Scripts\activate`, then run the installation command. To exit, run `deactivate` inside of **virtual environment**.
4. Run the project: In the **virtual environment**, Run `python main.py` to run the website.

### To save new libraries to virtual environment
1. Go into the project **virtual environment** via terminal
2. Install necessary packages
3. Do `pip freeze > requirements.txt` after you are done installing packages
4. Update and commit requirements.txt to github, by doing `git add .` and doing `git commit -m "message"`

### How to commit changes (IMPORTANT)
**NOTE: Before running the app in a new branch, please do so in a virtual environment.**
1. Before you make any changes, please **create a new branch** from the main branch by doing `git checkout -B yourname` in your terminal
2. Proceed to open the project by doing `code .` this should open your branch of the project.
3. To save changes, do `git add .` > `git commit -m "message"` > `git push origin yourbranchname`
4. Go to the Github, to the team repository and go to your branch. There should be a box saying that you have recent pushes. There should be a button that says **"Compare & Pull Request"**. Click on it to make a new request for the leader to approve and make suggestions to. 
5. If there is a suggestion, you can make changes to your project branch again and update the push with git add etc. in the pull request, the change should **remain in the same pull request**.
6. After your pull request has been approved and merged, **delete the branch** and switch back to the main repository. Do `git pull` on the main branch to update your vscode with the latest changes and you can run the website from there, but remember **do not edit the main branch if you are editing/making changes**.