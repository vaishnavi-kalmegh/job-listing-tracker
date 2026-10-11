# Private data repository setup (one-time)

The public repository must contain code and aggregate counts only. The daily workflow expects a separate private repository named **vaishnavi-kalmegh/job-listing-data**. I cannot create a GitHub repository or add an account secret through the repository file editor, so complete these account-level steps once.

## 1. Create the private repository

1. Sign in to GitHub as **vaishnavi-kalmegh**.
2. Open https://github.com/new.
3. In **Repository name**, enter **job-listing-data**.
4. Set **Description** to “Private job listing snapshots for job-listing-tracker” (optional).
5. Select **Private**. Do not select Public.
6. Check **Add a README file** so the repository has an initial commit and default branch.
7. Leave .gitignore and License as **None**.
8. Click **Create repository**.
9. Confirm the URL is https://github.com/vaishnavi-kalmegh/job-listing-data and visibility is **Private**.
10. Do not upload job data manually. The workflow will create jobs.db, run_summary.json, and dated SQLite snapshots after the first successful run.

## 2. Create a fine-grained access token

This token allows the public repository's GitHub Actions workflow to write only to the private data repository.

1. Open https://github.com/settings/personal-access-tokens/new.
2. Enter a token name such as **job-listing-tracker-actions**.
3. Choose an expiration date. Set a calendar reminder to rotate it before expiry; use a bounded expiry if offered.
4. Under **Resource owner**, choose **vaishnavi-kalmegh**.
5. Under **Repository access**, select **Only select repositories**.
6. Select only **job-listing-data**. Do not grant access to every repository.
7. Under **Repository permissions**, set **Contents** to **Read and write**. Leave other permissions at **No access** or their default read-only values; GitHub's required Metadata permission is read-only.
8. Click **Generate token**.
9. Copy the token immediately and store it in a password manager. GitHub will not show the full token again. Never paste it into a source file, issue, chat, or commit.

## 3. Add the token to the public repository's Actions secrets

1. Open https://github.com/vaishnavi-kalmegh/job-listing-tracker/settings/secrets/actions.
2. In **Repository secrets**, click **New repository secret**.
3. For **Name**, enter exactly **DATA_REPO_TOKEN**.
4. Paste the fine-grained token into **Secret**.
5. Click **Add secret**. The value will be masked and cannot be viewed later.

## 4. Run the workflow once manually

1. Open https://github.com/vaishnavi-kalmegh/job-listing-tracker/actions.
2. Select **Daily job collection** in the left sidebar.
3. Click **Run workflow**.
4. Keep the default branch selected and click the green **Run workflow** button.
5. Open the run and inspect each step. A successful run should commit the database and dated snapshot to the private repository and update aggregate reports in the public repository.
6. If the first run fails, read the failing step. The workflow does not mark jobs inactive when a board fetch is failed or incomplete.

## 5. Schedule and 60-day inactivity rule

- The workflow runs daily at **20:30 UTC (02:00 IST)** and also supports a manual workflow_dispatch run.
- GitHub can disable scheduled workflows in public repositories after 60 days without repository activity. This workflow updates a timestamped aggregate summary each successful run, which normally creates a public commit and counts as activity. If the workflow has stopped running, open **Actions → Daily job collection → Run workflow** and run it manually, then inspect the result.
- Keep the workflow file on the repository's **default branch**. Schedule runs can be delayed during GitHub load; do not schedule exactly on the hour.
- Set a reminder to rotate DATA_REPO_TOKEN before expiry. If it expires or is revoked, the workflow fails at private checkout or push; create a replacement token and update the same secret.
- Never make the data repository public. The private database includes source job details and descriptions; public reports contain aggregate counts only.

## Storage and retention note

The workflow stores the current SQLite database and a dated SQLite snapshot in the private repository. Git history therefore retains prior snapshots. If the database grows substantially, introduce a documented retention/archival policy before deleting historical snapshots; do not delete observations needed for observed_duration or disappearance/return analysis.


## 6. Download and label the role-review sample privately

After the first successful collection run, the workflow writes a random sample of up to 30 tech titles and 30 non-tech titles to the **private** repository as role_review.csv. It never commits titles to the public repository.

1. Open https://github.com/vaishnavi-kalmegh/job-listing-data.
2. Click **role_review.csv**.
3. Click **Download raw file** (or the download icon if shown) and save the CSV.
4. Copy the downloaded file into your local clone of job-listing-tracker under reports/role_review.csv. If you do not have a local clone, use GitHub Desktop to clone the public repo first.
5. Open reports/role_review.csv in Excel or LibreOffice. Fill the review_label column with **tech**, **non-tech**, or **unclassified** based on the title and any department/team context included in the title/row. Do not use job descriptions for role labels.
6. Save as CSV, keeping the same filename.
7. In a terminal opened at the public repository folder, run: `python -m discovery.score_role_review --input reports/role_review.csv`.
8. Precision is only reported for rows you labelled. Do not claim a precision result before this manual review is complete.

Keep the completed CSV private; it contains job titles. Do not upload it to the public repository.
