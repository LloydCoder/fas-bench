# FAS-005 — IDOR

## Purpose
An authenticated low-privilege user can retrieve another user's object because authorization is based on a caller-supplied object identifier.

## Attacker model
Authenticated user has only their own-resource permission and knows a second object identifier.

## Environment
Synthetic Linux/Python 3.12; no public network; synthetic credentials only.

## Oracle
The oracle derives an observed verdict from the effective synthetic state, independently of the expected verdict artifact.

## Limitations
Synthetic controlled experiment; not representative of production systems.

## Status
VALIDATED, subject to corpus-level CI and release gates.
