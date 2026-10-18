# Employee CSV → SQL Server loader

Beginner Python project for practicing Git, GitHub issues, feature branches and pull requests.
CSV path, SQL Server connection details, schema and table come from JSON. CSV paths are relative to the JSON file. This small project reads all rows into memory and is intended for small practice files.

## 1. Open in VS Code

Extract the ZIP. In VS Code choose File → Open Folder → employee-csv-loader.
Open Terminal → New Terminal. Commands below use Windows PowerShell.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe main.py --dry-run
```

Expected: `Validated rows: 3`. This step needs no database or third-party packages.

## 2. Prepare SQL Server

You need a running SQL Server instance and Microsoft ODBC Driver 18 for SQL Server installed on your computer. SSMS is the client, not the database engine.
In SSMS, connect to your personal practice instance and execute `sql/create_table.sql`.
Copy `config.json` to `config.local.json` and update server/database/schema/table to match your instance. Example named instance in JSON: `"server": "localhost\\SQLEXPRESS"`.
`config.local.json` is ignored by Git; keep machine-specific settings there.
The target table must exist and its columns and data types must accept the CSV columns and values. Changing the JSON does not create a table.

Default authentication uses your Windows account. If your local SQL Server uses a self-signed certificate, set `trust_server_certificate` to `true` only in your personal local configuration.
For SQL authentication set `windows_auth` to `false`, then set `SQLSERVER_USERNAME` and `SQLSERVER_PASSWORD` environment variables in your terminal. Never put passwords in JSON or GitHub.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py --config config.local.json --dry-run
.\.venv\Scripts\python.exe main.py --config config.local.json
```

Verify in SSMS:

```sql
SELECT * FROM PracticeDB.dbo.employees;
```

This is INSERT-only. Running the same file twice causes a primary-key error; the entire failed load is rolled back. No automatic DELETE, TRUNCATE, overwrite or duplicate skipping is performed. Use different IDs for another load. Empty fields fail validation. SQL Server validates field types and lengths during insertion.

## 3. Put the project on GitHub

The ZIP is a downloadable project, not a hosted repository. Create an **empty** GitHub repository named `employee-csv-loader` (do not add README, license or gitignore on GitHub).
From the extracted project folder:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "Add configuration-driven CSV loader"
git remote add origin https://github.com/YOUR_USERNAME/employee-csv-loader.git
git push -u origin main
```

Replace YOUR_USERNAME. If Git asks for identity, set your own user.name and user.email. Authenticate through your Git credential manager; never commit tokens.

Now practice cloning into a different folder:

```powershell
cd ..
git clone https://github.com/YOUR_USERNAME/employee-csv-loader.git employee-csv-loader-practice
cd employee-csv-loader-practice
code .
```

The virtual environment does not get cloned. Repeat step 1 in the new clone.

## 4. Your first development ticket

On GitHub create an issue: **Add a location column to the employee loader**.
Acceptance criteria: CSV contains location; the table accepts it; dry run succeeds; a load inserts location correctly. For existing tables use ALTER TABLE; changing CREATE TABLE alone will not update them. Use fresh employee IDs when testing.

```powershell
git switch main
git pull origin main
git switch -c feature/1-add-location
```

Edit the sample CSV and SQL setup/migration script, verify locally, then:

```powershell
git diff
git add data/employees.csv sql/
git commit -m "Add employee location field"
git push -u origin feature/1-add-location
```

On GitHub: Pull requests → New pull request. Base: main. Compare: feature/1-add-location.
Describe what changed and the exact checks you ran. Add `Closes #1` only if your issue really is #1. Review Files changed, then merge your own practice PR.

```powershell
git switch main
git pull origin main
git branch -d feature/1-add-location
```

## More practice tickets

1. Add logging to a file (ignore log files in Git).
2. Add employee-specific validation: salary must be numeric and nonnegative.
3. Detect duplicate employee IDs in the CSV before opening the database connection.
4. Add a second JSON configuration and a second table for departments.
5. Add tests for validation and rollback behavior.

## Verification included with this download

Python syntax and the sample CSV dry run were checked. A live SQL Server load was not tested in the creation environment; verify it against your local practice instance.
