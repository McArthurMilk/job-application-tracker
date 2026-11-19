# AI Usage Documentation

This file documents how I used generative AI while building the Job Application Tracker (Flask + MySQL + HTML/CSS). AI helped me get started faster and work through errors. I reviewed, tested and adjusted all of the code myself before committing it.

---

## Tools Used

| Tool | What I used it for |
|------|--------------------|
| **Claude** | Planning the Flask project structure, writing the first drafts of the CRUD routes, debugging errors, the HTML/CSS layout, and organizing the README |

---

## Key Prompts

These are the main prompts I used. They're grouped by what I was working on.

### 1. Project Setup & CRUD Routes

**Prompt 1: Project structure**
> I'm building a job application tracker with Python Flask and MySQL. It has 4 tables: companies, jobs, applications, and contacts. What's a simple folder structure I should use? I want an app.py, a separate file for database code, a templates folder, and a static folder for CSS.

**Prompt 2: Database helper**
> Write a small `database.py` file using `mysql.connector` with a `get_db()` function and two helpers: `query()` for SELECT statements that returns rows as dictionaries, and `execute()` for INSERT/UPDATE/DELETE that commits the change. Please read the connection settings from environment variables so I don't hardcode my password.

**Prompt 3: First CRUD route (companies)**
> Here is my companies table: `company_id, company_name (required), industry, website, city, state, notes`. Write Flask routes to list all companies, add a new company from a form, edit an existing one, and delete one. Use parameterized queries (`%s`) so it's safe from SQL injection.

**Prompt 4: Reusing the pattern for the other tables**
> The companies routes work. Now write the same list/add/edit/delete routes for my `jobs` table. jobs has a `company_id` foreign key, so the list page should show the company name using a JOIN, and the add form needs a dropdown of companies.

**Prompt 5: JSON columns**
> My `jobs.requirements` column is JSON and `applications.interview_data` is also JSON. How do I save a comma-separated list of skills from a form input into a JSON column, and then turn it back into a Python list when I read it?

**Prompt 6: Dashboard**
> Write a dashboard route that shows the total count of companies, jobs, applications, and contacts, and a count of applications grouped by status.

**Prompt 7: Job Match feature**
> I need a function that takes a list of skills a user typed in (like "Python, SQL, Flask") and compares them to each job's required skills. It should return the jobs sorted by match percentage, and show which skills matched and which are missing. The comparison should ignore upper/lowercase.

### 2. Debugging

**Prompt 8: Database connection error**
> I'm getting `mysql.connector.errors.ProgrammingError: 1045 (28000): Access denied for user 'root'@'localhost'`. My MySQL server is running. What should I check?

**Prompt 9: Empty number fields**
> When I submit the job form and leave Minimum Salary blank, I get `Incorrect integer value: '' for column 'salary_min'`. How do I store an empty form field as NULL instead of an empty string?

**Prompt 10: JSON coming back as a string**
> When I loop over `job["requirements"]` in my template, it prints one letter at a time instead of one skill at a time. I think MySQL is returning the JSON column as a string. How do I fix this?

**Prompt 11: Can't delete a company**
> When I try to delete a company that has jobs, I get `IntegrityError: Cannot delete or update a parent row: a foreign key constraint fails`. What's the best way to handle this?

**Prompt 12: Flash messages not working**
> I added `flash("Company added!")` but I get `RuntimeError: The session is unavailable because no secret key was set`. What does this mean?

**Prompt 13: Navigation highlight bug**
> I'm trying to highlight the current page in my navbar using `request.path.startswith(url)`. But the Dashboard link (`/`) is always highlighted on every page. How do I fix that?

### 3. HTML & CSS Design

**Prompt 14: Base template**
> Make a Jinja `base.html` template with a dark header that has the app name on the left and navigation links on the right (Dashboard, Companies, Jobs, Applications, Contacts, Job Match). It should also show flash messages above the page content. My other pages will extend it.

**Prompt 15: Reusing one form for Add and Edit**
> Can I use the same form in my template for both adding and editing a record? When editing, the form should be filled in with the current values and the button should say "Save Changes" instead of "Add".

**Prompt 16: Overall styling**
> Write a clean, simple `style.css` for my app without using Bootstrap. I'd like a light gray background, white "cards" with rounded corners for each section, styled tables, and blue buttons. Please use CSS variables for the colors so I can change them easily.

**Prompt 17: Form layout**
> My forms are just one long column of inputs. How can I use CSS grid so the inputs sit side by side on wide screens and stack on small screens? Some fields like Notes should take up the full width.

