"""Job Application Tracker - Flask application."""
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from database import query, execute

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # needed for flash messages

JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]
STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]


# ---------- Small helpers ----------

def load_json(value, default):
    """MySQL returns JSON columns as text, so turn them back into Python objects."""
    if value is None:
        return default
    if isinstance(value, (bytes, bytearray)):
        value = value.decode()
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return default
    return value


def blank_to_none(value):
    """Store empty form fields as NULL instead of an empty string."""
    value = (value or "").strip()
    return value or None


def to_int(value, label, errors):
    """Convert an optional form field to an int, recording an error if it isn't a whole number."""
    value = blank_to_none(value)
    if value is None:
        return None
    if not value.isdigit():
        errors.append(f"{label} must be a whole number.")
        return None
    return int(value)


@app.template_filter("blank")
def blank_filter(value):
    """Show None as an empty string in templates."""
    return "" if value is None else value


# ---------- Dashboard ----------

@app.route("/")
def dashboard():
    counts = {
        "companies": query("SELECT COUNT(*) AS n FROM companies", one=True)["n"],
        "jobs": query("SELECT COUNT(*) AS n FROM jobs", one=True)["n"],
        "applications": query("SELECT COUNT(*) AS n FROM applications", one=True)["n"],
        "contacts": query("SELECT COUNT(*) AS n FROM contacts", one=True)["n"],
    }
    by_status = query("SELECT status, COUNT(*) AS n FROM applications GROUP BY status")
    status_counts = {s: 0 for s in STATUSES}
    for row in by_status:
        status_counts[row["status"]] = row["n"]
    recent = query("""
        SELECT a.application_date, a.status, j.job_title, c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        LEFT JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC LIMIT 5
    """)
    return render_template("dashboard.html", counts=counts,
                           status_counts=status_counts, recent=recent)


# ---------- Companies ----------

def company_form():
    """Read the company form and return (data, errors)."""
    f = request.form
    data = {
        "company_name": blank_to_none(f.get("company_name")),
        "industry": blank_to_none(f.get("industry")),
        "website": blank_to_none(f.get("website")),
        "city": blank_to_none(f.get("city")),
        "state": blank_to_none(f.get("state")),
        "notes": blank_to_none(f.get("notes")),
    }
    errors = []
    if not data["company_name"]:
        errors.append("Company name is required.")
    if data["website"] and not data["website"].startswith(("http://", "https://")):
        errors.append("Website must start with http:// or https://")
    return data, errors


def show_companies(item=None, edit_id=None):
    companies = query("SELECT * FROM companies ORDER BY company_name")
    return render_template("companies.html", companies=companies,
                           item=item or {}, edit_id=edit_id)


@app.route("/companies", methods=["GET", "POST"])
def companies():
    if request.method == "POST":
        data, errors = company_form()
        if errors:
            for e in errors:
                flash(e, "error")
            return show_companies(item=data)
        execute("""INSERT INTO companies (company_name, industry, website, city, state, notes)
                   VALUES (%s, %s, %s, %s, %s, %s)""", tuple(data.values()))
        flash("Company added.", "success")
        return redirect(url_for("companies"))
    return show_companies()


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def edit_company(company_id):
    if request.method == "POST":
        data, errors = company_form()
        if errors:
            for e in errors:
                flash(e, "error")
            return show_companies(item=data, edit_id=company_id)
        execute("""UPDATE companies SET company_name=%s, industry=%s, website=%s,
                   city=%s, state=%s, notes=%s WHERE company_id=%s""",
                (*data.values(), company_id))
        flash("Company updated.", "success")
        return redirect(url_for("companies"))
    item = query("SELECT * FROM companies WHERE company_id=%s", (company_id,), one=True)
    if not item:
        flash("Company not found.", "error")
        return redirect(url_for("companies"))
    return show_companies(item=item, edit_id=company_id)


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def delete_company(company_id):
    execute("DELETE FROM companies WHERE company_id=%s", (company_id,))
    flash("Company deleted (along with its jobs, applications and contacts).", "success")
    return redirect(url_for("companies"))


# ---------- Jobs ----------

def job_form():
    f = request.form
    errors = []
    skills = [s.strip() for s in f.get("requirements", "").split(",") if s.strip()]
    data = {
        "company_id": to_int(f.get("company_id"), "Company", errors),
        "job_title": blank_to_none(f.get("job_title")),
        "job_type": blank_to_none(f.get("job_type")),
        "salary_min": to_int(f.get("salary_min"), "Minimum salary", errors),
        "salary_max": to_int(f.get("salary_max"), "Maximum salary", errors),
        "job_url": blank_to_none(f.get("job_url")),
        "date_posted": blank_to_none(f.get("date_posted")),
        "requirements": json.dumps(skills),
    }
    if not data["company_id"]:
        errors.append("Please choose a company.")
    if not data["job_title"]:
        errors.append("Job title is required.")
    if data["job_type"] and data["job_type"] not in JOB_TYPES:
        errors.append("Invalid job type.")
    if data["salary_min"] and data["salary_max"] and data["salary_min"] > data["salary_max"]:
        errors.append("Minimum salary cannot be greater than maximum salary.")
    if data["job_url"] and not data["job_url"].startswith(("http://", "https://")):
        errors.append("Job URL must start with http:// or https://")
    return data, errors


