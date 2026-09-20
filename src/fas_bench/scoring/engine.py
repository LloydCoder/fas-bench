"""Phase 8 scoring over authoritative Phase 4-7 outputs."""
from __future__ import annotations
import json
from pathlib import Path
from ..contract import BENCHMARK_VERSION,EVALUATOR_VERSION,SCHEMA_VERSION
from ..cases import CASES_ROOT
from .metrics import binary_metrics,evidence_score,brier_score,expected_calibration_error
from .models import CaseScore,ScoreComponent,ScoringConfig
DEFAULT_CONFIG_PATH=Path(__file__).resolve().parents[3]/"configs/scoring/v0.1.json"
def load_config(path=None): return ScoringConfig.from_dict(json.loads((path or DEFAULT_CONFIG_PATH).read_text(encoding="utf-8")))
def _gold(case_id,cases_root=None):
    root=Path(cases_root or CASES_ROOT)/case_id; exp=root/"expected"
    read=lambda n:json.loads((exp/n).read_text(encoding="utf-8"))
    case=json.loads((root/"case.json").read_text(encoding="utf-8"))
    return {"case":case,"finding":read("findings.json"),"verdict":read("verdict.json"),"claims":read("claims.json"),"graph":read("attack_graph.json"),"remediation":read("remediation.json")}
def _component(name,norm,weight,raw,formula,available=True): return ScoreComponent(name,float(norm),float(weight),available,float(norm)*float(weight),formula=formula,raw=raw)
def _reachability(e):
    path=e.security_condition.path_status; expected=e.expected_verdict in {"EXPLOITABLE","CONDITIONALLY_EXPLOITABLE"}; observed=path in {"VIABLE","COMPLETE"}
    return {"source_reachable":path in {"VIABLE","COMPLETE","BLOCKED"},"sink_reachable":observed,"path_reachable":observed,"control_effective":e.security_condition.effective_control_state=="EFFECTIVE","score":1.0 if observed==expected else 0.0}
def _impact(sub,gold):
    a=sub.get("impact"); b=gold.get("impact") or gold["case"].get("impact") or {}
    if not isinstance(a,dict) or not b:return {"available":False}
    keys=sorted(set(a)|set(b)); correct=sum(a.get(k)==b.get(k) for k in keys)
    return {"available":True,"accuracy":correct/len(keys) if keys else 1.0,"matched_dimensions":correct,"dimensions":len(keys)}
def _specificity(sub,verified):
    claims=sub.get("claims",[]); supported=sum(1 for c in claims if c.get("related_evidence"))
    return min(1.0,verified/max(1,supported)) if claims else 0.0
