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

## 2026-03-01 - Dynamic Content Announcements
**Learning:** The application relies heavily on `React.lazy` for code splitting, making the `LoadingSpinner` a frequent transient state. Without `role="status"`, screen reader users experienced silence during these navigations.
**Action:** Ensure all `Suspense` fallbacks and global loading states utilize `role="status"` and `aria-live="polite"` to provide immediate auditory feedback during component transitions.

## 2026-03-01 - Consistent Result Interactions
**Learning:** Results often include logs or data that users may want to extract. `ColGenSolver` provided a copy mechanism, while `LagrangianSolver` did not, forcing users to manually select and copy text.
**Action:** Identify text-heavy result sections (logs, large matrices) and consistently provide a "Copy" utility to improve usability and data portability.

## 2026-03-02 - Skip to Main Content Link
**Learning:** For keyboard and screen reader users, repeatedly tabbing through navigation and header elements to reach the primary content (the solver forms) can be tedious. A "Skip to main content" link is a critical accessibility standard that was missing.
**Action:** Implemented a skip link that is visually hidden until focused, and ensured the target `<main>` element has `tabIndex="-1"` and `focus:outline-none` so it can receive focus programmatically without showing an awkward outline. Also updated semantic HTML tags (`<header>`, `<main>`) for better structure.

## 2026-03-02 - Explicit Label-Input Associations for Checkboxes
**Learning:** While wrapping an `<input type="checkbox">` inside a `<label>` provides implicit association, screen readers and older assistive technologies perform significantly better when inputs are *explicitly* tied via `id` and `htmlFor`. `LPSolver` and `IPSolver` lacked this.
**Action:** Always include explicit `id` and `htmlFor` attributes on inputs and their wrapping labels, even when implicitly nested.

## 2026-04-01 - Cryptic JSON Parsing Errors
**Learning:** Many solvers accept complex matrix and array data as JSON strings. When users made a typo, `JSON.parse` failed and threw generic JavaScript exceptions ("Unexpected token..."). Displaying this directly in the UI confused users who didn't understand JSON syntax errors.
**Action:** Intercept `JSON.parse` errors in UI components before they bubble up, and replace them with clear, actionable validation guidance explaining the required format (e.g., "[[1, 2], [3, 4]]") to reduce user frustration.

## 2026-03-03 - Disable Spellcheck on Data Inputs
**Learning:** Browsers natively attempt to spellcheck text areas and text inputs. For inputs that expect raw data formats like JSON, arrays, or matrices, this results in annoying visual noise (red squiggly lines) under variable names, numbers, or JSON syntax, which can confuse users into thinking they have made a syntax error.
**Action:** Always explicitly add `spellCheck={false}` to any `<input>` or `<textarea>` that is designed to capture raw data, code, or JSON payloads.
