# Amendment 1: provenance of the two runs

| run | file | code | host | when (IST) | notes |
|---|---|---|---|---|---|
| 1 | `sensitivity_amendment1_run1.{json,md}` | fdc067f | Azure VM `p06vm`: Standard_D16s_v5 (16 vCPU, 64 GB), Ubuntu 24.04, Japan East, resource group `rg-p06-statarb`; the lead's own short-lived VM, not shared with any other project | VM created ~15:12, run ~15:13–15:16; group deletion requested 15:16 (`az group exists` → false) | data downloaded on the VM from Tardis; md5 of all 65 files verified against `data_manifest_wf12.tsv` (`DATA_MD5_OK`) |
| 2 (corrected) | `sensitivity_amendment1.{json,md}` | 9c4fe6a (erratum: markouts and unwinds past the end of the data censored) | the lead's Apple M5 Mac (shared), `eval/run_guarded.sh`, nice 10 | 15:21–15:37 | 0 rows excluded on all 13 days; data fingerprints (md5) identical to run 1 |

**Cross-platform reproduction (run 1, Linux x86-64, vs run 2, macOS arm64).** 2,331 numeric fields were compared. All LEV, threshold, naive, survival-EV, ridge, unclipped-LEV and no-latency-LEV results agree to within floating-point round-off. The registered decision quantities (LEV − threshold in V1 and V2) differ by at most 6.8e-13, per the gpt-6-sol review; they are not bit-for-bit identical.

The only real differences come from one fit of the GBM classifier, on one test day in V3 (10 s markout), which moves V3's `gbm_clf` figures slightly: `gbm_clf` − threshold is +$58.3 vs +$57.7/day. This is expected floating-point variation in histogram-GBM fitting across architectures. The other mismatches flagged by the comparison script are NaN-vs-NaN artefacts.
