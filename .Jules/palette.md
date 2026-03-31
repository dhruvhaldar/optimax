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
