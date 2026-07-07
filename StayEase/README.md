# StayEase — AI-Powered Hotel Booking & Management System

A full-stack hotel booking platform built with **Python, Django, HTML/CSS/JS**,
featuring a smart AI room-recommendation engine, an AI support chatbot, and
automatic AI review-sentiment analysis. Runs out-of-the-box on SQLite (zero
setup) with an easy switch to MySQL.

---

## ✨ Features

**Customer side**
- Registration / login / OTP email verification / forgot & reset password
- Browse, search & filter rooms (price, category, capacity, amenities)
- **AI Smart Room Recommendation** — scores every room against your budget,
  guest count, room type & purpose of stay
- **AI Personalized Suggestions** — "recommended for you" based on booking
  and wishlist history
- Room booking with date validation, guest count & special requests
- Simulated UPI / Card payment gateway
- PDF invoice generation & download
- Wishlist, booking history, cancellation
- Leave reviews — automatically classified as Positive / Neutral / Negative
  by an **AI sentiment analysis engine (TextBlob/NLP)**
- **AI Chatbot ("StayBot")** — floating widget answering FAQs about
  check-in/out, booking, cancellation, facilities & payments

**Admin side** (`/manage/`, staff login required)
- Dashboard with revenue chart, occupancy rate, booking-status breakdown,
  and AI sentiment summary (Chart.js)
- **🔔 Live notification bell** in the navbar — new bookings, payments,
  reviews & contact messages appear instantly with an unread badge, plus
  an email is sent to every staff user (prints to console in dev mode)
- Room management (add / edit / delete, images, amenities)
- Booking management (confirm / cancel / complete)
- User management (activate / deactivate / delete)
- Review management with AI sentiment tags
- Reports: export bookings to Excel, revenue to PDF
- Full Django Admin also available at `/django-admin/`

---

## 🧠 AI Features — how they work

| Feature | Technique | File |
|---|---|---|
| Smart Room Recommendation | Weighted multi-factor scoring (budget, capacity, category, purpose) | `rooms/ai.py` |
| Personalized Suggestions | Content-based filtering on booking/wishlist history | `rooms/ai.py` |
| AI Chatbot | Keyword/intent classification | `chatbot/ai.py` |
| Review Sentiment Analysis | NLP polarity scoring via TextBlob | `reviews/ai.py` |

These are lightweight, fully explainable, dependency-free approaches (no
external AI API keys or GPU needed) — ideal for a portfolio/resume project
that should run anywhere instantly, while still demonstrating real applied-AI
engineering (feature scoring, NLP sentiment classification, intent
recognition).

---

## 🔑 Booking approval workflow

Bookings do **not** auto-confirm after payment. The flow is:

```
Customer books room       → status: Pending
Customer completes payment → status stays Pending ("Awaiting Confirmation")
                              admin gets a bell notification + email
Admin reviews & clicks "Confirm" in /manage/bookings/
                              → status: Confirmed
                              → customer gets an email confirming their stay
```

This gives the hotel (admin) a manual checkpoint before a room is treated as
actually booked — useful for verifying real-world availability, or just for
demoing the approval flow. Admin can also **Cancel** or mark a stay
**Completed** from the same screen, and the customer is emailed either way.

---

## 📱 Phone (SMS) OTP verification

Signup now requires a phone number, and the account **cannot log in** until
that phone is verified with a 6-digit OTP.

```
Signup (with phone number) → OTP sent via SMS
                              → account created but LOGIN IS BLOCKED
Enter OTP on the verify page → phone marked verified → can now log in
```

**By default (no setup needed):** if Twilio isn't configured, the OTP is
printed to the server console instead of actually texted — so this works
immediately for local demos, no paid account required.

**To send real SMS via Twilio:**
1. Create a free account at [twilio.com](https://www.twilio.com)
2. From the Twilio Console, grab your **Account SID**, **Auth Token**, and a
   **Twilio phone number**
3. Set them as environment variables before running the server:
   ```bash
   export TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   export TWILIO_AUTH_TOKEN=your_auth_token
   export TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
   ```
4. Run `python manage.py runserver` as usual — OTPs will now be real SMS.

> ⚠️ **Twilio trial account limitation:** a free/trial Twilio account can
> only SMS phone numbers you've manually verified in the Twilio console
> (Console → Phone Numbers → Verified Caller IDs). To message *any* signup
> automatically, you need to add billing to the Twilio account (pay-as-you-go,
> a few paisa per SMS). This is a Twilio platform rule, not a bug in the code.

Demo accounts created by `seed_data` (`admin`, `demo_guest`) are
pre-verified, so you don't need to go through this flow to log in with them.

---

## 🚀 Quick Start

```bash
# 1. Create & activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Seed demo data (rooms, categories, amenities, admin + demo user, AI-analyzed reviews)
python manage.py seed_data

# 5. Run the server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

**Demo logins (created by `seed_data`):**
| Role | Username | Password |
|---|---|---|
| Admin (staff) | `admin` | `admin123` |
| Customer | `demo_guest` | `guest12345` |

Admin dashboard: **http://127.0.0.1:8000/manage/**
Django Admin: **http://127.0.0.1:8000/django-admin/**

> ⚠️ Change these credentials before deploying anywhere public.

---

## 🗄️ Switching to MySQL

By default the project uses SQLite so it works with zero configuration. To
use MySQL (as in the original spec):

```bash
pip install mysqlclient
export USE_MYSQL=1
export DB_NAME=stayease_db
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=3306

python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

(On Windows, use `set` instead of `export`.)

---

## 📁 Project Structure

```
StayEase/
├── stayease_project/   # settings, root urls
├── core/                # home, about, faq, contact
├── accounts/             # auth, profile, dashboard
├── rooms/                # rooms, categories, search/filter, AI recommender
├── bookings/              # booking flow, payment, PDF invoice
├── reviews/               # reviews + AI sentiment analysis
├── chatbot/                # AI chatbot + API endpoint
├── adminpanel/              # custom staff dashboard, management, reports
├── templates/                # all HTML templates
├── static/                    # css/js
└── manage.py
```

---

## 🛠️ Tech Stack

- **Backend:** Python, Django 5/6
- **Database:** SQLite (default) / MySQL (optional)
- **Frontend:** HTML5, CSS3 (custom design system), vanilla JavaScript, Chart.js
- **AI/NLP:** TextBlob (sentiment analysis), custom rule-based recommender & chatbot
- **PDF/Excel:** ReportLab, openpyxl
- **Auth:** Django's built-in auth system + custom OTP email verification

---

## 📌 Notes for your resume/demo

- This is a self-contained student/portfolio project — the payment gateway
  is **simulated** (no real transactions), and OTP emails print to the
  console in dev mode (`EMAIL_BACKEND = console`).
- To connect a real email provider, update `EMAIL_BACKEND` /
  `EMAIL_HOST*` settings in `stayease_project/settings.py`.
- To connect a real payment gateway (Razorpay/Stripe/PayU), replace the
  simulated logic in `bookings/views.py::payment_view`.
