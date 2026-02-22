## 2024-05-23 - Inconsistent Form Accessibility Pattern
**Learning:** While the initial `LPSolver` component had accessible form labels, subsequent components (`IPSolver`, `ColGenSolver`, etc.) lacked `htmlFor` and `id` associations. This inconsistency suggests that accessibility practices are not yet institutionalized in the development workflow.
**Action:** When creating or refactoring form components, explicitly check for label-input associations. Consider adding a linter rule (e.g., `jsx-a11y/label-has-associated-control`) to catch this automatically in the future.

## 2024-05-23 - Standardized Async Button Pattern
**Learning:** `IPSolver` had a superior button implementation with a spinner and flex layout, while other solvers lacked visual feedback during loading. This inconsistency degraded the user experience for other solvers.
**Action:** Always use the `glass-btn-primary` with `flex items-center justify-center gap-2`, `aria-busy`, and the conditional spinner SVG for async actions to maintain consistency and provide feedback.

## 2024-05-24 - Standardized Error Alert Pattern
**Learning:** Error messages were inconsistent; while `IPSolver` used `role="alert"`, other solvers lacked it. This inconsistency meant that screen reader users might miss critical error feedback in most of the application.
**Action:** When implementing error states, always wrap the error message in a container with `role="alert"` to ensure immediate announcement by assistive technologies.

## 2024-05-24 - Missing Focus Indicators
**Learning:** The custom `.glass-btn` and `.glass-btn-primary` classes relied on default browser behavior which was often overridden or insufficient, leaving keyboard users without clear focus indicators.
**Action:** Always verify focus states for custom interactive components. Added `focus-visible:ring` utilities to ensure high visibility for keyboard navigation.

## 2026-02-22 - Complex Input Guidance
**Learning:** Solvers requiring JSON or matrix inputs (e.g., `IPSolver`, `StochasticSolver`) lacked explicit format guidance, leading to potential user confusion. Standard HTML `placeholder` attributes proving sufficient for documenting these structures directly within the input field.
**Action:** Always verify complex input fields include `placeholder` examples demonstrating the expected JSON/list format to reduce cognitive load and potential errors.
