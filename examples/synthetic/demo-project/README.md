# Synthetic End-to-End Demo Project

This fully fictional home-organization profile exercises the four production Skills with deterministic local mock executors and explicit human-approval mocks. It uses no private staging, real account, performance metrics, external service, secret, or third-party asset.

Run from the repository root:

```powershell
python scripts/run_synthetic_demo.py
python -m unittest discover -s tests -p "test_core_gates.py"
```

The runner emits candidates, mock approvals, Task Card, Keyword Plan, Writing draft, approved Finalization, eight locally rendered SVG pages, Visual Output, QA checks, and Production Manifest under `artifacts/`. The run is deterministic in content; timestamps and output hashes are regenerated each run. Approval records are synthetic test fixtures and are not valid real approvals.
