import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from components.trust_audit.evaluate import evaluate

def main():
    df=evaluate((1,2,3,4,5),(0.10,))
    metric=float(df.risk_pps_block_mae_pp.mean())
    print(f"METRIC block_mae_pp_at_10pct_budget={metric:.3f}")
if __name__=="__main__": main()
