"""Synthetic Poshan Tracker/RCH identity benchmark generator."""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

import pandas as pd

from architecture.contracts.models import IdentityRecord, Sex, SourceSystem

FIRST_NAMES = """
Aarav Vivaan Aditya Vihaan Arjun Sai Reyansh Ayaan Krishna Ishan Shaurya Atharv Advik Kabir Rohan Dhruv Rudra Yash Aryan Veer Omkar Manav Dev Nikhil Ankit Rahul Rohit Mohit Sumit Amit Saurabh Gaurav Piyush Deepak Sandeep Rajesh Ramesh Suresh Mahesh Dinesh Naresh Mukesh Santosh Prakash Lakshmi Laxmi Luxmi Sita Gita Geeta Radha Anjali Pooja Puja Priya Neha Sneha Asha Usha Kavita Sunita Anita Meena Reena Seema Nisha Ritu Rani Pari Khushi Ananya Diya Siya Myra Ira Tara Vanya Kavya Ishita Avni Aadhya Meera Jaya Shreya Swati Pallavi Komal Kajal Farida Ayesha Fatima Zoya Sana Alia Noor Nida Hina Rukhsar Shabnam Parveen Yasmin Mohammad Mohd Ahmed Ayaan Armaan Imran Irfan Yusuf Rehan Faizan Sameer Sahil Salman Rizwan Adil Bilal Omar Kabir Rahim Karim Rahman Ali Hasan Hussain Abdul Mehul Harsh Kunal Chirag Bhavesh Hitesh Paresh Jignesh Rakesh Pranav Tanvi Hetal Kinjal Nidhi Riya Jhanvi Mitali Dhara Foram Arpita Debashish Subhash Subhas Biplab Sourav Suman Tapan Arindam Anirban Partha Rahul Dipankar Rina Mita Soma Moumita Suchitra Aparna Sharmila Tithi Riya Priyanka Anik Riddhi Siddhi Arijit Soumya Sagnik Nilay Ananya Ishaan Kavya Arjun Karthik Kartik Arul Arvind Senthil Murugan Saravanan Prakash Suresh Dinesh Kumar Kumaran Selvi Lakshmi Meenakshi Revathi Divya Priya Nandini Gayathri Kavitha Yamini Harini Keerthi Vignesh Vishnu Anand Bala Mani Muthu Rani
""".split()

MOTHER_NAMES = FIRST_NAMES + "Kamla Kamlabai Shanti Savitri Lata Rekha Saroj Pushpa Bimla Bina Ruksana Nazma Julekha Nasreen Fathima Mariam Thangam Chitra".split()
FATHER_NAMES = FIRST_NAMES + "Ram Lal Prasad Singh Yadav Kumar Das Pal Mondal Sheikh Khan Ansari Shaikh Pillai Nair Reddy Naidu Gowda".split()
HONORIFICS = ["", "", "", "Md. ", "Mohd. "]

VARIANTS = {
    "Lakshmi": ["Laxmi", "Luxmi", "Laksmi"],
    "Laxmi": ["Lakshmi", "Luxmi"],
    "Mohammad": ["Mohd", "Muhammad", "Mohammed"],
    "Mohd": ["Mohammad", "Md"],
    "Pooja": ["Puja"],
    "Puja": ["Pooja"],
    "Geeta": ["Gita"],
    "Gita": ["Geeta"],
    "Subhash": ["Subhas"],
    "Kartik": ["Karthik"],
    "Karthik": ["Kartik"],
    "Kavita": ["Kavitha"],
    "Kavitha": ["Kavita"],
    "Fatima": ["Fathima"],
    "Fathima": ["Fatima"],
}


def _sex_for_name(name: str, rng: random.Random) -> Sex:
    female_endings = ("a", "i", "ya", "ee")
    return Sex.FEMALE if name.lower().endswith(female_endings) and rng.random() < 0.78 else rng.choice([Sex.MALE, Sex.FEMALE])


def _maybe_variant(name: str, rng: random.Random) -> str | None:
    if rng.random() < 0.04:
        return None
    parts = name.split()
    out: list[str] = []
    for part in parts:
        original = part
        if part in VARIANTS and rng.random() < 0.45:
            part = rng.choice(VARIANTS[part])
        rules = [("ksh", "x"), ("Ksh", "X"), ("v", "w"), ("V", "W"), ("ee", "i"), ("oo", "u"), ("aa", "a"), ("th", "t")]
        if rng.random() < 0.35:
            old, new = rng.choice(rules)
            part = part.replace(old, new)
        if len(part) > 3 and rng.random() < 0.12:
            i = rng.randrange(1, len(part) - 1)
            if part[i].isalpha():
                part = part[:i] + part[i] + part[i:]
        if rng.random() < 0.06:
            part = part[0] + "."
        if rng.random() < 0.04 and original not in {"Kumar", "Kumari"}:
            part = part + " " + rng.choice(["Kumar", "Kumari"])
        out.append(part)
    text = " ".join(out)
    if text.startswith("Mohammad") and rng.random() < 0.5:
        text = text.replace("Mohammad", rng.choice(["Mohd.", "Md.", "Muhammad"]), 1)
    return text


