# Publishing this repository

No Git LFS, no command line. The repository is 21 MB with no file anywhere near
GitHub's 100 MB limit, so ordinary Git handles everything. The raw Kaggle data
is referenced rather than redistributed: see `docs/DATA_SOURCES.md`.

## 1. Put the project somewhere sensible

Unzip this package so the project folder sits directly in a normal location:

```
Documents/M13A-25-Beyond-the-Price-Tag/
```

Open it and confirm you see `README.md`, `code/`, `report/` and the rest at the
top level. If you see the project folder nested inside another folder of the
same name, move it up one level. The repository root must be the project root.

## 2. Create the repository on GitHub

New repository, named `M13A-25-Beyond-the-Price-Tag`.

Description: *Explainable AI decision-support for football player valuation,
exit-risk assessment and transfer-budget allocation.*

Set it **Private** for now.

**Do not tick** "Add a README", ".gitignore" or "Choose a license" — the project
already contains all three, and initialising would create a conflict.

## 3. Add it in GitHub Desktop

`File → Add Local Repository`, choose the project folder.

GitHub Desktop will say it is not a Git repository and offer to **create one
here**. Accept. Do not let it create a new subfolder.

## 4. Read the file list before committing

GitHub Desktop now lists every file it intends to commit. Read it.

You should see roughly **142 files**. You should **not** see `node_modules`,
`__pycache__`, `.venv`, or anything under `data/raw/`. If you do, `.gitignore`
has not been picked up: confirm the file is at the project root.

## 5. Commit

Summary: `Initial project release`

Description: *Complete Sports Analytics project: source code, frozen analytical
outputs, final report, presentation, decision workbook, prompt logbook and audit
controls.*

Click **Commit to main**.

## 6. Publish

Click **Publish repository**. Keep "Keep this code private" ticked for now.

## 7. Look at it in the browser

Open the repository on GitHub. Confirm the README renders, the folder structure
looks right, and the report and presentation are listed.

## 8. Clone it fresh — the step that actually proves something

Browsing the repository proves nothing about whether it works.

`File → Clone Repository`, choose your repository, clone it to a **different
folder** such as `Desktop/github_test/`.

Then, in that clone and a fresh Python environment:

```
pip install -r requirements.txt
python code/12_audit/final_audit.py
```

Expect **AUDIT PASSED** and exit code 0. If it fails, stop and read the output
rather than pushing more commits.

Then open the four deliverables from the clone — report, presentation, workbook,
logbook — and confirm they open cleanly.

## 9. Make it visible before you submit

The repository is Private. Either switch it to **Public**
(`Settings → General → Danger Zone → Change visibility`) or add your professor
as a collaborator. A private link your evaluator cannot open is worse than no
link at all.

## 10. Submit

```
https://github.com/YOUR_USERNAME/M13A-25-Beyond-the-Price-Tag
```

The README is the landing page and answers, in under a minute, what was built,
what data was used, what the analysis found, why the original hypothesis was
rejected, and how to inspect it.
