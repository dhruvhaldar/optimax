## 2024-05-22 - [Pattern: Form Labels]
**Learning:** Inputs in this codebase (e.g., LPSolver) consistently lack explicit `htmlFor`/`id` association, relying on implicit context or missing it entirely.
**Action:** Always verify label-input association manually or with tools.

## 2024-05-22 - [Issue: Git Tracking]
**Learning:** `__pycache__` files are tracked in git, causing phantom changes when running the backend.
**Action:** Be careful not to stage/commit these files. Use `git reset` or `git restore` on them if they appear modified.
