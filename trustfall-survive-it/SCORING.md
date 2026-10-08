# Scoring

TRUSTFALL is scored out of 100 points.

## Automated evaluation — 80 points

| Area | Points |
|---|---:|
| Security | 30 |
| Utility | 15 |
| Opponent resistance | 15 |
| Red-team effectiveness | 15 |
| Recovery | 5 |

Security alone is not enough. Blocking every request is a utility failure: honest reads, summaries, proposals, and authorized commits must still work. Opponent resistance measures how well the frozen build handles assigned attacks. Red-team attacks should be distinct, purposeful, and evidence-driven. Recovery rewards a demonstrated repair from the pre-patch snapshot to the final snapshot without breaking honest behavior.

## Engineering Leader review — 20 points

| Dimension | Points |
|---|---:|
| Implementation | 8 |
| Creativity | 4 |
| Explanation | 4 |
| Collaboration | 4 |

Reviewers use the code, test evidence, attack quality, snapshots, and Engineering Decision Card. Provider choice is not scored.
