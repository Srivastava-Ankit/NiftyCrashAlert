import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# ----------------- CONFIG -----------------
INDEX = "^NSEI"  # Nifty 50 index
DROP_ALERT = 1  # percent
EMAIL_FROM = "ankitsrivastava.nitp@gmail.com"
EMAIL_PASS = "pans bjdq ltdi ntpa"  # Use Gmail App Password
EMAIL_TO = "ankitsrivastava.nitp@gmail.com"


# -----------------------------------------
def get_nifty_data():
    """Fetch last 1 month of Nifty 50 data"""
    data = yf.download(INDEX, period="1mo", interval="1d", progress=False)
    data = data.dropna()  # remove missing values
    return data

def check_market_crash(data):
    """Check if decline >= threshold"""
    # Ensure these are floats (not Series)
    current_price = data["Close"].iloc[-1]
    month_high = data["Close"].max()
    drop = (1 - current_price / month_high) * 100
    return drop, current_price, month_high

def send_email(subject, body):
    """Send email alert"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.send_message(msg)

    print("📧 Email sent successfully!")

def main():
    print(f"📅 Checking Nifty 50 crash alert — {datetime.now():%Y-%m-%d %H:%M:%S}")

    data = get_nifty_data()
    if data is None or data.empty:
        print("⚠️ No valid market data available.")
        return

    try:
        drop, current_price, month_high = check_market_crash(data)

        # Safely convert all to floats
        if not isinstance(current_price, float):
            current_price = float(current_price.iloc[0] if hasattr(current_price, "iloc") else current_price)

        if not isinstance(month_high, float):
            month_high = float(month_high.iloc[0] if hasattr(month_high, "iloc") else month_high)

        if not isinstance(drop, float):
            drop = float(drop.iloc[0] if hasattr(drop, "iloc") else drop)

    except Exception as e:
        print(f"⚠️ Error processing market data: {e}")
        return

    print(f"Current Price: ₹{current_price:.2f}")
    print(f"Month High: ₹{month_high:.2f}")
    print(f"Decline: {drop:.2f}%")

    # Email alert trigger
    if drop >= DROP_ALERT:
        subject = f"🚨 Market Crash Alert: Nifty 50 down {drop:.2f}% this month!"
        body = (
            f"Nifty 50 has declined by {drop:.2f}% in the past month.\n\n"
            f"Month High: ₹{month_high:.2f}\n"
            f"Current Price: ₹{current_price:.2f}\n"
            f"Date: {datetime.now():%d-%b-%Y %H:%M}\n\n"
            "Stay alert and review your portfolio!"
        )
        send_email(subject, body)
        print("📧 Alert email sent successfully!")
    else:
        print(f"✅ Market stable: decline only {drop:.2f}%")

if __name__ == "__main__":
    main()
