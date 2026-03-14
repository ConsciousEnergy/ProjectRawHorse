## Scope

**Plan Phase/Todo ID:** <!-- e.g., Phase 5 / timeline-mvp -->

**Summary:** <!-- 1-2 sentences describing what this PR does -->

## Changes

- <!-- List key changes -->

## Risk Assessment

- **Risk Level:** <!-- Low / Medium / High -->
- **Rollback Plan:** <!-- How to revert if something goes wrong -->

## Test Evidence

- [ ] Backend syntax check passes
- [ ] Frontend build passes
- [ ] API contract tests pass (if applicable)
- [ ] Manual smoke test completed

## Migration / Deployment Impact

- [ ] No DB migration needed
- [ ] DB migration needed (describe):
- [ ] Environment variable changes needed (describe):
- [ ] Docker image rebuild required

## Quality Gates

- [ ] No `any` types introduced in frontend code
- [ ] New endpoints have input validation
- [ ] New data paths have source citations (timeline/events)
- [ ] Performance: no new queries without LIMIT clauses
- [ ] Security: no secrets in code, no SQL injection paths