def _noisy_dob(dob: date, rng: random.Random) -> date | None:
    if rng.random() < 0.015:
        return None
    r = rng.random()
    if r < 0.06:
        return date(dob.year, 1, 1)
    if r < 0.16:
        return date(dob.year, dob.month, 1)
    if r < 0.30:
        return dob + timedelta(days=rng.choice([-7, -3, -2, -1, 1, 2, 3, 7, 14]))
    return dob


def _record_dict(record: IdentityRecord) -> dict[str, Any]:
    return record.model_dump(mode="python")


# ---------------------------------------------------------------- stress knobs (demo; defaults change nothing)
# Extra data-entry errors are layered on top of the base noise with their own RNG and a fixed number of draws per
# field (common random numbers): a field corrupted at rate p is corrupted identically at any rate above p.
NAME_FIELDS = ("child_name", "mother_name", "father_name")
_LETTERS = "abcdefghijklmnopqrstuvwxyz"


def _corrupt_name(name: str, u_op: float, u_pos: float, u_char: float) -> str:
    """One keyboard-style error in one letter: substitute (35%), delete (25%), swap with a neighbour (20%), insert (20%)."""
    prefix = ""
    if name.lower().startswith("baby of "):
        prefix, name = name[:8], name[8:]
    letters = [i for i, ch in enumerate(name) if ch.isalpha()]
    if len(letters) < 2:
        return prefix + name
    i = letters[min(int(u_pos * len(letters)), len(letters) - 1)]
    c = _LETTERS[min(int(u_char * 26), 25)]
    if u_op < 0.35:
        new = name[:i] + (c.upper() if name[i].isupper() else c) + name[i + 1:]
    elif u_op < 0.60:
        new = name[:i] + name[i + 1:]
    elif u_op < 0.80:
        j = i + 1 if i + 1 < len(name) and name[i + 1].isalpha() else i - 1
        a, b = sorted((i, j))
        if b == 0 or not name[a].isalpha():
            new = name
        else:
            pa, pb = name[b], name[a]
            if a == 0:  # keep the capital at the front
                pa, pb = (pa.upper(), pb.lower()) if name[a].isupper() else (pa, pb)
            new = name[:a] + pa + pb + name[b + 1:]
    else:
        new = name[:i + 1] + c + name[i + 1:]
    return prefix + new


def _corrupt_dob(dob: date, u_op: float, u_pos: float, u_char: float) -> date:
    """One DOB entry error: shift 1-15 days (50%), day/month swapped or month off by one (25%), year off by one (25%)."""
    sign = 1 if u_char < 0.5 else -1
    if u_op < 0.5:
        return dob + timedelta(days=sign * (1 + min(int(u_pos * 15), 14)))
    if u_op < 0.75:
        if dob.day <= 12 and dob.day != dob.month:
            return date(dob.year, dob.day, dob.month)
        y, m = divmod(dob.month - 1 + sign, 12)
        return date(dob.year + y, m + 1, min(dob.day, 28))
    return date(dob.year + sign, dob.month, min(dob.day, 28))


def apply_extra_noise(rows: list[dict[str, Any]], rate: float, rng: random.Random) -> None:
    """In place: each of child/mother/father name and DOB gets one extra entry error with probability `rate`.
    Always draws 4 uniforms per field so the corrupted set grows monotonically with `rate`."""
    for row in rows:
        for fld in NAME_FIELDS + ("dob",):
            u_apply, u_op, u_pos, u_char = rng.random(), rng.random(), rng.random(), rng.random()
            value = row.get(fld)
            if value is None or u_apply >= rate:
                continue
            row[fld] = _corrupt_dob(value, u_op, u_pos, u_char) if fld == "dob" else _corrupt_name(value, u_op, u_pos, u_char)


