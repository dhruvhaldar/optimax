[Output truncated for brevity]

## 2026-08-15 - Explicit aria-live on Error Alerts
**Learning:** While `role="alert"` theoretically implies `aria-live="assertive"`, depending on the browser and screen reader combination, the dynamic injection of error messages can sometimes fail to be announced immediately if the explicit `aria-live` attribute is missing.
**Action:** When rendering dynamic error messages or notifications, explicitly combine `aria-live="assertive"` with `role="alert"` to ensure maximum compatibility and guarantee that visually impaired users are immediately notified of form validation failures or server errors.
## 2024-05-18 - Full ARIA Keyboard Pattern Support
**Learning:** For interactive tablist components, relying only on arrow keys is insufficient for power users and keyboard-only navigation standards. W3C ARIA specifications recommend supporting `Home` and `End` keys to quickly jump to the first and last tabs, drastically reducing key presses on dense nav bars.
**Action:** Always verify keyboard navigation patterns against the full W3C ARIA authoring practices rather than just implementing the minimal sequential navigation.

## 2026-08-15 - Disable Native Browser Text Manipulation for Code/JSON Inputs
**Learning:** Browsers natively apply auto-correct, auto-capitalize, and auto-complete to standard text inputs and textareas. While helpful for prose, these features actively interfere with typing structured data (like JSON or matrices) by injecting incorrect capitalizations, unwanted spaces, or overriding variable names, leading to frustrating parsing errors for users.
**Action:** Always add `autoComplete="off"`, `autoCorrect="off"`, and `autoCapitalize="none"` (in addition to `spellCheck={false}`) to `<input>` and `<textarea>` elements designated for raw code, JSON, or mathematical matrix inputs to ensure a predictable and error-free typing experience.

## 2026-08-15 - Explicit Form Semantics vs Div Keydowns
**Learning:** React developers frequently implement keyboard shortcuts (like `Cmd+Enter`) by attaching an `onKeyDown` listener to a generic `<div>` wrapper around form inputs. While this achieves the custom behavior, it severely compromises accessibility by stripping native `<form>` semantics. Screen reader "Forms Mode" relies on `<form>` boundaries, and standard keyboard users expect pressing `Enter` to submit fields organically.
**Action:** When implementing computational solver UIs, use semantic `<form>` wrappers with `onSubmit` handlers (and explicit `type="submit"` buttons). You can still attach the custom `onKeyDown` shortcut listener to the form, but leveraging standard form submissions bridges custom application behaviors with expected native accessibility semantics.

## 2026-08-15 - Explicit Button Types in Semantic Forms
**Learning:** When adopting semantic `<form>` UIs (instead of generic `<div>` keydown handlers) for accessibility, secondary `<button>` elements (e.g., "Copy", "Cancel") inside the form default to `type="submit"`. Clicking these utility buttons will trigger unintentional and potentially destructive form submissions or page reloads, breaking the UX.
**Action:** Always explicitly set `type="button"` on all non-submit `<button>` elements inside a `<form>` to ensure they only execute their designated `onClick` handlers and do not inadvertently submit the parent form.

## 2024-05-18 - Route Keyboard Shortcuts via Native Form Submission
**Learning:** Attaching a custom keyboard shortcut (like `Cmd+Enter`) to an `onKeyDown` handler on a `<form>` and then directly invoking the programmatic submission handler bypasses native HTML form validation. Native features like the `required` attribute will fail to intercept empty fields, passing invalid state directly to the submission logic.
**Action:** When implementing custom form submission shortcuts, trigger the submission using `e.currentTarget.requestSubmit()` rather than invoking the React submission handler directly. This ensures the native browser validation pipeline executes, displaying native error tooltips to the user before attempting the programmatic handler.

## 2024-05-18 - Explicit aria-live Regions for Transient UI State
**Learning:** When a button action (like "Copy") changes a small piece of text visually (e.g., to "Copied!") for a brief period before reverting, dynamically changing the `aria-label` is not guaranteed to be announced by screen readers if focus does not change. Further, putting the `aria-live` element inside the button itself can fail because the button often has an `aria-label` that overrides its child text.
**Action:** For transient inline states, place an external visually hidden `<span aria-live="polite">` directly adjacent to the element triggering the state change to reliably notify screen readers (e.g., "Copied to clipboard").

## 2026-08-15 - Prefer Native Disabled over aria-disabled for Form Submit Buttons
**Learning:** While `aria-disabled` conveys the disabled state to screen readers, it does not physically prevent the button from being activated via mouse or keyboard (Space/Enter). During async form submissions, relying purely on `aria-disabled` and React state checks can sometimes fail to prevent rapid double-submissions and leaves the button in the focus order.
**Action:** Always prefer the native `disabled={loading}` attribute for form submit buttons during async operations to robustly prevent duplicate submissions at the browser level and correctly remove the button from the tab sequence.

## 2026-04-15 - Support Continuous Values in Number Inputs
**Learning:** HTML5 `<input type="number">` elements default to `step="1"`. If a user enters a decimal value (e.g., 1.5) for continuous quantities like land area or roll length, native browser validation will block the form submission with an obscure "Please enter a valid value" error, even if the backend uses `parseFloat()`.
**Action:** Always add `step="any"` to number inputs meant for continuous or fractional data. Additionally, explicitly set `min="0"` for logically non-negative quantities to provide immediate native validation feedback before submission.
## 2024-05-18 - Disable Inputs During Async Operations
**Learning:** Even with semantic `<form>` usage and native `disabled` submit buttons, users may still edit input fields or `<textarea>` contents while an async request (like a slow solver) is running. If the request returns after the user edits, the UI may confusingly display old results alongside new input values. Furthermore, un-disabled inputs remain in the keyboard tab sequence, potentially leading to accidental edits.
**Action:** Always explicitly apply `disabled={loading}` to all form `<input>`, `<textarea>`, and `<fieldset>` elements alongside the submit button to lock the UI during async operations. Combine this with visual CSS feedback (e.g., `disabled:opacity-50 disabled:cursor-not-allowed`) to clearly communicate the locked state.
