"""End-to-end Phase 8 self-evaluation over the released public corpus."""
from fas_bench.cases import CASES_ROOT
from fas_bench.contract import CASE_IDS
from fas_bench.evaluator import evaluate_submission_document
from fas_bench.scoring import build_perfect_submission, load_config
from fas_bench.scoring.engine import score_case

def test_full_20_case_self_evaluation():
    config = load_config()
    results = []
    for case_id in CASE_IDS:
        submission = build_perfect_submission(case_id, CASES_ROOT)
        evaluation = evaluate_submission_document(submission, CASES_ROOT)
        result = score_case(submission, evaluation, config=config, cases_root=CASES_ROOT)
        assert result.evaluation_status == "SUCCESS"
        assert result.case_id == case_id
        assert result.benchmark_version
        assert result.evaluator_version
        assert result.scoring_version
        assert 0 <= result.case_score <= 1
        results.append(result.as_dict())
    assert len(results) == 20
    assert {row["case_id"] for row in results} == set(CASE_IDS)