def show_jobs(item=None, edit_id=None):
    jobs = query("""
        SELECT j.*, c.company_name FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.date_posted DESC
    """)
    for job in jobs:
        job["skills"] = load_json(job["requirements"], [])
    item = dict(item or {})
    if "requirements" in item:  # show the skill list as "Python, SQL" in the form
        item["requirements"] = ", ".join(load_json(item["requirements"], []))
    companies = query("SELECT company_id, company_name FROM companies ORDER BY company_name")
    return render_template("jobs.html", jobs=jobs, companies=companies,
                           job_types=JOB_TYPES, item=item, edit_id=edit_id)


@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    if request.method == "POST":
        data, errors = job_form()
        if errors:
            for e in errors:
                flash(e, "error")
            return show_jobs(item=data)
        execute("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
                   job_url, date_posted, requirements)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", tuple(data.values()))
        flash("Job added.", "success")
        return redirect(url_for("jobs"))
    return show_jobs()


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    if request.method == "POST":
        data, errors = job_form()
        if errors:
            for e in errors:
                flash(e, "error")
            return show_jobs(item=data, edit_id=job_id)
        execute("""UPDATE jobs SET company_id=%s, job_title=%s, job_type=%s, salary_min=%s,
                   salary_max=%s, job_url=%s, date_posted=%s, requirements=%s
                   WHERE job_id=%s""", (*data.values(), job_id))
        flash("Job updated.", "success")
        return redirect(url_for("jobs"))
    item = query("SELECT * FROM jobs WHERE job_id=%s", (job_id,), one=True)
    if not item:
        flash("Job not found.", "error")
        return redirect(url_for("jobs"))
    return show_jobs(item=item, edit_id=job_id)


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    execute("DELETE FROM jobs WHERE job_id=%s", (job_id,))
    flash("Job deleted (along with its applications).", "success")
    return redirect(url_for("jobs"))


# ---------- Applications ----------

def application_form():
    f = request.form
    errors = []
    interview = {
        "interview_date": blank_to_none(f.get("interview_date")),
        "interviewer": blank_to_none(f.get("interviewer")),
        "notes": blank_to_none(f.get("interview_notes")),
    }
    has_interview = any(interview.values())
    data = {
        "job_id": to_int(f.get("job_id"), "Job", errors),
        "application_date": blank_to_none(f.get("application_date")),
        "status": f.get("status") or "Applied",
        "resume_version": blank_to_none(f.get("resume_version")),
        "cover_letter_sent": 1 if f.get("cover_letter_sent") else 0,
        "interview_data": json.dumps(interview) if has_interview else None,
    }
    if not data["job_id"]:
        errors.append("Please choose a job.")
    if not data["application_date"]:
        errors.append("Application date is required.")
    if data["status"] not in STATUSES:
        errors.append("Invalid status.")
    return data, errors


def show_applications(item=None, edit_id=None):
    apps = query("""
        SELECT a.*, j.job_title, c.company_name FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        LEFT JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC
    """)
    for a in apps:
        a["interview"] = load_json(a["interview_data"], {})
    item = dict(item or {})
    item["interview"] = load_json(item.get("interview_data"), {})
    jobs = query("""SELECT j.job_id, j.job_title, c.company_name FROM jobs j
                    LEFT JOIN companies c ON j.company_id = c.company_id
                    ORDER BY c.company_name, j.job_title""")
    return render_template("applications.html", applications=apps, jobs=jobs,
                           statuses=STATUSES, item=item, edit_id=edit_id)


