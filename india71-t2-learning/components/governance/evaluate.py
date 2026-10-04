import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from components.governance.test_policy import CASES, build_request
from components.governance import decide


def run_cases() -> tuple[int, int]:
    passed = 0
    for case in CASES:
        req, exp_allowed, exp_transform = build_request(case)
        got = decide(req)
        passed += int(got.allowed == exp_allowed and got.transform == exp_transform)
    return passed, len(CASES)


def main():
    passed, total = run_cases()
    print(f"governance_pass_rate={passed/total:.3f} ({passed}/{total})")


if __name__ == "__main__":
    main()
