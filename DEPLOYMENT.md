
---

# 2. `Deployment.md`

```markdown
# Deployment Documentation

## 1. Overview

Smart Document & Image Toolkit is a Streamlit application that can be run locally or deployed using a Streamlit-compatible hosting platform.

The project source code is maintained in a Git repository.

---

## 2. Requirements

The deployment requires:

- Python
- Git
- Streamlit
- Required Python packages
- A GitHub repository for cloud deployment

Dependencies are defined in:

```text
requirements.txt
3. Project Structure
Smart-Document-Image-Toolkit/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
└── docs/
    ├── User_Manual.md
    ├── Developer_Documentation.md
    ├── Architecture.md
    ├── Deployment.md
    └── DFD.md
4. Local Deployment
Step 1: Open the project folder

Open a terminal in the project directory.

Step 2: Install dependencies
pip install -r requirements.txt
Step 3: Run the application
streamlit run app.py

The application will start locally and can be opened in a web browser.

5. Git Repository

The project uses Git for version control.

Check the current Git status:

git status

Add project changes:

git add .

Create a commit:

git commit -m "Update application"

Push changes to GitHub:

git push origin main
6. First-Time Git Setup

If Git has not previously been initialized:

git init

Add the project files:

git add .

Create the first commit:

git commit -m "Initial project commit"

Connect the local repository to GitHub:

git remote add origin <repository-url>

Push the project:

git branch -M main
git push -u origin main

git init and git remote add origin are normally one-time setup commands.

7. Updating an Existing Project

After changing app.py or documentation:

git status
git add .
git commit -m "Update application"
git push origin main

The normal development cycle is:

Modify Files
     ↓
Test Locally
     ↓
git status
     ↓
git add .
     ↓
git commit
     ↓
git push
     ↓
GitHub
     ↓
Streamlit Deployment
8. Streamlit Deployment

For cloud deployment, connect the GitHub repository to the Streamlit hosting service.

The main application file is:

app.py

The dependency file is:

requirements.txt

The deployment platform uses these files to build and run the application.

9. Deployment Configuration

The deployment should use:

Main file:
app.py

Dependencies:

requirements.txt

Python packages required by the application must be listed in requirements.txt.

10. Updating the Deployed Application

When the application is already connected to GitHub, update it by pushing new commits:

git status
git add .
git commit -m "Update application"
git push origin main

The hosting platform can detect the new GitHub commit and rebuild/redeploy the application according to its deployment configuration.

11. Deployment Testing

After deployment, test:

Image → PDF
Upload image
Test A4
Test Original
Create PDF
Download PDF
PDF → Image
Upload PDF
Test DPI
Test multi-page conversion
Test ZIP download
Scan Anything
Auto Crop
Perspective Correction
Each filter
Before/After preview
JPG download
PDF download
Compress Photo
Test different KB targets
Test maximum dimensions
Verify output file size
Download compressed image
PDF Tools
Merge
Compress
Split
Delete Pages
Reorder Pages
Rotate Pages
12. Troubleshooting
Application does not start

Run:

streamlit run app.py

Check the terminal for Python or dependency errors.

Missing package

Install dependencies again:

pip install -r requirements.txt
Git changes not appearing

Check:

git status

Then:

git add .
git commit -m "Update application"
git push origin main
Deployment build failure

Check:

requirements.txt
Python package names
Application logs
app.py errors
File paths
13. Security Considerations

Do not commit the following to Git:

Passwords
API keys
Access tokens
Private credentials
Sensitive personal documents
Temporary uploaded files

Use .gitignore to exclude unnecessary files.

14. Production Recommendations

For production deployment:

Keep dependencies updated.
Limit upload sizes.
Validate uploaded file types.
Avoid permanent storage of sensitive documents.
Monitor application memory usage.
Test every major feature after deployment.