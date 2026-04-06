## 2024-05-22 - [Pattern: Form Labels]
**Learning:** Inputs in this codebase (e.g., LPSolver) consistently lack explicit `htmlFor`/`id` association, relying on implicit context or missing it entirely.
**Action:** Always verify label-input association manually or with tools.

## 2024-05-22 - [Issue: Git Tracking]
**Learning:** `__pycache__` files are tracked in git, causing phantom changes when running the backend.
**Action:** Be careful not to stage/commit these files. Use `git reset` or `git restore` on them if they appear modified.

## 2025-03-14 - [UX/Crash Prevention on Formats]
**Learning:** Missing explicit null checks on solver results (like `result.fun` or array elements) before calling `.toFixed()` crashes the React application completely when a problem is infeasible, causing an abrupt and poor user experience (client-side DoS).
**Action:** Always verify variables are not `null` or `undefined` before chaining formatting methods to ensure graceful degradation and display of "N/A" fallback states.

## 2024-04-06 - Form Keyboard Shortcuts and Native Validation
**Learning:** When attaching custom keyboard shortcuts (e.g., `Cmd+Enter`) to forms, triggering submissions directly via a React handler bypasses native HTML form validation (such as `required` attributes). This leads to components trying to process empty or invalid inputs, potentially causing unhandled exceptions downstream.
**Action:** Always trigger programmatic form submissions using `e.currentTarget.requestSubmit()` rather than directly invoking the form's logic handler. This ensures native HTML validation intercepts invalid states before the programmatic handler is fired.
