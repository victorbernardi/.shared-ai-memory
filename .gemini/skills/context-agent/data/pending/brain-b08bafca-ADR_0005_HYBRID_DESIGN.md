# ADR-0005: Adopt Hybrid Liquid Glass UI with Snapshot Engine

## Status
Accepted

## Date
2026-04-30

## Context and Problem Statement
The Inova M6 Executive Dashboard underwent a visual modernization to an "Industrial Brutalist" theme (Dark mode, high contrast). The user rejected this design, preferring the original "Liquid Glass" (Light mode, Apple-esque) aesthetic. However, the original dashboard was monolithic (11MB) and exhibited poor performance.

## Decision Drivers
- **User Preference**: Strict requirement for the "Liquid Glass" visual identity.
- **Performance**: Must maintain the <1.5s TTI (Time to Interactive) achieved with the snapshot architecture.
- **Maintainability**: Need for modular data handling to prevent browser execution timeouts.

## Considered Options
1.  **Pure Revert**: Return to `Dashboard_Executivo_M6.html` as-is. (Rejected: 11MB file size, slow loading).
2.  **Stay with Industrial**: Convince user of the new design. (Rejected: Explicit user disapproval).
3.  **Hybrid Approach**: Reconstruct the Liquid Glass UI using the Snapshot Engine. (Accepted).

## Decision Outcome
Adopt the hybrid approach. We will use the HTML/CSS from the original design but replace the internal data block with the `DataLoader` pattern developed in the current session.

### Consequences
- **Positive**: Restores user-approved visuals while keeping performance gains.
- **Negative**: Requires careful mapping between English data keys and Portuguese UI labels.
- **Neutral**: Requires updating `aggregator.py` to support legacy UI filter metadata.

## Confirmation
- Verification of TTI using Chrome DevTools (simulated).
- Visual check against original v4.3 screenshots.
- Financial parity audit (Diff Zero).
