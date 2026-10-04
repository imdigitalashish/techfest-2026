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


def generate_benchmark(n: int = 5000, seed: int = 2026) -> tuple[pd.DataFrame, pd.DataFrame, dict[tuple[str, str], str]]:
    """Return (poshan_df, rch_df, truth), with IdentityRecord-compatible columns."""
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
            if in_rch and rng.random() < 0.35:
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

    return pd.DataFrame(poshan_rows), pd.DataFrame(rch_rows), truth


if __name__ == "__main__":
    p, r, t = generate_benchmark()
    print({"poshan": len(p), "health": len(r), "truth_records": len(t)})
