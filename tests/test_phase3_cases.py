from fas_bench.cases import reproduce_all, run_oracle, validate_all


def test_phase3_registry_and_packages_validate():
    result = validate_all()
    assert result["status"] == "PASS", result


def test_phase3_oracles_match_ground_truth():
    result = reproduce_all()
    assert result["status"] == "PASS", result


def test_gold_oracle_mutations_change_security_semantics():
    mutations = {
        "FAS-001": {"allowlist": False, "path_viable": True},
        "FAS-002": {"allowlist": True, "path_viable": False},
        "FAS-006": {"authorization": False, "path_viable": True},
        "FAS-016": {"explicit_deny": False},
        "FAS-020": {"alternate_path_viable": False, "alternate_protected": True},
    }
    expected = {
        "FAS-001": "EXPLOITABLE",
        "FAS-002": "NOT_EXPLOITABLE",
        "FAS-006": "EXPLOITABLE",
        "FAS-016": "EXPLOITABLE",
        "FAS-020": "REMEDIATED",
    }
    for case_id, mutation in mutations.items():
        result = run_oracle(case_id, mutation=mutation)
        assert result["observed_verdict"] == expected[case_id], (case_id, result)


def test_case_ids_are_exactly_the_initial_twenty():
    result = validate_all()
    assert result["case_count"] == 20
    assert [r["case_id"] for r in result["results"]] == [f"FAS-{i:03d}" for i in range(1, 21)]
