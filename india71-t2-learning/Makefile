.PHONY: test eval coverage docs pdf

test:
	python3 -m pytest -q eval/sim components eval/check_docs.py

eval:
	nice -n 10 python3 eval/run_eval.py

coverage:
	nice -n 10 python3 eval/coverage_test.py --seeds 101-130 --out eval/results/coverage_heldout.json

docs:
	python3 eval/check_docs.py

pdf:
	python3 deliverables/build_pdf.py && python3 deliverables/build_pdf.py --check
