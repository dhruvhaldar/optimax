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

## 2026-03-04 - Initial State Visual Guidance
**Learning:** Forms that handle complex computations often feel visually unbalanced before submission, leaving users without clear initial guidance or anticipation of the output format. Empty states not only fill this visual void but serve as an excellent place to provide a call-to-action and set expectations for the results.
**Action:** Always include a styled empty state block for result sections in computational interfaces when the initial state has no data to display.

## 2026-03-05 - Visual Feedback During Async Operations for Stale Content
**Learning:** When users re-submit forms that already have results (or empty states), leaving the existing content fully visible and interactive during the new network request creates confusion. Users may try to interact with the stale results (like copying logs) or wonder if the new request actually started.
**Action:** When handling async form submissions, always apply a visual fading effect (e.g., `opacity-50`) and disable interactions (e.g., `pointer-events-none`) on the existing result or empty state blocks to clearly signal that the UI is busy processing the new request.

## 2026-03-05 - Dynamic Document Titles in SPAs
**Learning:** Single Page Applications (SPAs) often fail to update the `<title>` element when the user navigates between virtual views (like tabs). This means screen reader users and sighted users with multiple tabs open lose context of which specific tool or sub-page they are currently on, as the title remains static.
**Action:** Always implement dynamic document title updates (e.g., via `useEffect` observing the active view state) in SPAs to explicitly reflect the current view or tool name, ensuring users have persistent context.

## 2026-05-15 - Focus Loss from Native Disabled Attribute
**Learning:** Using the native `disabled={loading}` attribute on form submit buttons immediately removes the element from the tab order when it becomes disabled. If the element currently has focus (which it typically does after a click or enter key press), the browser resets focus to the `<body>` element. This completely breaks the logical navigation flow for keyboard users, forcing them to navigate back through the entire page structure to reach the newly loaded results.
**Action:** Always replace `disabled={loading}` on submit buttons with `aria-disabled={loading}`, add explicit CSS classes for visual feedback (e.g., `opacity-80 cursor-wait`), and ensure the corresponding click handler has a guard (`if (loading) return;`) to prevent duplicate submissions while correctly preserving keyboard focus.

## 2026-03-08 - Keyboard Navigation for Scrollable Content
**Learning:** Native elements like `<pre>` or `<div>` that use CSS `overflow: auto` or `overflow: scroll` to manage large content (such as execution logs) are inaccessible to keyboard-only users by default. Without a `tabIndex`, users cannot tab into the container to scroll its contents using the arrow keys, effectively locking them out of the information if it exceeds the visible area.
**Action:** Always add `tabIndex={0}`, an appropriate `role` (like `"region"`), an `aria-label`, and clear focus styles (e.g., `focus-visible:ring`) to any container that scrolls content independently of the main page, ensuring keyboard users can navigate and consume the full content.

## 2024-05-25 - Decorative SVGs and Screen Readers
**Learning:** Decorative SVG icons (like loading spinners or empty state graphics) without `aria-hidden="true"` can be announced confusingly by screen readers as unlabelled graphics, adding noise to the user experience.
**Action:** Always add `aria-hidden="true"` to `<svg>` elements that are purely decorative or redundant to accompanying text (like "Loading...").

## 2026-06-15 - Dynamic Platform Keyboard Shortcuts
**Learning:** Hardcoded keyboard shortcuts (like `⌘↵`) in titles or visual hints can be confusing or misleading for users on non-Mac platforms (Windows, Linux), leading to frustration when trying to use keyboard navigation.
**Action:** Implemented a custom hook (`useOsShortcut`) that dynamically checks the OS platform and renders the appropriate shortcut symbols (`⌘↵` for Mac, `Ctrl+↵` for others) along with accurate `aria` and `title` attributes across all solver form actions.

## 2026-06-16 - Ambiguous Binary States
**Learning:** Using a single checkbox for a binary state where the "unchecked" state isn't simply "off" (e.g., "Maximize Objective" where unchecked implies "Minimize") creates cognitive load and ambiguity. Users might wonder if unchecked means "don't care", "minimize", or something else.
**Action:** Replaced ambiguous single checkboxes with an explicit semantic `<fieldset>` containing radio buttons for both explicit states (Maximize / Minimize). This guarantees clarity of intent and improves accessibility by using appropriate form grouping constructs.
\n## 2026-03-15 - Focus Management for Dynamic Content\n**Learning:** When results are loaded asynchronously, users using screen readers may not be aware that new content has appeared below the form. Sighted users relying on keyboard navigation must manually tab all the way down to reach it. Programmatically managing focus is necessary to ensure the context change is announced and the user is brought to the updated content.\n**Action:** Implemented a `useResultFocus` hook to automatically shift focus to the "Results" header when new results arrive, adding `tabIndex="-1"` and `focus:outline-none` to handle the programmatic focus gracefully.