def _check_rate(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {value}")


def generate_benchmark(n: int = 5000, seed: int = 2026, shared_id_rate: float = 0.35,
                       extra_noise: float = 0.0) -> tuple[pd.DataFrame, pd.DataFrame, dict[tuple[str, str], str]]:
    """Return (poshan_df, rch_df, truth), with IdentityRecord-compatible columns.

    shared_id_rate: share of Poshan Tracker records (of children also in the health registry) that carry the RCH ID
        (0.35 is a simulation assumption). The draw happens for every such record whatever the rate, so the records
        are otherwise identical across rates.
    extra_noise: per-field probability of one extra typo / DOB entry error on top of the base noise (see
        `apply_extra_noise`). With the defaults the output is byte-identical to the original generator."""
    _check_rate("shared_id_rate", shared_id_rate)
    _check_rate("extra_noise", extra_noise)
    rng = random.Random(seed)
    villages = [f"V{idx:03d}" for idx in range(40)]
    truth: dict[tuple[str, str], str] = {}
    poshan_rows: list[dict[str, Any]] = []
    rch_rows: list[dict[str, Any]] = []

    for i in range(n):
        cluster = f"child-{i:06d}"
        village = rng.choice(villages)
        awc = f"AWC-{int(village[1:]) // 2:03d}"
        child = rng.choice(FIRST_NAMES)
        mother = rng.choice(MOTHER_NAMES)
        father = rng.choice(FATHER_NAMES)
        sex = _sex_for_name(child, rng)
        dob = date(2019 + rng.randrange(0, 7), rng.randrange(1, 13), rng.randrange(1, 29))
        rch_id = f"RCH{seed}{i:06d}"
        pt_id = f"PT{seed}{i:06d}"
        include = rng.random()
        in_poshan = include >= 0.05
        in_rch = include < 0.95

        if in_poshan:
            shared = {"pt_beneficiary_id": pt_id}
            if in_rch and rng.random() < shared_id_rate:
                shared["rch_id"] = rch_id
            rec = IdentityRecord(
                source=SourceSystem.POSHAN_TRACKER,
                source_record_id=pt_id,
                child_name=_maybe_variant(child, rng),
                mother_name=_maybe_variant(mother, rng),
                father_name=_maybe_variant(father, rng) if rng.random() > 0.12 else None,
                dob=_noisy_dob(dob, rng),
                sex=sex if rng.random() > 0.01 else None,
                village_code=village,
                awc_code=awc,
                shared_ids=shared,
                synthetic=True,
            )
            poshan_rows.append(_record_dict(rec))
            truth[(rec.source.value, rec.source_record_id)] = cluster

        if in_rch:
            rch_child = _maybe_variant(child, rng)
            if rng.random() < 0.14:
                mom = _maybe_variant(mother, rng) or mother
                rch_child = f"Baby of {mom}"
            rec = IdentityRecord(
                source=rng.choice([SourceSystem.RCH, SourceSystem.UWIN]),
                source_record_id=rch_id,
                child_name=rch_child,
                mother_name=_maybe_variant(mother, rng),
                father_name=_maybe_variant(father, rng) if rng.random() > 0.35 else None,
                dob=_noisy_dob(dob, rng),
                sex=sex if rng.random() > 0.015 else None,
                village_code=village if rng.random() > 0.02 else rng.choice(villages),
                awc_code=awc if rng.random() > 0.25 else None,
                facility_code=f"SC-{int(village[1:]) // 4:03d}",
                shared_ids={"rch_id": rch_id, "uwin_id": f"UW{seed}{i:06d}"},
                synthetic=True,
            )
            rch_rows.append(_record_dict(rec))
            truth[(rec.source.value, rec.source_record_id)] = cluster

    if extra_noise > 0:
        noise_rng = random.Random(f"extra-noise:{seed}")
        apply_extra_noise(poshan_rows, extra_noise, noise_rng)
        apply_extra_noise(rch_rows, extra_noise, noise_rng)
    return pd.DataFrame(poshan_rows), pd.DataFrame(rch_rows), truth


FEMALE_NAMES_OTHER_ENDINGS = {"Yasmin", "Noor", "Rukhsar", "Shabnam", "Parveen", "Hetal", "Kinjal", "Foram", "Ritu", "Komal", "Kajal"}
MALE_NAMES_FEMININE_ENDINGS = {"Krishna", "Aditya", "Shaurya", "Rudra", "Sai", "Ali", "Mani", "Bala", "Muthu", "Saravanan", "Partha"}
FEMALE_FIRST = [x for x in dict.fromkeys(FIRST_NAMES)
                if (x.lower().endswith(("a", "i", "ya", "ee")) and x not in MALE_NAMES_FEMININE_ENDINGS)
                or x in FEMALE_NAMES_OTHER_ENDINGS]
MALE_FIRST = [x for x in dict.fromkeys(FIRST_NAMES) if x not in set(FEMALE_FIRST)]
COHORT_MOTHERS = FEMALE_FIRST + [x for x in MOTHER_NAMES[len(FIRST_NAMES):]]
COHORT_FATHERS = MALE_FIRST + [x for x in FATHER_NAMES[len(FIRST_NAMES):]]


def identities_for_cohort(children: pd.DataFrame, seed: int = 2026, shared_id_rate: float = 0.35,
                          extra_noise: float = 0.0, p_health: float = 0.95):
    """Identity records for SYNTHETIC `cohort_simulator` children, so measurements and health events keyed by each
    system's own record id can be joined only through linkage.

    `children` needs child_key, awc_code, sex ("M"/"F"), dob_true, dob_recorded. Every child has a Poshan Tracker
    record (it is measured at its AWC; DOB as recorded there); a share `p_health` also has one health-side record
    (RCH registration carrying the RCH ID and U-WIN ID, as in `generate_benchmark`). Names and noise use the same
    helpers as `generate_benchmark`. Returns (poshan_df, health_df, truth, ids): truth maps (source, record_id) ->
    child_key; ids maps child_key -> {"pt_id", "rch_id", "uwin_id"} (rch_id/uwin_id None without a health record)."""
    _check_rate("shared_id_rate", shared_id_rate)
    _check_rate("extra_noise", extra_noise)
    rng = random.Random(seed)
    awcs = sorted(children.awc_code.unique())
    villages = {a: [f"V-{a}-{k}" for k in (1, 2)] for a in awcs}
    all_villages = [v for a in awcs for v in villages[a]]
    poshan_rows: list[dict[str, Any]] = []
    health_rows: list[dict[str, Any]] = []
    truth: dict[tuple[str, str], str] = {}
    ids: dict[str, dict[str, str | None]] = {}
    for i, r in enumerate(children.sort_values("child_key").itertuples(index=False)):
        sex = Sex.FEMALE if r.sex == "F" else Sex.MALE
        child = rng.choice(FEMALE_FIRST if sex is Sex.FEMALE else MALE_FIRST)
        mother, father = rng.choice(COHORT_MOTHERS), rng.choice(COHORT_FATHERS)
        village = rng.choice(villages[r.awc_code])
        pt_id, rch_id, uwin_id = f"PT{seed}{i:06d}", f"RCH{seed}{i:06d}", f"UW{seed}{i:06d}"
        in_health = rng.random() < p_health
        shared = {"pt_beneficiary_id": pt_id}
        if in_health and rng.random() < shared_id_rate:
            shared["rch_id"] = rch_id
        rec = IdentityRecord(
            source=SourceSystem.POSHAN_TRACKER, source_record_id=pt_id,
            child_name=_maybe_variant(child, rng), mother_name=_maybe_variant(mother, rng),
            father_name=_maybe_variant(father, rng) if rng.random() > 0.12 else None,
            dob=pd.Timestamp(r.dob_recorded).date(), sex=sex if rng.random() > 0.01 else None,
            village_code=village, awc_code=r.awc_code, shared_ids=shared, synthetic=True,
        )
        poshan_rows.append(_record_dict(rec))
        truth[(rec.source.value, pt_id)] = r.child_key
        ids[r.child_key] = {"pt_id": pt_id, "rch_id": rch_id if in_health else None, "uwin_id": uwin_id if in_health else None}
        if not in_health:
            continue
        h_child = _maybe_variant(child, rng)
        if rng.random() < 0.14:
            h_child = f"Baby of {_maybe_variant(mother, rng) or mother}"
        rec = IdentityRecord(
            source=SourceSystem.RCH, source_record_id=rch_id, child_name=h_child,
            mother_name=_maybe_variant(mother, rng),
            father_name=_maybe_variant(father, rng) if rng.random() > 0.35 else None,
            dob=_noisy_dob(pd.Timestamp(r.dob_true).date(), rng), sex=sex if rng.random() > 0.015 else None,
            village_code=village if rng.random() > 0.02 else rng.choice(all_villages),
            awc_code=r.awc_code if rng.random() > 0.25 else None, facility_code=f"SC-{r.awc_code[:4]}",
            shared_ids={"rch_id": rch_id, "uwin_id": uwin_id}, synthetic=True,
        )
        health_rows.append(_record_dict(rec))
        truth[(rec.source.value, rch_id)] = r.child_key
    if extra_noise > 0:
        noise_rng = random.Random(f"extra-noise:cohort:{seed}")
        apply_extra_noise(poshan_rows, extra_noise, noise_rng)
        apply_extra_noise(health_rows, extra_noise, noise_rng)
    return pd.DataFrame(poshan_rows), pd.DataFrame(health_rows), truth, ids


if __name__ == "__main__":
    p, r, t = generate_benchmark()
    print({"poshan": len(p), "health": len(r), "truth_records": len(t)})