@app.route("/applications", methods=["GET", "POST"])
def applications():
    if request.method == "POST":
        data, errors = application_form()
        if errors:
            for e in errors:
                flash(e, "error")
            return show_applications(item=data)
        execute("""INSERT INTO applications (job_id, application_date, status, resume_version,
                   cover_letter_sent, interview_data)
                   VALUES (%s, %s, %s, %s, %s, %s)""", tuple(data.values()))
        flash("Application added.", "success")
        return redirect(url_for("applications"))
    return show_applications()


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def edit_application(application_id):
    if request.method == "POST":
        data, errors = application_form()
        if errors:
            for e in errors:
                flash(e, "error")
            return show_applications(item=data, edit_id=application_id)
        execute("""UPDATE applications SET job_id=%s, application_date=%s, status=%s,
                   resume_version=%s, cover_letter_sent=%s, interview_data=%s
                   WHERE application_id=%s""", (*data.values(), application_id))
        flash("Application updated.", "success")
        return redirect(url_for("applications"))
    item = query("SELECT * FROM applications WHERE application_id=%s",
                 (application_id,), one=True)
    if not item:
        flash("Application not found.", "error")
        return redirect(url_for("applications"))
    return show_applications(item=item, edit_id=application_id)


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def delete_application(application_id):
    execute("DELETE FROM applications WHERE application_id=%s", (application_id,))
    flash("Application deleted.", "success")
    return redirect(url_for("applications"))


# ---------- Contacts ----------

def contact_form():
    f = request.form
    errors = []
    data = {
        "company_id": to_int(f.get("company_id"), "Company", errors),
        "contact_name": blank_to_none(f.get("contact_name")),
        "title": blank_to_none(f.get("title")),
        "email": blank_to_none(f.get("email")),
        "phone": blank_to_none(f.get("phone")),
        "linkedin_url": blank_to_none(f.get("linkedin_url")),
        "notes": blank_to_none(f.get("notes")),
    }
    if not data["company_id"]:
        errors.append("Please choose a company.")
    if not data["contact_name"]:
        errors.append("Contact name is required.")
    if data["email"] and "@" not in data["email"]:
        errors.append("Email address is not valid.")
    if data["phone"] and len(data["phone"]) > 20:
        errors.append("Phone number must be 20 characters or less.")
    if data["linkedin_url"] and not data["linkedin_url"].startswith(("http://", "https://")):
        errors.append("LinkedIn URL must start with http:// or https://")
    return data, errors


def show_contacts(item=None, edit_id=None):
    contacts = query("""
        SELECT ct.*, c.company_name FROM contacts ct
        LEFT JOIN companies c ON ct.company_id = c.company_id
        ORDER BY ct.contact_name
    """)
    companies = query("SELECT company_id, company_name FROM companies ORDER BY company_name")
    return render_template("contacts.html", contacts=contacts, companies=companies,
                           item=item or {}, edit_id=edit_id)


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        data, errors = contact_form()
        if errors:
            for e in errors:
                flash(e, "error")
            return show_contacts(item=data)
        execute("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
                   linkedin_url, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                tuple(data.values()))
        flash("Contact added.", "success")
        return redirect(url_for("contacts"))
    return show_contacts()


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def edit_contact(contact_id):
    if request.method == "POST":
        data, errors = contact_form()
        if errors:
            for e in errors:
                flash(e, "error")
            return show_contacts(item=data, edit_id=contact_id)
        execute("""UPDATE contacts SET company_id=%s, contact_name=%s, title=%s, email=%s,
                   phone=%s, linkedin_url=%s, notes=%s WHERE contact_id=%s""",
                (*data.values(), contact_id))
        flash("Contact updated.", "success")
        return redirect(url_for("contacts"))
    item = query("SELECT * FROM contacts WHERE contact_id=%s", (contact_id,), one=True)
    if not item:
        flash("Contact not found.", "error")
        return redirect(url_for("contacts"))
    return show_contacts(item=item, edit_id=contact_id)


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def delete_contact(contact_id):
    execute("DELETE FROM contacts WHERE contact_id=%s", (contact_id,))
    flash("Contact deleted.", "success")
    return redirect(url_for("contacts"))


# ---------- Job Match ----------

def match_jobs(user_skills):
    """Rank every job by the percentage of its required skills the user has."""
    have = {s.lower() for s in user_skills}
    jobs = query("""SELECT j.job_id, j.job_title, j.requirements, c.company_name
                    FROM jobs j LEFT JOIN companies c ON j.company_id = c.company_id""")
    results = []
    for job in jobs:
        required = load_json(job["requirements"], [])
        if not required:
            continue  # can't score a job with no listed skills
        matched = [s for s in required if s.lower() in have]
        missing = [s for s in required if s.lower() not in have]
        results.append({
            "job_title": job["job_title"],
            "company_name": job["company_name"],
            "matched": matched,
            "missing": missing,
            "total": len(required),
            "percent": round(len(matched) / len(required) * 100),
        })
    results.sort(key=lambda r: r["percent"], reverse=True)
    return results


@app.route("/match")
def job_match():
    skills_text = request.args.get("skills", "")
    skills = [s.strip() for s in skills_text.split(",") if s.strip()]
    results = match_jobs(skills) if skills else None
    return render_template("job_match.html", skills_text=skills_text,
                           skills=skills, results=results)


if __name__ == "__main__":
    app.run(debug=True)
