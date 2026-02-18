## 2024-05-23 - Inconsistent Form Accessibility Pattern
**Learning:** While the initial `LPSolver` component had accessible form labels, subsequent components (`IPSolver`, `ColGenSolver`, etc.) lacked `htmlFor` and `id` associations. This inconsistency suggests that accessibility practices are not yet institutionalized in the development workflow.
**Action:** When creating or refactoring form components, explicitly check for label-input associations. Consider adding a linter rule (e.g., `jsx-a11y/label-has-associated-control`) to catch this automatically in the future.

## 2024-05-23 - Standardized Async Button Pattern
**Learning:** `IPSolver` had a superior button implementation with a spinner and flex layout, while other solvers lacked visual feedback during loading. This inconsistency degraded the user experience for other solvers.
**Action:** Always use the `glass-btn-primary` with `flex items-center justify-center gap-2`, `aria-busy`, and the conditional spinner SVG for async actions to maintain consistency and provide feedback.
