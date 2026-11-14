# RF job facade acceptance drill (offline)

- PASS `5.1 help outputs`
- PASS `5.3 kill mid-run (process tree terminated)`
- PASS `5.3 restart get-status`
- PASS `5.3 reconcile after restart`
- PASS `5.3 resume to completion without re-running source`
- PASS `5.2 idempotent resubmit (no re-orchestration)`
- PASS `5.4 natural source failure JobView`
- PASS `5.5 cost known + unknown samples`

Failures: 0
Budget: see budget_observation.json (zero new downloads, zero paid calls).