def score_case(submission,evaluation,*,config=None,cases_root=None):
    cfg=config or load_config()
    if evaluation.case_id!=submission.get("case_id") or evaluation.submission_id!=submission.get("submission_id"):raise ValueError("submission/evaluation identity mismatch")
    gold=_gold(evaluation.case_id,cases_root); finding=evaluation.finding
    fm=binary_metrics(1 if finding.matched else 0,max(0,len(submission.get("findings",[]))-(1 if finding.matched else 0)),0 if finding.matched else 1)
    em=evaluation.evidence; submitted=int(em["submitted_evidence_count"]); invalid=int(em["invalid_evidence_count"]); verified=int(em["verified_evidence_count"])
    validity=verified/submitted if submitted else 0.0; coverage=float(em["coverage"]); relevance=(verified+0.25*int(em["unresolved_evidence_count"]))/submitted if submitted else 0.0; specificity=_specificity(submission,verified)
    es=evidence_score(validity,relevance,coverage,specificity,cfg.evidence_weights); integrity=invalid/submitted if submitted else 0.0
    p=cfg.integrity_policy; cap=1.0 if integrity<=p["max_unpenalized"] else p["cap_50"] if integrity<=p["max_capped_50"] else p["cap_25"]
    verdict=1.0 if evaluation.verdict.verdict_correct else 0.0; reach=_reachability(evaluation); graph=evaluation.graph or {}; graph_score=float(graph.get("graph_score",0)) if graph else 0.0
    impact=_impact(submission,gold); conf=float(submission["verdict"]["confidence"]); outcome=evaluation.verdict.verdict_correct; bs=brier_score([conf],[outcome]); cal=expected_calibration_error([conf],[outcome],cfg.calibration["bins"]); cal_score=(2-bs-cal["ece"])/2
    remediation={"available":False,"status":"NOT_APPLICABLE","correct":None}
    if evaluation.expected_verdict in {"REMEDIATED","REMEDIATION_FAILED","REGRESSED"}:
        candidate=(submission.get("remediation") or {}).get("status") or (submission.get("remediation") or {}).get("verification_status"); remediation={"available":True,"status":candidate,"correct":candidate==evaluation.expected_verdict}
    telemetry=(submission.get("metadata") or {}).get("telemetry"); efficiency={"available":isinstance(telemetry,dict) and bool(telemetry),"telemetry":telemetry if isinstance(telemetry,dict) else None}
    fp_res=1.0 if evaluation.expected_verdict=="NOT_EXPLOITABLE" and evaluation.verdict.verdict_correct else (1.0 if evaluation.expected_verdict!="NOT_EXPLOITABLE" else 0.0)
    raw={"evidence":(es,cfg.composite_weights["evidence"],{"score":es},"weighted evidence"),"verdict":(verdict,cfg.composite_weights["verdict"],{"accuracy":verdict},"exact verdict correctness"),"reachability":(reach["score"],cfg.composite_weights["reachability"],reach,"path-state agreement"),"attack_path":(graph_score,cfg.composite_weights["attack_path"],graph,"Phase 6 graph score"),"false_positive_resistance":(fp_res,cfg.composite_weights["false_positive_resistance"],{"score":fp_res},"case-aware false-positive metric"),"remediation":((1 if remediation["correct"] else 0) if remediation["available"] else 1,cfg.composite_weights["remediation"],remediation,"Phase 7 status agreement or not applicable"),"calibration":(cal_score,cfg.composite_weights["calibration"],{"brier":bs,"ece":cal["ece"]},"mean of 1-Brier and 1-ECE"),"efficiency":(0,cfg.composite_weights["efficiency"],efficiency,"telemetry required; unavailable is excluded")}
    available={k:v for k,v in raw.items() if k!="efficiency" or efficiency["available"]}; denom=sum(v[1] for v in available.values()); comps={k:_component(k,*v,available=k in available) for k,v in raw.items()}; uncapped=sum(v[0]*v[1] for v in available.values())/denom if denom else 0.0; final=min(uncapped,cap)
    warnings=("efficiency telemetry unavailable; excluded from composite denominator",) if not efficiency["available"] else ()
    case_meta=gold["case"].get("metadata",{})
    return CaseScore(evaluation.case_id,BENCHMARK_VERSION,EVALUATOR_VERSION,cfg.scoring_version,submission["submission_id"],evaluation.expected_verdict,submission["verdict"]["verdict"],evaluation.verdict.verdict_correct,fm,{"score":es,"validity":validity,"relevance":relevance,"coverage":coverage,"specificity":specificity},reach,{"available":bool(graph),"score":graph_score,"node_metrics":graph.get("node_metrics",{}),"edge_metrics":graph.get("edge_metrics",{}),"path_completeness":graph.get("path_completeness",0),"boundary_crossing_metrics":graph.get("boundary_crossing_metrics",{})},impact,remediation,{"brier":bs,"ece":cal["ece"],"score":cal_score,"bins":cal["bins"],"target":"verdict_correctness"},efficiency,{"evidence_integrity_rate":integrity,"invalid_evidence_count":invalid,"verified_evidence_count":verified,"score_cap":cap,"uncapped_score":uncapped,"integrity_status":"CAPPED" if cap<1 else "CLEAR"},comps,final,"SUCCESS",(),warnings)
def score_submission(submission_path,*,cases_root=None,config=None):
    from ..evaluator import evaluate_submission_document
    submission=json.loads(Path(submission_path).read_text(encoding="utf-8")); evaluation=evaluate_submission_document(submission,cases_root); return score_case(submission,evaluation,config=config,cases_root=cases_root)
def build_perfect_submission(case_id,cases_root=None):
    root=Path(cases_root or CASES_ROOT)/case_id/"expected"; read=lambda n:json.loads((root/n).read_text(encoding="utf-8")); finding=read("findings.json"); claim=read("claims.json"); evidence=read("evidence.json"); verdict=read("verdict.json"); graph=read("attack_graph.json")
    return {"benchmark_version":BENCHMARK_VERSION,"schema_version":SCHEMA_VERSION,"submission_id":f"SUB-SELF-{case_id}","case_id":case_id,"system":{"system_name":"fas-bench-self-test","system_version":"0.1.0","timestamp":"2026-01-01T00:00:00Z"},"verdict":verdict,"findings":[finding],"claims":[claim],"evidence":evidence,"attack_paths":graph.get("paths",[]),"attack_graph":graph,"impact":(read("remediation.json").get("impact") if isinstance(read("remediation.json"),dict) else None),"remediation":None,"verification":{"verification_id":f"VER-SELF-{case_id}","status":"VERIFIED","method":"deterministic self-test","evidence_ids":[e["evidence_id"] for e in evidence]},"metadata":{"self_test":True}}
