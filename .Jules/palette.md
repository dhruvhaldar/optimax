[Output truncated for brevity]

## 2026-08-15 - Explicit aria-live on Error Alerts
**Learning:** While `role="alert"` theoretically implies `aria-live="assertive"`, depending on the browser and screen reader combination, the dynamic injection of error messages can sometimes fail to be announced immediately if the explicit `aria-live` attribute is missing.
**Action:** When rendering dynamic error messages or notifications, explicitly combine `aria-live="assertive"` with `role="alert"` to ensure maximum compatibility and guarantee that visually impaired users are immediately notified of form validation failures or server errors.