**Prompt 18: Status badges**
> I want the application status (Applied, Screening, Interview, Offer, Rejected, Withdrawn) to show as small colored pill badges in the table, with a different color for each status.

**Prompt 19: Delete confirmation**
> What's a simple way to make the user confirm before deleting a record? I don't want a separate confirmation page.

### 4. README Documentation

**Prompt 20: README outline**
> I'm finishing my Flask + MySQL job tracker project and need a README.md for GitHub. What sections should a good README have for a school project like this? I want someone else to be able to clone it and run it.

**Prompt 21: Setup instructions**
> Write step-by-step setup instructions for my README. The steps are: install Python packages from requirements.txt, run schema.sql to create the database, set the MySQL password, and run `python app.py`. My `database.py` reads the password from a `DB_PASSWORD` environment variable. Please show how to set it on both Mac and Windows.

**Prompt 22: Project structure and database table**
> Make a folder tree for my README showing my project files with a short comment next to each one. Also make a small markdown table that summarizes my 4 tables, their key columns, and their foreign key relationships.

**Prompt 23: Troubleshooting section**
> What are the most common errors someone might hit when running a Flask app with mysql-connector for the first time? Write a short troubleshooting section for my README with each error and how to fix it.

---

## What Worked Well

- **CRUD routes came together quickly.** Once I had working company routes, asking the AI to follow the same pattern for jobs, applications and contacts saved a lot of time and kept the code consistent.
- **Parameterized queries.** The AI used `%s` placeholders from the start, which protects against SQL injection.
- **Explaining error messages.** The AI was very good at explaining what an error meant before giving a fix. For example, it explained that a foreign key error happens because child rows still point at the parent row.
- **The `query()` / `execute()` helpers.** Moving the connection code into `database.py` made `app.py` much shorter and easier to read.
- **CSS grid for forms.** `grid-template-columns: repeat(auto-fill, minmax(230px, 1fr))` made the forms responsive without needing any media queries.
- **`confirm()` for deletes.** A one-line `onsubmit="return confirm(...)"` on the delete form met the "delete with confirmation" requirement without an extra page.
- **README structure.** The AI suggested a clear order for the README (features, project structure, setup, usage, database design, troubleshooting), which made it easy to fill in.

---

## What I Changed / Modified

- **Matched my actual schema.** The first drafts used column names like `name` and `title`. I changed them to my real column names (`company_name`, `job_title`, `contact_name`, etc.).
- **Added input validation.** The AI's routes didn't check the input. I added checks for required fields, whole numbers for salary, and that the minimum salary isn't higher than the maximum. I also added a `to_int()` helper that collects error messages to flash back to the user.
- **Empty fields become NULL.** After the salary bug (Prompt 9), I wrote a `blank_to_none()` helper and used it on every optional field, not just salary.
- **Safer JSON loading.** I wrapped the AI's `json.loads()` in a `load_json()` helper that also handles `None`, bytes, and invalid JSON, so one bad row can't crash the page.
- **Chose `ON DELETE CASCADE`.** For the foreign key error, the AI suggested a few options. I picked `ON DELETE CASCADE` in `schema.sql` and updated the confirm messages to warn the user that deleting a company also deletes its jobs, applications and contacts.
- **Moved the database password out of the code.** I changed the config so it reads `DB_PASSWORD` and the other settings from environment variables, so my real password isn't on GitHub.
- **Nav highlight fix.** I used the AI's idea of checking `/` with an exact match and the other pages with `startswith()`.
- **Job Match edge case.** I skip jobs that have no listed skills so the app doesn't divide by zero.
- **Simplified the CSS.** The first stylesheet had more effects than I needed. I removed some of them, picked my own colors, and added the status badge colors.
- **Tested and edited the README.** I followed my own setup steps from scratch to make sure they worked. I added a warning that running `schema.sql` drops and recreates the database, a "Using the App" section explaining you need to add a company before jobs and contacts, and a note about what gets deleted with a company. I also trimmed the troubleshooting list to the four errors I actually ran into.

---

## Lessons Learned

- **Always test AI code.** Most of the code worked, but small things like column names, empty form fields and JSON types only showed up when I actually ran the app.
- **Give the AI context.** I got much better answers when I pasted my table schema or the full error message, compared to describing the problem vaguely.
- **Build one piece first, then repeat the pattern.** Getting the companies CRUD fully working before asking for the other tables meant fewer bugs to fix later.
- **Understand before you paste.** Asking "why does this happen?" for each error helped me learn how Flask, Jinja and MySQL fit together, instead of just copying fixes.
- **AI doesn't know your requirements.** It didn't add validation or think about what should happen when a parent record is deleted. Those decisions were still up to me.
