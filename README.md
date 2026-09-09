# MindMirror

## MongoDB setup

Install the dependencies from `requirements.txt`, then set `MONGODB_URI` before starting Flask. Use the Atlas connection string with the database password substituted locally; URL-encode special characters such as `#` as `%23`, and do not commit the URI or password.

PowerShell example:

```powershell
$env:MONGODB_URI = "mongodb+srv://shehanviduranga22:<db_password>@cluster0.euah1dp.mongodb.net/?appName=Cluster0"
c:/Users/ASUS/Documents/GitHub/MindMirror_Project/venv/Scripts/python.exe app.py
```

Accounts are stored in the `mindmirror.accounts` collection with hashed passwords. Successful login renders the home page with the username greeting.
# MindMirror_Project

