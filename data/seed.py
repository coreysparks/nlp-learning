"""
Creates and populates data/complaints.db with synthetic customer complaint data.
Run from the project root: python data/seed.py

Design goals for sentiment signal quality:
  - Balanced classes: roughly equal negative / neutral / positive per category
  - Positive texts contain clear praise, satisfaction, and gratitude language
  - Neutral texts contain question/inquiry language with no strong emotion
  - Negative texts contain frustration, urgency, and problem language
  - Some realistic noise (typos, informal writing) preserved in negative/neutral only
  - Avoids leaking cross-sentiment language (e.g. a "positive" text that also complains)
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
        # --- NEGATIVE ---
        ("negative", "I was charged a late fee even though I paid on time. This is completely unacceptable and I want it reversed immediately."),
        ("negative", "My credit limit was lowered without any notice. I was embarrassed when my card was declined at the store."),
        ("negative", "There are unauthorized charges on my statement that I did not make. I need this investigated right away."),
        ("negative", "The rewards points I earned last quarter never posted to my account. I have been waiting over a month."),
        ("negative", "Your interest rate is way too high compared to competitors. I am considering closing this account."),
        ("negative", "late fee charged again!!! i payed on time why is this so hard"),
        ("negative", "card got declined at grocery store so embarrassing, limit was lowered and nobody told me"),
        ("negative", "theres charges on here i didnt make, fraud i think, please help"),
        ("negative", "points from last quarter still not showing up, been a month, fix this"),
        ("negative", "i got charged an annual fee i dont remember signing up for"),
        ("negative", "my card number was stolen, saw charges i didnt make, called and was on hold forever"),
        ("negative", "interest charges look wrong on my statement this month"),
        ("negative", "everything about this is wrong and i am very frustrated"),
        # --- NEUTRAL ---
        ("neutral",  "I requested a credit limit increase two weeks ago and still have not received a decision. How long does this process take?"),
        ("neutral",  "I am trying to understand how the cashback tiers work. The terms on the website are confusing."),
        ("neutral",  "been waiting 2 weeks on limit increase request, no response yet"),
        ("neutral",  "dont really understand the rewards tiers, can someone explain"),
        ("neutral",  "trying to dispute a charge but the form on the website wont load"),
        ("neutral",  "called about my account and they transferred me, still dont have an answer about my balance"),
        ("neutral",  "can you clarify how the grace period works for new purchases?"),
        ("neutral",  "what is the process for adding an authorized user to my credit card?"),
        ("neutral",  "i need to update my mailing address for my card statements"),
        # --- POSITIVE ---
        ("positive", "I wanted to let you know that your fraud team caught suspicious activity on my account before I even noticed. Great job."),
        ("positive", "fraud alert text saved me right away, caught it fast, really impressed with your security team"),
        ("positive", "The customer service rep resolved my billing dispute in under five minutes. Extremely professional and helpful."),
        ("positive", "I love the new cashback rewards program. The earnings have been fantastic and the redemption process is seamless."),
        ("positive", "Your app made it so easy to freeze my card instantly when I thought I lost it. Found the card later but felt very safe knowing I had that control."),
        ("positive", "The credit card onboarding experience was smooth and my card arrived earlier than expected. Very happy with everything so far."),
        ("positive", "I called to ask about my rewards balance and the agent was incredibly knowledgeable and friendly. Best customer experience I have had."),
        ("positive", "Really appreciate the zero-liability fraud protection. You reversed the unauthorized charge same day with no hassle at all."),
        ("positive", "The travel benefits on this card are outstanding. Used the airport lounge access for the first time and it was well worth it."),
    ],

    "Mortgage": [
        # --- NEGATIVE ---
        ("negative", "My escrow analysis is wrong and my monthly payment jumped by $400 with no explanation. Someone needs to call me back."),
        ("negative", "I have been trying to get a payoff statement for three weeks. Every time I call I am transferred and nobody can help me."),
        ("negative", "The property tax payment from my escrow was sent to the wrong county. Now I have a late penalty and your company should pay it."),
        ("negative", "I submitted a loan modification application 60 days ago and have heard nothing. Is there any update?"),
        ("negative", "escrow is messed up my payment went up $400 no warning at all someone call me"),
        ("negative", "been trying to get payoff statement for 3 weeks keep getting transferred"),
        ("negative", "property tax got sent to wrong county now i have a penalty, YOUR fault"),
        ("negative", "loan mod application from 2 months ago still no update is anyone working on this"),
        ("negative", "payment amount changed again, third time this year, escrow keeps fluctuating"),
        ("negative", "closing was delayed 3 times because of paperwork errors on your end, cost me money"),
        ("negative", "hazard insurance was cancelled because you guys didnt pay it from escrow, fix this NOW"),
        ("negative", "nobody can give me a straight answer, ive called 4 times"),
        # --- NEUTRAL ---
        ("neutral",  "I would like to know what options are available for refinancing my current 30-year mortgage."),
        ("neutral",  "I need to remove PMI from my loan. I believe I have reached 20 percent equity based on recent appraisals."),
        ("neutral",  "want to refi my 30yr, what options do i have"),
        ("neutral",  "how do i get pmi removed, i think i have enough equity now"),
        ("neutral",  "i want to set up biweekly payments instead of monthly, how do i do that"),
        ("neutral",  "what documents do i need to bring to my closing appointment?"),
        ("neutral",  "can you explain how my escrow account is calculated each year?"),
        ("neutral",  "i want to make an extra principal payment, how do i make sure it applies to principal only"),
        # --- POSITIVE ---
        ("positive", "Your mortgage advisor walked me through every step of the closing process. Made what could have been stressful very smooth."),
        ("positive", "The closing went perfectly. Your team was organized, responsive, and I felt informed at every step. Highly recommend."),
        ("positive", "Refinancing was much easier than I expected. The rate we locked in was excellent and the process took less than three weeks."),
        ("positive", "I really appreciate how the mortgage team kept me updated throughout the entire process. Communication was outstanding."),
        ("positive", "The online portal makes it easy to see my loan balance and payment history. Everything is transparent and well organized."),
        ("positive", "I was nervous about the home buying process but your loan officer made it so straightforward. Closed on time with no surprises."),
        ("positive", "Called to ask about escrow adjustment and the rep explained everything clearly and patiently. Left the call feeling completely informed."),
        ("positive", "The rate I received was better than any competitor I spoke with. Very happy I chose to go with your mortgage team."),
        ("positive", "Got pre-approved quickly and the whole experience from application to closing was professional and efficient. Thank you."),
    ],

    "Personal Loan": [
        # --- NEGATIVE ---
        ("negative", "I was approved for a loan and then told the funds would be deposited within two business days. It has been a week."),
        ("negative", "The interest rate I was given at closing does not match what I was quoted during the application. I need this corrected."),
        ("negative", "My autopay keeps failing even though my bank account has sufficient funds. I should not be charged late fees for your system error."),
        ("negative", "approved last week funds still not here, told 2 business days what is going on"),
        ("negative", "rate at closing is higher than what they quoted me on the phone, bait and switch??"),
        ("negative", "autopay failed again and i have money in my account!!! stop charging me late fees for YOUR error"),
        ("negative", "got a loan 3 months ago and still confused about what im actually paying for, fees dont make sense"),
        ("negative", "loan funded but amount was $500 less than approved amount, no explanation given"),
        ("negative", "the monthly payment doesnt match what was in my documents when i signed"),
        ("negative", "this is a mess, wrong amount, wrong rate, nothing is right"),
        # --- NEUTRAL ---
        ("neutral",  "I want to pay off my loan early. Can you confirm there is no prepayment penalty on my account?"),
        ("neutral",  "can i pay off early, is there a penalty, need to know"),
        ("neutral",  "how do i change my payment due date on my personal loan"),
        ("neutral",  "what is the difference between the APR and the interest rate on my loan?"),
        ("neutral",  "i need a payoff amount letter for my personal loan, how do i request one"),
        ("neutral",  "can i skip a payment if i am ahead on my loan, or does that incur a fee?"),
        ("neutral",  "how long does it typically take to get approved for a personal loan?"),
        # --- POSITIVE ---
        ("positive", "Getting approved was fast and easy. The rate was competitive and the funds arrived exactly when promised."),
        ("positive", "The personal loan process was incredibly smooth. Applied online, approved the same day, and funds arrived in two days. Excellent experience."),
        ("positive", "I shopped around and your rate was the best I found. The application was simple and the agent explained everything clearly."),
        ("positive", "Really appreciate how quickly the loan was processed. I needed the funds for a home repair and everything moved faster than expected."),
        ("positive", "The loan officer was transparent about all the terms and fees upfront. No surprises at all. I felt respected as a customer."),
        ("positive", "Autopay setup was simple and the reminders before each payment are a nice touch. Makes managing my loan completely stress-free."),
        ("positive", "I called with a question about my payoff amount and got a clear answer immediately. The rep was friendly and efficient."),
        ("positive", "The online loan management portal is well designed. I can see my balance, payment history, and payoff date all in one place."),
    ],

    "Checking Account": [
        # --- NEGATIVE ---
        ("negative", "I was hit with an overdraft fee for a charge that posted before a deposit that arrived the same morning. This is not fair."),
        ("negative", "My direct deposit did not post on payday. I have bills due and this caused a cascade of problems."),
        ("negative", "Your teller gave me incorrect information about account fees and I was charged things I never expected. I want a refund."),
        ("negative", "I have been a customer for 15 years and the new monthly maintenance fee with no warning is insulting."),
        ("negative", "overdraft fee is wrong, the deposit was the same morning as the charge, this isnt fair"),
        ("negative", "direct deposit not there and its payday, rent is due, THIS IS A PROBLEM"),
        ("negative", "teller told me wrong info about fees now im being charged stuff i never agreed to"),
        ("negative", "monthly fee showed up on my statement, been here 15 years and no warning, ridiculous"),
        ("negative", "debit card charged twice for same transaction and nobody can explain why"),
        ("negative", "account says negative but i have money deposited, something is very wrong"),
        ("negative", "branch told me one thing, phone rep told me different, which is it"),
        ("negative", "something is wrong with my account and i cant get anyone to fix it"),
        # --- NEUTRAL ---
        ("neutral",  "I need to update the beneficiary on my account. The website keeps erroring out when I try to save the changes."),
        ("neutral",  "Can you explain the difference between available balance and current balance? I keep getting confused."),
        ("neutral",  "website wont let me update beneficiary info, keeps throwing an error"),
        ("neutral",  "whats the difference between available balance and current balance"),
        ("neutral",  "trying to set up zelle but keeps saying my account isnt eligible"),
        ("neutral",  "how do i order new checks for my checking account"),
        ("neutral",  "what is the cutoff time for same-day deposits at your branches?"),
        ("neutral",  "can i link an external bank account to make transfers from here?"),
        # --- POSITIVE ---
        ("positive", "I lost my debit card and a new one was in my mailbox within two days. Really appreciate the quick turnaround."),
        ("positive", "The new debit card arrived fast and activating it through the app took about thirty seconds. Seamless experience."),
        ("positive", "I accidentally overdrafted and the fee was waived immediately when I called. The rep was understanding and resolved it right away."),
        ("positive", "Your branch staff are always friendly and helpful. The teller remembered my name and made the whole visit pleasant."),
        ("positive", "The mobile check deposit feature works perfectly every time. I never have to go to a branch for basic transactions anymore."),
        ("positive", "The account alerts keep me informed of every transaction in real time. I feel completely in control of my spending."),
        ("positive", "Opening a checking account online was quick and easy. The whole process took less than ten minutes and my card arrived in three days."),
        ("positive", "I really appreciate that you waived the monthly fee when I set up direct deposit. It shows you value loyal customers."),
        ("positive", "The customer service agent helped me set up automatic transfers to savings and was patient through every step. Great service."),
    ],

    "Savings Account": [
        # --- NEGATIVE ---
        ("negative", "I transferred money out of savings and the funds did not appear in my checking for three days. This caused a bounced payment."),
        ("negative", "My savings account was closed without my knowledge. I demand an explanation and immediate restoration."),
        ("negative", "transferred money out 3 days ago still not in checking, caused a bounced payment"),
        ("negative", "account closed without my knowledge!! i never asked for this, restore it now"),
        ("negative", "withdrawal limit hit me by surprise, didnt know there was one, caused problems"),
        ("negative", "interest hasnt posted in two months, where is it"),
        ("negative", "moved money between savings and checking and now both balances look wrong"),
        ("negative", "my account doesnt look right and i cant figure out why"),
        # --- NEUTRAL ---
        ("neutral",  "I notice my APY dropped again this month. Is there a higher-yield product I should consider?"),
        ("neutral",  "I want to open a savings account for my child. What documentation is required for a custodial account?"),
        ("neutral",  "apy dropped again this month, should i switch products or what"),
        ("neutral",  "want to open savings for my kid, what do i need for that"),
        ("neutral",  "is there a penalty for withdrawing early from this account"),
        ("neutral",  "how many withdrawals am i allowed per month from my savings account?"),
        ("neutral",  "can i set up automatic transfers from checking to savings on a schedule?"),
        ("neutral",  "what is the minimum balance required to avoid fees on this savings account?"),
        # --- POSITIVE ---
        ("positive", "The high-yield savings rate you offered beat every competitor I checked. Very happy with the switch."),
        ("positive", "I switched my savings here from another bank and the rate difference is significant. Really pleased with the decision."),
        ("positive", "The automatic savings feature is fantastic. I set it up once and it moves money every week without me thinking about it."),
        ("positive", "Opening the savings account online was effortless. The interface was clear and my account was active immediately."),
        ("positive", "The interest posted right on schedule and the rate is genuinely competitive. I have been recommending this account to friends."),
        ("positive", "The savings goal tracker in the app is a great feature. It keeps me motivated and makes it easy to see my progress."),
        ("positive", "I was surprised by how easy it was to link my external accounts. The whole setup took just a few minutes and it works perfectly."),
        ("positive", "Your savings rates are among the best I have found. Combined with the excellent app, it has been a great banking experience."),
    ],

    "Auto Insurance": [
        # --- NEGATIVE ---
        ("negative", "It has been six weeks since I filed my claim and I still do not have a check. My car is sitting in the driveway undrivable."),
        ("negative", "Your adjuster lowballed my repair estimate by almost two thousand dollars. The body shop says your number is not realistic."),
        ("negative", "My premium went up 30 percent at renewal and I have had zero claims. Please explain this increase."),
        ("negative", "The rental car coverage I thought I had was apparently not on my policy. Nobody told me that when I enrolled."),
        ("negative", "filed claim 6 weeks ago still no check car is just sitting there undrivable"),
        ("negative", "adjuster offered way less than what body shop quoted, $2000 difference, not acceptable"),
        ("negative", "premium jumped 30% at renewal zero claims zero accidents why"),
        ("negative", "thought i had rental coverage, didnt, nobody told me when i signed up"),
        ("negative", "claim number assigned 3 weeks ago still nobody has called me to inspect the car"),
        ("negative", "got in an accident, other driver was at fault, your company is making this way harder than it needs to be"),
        ("negative", "my claim was denied and the reason doesnt make sense, called to appeal and got nowhere"),
        ("negative", "this claim process is a nightmare i just want my car fixed"),
        # --- NEUTRAL ---
        ("neutral",  "I added a new vehicle to my policy. Can you confirm the coverage details and new premium amount?"),
        ("neutral",  "added new car to policy, can you confirm coverage and new price"),
        ("neutral",  "need to know if my policy covers rideshare driving"),
        ("neutral",  "what is the process for filing a claim after a minor fender bender?"),
        ("neutral",  "how do i add roadside assistance to my existing auto policy?"),
        ("neutral",  "can you explain the difference between comprehensive and collision coverage?"),
        ("neutral",  "what happens to my premium if i add a teen driver to my policy?"),
        # --- POSITIVE ---
        ("positive", "When I called after my accident everyone was compassionate and professional. The whole claim process was painless."),
        ("positive", "The claims process was faster than I expected. The adjuster was fair and my car was repaired within a week. Excellent service."),
        ("positive", "I was dreading filing a claim but your team made it completely stress-free. A rental was arranged immediately and the repair was handled smoothly."),
        ("positive", "The agent who helped me update my policy was incredibly helpful. She found a discount I did not even know I qualified for."),
        ("positive", "Renewal was easy and the premium actually went down. I appreciate the loyalty discount and the transparency about how it was calculated."),
        ("positive", "The online claims portal is well designed. I could upload photos, track progress, and communicate with the adjuster all in one place."),
        ("positive", "I got into an accident and your team contacted me before I even finished filing. Response time was outstanding and I felt taken care of."),
        ("positive", "The roadside assistance arrived in under thirty minutes when I had a flat tire. Really grateful for that fast response."),
        ("positive", "Switching my auto insurance to your company saved me over three hundred dollars a year with better coverage. Very satisfied customer."),
    ],

    "Home Insurance": [
        # --- NEGATIVE ---
        ("negative", "My roof claim was denied and the reason given does not match the actual damage report from the contractor."),
        ("negative", "I have called four times about my water damage claim and every time I am told someone will call me back. No one ever does."),
        ("negative", "The policy I received does not match what the agent described when I signed up. I feel misled."),
        ("negative", "roof claim denied but contractors report clearly shows storm damage, makes no sense"),
        ("negative", "called 4 times about water damage claim, always told someone will call back, no one ever does"),
        ("negative", "policy i got is different from what agent described, i feel like i was lied to"),
        ("negative", "mold found after the leak, claim adjuster says its not covered, everything i read says it should be"),
        ("negative", "settlement offer is way below what the contractor quoted, not even close"),
        ("negative", "premium renewal went up a lot, no claims ever filed, explanation given makes no sense"),
        ("negative", "adjuster came out weeks ago and i still havent heard anything about my settlement"),
        ("negative", "my claim keeps getting denied and i dont understand why, ive submitted everything they asked for"),
        # --- NEUTRAL ---
        ("neutral",  "I am renovating my kitchen and want to make sure my policy covers the increased home value during and after construction."),
        ("neutral",  "doing a kitchen remodel, need to know if coverage goes up during construction"),
        ("neutral",  "added a new addition to the house, do i need to update my policy"),
        ("neutral",  "what is the claims process if i have water damage from a burst pipe?"),
        ("neutral",  "how do i find out what my home replacement value is listed as on my policy?"),
        ("neutral",  "does my policy cover damage from a tree falling on the house during a storm?"),
        ("neutral",  "i want to increase my liability coverage, what are my options?"),
        # --- POSITIVE ---
        ("positive", "Filed a claim after the storm and an adjuster was at my house the next morning. Settlement was fair and fast."),
        ("positive", "The claim process after our basement flooded was handled incredibly well. The adjuster was thorough and the payout was fair."),
        ("positive", "I was worried the storm claim would be a fight but your team was professional and the settlement came in right where the contractor estimated."),
        ("positive", "The agent helped me find gaps in my coverage I was not aware of. I feel much better protected now and the premium barely changed."),
        ("positive", "Renewal was simple and the agent explained every line item. I always know exactly what I am paying for and why."),
        ("positive", "When a pipe burst in our house your emergency response line connected me to a mitigation crew within the hour. Incredible service."),
        ("positive", "The online policy management portal is excellent. I can view my coverage, make payments, and file claims all in one place."),
        ("positive", "The adjuster who came to inspect the roof damage was professional, thorough, and explained everything clearly. Great experience overall."),
        ("positive", "Switching home insurance to your company lowered my annual premium significantly while keeping the same level of coverage. Very happy."),
    ],

    "Investment Account": [
        # --- NEGATIVE ---
        ("negative", "A trade I placed was executed at a price far outside what was quoted. I want a full audit of this transaction."),
        ("negative", "My quarterly statement has an error in the cost basis for several positions. This needs to be corrected before tax season."),
        ("negative", "I requested a distribution from my IRA two weeks ago and the funds have not arrived. I need this urgently."),
        ("negative", "trade executed way off from quoted price, i want a full audit NOW"),
        ("negative", "cost basis is wrong on my statement, gonna be a tax nightmare, fix it"),
        ("negative", "ira distribution requested 2 weeks ago funds still not here, urgent"),
        ("negative", "dividend payment didnt post this quarter, i should have received it last week"),
        ("negative", "fees on my account are way higher than advertised when i opened it"),
        ("negative", "cant log into the platform to check my portfolio, app keeps crashing, missing trades because of this"),
        ("negative", "the app showed my account balance wrong and i made a trade based on that, lost money"),
        ("negative", "something is very wrong with my account and i need someone who actually knows what theyre doing"),
        # --- NEUTRAL ---
        ("neutral",  "I am trying to set up automatic monthly contributions to my IRA. The instructions on the app are unclear."),
        ("neutral",  "What is the process for transferring my brokerage account from another institution?"),
        ("neutral",  "trying to set up auto contributions to ira, app instructions are confusing"),
        ("neutral",  "how do i transfer my brokerage from another firm to here"),
        ("neutral",  "cant figure out how to change my beneficiary on the investment account"),
        ("neutral",  "what are the tax implications of converting a traditional IRA to a Roth?"),
        ("neutral",  "how do i read the cost basis information on my quarterly statement?"),
        ("neutral",  "what is the process for taking a required minimum distribution from my IRA?"),
        # --- POSITIVE ---
        ("positive", "The research tools on the platform are genuinely excellent. Makes it much easier to manage my own portfolio."),
        ("positive", "The investment platform is best in class. The research tools, charting, and trade execution are all excellent."),
        ("positive", "I moved my IRA here from a big brokerage and I am very impressed. The fee structure is transparent and the platform is easy to use."),
        ("positive", "The financial advisor I spoke with was knowledgeable and helped me rebalance my portfolio in a way that matched my actual goals."),
        ("positive", "Tax documents were available earlier than expected and the interface makes it easy to download everything I need for filing."),
        ("positive", "The automatic rebalancing feature is fantastic. My portfolio stays aligned to my targets without me having to monitor it constantly."),
        ("positive", "I had a question about my RMD and the specialist I spoke with was extremely knowledgeable and walked me through the entire calculation."),
        ("positive", "The platform is intuitive and the mobile app is excellent. I can manage my entire portfolio from my phone with confidence."),
        ("positive", "Opening the IRA online was simple and the educational resources helped me choose the right account type for my situation."),
    ],

    "Mobile Banking App": [
        # --- NEGATIVE ---
        ("negative", "The app crashes every time I try to deposit a check. I have tried reinstalling three times on two different phones."),
        ("negative", "Face ID stopped working after your last update. I cannot log in and this is costing me time every single day."),
        ("negative", "I was logged out of the app mid-transfer and now I do not know if the payment went through or not. Very stressful."),
        ("negative", "Push notifications for transactions are delayed by hours. By the time I see a fraud alert it is too late to act."),
        ("negative", "app crashes every time i try to deposit a check, tried reinstalling, still broken"),
        ("negative", "face id doesnt work since last update, cant log in, this is every single day"),
        ("negative", "got logged out mid transfer, dont know if it went through or not, stressful"),
        ("negative", "fraud alert notification came hours late, almost too late to do anything"),
        ("negative", "app updated and now nothing works, transfer button is gone, balance wont load"),
        ("negative", "biometric login broken again, third time this year, have to type password every time"),
        ("negative", "tried to pay a bill and app froze, money left account but payee says they didnt get it"),
        ("negative", "transfer went missing in the app, cant tell if it hit my account or not"),
        ("negative", "app is completely broken right now, nothing works, very frustrated"),
        # --- NEUTRAL ---
        ("neutral",  "I would really like the app to show transaction categories so I can track my spending without a third-party app."),
        ("neutral",  "Is there a way to export my transaction history to a CSV file from the app?"),
        ("neutral",  "would love spending categories in the app so i dont need a separate budgeting app"),
        ("neutral",  "how do i export my transactions to csv from the app"),
        ("neutral",  "dark mode option disappeared after the update, how do i get it back"),
        ("neutral",  "how do i set up two-factor authentication in the mobile app?"),
        ("neutral",  "is there a way to schedule recurring payments through the app?"),
        ("neutral",  "how do i dispute a transaction directly from the mobile app?"),
        # --- POSITIVE ---
        ("positive", "The recent redesign made everything so much easier to find. Bill pay especially is much faster now."),
        ("positive", "The app is genuinely one of the best banking apps I have used. Everything is fast, intuitive, and reliable."),
        ("positive", "Mobile check deposit works perfectly every time. I used to have to drive to a branch for this and now it takes thirty seconds."),
        ("positive", "The spending insights feature in the new app update is excellent. I can finally see where my money is going each month."),
        ("positive", "The app notifies me instantly every time there is a transaction. I feel completely on top of my finances in a way I never did before."),
        ("positive", "I reported a bug through the app and received a follow-up from your team within two days. Really impressive responsiveness."),
        ("positive", "The new update is a huge improvement. Navigation is so much cleaner and the new bill pay flow is much easier to use."),
        ("positive", "Setting up Face ID for login was effortless and it works every single time. The security features give me real peace of mind."),
        ("positive", "The app is stable, fast, and full-featured. I manage all my accounts through it and have never had a problem. Excellent work."),
    ],

    "Customer Service": [
        # --- NEGATIVE ---
        ("negative", "I was on hold for 47 minutes and then disconnected. I never received a callback. This is completely unacceptable."),
        ("negative", "The representative I spoke with was rude and dismissive. I have never felt so disrespected as a customer."),
        ("negative", "I have now explained my issue to five different agents. Every time I call I have to start from scratch. Fix your notes system."),
        ("negative", "I was promised a callback within 24 hours. Three days later and nothing. Your follow-through is terrible."),
        ("negative", "The agent confirmed a waiver on a fee and then it was never applied. Now I am being told there is no record of that promise."),
        ("negative", "47 min hold then disconnected, no callback, completely unacceptable"),
        ("negative", "rep was rude and dismissive, never felt so disrespected, i want to escalate"),
        ("negative", "explained my problem to 5 different agents, have to start over every time"),
        ("negative", "promised callback in 24hrs its been 3 days, terrible follow through"),
        ("negative", "agent said fee would be waived, its not, now nobody has a record of what was said"),
        ("negative", "chat bot is useless, wont transfer me to a person, just loops me in circles"),
        ("negative", "been dealing with this same issue for 3 weeks now, different rep every time, zero progress"),
        ("negative", "supervisor i was transferred to was also unhelpful, felt like nobody actually wanted to help"),
        ("negative", "i have called multiple times and nobody can help me, i dont know what else to do"),
        # --- NEUTRAL ---
        ("neutral",  "I would like to submit a compliment for the agent named Sarah who helped me resolve a billing dispute last week."),
        ("neutral",  "Is there a direct number or extension I can use to reach the same department without going through the main menu?"),
        ("neutral",  "want to leave a compliment for an agent, she was great and actually resolved my issue"),
        ("neutral",  "is there a direct number so i dont have to go through the whole phone menu every time"),
        ("neutral",  "i want to file a formal complaint about the service i received, how do i do that"),
        ("neutral",  "what are your customer service hours and how do i reach the escalations team?"),
        ("neutral",  "is there a way to continue a previous chat session with the same agent?"),
        ("neutral",  "how long does it typically take to get a response to an email inquiry?"),
        # --- POSITIVE ---
        ("positive", "Called expecting the usual runaround and instead had my problem solved in under five minutes. Shocked in the best way."),
        ("positive", "The agent I spoke with was patient, knowledgeable, and resolved my issue on the first call. Fantastic service."),
        ("positive", "I was transferred once and the second agent already had all my information. Felt like a seamless and respectful experience."),
        ("positive", "The wait time was short and the representative was professional and thorough. My issue was resolved completely. Very satisfied."),
        ("positive", "Your chat support resolved my issue in minutes without needing to escalate. The agent was friendly and clearly knew the product."),
        ("positive", "I want to recognize the agent who helped me today. She went above and beyond to make sure my issue was fully resolved."),
        ("positive", "Called with a complicated question and the agent stayed on the line until everything was sorted. That kind of dedication is rare."),
        ("positive", "The callback feature worked perfectly. I requested a callback, got one right on time, and my issue was handled efficiently."),
        ("positive", "Every interaction I have had with your customer service team has been positive. You have a great team and it shows."),
        ("positive", "I left the call feeling genuinely cared for as a customer. The rep took time to understand my situation before jumping to solutions."),
    ],
}


def random_date(start_year=2023, end_year=2025):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def seed(n_rows=500):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS complaints")
    conn.execute("DROP TABLE IF EXISTS complaints_unlabeled")
    try:
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('complaints','complaints_unlabeled')")
    except sqlite3.OperationalError:
        pass
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

    # Print class distribution for verification
    for label in ("negative", "neutral", "positive"):
        count = conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE sentiment_label = ?", (label,)
        ).fetchone()[0]
        print(f"  {label}: {count} ({count/total*100:.1f}%)")

    conn.close()
    print(f"\nSeeded {total} complaint rows into {DB_PATH}")
    print(f"Rebuilt complaints_unlabeled with {unlabeled} rows")


if __name__ == "__main__":
    seed()
