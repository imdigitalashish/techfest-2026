"""Record simulator facts quoted in the docs (agent counts, ABIDES commit, task) in eval/results/sim_facts.json."""
import json, os, subprocess, sys, warnings
warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "components", "sim_env"))
import sim_env  # noqa: E402,F401
from abides_markets.configs import rmsc04  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "eval"))
from run_experiment import CFG  # noqa: E402

cfg = rmsc04.build_config(seed=0, end_time="10:05:00", stdout_log_level="WARNING", log_orders=False)
counts = {}
for ag in cfg["agents"]:
    counts[type(ag).__name__] = counts.get(type(ag).__name__, 0) + 1
commit = subprocess.run(["git", "-C", sim_env.ABIDES_DIR, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
import inspect  # noqa: E402
r_bar = inspect.signature(rmsc04.build_config).parameters["r_bar"].default
facts = dict(config="rmsc04", r_bar_cents=r_bar, tick_bps=1e4 / r_bar, agents_by_type=counts, n_agents_total=sum(counts.values()),
             n_trading_agents=sum(v for k, v in counts.items() if k != "ExchangeAgent"),
             abides_commit=commit, task=dict(side=CFG["side"], qty_default=4000, start=CFG["start"], end=CFG["end"],
                                             n_slots=CFG["n_slots"], end_time=CFG["end_time"]))
json.dump(facts, open(os.path.join(ROOT, "eval", "results", "sim_facts.json"), "w"), indent=1)
print(json.dumps(facts))
