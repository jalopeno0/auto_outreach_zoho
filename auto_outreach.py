import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Template:
    subject: str
    body: str
    signature: str = ""


def load_contacts(excel_path: str, sheet_name=0) -> pd.DataFrame:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # Trim column names
    df.columns = [str(c).strip() for c in df.columns]

    # Rename only the columns we care about
    df = df.rename(columns={
        "First Name": "first_name",
        "Email Address": "email",
        "tone": "tone"
    })

    # Trim string cells
    for c in df.columns:
        if pd.api.types.is_object_dtype(df[c]):
            df[c] = df[c].astype(str).str.strip()

    return df


def validate(df: pd.DataFrame) -> None:
    required = ["first_name", "email", "tone"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    bad = df[~df["email"].apply(lambda x: bool(EMAIL_RE.match(str(x).strip())))]
    if len(bad) > 0:
        raise ValueError(f"Found {len(bad)} invalid email(s). Example: {bad.iloc[0]['email']}")


def safe_format(template: str, row: Dict[str, str]) -> str:
    """
    Fill placeholders using row dict.
    If a placeholder is missing, leave it as {placeholder} so you can spot it in QA.
    """
    class SafeDict(dict):
        def __missing__(self, key):
            return "{" + key + "}"
    return template.format_map(SafeDict(**row))


def build_templates() -> Dict[str, Template]:
    """
    You manually edit the subject/body strings below.
    Use placeholders like {first_name}, {last_name}, {company}, {role}.
    NOTE: 'hot' is HTML so you can retain bold/colors/formatting.
    """
    TEMPLATES = {
        "hot": Template(
            subject="BCLA + BPI US West 2026: Your Invitation to the Premier Bioprocessing Event on the West Coast, {first_name}!",
            body=(
                "Hi {first_name},<br><br>"

                "I hope you are well! I wanted to reach out again on behalf of "
                "<strong>Biotech Connection Los Angeles (BCLA)</strong> to share details about the upcoming "
                "<strong>BioProcess International (BPI) US West 2026 Conference</strong>.<br><br>"

                "Held in partnership with BPI, this flagship West Coast bioprocessing event brings together leaders in the field "
                "to discuss advancements from cell line development to commercial manufacturing. The conference will take place "
                "from <strong>March 9–11, 2026</strong> at the <strong>San Diego Convention Center in San Diego, CA</strong>.<br><br>"

                "<div style='background-color:#f4f4f4; padding:12px; border-radius:6px;'>"
                "With the event just around the corner, don’t miss your chance to grab tickets at the lowest prices of the year! "
                "Connect with 900+ senior decision-makers, scientists, and engineers from across the globe to explore cutting-edge "
                "advancements in bioprocessing, including AI-driven innovation, biomanufacturing optimization, and more. "
                "With 5 dedicated content tracks covering all phases of bioprocessing, BPI West is the go-to platform for industry "
                "leaders to exchange ideas, discover solutions, and accelerate your journey from molecule to market. "
                "Don’t just keep up with the industry; get the resources needed to lead it."
                "</div><br>"

                "<strong>New for 2026, attendees have two great opportunities to participate at this year’s event in San Diego:</strong><br><br>"

                "<ul>"
                "<li>"
                "<strong>Complimentary Wednesday March 11th Exhibit Hall Pass:</strong> "
                "This complimentary one-day exhibit hall pass provides access to all 90+ exhibitors, live technology demonstrations, "
                "Innovation and Community Stage, and networking opportunities with 800+ attendees. "
                "The exhibit hall is open on Wednesday from 9:00 AM – 4:30 PM."
                "</li>"
                "</ul>"

                "<p style='color:#d32f2f; font-weight:bold; margin: 0 0 12px 0;'>"
                "Register by February 27, 2026. Ticket quantities are limited."
                "</p>"

                "<ul>"
                "<li>"
                "<strong>30% Discount for All Access Main Conference Pass –</strong> "
                "Receive a 30% discount (discount code <strong>BCLA30</strong>) to attend the full conference and access to 125+ "
                "scientific presentations across 5 tracks designed to optimize efficiency and innovation across bioprocessing."
                "</li>"
                "</ul><br>"

                "<p><strong>Registration:</strong> "
                "<a href='https://informaconnect.com/bioprocess-international-us-west-partner-bookings/purchase/select-package/?vip_code=BCLA30&utm_source=BCLA&utm_medium=web&utm_campaign=BCLA'>Register here</a>"
                "</p><br>"

                "We would greatly appreciate your help in sharing this event within your network and thank you again for your continued support!<br>"
            ),
            signature=(
                "Kind regards,<br><br>"
                "<strong>Pepper Yang</strong><br>"
                "Chemistry PhD Student, UCLA<br>"
                "Outreach Associate, Biotech Connection Los Angeles (BCLA)"
            ),
        ),

        "cold": Template(
            subject="YOUR COLD SUBJECT HERE, {first_name}",
            body=(
                "Hi {first_name},\n\n"
                "YOUR COLD EMAIL BODY HERE.\n\n"
                "Thanks!"
            ),
            signature="Best,\nPepper"
        ),
    }
    return TEMPLATES