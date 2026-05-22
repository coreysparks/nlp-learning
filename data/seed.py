"""
Creates and populates data/complaints.db with synthetic customer complaint data.
Run from the project root: python data/seed.py

Noise features baked in:
  - Typos and misspellings (common real-world patterns)
  - Informal / abbreviated writing ("cant", "wont", "app keeps crashing lol")
  - Vague complaints with no product-specific vocabulary
  - Ambiguous cross-category text (e.g. "fee" language in both Credit Card and Checking)
  - Mixed-topic complaints referencing two categories at once
  - Capitalization inconsistencies and missing punctuation
  - Filler/emotional text with low information content
"""

import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "complaints.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS complaints (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    submitted_at    TEXT NOT NULL,
    customer_id     INTEGER NOT NULL,
    product_category TEXT NOT NULL,
    channel         TEXT NOT NULL,
    sentiment_label TEXT NOT NULL,
    resolved        INTEGER NOT NULL,
    complaint_text  TEXT NOT NULL
);
"""

PRODUCT_CATEGORIES = [
    "Credit Card",
    "Mortgage",
    "Personal Loan",
    "Checking Account",
    "Savings Account",
    "Auto Insurance",
    "Home Insurance",
    "Investment Account",
    "Mobile Banking App",
    "Customer Service",
]

CHANNELS = ["web", "phone", "email", "chat"]

COMPLAINTS = {
    "Credit Card": [
        # Clean originals
        ("negative", "I was charged a late fee even though I paid on time. This is completely unacceptable and I want it reversed immediately."),
        ("negative", "My credit limit was lowered without any notice. I was embarrassed when my card was declined at the store."),
        ("negative", "There are unauthorized charges on my statement that I did not make. I need this investigated right away."),
        ("neutral",  "I requested a credit limit increase two weeks ago and still have not received a decision. How long does this process take?"),
        ("negative", "The rewards points I earned last quarter never posted to my account. I have been waiting over a month for this to be corrected."),
        ("positive", "I wanted to let you know that your fraud team caught suspicious activity on my account before I even noticed. Great job."),
        ("negative", "Your interest rate is way too high compared to competitors. I am considering closing this account."),
        ("neutral",  "I am trying to understand how the cashback tiers work. The terms on the website are confusing."),
        # Noisy additions
        ("negative", "late fee charged again!!! i payed on time why is this so hard"),
        ("negative", "card got declined at grocery store so embarasing. limit was lowered and nobody told me??"),
        ("negative", "theres charges on here i didnt make. fraud i think. plz help asap"),
        ("neutral",  "been waiting 2 weeks on limit increase request no response yet"),
        ("negative", "points from last quarter still not showing up. been a month. fix this"),
        ("negative", "APR is ridiculous compared to other cards im looking at canceling"),
        ("neutral",  "dont really understand the rewards tiers can someone explain"),
        ("negative", "i got charged an annual fee i dont remember signing up for"),
        ("negative", "my card number was stolen, saw charges i didnt make, called and was on hold forever"),
        ("neutral",  "trying to dispute a charge but the form on the website wont load"),
        ("negative", "interest charges look wrong on my statment this month"),
        ("positive", "fraud alert text saved me, caught it fast, great service"),
        # Ambiguous / cross-category (fee language overlaps with Checking)
        ("negative", "got hit with a fee i didnt expect, not sure if its from my card or checking account but its wrong either way"),
        ("negative", "the customer service rep told me my payment posted but i was still charged a fee, nobody knows whats going on"),
        ("neutral",  "called about my account and they transferred me three times and i still dont have an answer about my balance"),
        # Vague / low signal
        ("negative", "everything about this is wrong and i am very frustrated"),
        ("negative", "this is unacceptable i want someone to call me back today"),
    ],

    "Mortgage": [
        ("negative", "My escrow analysis is wrong and my monthly payment jumped by $400 with no explanation. Someone needs to call me back."),
        ("negative", "I have been trying to get a payoff statement for three weeks. Every time I call I am transferred and nobody can help me."),
        ("neutral",  "I would like to know what options are available for refinancing my current 30-year mortgage."),
        ("negative", "The property tax payment from my escrow was sent to the wrong county. Now I have a late penalty and your company should pay it."),
        ("negative", "I submitted a loan modification application 60 days ago and have heard nothing. Is there any update?"),
        ("positive", "Your mortgage advisor walked me through every step of the closing process. Made what could have been stressful very smooth."),
        ("neutral",  "I need to remove PMI from my loan. I believe I have reached 20 percent equity based on recent appraisals in my area."),
        # Noisy additions
        ("negative", "escrow is messed up my payment went up $400 no warning at all someone call me"),
        ("negative", "been trying to get payoff statement for 3 weeks keep getting transfered"),
        ("neutral",  "want to refi my 30yr what options do i have"),
        ("negative", "property tax got sent to wrong county now i have a penaly YOUR fault"),
        ("negative", "loan mod application from 2 months ago still no update is anyone working on this"),
        ("negative", "payment amount changed again, third time this year, escrow keeps fluctuating"),
        ("neutral",  "how do i get pmi removed i think i have enough equity now"),
        ("negative", "closing was delayed 3 times because of paperwork errors on your end cost me money"),
        ("negative", "hazard insurance was cancelled because you guys didnt pay it from escrow. fix this NOW"),
        ("neutral",  "i want to set up biweekly payments instead of monthly how do i do that"),
        # Ambiguous (loan language overlaps with Personal Loan)
        ("negative", "my monthly payment changed and nobody explained why, i thought the rate was fixed"),
        ("negative", "i have a loan with you and the terms dont match what i signed, need someone to review"),
        # Vague
        ("negative", "nobody can give me a straight answer, ive called 4 times"),
        ("negative", "i just need someone to actually help me and not transfer me again"),
    ],

    "Personal Loan": [
        ("negative", "I was approved for a loan and then told the funds would be deposited within two business days. It has been a week."),
        ("neutral",  "I want to pay off my loan early. Can you confirm there is no prepayment penalty on my account?"),
        ("negative", "The interest rate I was given at closing does not match what I was quoted during the application. I need this corrected."),
        ("negative", "My autopay keeps failing even though my bank account has sufficient funds. I should not be charged late fees for your system error."),
        ("positive", "Getting approved was fast and easy. The rate was competitive and the funds arrived exactly when promised."),
        # Noisy additions
        ("negative", "approved last week funds still not here, told 2 business days what is going on"),
        ("neutral",  "can i pay off early? is there a penalty? need to know asap"),
        ("negative", "rate at closing is higher than what they quoted me on the phone. bait and switch??"),
        ("negative", "autopay failed again and i have money in my account!!! stop charging me late fees for YOUR error"),
        ("negative", "got a loan 3 months ago and still confused about what im actually paying for, fees dont make sense"),
        ("neutral",  "how do i change my payment due date on my personal loan"),
        ("negative", "loan funded but amount was $500 less than approved amount no explanation given"),
        # Ambiguous (overlaps with Mortgage on rate/payment language)
        ("negative", "the monthly payment doesnt match what was in my documents when i signed"),
        ("negative", "interest rate went up on my loan i thought it was fixed rate"),
        # Vague
        ("negative", "this is a mess, wrong amount, wrong rate, nothing is right"),
    ],

    "Checking Account": [
        ("negative", "I was hit with an overdraft fee for a charge that posted before a deposit that arrived the same morning. This is not fair."),
        ("negative", "My direct deposit did not post on payday. I have bills due and this caused a cascade of problems."),
        ("neutral",  "I need to update the beneficiary on my account. The website keeps erroring out when I try to save the changes."),
        ("negative", "Your teller gave me incorrect information about account fees and I was charged things I never expected. I want a refund."),
        ("positive", "I lost my debit card and a new one was in my mailbox within two days. Really appreciate the quick turnaround."),
        ("negative", "I have been a customer for 15 years and the new monthly maintenance fee with no warning is insulting."),
        ("neutral",  "Can you explain the difference between available balance and current balance? I keep getting confused and it has caused problems."),
        # Noisy additions
        ("negative", "overdraft fee is BS the deposit was the same morning as the charge this isnt fair"),
        ("negative", "direct deposit not there and its payday. rent is due. THIS IS A PROBLEM"),
        ("neutral",  "website wont let me update beneficiary info keeps throwing an error"),
        ("negative", "teller told me wrong info about fees now im being charged stuff i never agreed to"),
        ("negative", "monthly fee showed up on my statment, been here 15 years and no warning? ridiculous"),
        ("neutral",  "whats the diff between available balance and current balance confusing"),
        ("negative", "debit card charged twice for same transaction and nobody can explain why"),
        ("negative", "account says negative but i have money deposited, something is very wrong"),
        ("neutral",  "trying to set up zelle but keeps saying my account isnt eligible"),
        ("negative", "branch told me one thing, phone rep told me different, which is it"),
        # Ambiguous (fee language overlaps with Credit Card)
        ("negative", "charged a fee i dont recognize, could be from my debit card or account not sure"),
        ("negative", "payment went through twice on my account, need a refund, contacted support twice no resolution"),
        # Vague
        ("negative", "something is wrong with my account and i cant get anyone to fix it"),
        ("negative", "i just want my money back its really that simple"),
    ],

    "Savings Account": [
        ("neutral",  "I notice my APY dropped again this month. Is there a higher-yield product I should consider?"),
        ("negative", "I transferred money out of savings and the funds did not appear in my checking for three days. This caused a bounced payment."),
        ("positive", "The high-yield savings rate you offered beat every competitor I checked. Very happy with the switch."),
        ("neutral",  "I want to open a savings account for my child. What documentation is required for a custodial account?"),
        ("negative", "My savings account was closed without my knowledge. I demand an explanation and immediate restoration."),
        # Noisy additions
        ("neutral",  "apy dropped again this month, should i switch products or what"),
        ("negative", "transferred money out 3 days ago still not in checking, caused a bounced payment thanks"),
        ("neutral",  "want to open savings for my kid, what do i need for that"),
        ("negative", "account closed without my knowledge!! i never asked for this, restore it now"),
        ("negative", "withdrawal limit hit me by surprise, didnt know there was one, caused problems"),
        ("neutral",  "is there a penalty for withdrawing early from this account"),
        ("negative", "interest hasnt posted in two months, where is it"),
        # Ambiguous (transfer language overlaps with Checking)
        ("negative", "moved money between savings and checking and now both balances look wrong"),
        ("negative", "transfer didnt go through and i dont know if my savings or checking is the problem"),
        # Vague
        ("negative", "my account doesnt look right and i cant figure out why"),
    ],

    "Auto Insurance": [
        ("negative", "It has been six weeks since I filed my claim and I still do not have a check. My car is sitting in the driveway undrivable."),
        ("negative", "Your adjuster lowballed my repair estimate by almost two thousand dollars. The body shop says your number is not realistic."),
        ("neutral",  "I added a new vehicle to my policy. Can you confirm the coverage details and new premium amount?"),
        ("negative", "My premium went up 30 percent at renewal and I have had zero claims. Please explain this increase."),
        ("positive", "When I called after my accident everyone was compassionate and professional. The whole claim process was painless."),
        ("negative", "The rental car coverage I thought I had was apparently not on my policy. Nobody told me that when I enrolled."),
        # Noisy additions
        ("negative", "filed claim 6 weeks ago still no check car is just sitting there undrivable"),
        ("negative", "adjuster offered way less than what body shop quoted, $2000 difference, not acceptable"),
        ("neutral",  "added new car to policy can you confirm coverage and new price"),
        ("negative", "premium jumped 30% at renewal zero claims zero accidents why"),
        ("negative", "thought i had rental coverage, didnt, nobody told me when i signed up"),
        ("negative", "claim number assigned 3 weeks ago still nobody has called me to inspect the car"),
        ("neutral",  "need to know if my policy covers rideshare driving"),
        ("negative", "got in an accident, other driver was at fault, your company is making this way harder than it needs to be"),
        ("negative", "repair shop says you wont authorize OEM parts, i want original parts not cheap replacements"),
        # Ambiguous (overlaps with Home Insurance on claim/policy language)
        ("negative", "my claim was denied and the reason doesnt make sense, called to appeal and got nowhere"),
        ("negative", "policy doesnt cover what i thought it did when i signed up, agent misled me"),
        # Vague
        ("negative", "this claim process is a nightmare i just want my car fixed"),
        ("negative", "nobody calls back nobody helps, worst insurance experience ive ever had"),
    ],

    "Home Insurance": [
        ("negative", "My roof claim was denied and the reason given does not match the actual damage report from the contractor."),
        ("neutral",  "I am renovating my kitchen and want to make sure my policy covers the increased home value during and after construction."),
        ("negative", "I have called four times about my water damage claim and every time I am told someone will call me back. No one ever does."),
        ("positive", "Filed a claim after the storm and an adjuster was at my house the next morning. Settlement was fair and fast."),
        ("negative", "The policy I received does not match what the agent described when I signed up. I feel misled."),
        # Noisy additions
        ("negative", "roof claim denied but contractors report clearly shows storm damage, makes no sense"),
        ("neutral",  "doing a kitchen remodel, need to know if coverage goes up during construction"),
        ("negative", "called 4 times about water damage claim, always told someone will call back, no one ever does"),
        ("negative", "policy i got is different from what agent described, i feel like i was lied to"),
        ("negative", "mold found after the leak, claim adjuster says its not covered, everything i read says it should be"),
        ("neutral",  "added a new addition to the house, do i need to update my policy"),
        ("negative", "settlement offer is way below what the contractor quoted, not even close"),
        ("negative", "premium renewal went up a lot, no claims ever filed, explanation given makes no sense"),
        # Ambiguous (overlaps with Auto Insurance on claim/adjuster language)
        ("negative", "adjuster came out weeks ago and i still havent heard anything about my settlement"),
        ("negative", "my claim keeps getting denied and i dont understand why, ive submitted everything they asked for"),
        # Vague
        ("negative", "i have been patient long enough, someone needs to actually resolve this"),
    ],

    "Investment Account": [
        ("negative", "A trade I placed was executed at a price far outside what was quoted. I want a full audit of this transaction."),
        ("neutral",  "I am trying to set up automatic monthly contributions to my IRA. The instructions on the app are unclear."),
        ("negative", "My quarterly statement has an error in the cost basis for several positions. This needs to be corrected before tax season."),
        ("positive", "The research tools on the platform are genuinely excellent. Makes it much easier to manage my own portfolio."),
        ("neutral",  "What is the process for transferring my brokerage account from another institution? I want to consolidate everything here."),
        ("negative", "I requested a distribution from my IRA two weeks ago and the funds have not arrived. I need this urgently."),
        # Noisy additions
        ("negative", "trade executed way off from quoted price, i want a full audit NOW"),
        ("neutral",  "trying to set up auto contributions to ira, app instructions are confusing"),
        ("negative", "cost basis is wrong on my statement, gonna be a tax nightmare, fix it"),
        ("neutral",  "how do i transfer my brokerage from another firm to here"),
        ("negative", "ira distribution requested 2 weeks ago funds still not here, urgent"),
        ("negative", "dividend payment didnt post this quarter, i should have received it last week"),
        ("neutral",  "cant figure out how to change my beneficiary on the investment account"),
        ("negative", "fees on my account are way higher than advertised when i opened it"),
        # Ambiguous (overlaps with Mobile Banking App on app/login issues)
        ("negative", "cant log into the platform to check my portfolio, app keeps crashing, miss trades because of this"),
        ("negative", "the app showed my account balance wrong and i made a trade based on that, lost money"),
        # Vague
        ("negative", "something is very wrong with my account and i need someone who actually knows what theyre doing"),
    ],

    "Mobile Banking App": [
        ("negative", "The app crashes every time I try to deposit a check. I have tried reinstalling three times on two different phones."),
        ("negative", "Face ID stopped working after your last update. I cannot log in and this is costing me time every single day."),
        ("neutral",  "I would really like the app to show transaction categories so I can track my spending without a third-party app."),
        ("negative", "I was logged out of the app mid-transfer and now I do not know if the payment went through or not. Very stressful."),
        ("positive", "The recent redesign made everything so much easier to find. Bill pay especially is much faster now."),
        ("negative", "Push notifications for transactions are delayed by hours. By the time I see a fraud alert it is too late to act."),
        ("neutral",  "Is there a way to export my transaction history to a CSV file from the app? I cannot find this option anywhere."),
        # Noisy additions
        ("negative", "app crashes every time i try to deposit a check, tried reinstalling, still broken"),
        ("negative", "face id doesnt work since last update, cant log in, this is every single day"),
        ("neutral",  "would love spending categories in the app so i dont need a separate budgeting app"),
        ("negative", "got logged out mid transfer, dont know if it went thru or not, stressful"),
        ("negative", "fraud alert notification came hours late, almost too late to do anything"),
        ("neutral",  "how do i export my transactions to csv from the app"),
        ("negative", "app updated and now nothing works, transfer button is gone, balance wont load"),
        ("negative", "biometric login broken again, third time this year, have to type password every time"),
        ("neutral",  "dark mode option disappeared after the update, how do i get it back"),
        ("negative", "tried to pay a bill and app froze, money left account but payee says they didnt get it"),
        # Ambiguous (overlaps with Checking/Savings on transfer language)
        ("negative", "transfer went missing in the app, cant tell if it hit my account or not"),
        ("negative", "balance shown in app doesnt match what the atm shows, which one is right"),
        # Vague
        ("negative", "app is completely broken right now, nothing works, very frustrated"),
        ("negative", "every update makes it worse, i liked the old version better"),
    ],

    "Customer Service": [
        ("negative", "I was on hold for 47 minutes and then disconnected. I never received a callback. This is completely unacceptable."),
        ("negative", "The representative I spoke with was rude and dismissive. I have never felt so disrespected as a customer."),
        ("neutral",  "I would like to submit a compliment for the agent named Sarah who helped me resolve a billing dispute last week."),
        ("negative", "I have now explained my issue to five different agents. Every time I call I have to start from scratch. Fix your notes system."),
        ("positive", "Called expecting the usual runaround and instead had my problem solved in under five minutes. Shocked in the best way."),
        ("negative", "I was promised a callback within 24 hours. Three days later and nothing. Your follow-through is terrible."),
        ("neutral",  "Is there a direct number or extension I can use to reach the same department without going through the main menu?"),
        ("negative", "The agent confirmed a waiver on a fee and then it was never applied. Now I am being told there is no record of that promise."),
        # Noisy additions
        ("negative", "47 min hold then disconnected, no callback, completely unacceptable"),
        ("negative", "rep was rude and dismissive, never felt so disrespected, i want to escalate"),
        ("neutral",  "want to leave a compliment for sarah she was fantastic and actually resolved my issue"),
        ("negative", "explained my problem to 5 different agents, have to start over every time, fix ur notes"),
        ("negative", "promised callback in 24hrs its been 3 days, terrible follow through"),
        ("neutral",  "is there a direct number so i dont have to go thru the whole phone menu every time"),
        ("negative", "agent said fee would be waived, its not, now nobody has a record of what was said"),
        ("negative", "chat bot is useless, wont transfer me to a person, just loops me in circles"),
        ("negative", "been dealing with this same issue for 3 weeks now, different rep every time, zero progress"),
        ("neutral",  "i want to file a formal complaint about the service i received, how do i do that"),
        ("negative", "supervisor i was transferred to was also unhelpful, felt like nobody actually wanted to help"),
        # Ambiguous (general frustration with no specific product context)
        ("negative", "i have called multiple times and nobody can help me, i dont know what else to do"),
        ("negative", "every person i talk to says something different, i just want one consistent answer"),
        ("negative", "this is the worst customer experience i have ever had, period"),
        # Vague
        ("negative", "nobody helps, nobody calls back, whats the point"),
        ("negative", "i give up, i will be taking my business elsewhere"),
    ],
}


def random_date(start_year=2023, end_year=2025):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def seed(n_rows=500):
    conn = sqlite3.connect(DB_PATH)
    # Drop and recreate so re-running gives a clean slate.
    conn.execute("DROP TABLE IF EXISTS complaints")
    conn.execute("DROP TABLE IF EXISTS complaints_unlabeled")
    conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('complaints','complaints_unlabeled')")
    conn.execute(SCHEMA)

    rows = []
    for _ in range(n_rows):
        category = random.choice(PRODUCT_CATEGORIES)
        sentiment_label, complaint_text = random.choice(COMPLAINTS[category])
        rows.append((
            random_date(),
            random.randint(1000, 9999),
            category,
            random.choice(CHANNELS),
            sentiment_label,
            random.choice([0, 1]) if sentiment_label == "neutral" else (1 if sentiment_label == "positive" else random.choice([0, 0, 1])),
            complaint_text,
        ))

    conn.executemany(
        "INSERT INTO complaints (submitted_at, customer_id, product_category, channel, sentiment_label, resolved, complaint_text) VALUES (?,?,?,?,?,?,?)",
        rows,
    )

    # Rebuild the unlabeled table from the new complaints.
    conn.execute("""
        CREATE TABLE complaints_unlabeled (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            submitted_at    TEXT NOT NULL,
            customer_id     INTEGER NOT NULL,
            channel         TEXT NOT NULL,
            complaint_text  TEXT NOT NULL
        )
    """)
    conn.execute("""
        INSERT INTO complaints_unlabeled (submitted_at, customer_id, channel, complaint_text)
        SELECT submitted_at, customer_id, channel, complaint_text FROM complaints
    """)

    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    unlabeled = conn.execute("SELECT COUNT(*) FROM complaints_unlabeled").fetchone()[0]
    conn.close()
    print(f"Seeded {total} complaint rows into {DB_PATH}")
    print(f"Rebuilt complaints_unlabeled with {unlabeled} rows")


if __name__ == "__main__":
    seed()
