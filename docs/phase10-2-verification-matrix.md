# Phase 10.2 Verification Matrix

| Area | Implementation | Independent check | Adversarial test | Reproducibility | CI gate |
|---|---|---|---|---|---|
| Canonical JSON | canonical.py | verification.canonical_json | non-finite rejection | deterministic serialization | CI |
| Tree identity | phase10.py | verification.digest_tree | symlink/order tests | repeated digest | CI |
| Release manifest | phase10.py | independent manifest verifier | component tamper | rebuild equality | Release Gate |
| Evidence | Phase 4 resolver | reference location primitives | wrong range/snippet | deterministic | CI |
| Graph identity | Phase 6 engine | reference graph identity | reordered graph fixture | deterministic | CI |
| Scoring boundary | Phase 8 engine | reference score | invalid boundaries | deterministic | CI |
| Secure harness | Phase 9 runner | existing security integration | isolation/resource tests | repeated policy semantics | CI/Security |
| Corpus | cases.py/phase10.py | population/digest checks | case/fixture mutation | gold reproduction | Release Gate |
| Independence | phase10 audit | AST-based regression | forbidden import surface | clean environment | CI/Security |
| Packaging | pyproject/build | installed CLI smoke tests | package leakage | clean wheel install | Release Gate |
| Certification | verification.certify | derived policy | NOT_ASSESSED/tamper | deterministic report | Release Gate |

## Independence boundary

The independent verifier is separately implemented and does not call the production release verifier. The differential suite deliberately compares selected production primitives against the simpler reference implementations.

This matrix is not a claim that every benchmark semantic has been independently proven. Complete evaluator correctness, scientific ground-truth validity, statistical representativeness, model-training contamination freedom and host/kernel security remain external-review boundaries.
