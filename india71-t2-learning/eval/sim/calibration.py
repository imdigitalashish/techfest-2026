"""Published aggregates the synthetic district is calibrated to (single source of truth).

ASER 2024 (Rural), Std III children in GOVERNMENT schools, All India:
- 23.4 % can read a Std II level text ("increased from 16.3% in 2022 to 23.4%")
- 27.6 % can do at least subtraction ("from 20.2% to 27.6% — in government schools")
Source: ASER Centre, Annual Status of Education Report (Rural) 2024, national report,
https://asercentre.org/wp-content/uploads/2022/12/ASER_2024_Final-Report_13_2_24-1.pdf
(accessed 2026-10-04; tidy copy: data/public/aser2024_state_std3.csv).
"""
ASER2024_GOVT_STD3 = {"target_read_goal": 0.234, "target_math_goal": 0.276}
