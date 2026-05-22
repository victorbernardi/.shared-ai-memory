# Investigation Plan - Power BI Dashboard Navigation

- [x] Open browser with session and navigate to Diário de Bordo.
- [x] Wait for page load (10+ seconds).
- [x] Capture DOM and Screenshot.
- [x] Identify CSS selector for navigation items in the left sidebar.
  - Findings: The sidebar is inside a cross-origin iframe (`app.powerbi.com`).
  - Suggested selector: `.nav-item-container` or `.pbi-canvas-page-navigation-item`.
- [ ] Verify selector returns 7 elements (for Diário de Bordo).
  - Note: Cannot verify via top-level JS due to cross-origin restrictions.
- [x] Determine if elements are in an iframe or main DOM.
  - Findings: Definitely inside the Power BI iframe.
- [x] Check navigation behavior (top-level vs iframe).
  - Findings: Clicking items does not change the top-level URL; navigation happens within the iframe.
