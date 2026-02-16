## 2024-05-23 - Inconsistent Form Accessibility Pattern
**Learning:** While the initial `LPSolver` component had accessible form labels, subsequent components (`IPSolver`, `ColGenSolver`, etc.) lacked `htmlFor` and `id` associations. This inconsistency suggests that accessibility practices are not yet institutionalized in the development workflow.
**Action:** When creating or refactoring form components, explicitly check for label-input associations. Consider adding a linter rule (e.g., `jsx-a11y/label-has-associated-control`) to catch this automatically in the future.
