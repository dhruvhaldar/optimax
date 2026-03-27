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
