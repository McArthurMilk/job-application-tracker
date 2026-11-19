# Job Application Tracker

A web app for tracking job applications, built with **MySQL**, **Python/Flask**, and **HTML/CSS**.

## Features
- **Dashboard** – totals for companies, jobs, applications and contacts, applications by status, and recent applications
- **Companies, Jobs, Applications, Contacts** – full CRUD (add, view, edit, delete with confirmation) with form validation
- **Job Match** – enter your skills and see every job ranked by the percentage of its required skills you have, plus which skills you're missing
- JSON columns: `jobs.requirements` stores the list of required skills, `applications.interview_data` stores interview details

## Project Structure
```
job_tracker/
├── app.py              # Flask routes (CRUD + dashboard + job match)
├── database.py         # Database connection and query helpers
├── schema.sql          # Creates the database, 4 tables, and sample data
├── requirements.txt    # Python dependencies
├── templates/          # HTML pages (base, dashboard, companies, jobs, applications, contacts, job_match)
├── static/style.css    # Styles
├── AI_USAGE.md         # GenAI documentation
└── README.md
```

## Setup Instructions

### 1. Requirements
- Python 3.8 or newer
- MySQL 8.0 (MySQL Server running locally)

### 2. Clone the repository
```bash
git clone <your-repo-url>
cd job_tracker
```

### 3. Install Python packages
```bash
pip install -r requirements.txt
```

### 4. Open the database

Open `schema.sql` in MySQL Workbench and run the whole script.


### 5. Set your MySQL password
Open `database.py` and replace `YOUR_PASSWORD` with your MySQL root password:
```python
"password": os.environ.get("DB_PASSWORD", "YOUR_PASSWORD"),
```
Or, instead of editing the file, set an environment variable before running:
- macOS/Linux: `export DB_PASSWORD=yourpassword`
- Windows (PowerShell): `$env:DB_PASSWORD="yourpassword"`

`DB_HOST`, `DB_USER` and `DB_NAME` can be set the same way if yours differ from `localhost`, `root` and `job_tracker`.

### 6. Run the app
```bash
python app.py
```
Then open **http://127.0.0.1:5000** in your browser.

## Using the App
1. Add a **company** first; jobs and contacts are linked to a company.
2. Add **jobs** for that company. Enter required skills separated by commas (e.g. `Python, SQL, Flask`).
3. Track **applications** for each job, including status, resume version, and optional interview details.
4. Add **contacts** you know at each company.
5. Use **Job Match** to type your skills and see which jobs fit you best.

Deleting a company also deletes its jobs, contacts, and the applications for those jobs (`ON DELETE CASCADE`). You'll be asked to confirm first.

## Database Design
| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `companies` | company_id (PK), company_name | — |
| `jobs` | job_id (PK), job_title, requirements (JSON) | company_id → companies |
| `applications` | application_id (PK), application_date, status, interview_data (JSON) | job_id → jobs |
| `contacts` | contact_id (PK), contact_name | company_id → companies |

## Troubleshooting
- **`Access denied for user 'root'@'localhost'`** – the password in `database.py` doesn't match your MySQL password.
- **`Unknown database 'job_tracker'`** – run `schema.sql` (step 4).
- **`Can't connect to MySQL server`** – make sure the MySQL service is running.
- **`ModuleNotFoundError: No module named 'flask'`** – run `pip install -r requirements.txt`.
