import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from components.governance.test_policy import ADVERSARIAL, CASES, build_adversarial, build_request
from components.governance import decide


def run_cases() -> tuple[int, int]:
    passed = 0
    rows = [build_request(c) for c in CASES] + [build_adversarial(c) for c in ADVERSARIAL]
    for req, ctx, exp_allowed, exp_transform in rows:
        got = decide(req, ctx)
        passed += int(got.allowed == exp_allowed and got.transform == exp_transform)
    return passed, len(rows)


def main():
    passed, total = run_cases()
    print(f"governance_pass_rate={passed/total:.3f} ({passed}/{total})")


if __name__ == "__main__":
    main()
