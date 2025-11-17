# Doctor Bot

Simple Telegram bot to manage a list of doctors (search, add, list).

## Quick setup

1. Create a Python virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure the bot token and admin IDs.

- Preferred: set environment variables in your session or a `.env` file (don't commit `.env`):

```powershell
$env:BOT_TOKEN = "<your-bot-token>"
$env:ADMIN_IDS = "11111111,22222222"  # comma-separated numeric IDs
python bot.py
```

- Or copy `config_example.py` to `config.py` and fill values (not recommended to commit real token).

3. Run the bot:

```powershell
python bot.py
```

## GitHub

To create a repo and push from PowerShell (option A uses GitHub CLI):

Option A — with `gh` installed:

```powershell
cd "E:\عمل خاص\برمجة\python\doctor_bot"
git init
git add .
git commit -m "Initial commit"
gh repo create YOUR_GITHUB_USERNAME/doctor_bot --public --source=. --remote=origin --push
```

Option B — without `gh` (create a repo on github.com first):

```powershell
cd "E:\عمل خاص\برمجة\python\doctor_bot"
git init
git add .
git commit -m "Initial commit"
# then on GitHub: create a new repo and copy the remote URL
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/doctor_bot.git
git branch -M main
git push -u origin main
```

## Notes

- `config.py` is excluded from git in `.gitignore` to avoid leaking the bot token.
- Use `config_example.py` or environment variables to configure secrets.
- If you want me to push the repo for you, I can prepare everything but I cannot create the remote repo without your GitHub authentication (`gh` or a remote URL). I can provide exact commands to run locally.