## 2026-06-18 - Accessibility of Inline JSON Arrays in Flex Layouts
**Learning:** Displaying long arrays (like generated patterns in Column Generation) as simple inline text (`<span>`) inside a flex container breaks the layout on smaller screens, forcing text to overflow off-screen without a scrollbar. Furthermore, sighted users can't easily see it all, and keyboard-only users are completely unable to access the hidden content because it lacks scrollable focus.
**Action:** Always wrap dynamically generated arrays or JSON strings inside flex lists in a dedicated container or `<code>` block with `overflow-x-auto block`, `tabIndex={0}`, `role="region"`, a descriptive `aria-label`, and `focus-visible:ring`. This guarantees responsiveness and ensures full keyboard accessibility for horizontally scrolled content.

## 2026-06-21 - Keyboard Navigable Data Visualizations
**Learning:** Automatically generated base64 plots (e.g., from Matplotlib) displayed as `<img />` tags convey critical problem state information to users. By default, these images are ignored during keyboard navigation, meaning keyboard-only users can easily scroll past them without realizing they are there.
**Action:** Always add `tabIndex={0}` and a clear visual focus ring (e.g., `focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400`) to important data visualization images so keyboard users can intentionally focus on them and be aware of their presence.

## 2026-07-01 - Semantic Description Lists for Key-Value Data
**Learning:** Using multiple `div`s with `span` tags to display key-value pairs (like "Status: Optimal" or "Objective Value: 12.5") lacks semantic structure, making it harder for screen readers to interpret the explicit association between the label and its data.
**Action:** Always use HTML5 `<dl>` (description list) tags combined with `<dt>` (description term) and `<dd>` (description detail) for groups of key-value metrics. This provides a robust semantic structure for assistive technologies while maintaining CSS grid layouts.

## 2026-07-05 - Semantic Tagging for Visual Shortcuts
**Learning:** Visual keyboard shortcut hints (like `⌘↵`) were embedded in generic `<span>` tags. Using a semantic `<kbd>` tag is standard practice to indicate user input. When placed inside interactive elements (like a button) that already have descriptions, adding `aria-hidden="true"` remains critical to prevent screen readers from redundantly announcing the shortcut text which might be distracting or confusing.
**Action:** Replaced generic `<span>` tags with semantic `<kbd>` tags for all keyboard shortcuts in interactive components, while retaining `aria-hidden="true"` and styling them as explicit 'keycaps' to improve user recognition.

## 2026-07-10 - WAI-ARIA Tablist Navigation Pattern
**Learning:** Using a generic `<nav>` with `<button>` elements for a tabbed interface creates a confusing experience for screen reader users and requires sighted keyboard users to tab through every single unselected option to reach the content. A proper WAI-ARIA `tablist` makes the structure semantically clear and allows keyboard users to focus the active tab immediately, using arrow keys to navigate options.
**Action:** Always implement the WAI-ARIA Tablist pattern (`role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`, `aria-controls`, `aria-labelledby`, and dynamic `tabIndex`) with custom arrow key navigation (`onKeyDown`) whenever building a tabbed view interface.

## 2026-07-20 - Unmounting Components in Tab Interfaces Causes Data Loss
**Learning:** In React applications with tabbed navigation, conditionally rendering active tabs (e.g., `{activeTab === 'lp' && <LPSolver />}`) causes the currently active component to unmount when the user switches tabs. If the component contains unsaved user input in complex forms (like JSON parameters), that data is immediately and irrevocably lost, leading to a highly frustrating user experience.
**Action:** When building tabbed interfaces containing forms or interactive data, avoid conditional rendering. Instead, mount all tab panels and use CSS properties like the HTML5 `hidden` attribute or Tailwind's `hidden` class to toggle visibility. This preserves the local component state while maintaining the illusion of tab switching.

## 2026-08-01 - Visual Confirmation for Inline Actions
**Learning:** Changing the text from "Copy" to "Copied!" provides minimal feedback and can be easily missed if the user's attention is focused on the data itself or if the button is small. To effectively communicate the success of a transient action like copying to the clipboard, changing the color state (e.g., swapping a neutral/accent color to a semantic success color like green) provides immediate, pre-attentive visual reinforcement.
**Action:** When implementing transient inline actions like "Copy", always toggle the background and text color to semantic success colors (e.g., green-500/20) along with the text change to provide strong visual confirmation of the successful action.
