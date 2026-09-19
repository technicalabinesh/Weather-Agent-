"""
Pune Weather Update - Automatic Email Sender
=============================================

What this program does:
1. Fetches the current weather for Pune, Maharashtra from the free
   Open-Meteo API (no API key needed).
2. Builds a nicely formatted email with the weather details.
3. Sends that email to you using Gmail's SMTP server.

How to use:
1. Install the only external library needed:
       pip install requests
2. Fill in your Gmail address and Gmail "App Password" in the
   CONFIGURATION section below.
3. Run the program:
       python pune_weather_email.py

No .env files, no environment variables, no JSON config files,
no Zapier, no external automation tools. Everything lives right here
in this one file.
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import requests

# Reconfigure stdout/stderr encoding for UTF-8 (fixes Windows console emoji printing)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# =========================================================
# CONFIGURATION (edit these values yourself or use env vars)
# =========================================================

# --- Weather API settings (Open-Meteo, free, no API key required) ---
WEATHER_API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=18.5204&longitude=73.8567"
    "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
    "&timezone=Asia%2FKolkata"
)

# --- Gmail SMTP settings ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Replace these with your own details or pass via environment variables (e.g. in GitHub Secrets)
SENDER_EMAIL = os.environ.get("SENDER_EMAIL") or "mylyrical226@gmail.com"
SENDER_APP_PASSWORD = (os.environ.get("SENDER_APP_PASSWORD") or "ykhn ezhq nrqd hknm").replace(" ", "")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL") or "m.abinesh555@gmail.com"


# WMO Weather interpretation codes (WW)
WEATHER_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌧️"),
    53: ("Moderate Drizzle", "🌧️"),
    55: ("Dense Drizzle", "🌧️"),
    61: ("Slight Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    71: ("Slight Snow", "❄️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "❄️"),
    80: ("Slight Rain Showers", "🌦️"),
    81: ("Moderate Rain Showers", "🌦️"),
    82: ("Violent Rain Showers", "⛈️"),
    85: ("Slight Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "🌨️"),
    95: ("Thunderstorm", "🌩️"),
    96: ("Thunderstorm with Light Hail", "⛈️"),
    99: ("Thunderstorm with Heavy Hail", "⛈️"),
}


def get_weather_info(code):
    """Returns (description, emoji) for a given WMO weather code."""
    return WEATHER_CODES.get(code, ("Unknown", "🌤️"))


# =========================================================
# STEP 1: Get the weather data
# =========================================================
def get_weather():
    """
    Contacts the Open-Meteo API and returns the current weather
    for Pune/Chennai as a dictionary with:
        temperature, humidity, weather_code, wind_speed, timestamp
    """
    try:
        response = requests.get(WEATHER_API_URL, timeout=10)
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to the internet. Please check your connection."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("The weather request timed out. Please try again.")
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Something went wrong contacting the weather service: {error}")

    if response.status_code != 200:
        raise RuntimeError(
            f"Weather service returned an error (status code {response.status_code})."
        )

    try:
        data = response.json()
        current = data["current"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        weather_code = current["weather_code"]
        wind_speed = current["wind_speed_10m"]
        timestamp = current["time"]
    except (KeyError, ValueError, TypeError):
        raise RuntimeError("The weather service sent back an unexpected response format.")

    return {
        "temperature": temperature,
        "humidity": humidity,
        "weather_code": weather_code,
        "wind_speed": wind_speed,
        "timestamp": timestamp,
    }


# =========================================================
# STEP 2: Create the email (FlowCRM-inspired Designer HTML)
# =========================================================
def create_email(weather_data):
    """
    Builds the email subject, plain text body, and high-end responsive HTML body
    inspired by modern SaaS email designs (purple theme, cards grid, dark hero highlights).
    """
    subject = "🌤️ Chennai Weather Update"

    # Format timestamp nicely
    try:
        parsed_time = datetime.fromisoformat(weather_data["timestamp"])
        readable_time = parsed_time.strftime("%b %d, %Y • %I:%M %p")
    except (ValueError, TypeError):
        readable_time = weather_data["timestamp"]

    code = weather_data.get("weather_code", 0)
    condition_text, condition_emoji = get_weather_info(code)
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    wind = weather_data["wind_speed"]

    # Plain text fallback
    plain_body = f"""Hello Abinesh M,

Here is your live weather update for Chennai, Tamil Nadu:

📍 Location: Chennai, Tamil Nadu, India
🌡️ Temperature: {temp} °C
💧 Humidity: {humidity} %
🌤️ Condition: {condition_text} ({condition_emoji})
💨 Wind Speed: {wind} km/h
🕒 Updated: {readable_time}

This weather report was generated automatically by Python.
"""

    # High-End HTML Email (FlowCRM purple theme style)
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f3f0ff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f3f0ff; padding: 40px 10px;">
    <tr>
      <td align="center">
        <!-- Main Email Container Card -->
        <table role="presentation" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 32px; overflow: hidden; box-shadow: 0 20px 40px rgba(124, 58, 237, 0.08); border: 1px solid #e9d5ff;" cellspacing="0" cellpadding="0">
          
          <!-- Top Brand Header -->
          <tr>
            <td align="center" style="padding: 36px 30px 20px 30px; background-color: #ffffff;">
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="font-size: 24px; padding-right: 8px;">🌤️</td>
                  <td style="font-size: 22px; font-weight: 800; color: #1e1b4b; letter-spacing: -0.5px;">Weather<span style="color: #7c3aed;">Pulse</span></td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Hero Purple Backdrop Section -->
          <tr>
            <td align="center" style="padding: 0 24px 30px 24px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, #ede9fe 0%, #f5f3ff 100%); border-radius: 28px; padding: 36px 24px; text-align: center; border: 1px solid #ddd6fe;">
                <tr>
                  <td align="center">
                    <h1 style="margin: 0; font-size: 32px; font-weight: 800; color: #1e1b4b; letter-spacing: -0.8px; line-height: 1.2;">
                      Welcome to<br/>
                      <span style="color: #7c3aed; font-size: 36px;">Chennai Weather</span>
                    </h1>
                    <p style="margin: 10px 0 24px 0; font-size: 13px; color: #6b21a8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                      📍 Chennai, Tamil Nadu • {readable_time}
                    </p>

                    <!-- Main Temperature Box (Mockup style card) -->
                    <table role="presentation" width="100%" style="max-width: 440px; background-color: #ffffff; border-radius: 20px; box-shadow: 0 12px 30px rgba(124, 58, 237, 0.12); border: 1px solid #e9d5ff;" cellspacing="0" cellpadding="0">
                      <tr>
                        <td style="padding: 26px; text-align: center;">
                          <div style="font-size: 54px; line-height: 1; margin-bottom: 8px;">{condition_emoji}</div>
                          <div style="font-size: 50px; font-weight: 800; color: #1e1b4b; line-height: 1;">
                            {temp}<span style="font-size: 26px; font-weight: 600; color: #7c3aed; vertical-align: super;">°C</span>
                          </div>
                          <div style="margin-top: 10px; font-size: 15px; font-weight: 700; color: #6b21a8;">
                            {condition_text}
                          </div>
                        </td>
                      </tr>
                    </table>

                    <!-- CTA Pill Button -->
                    <table role="presentation" cellspacing="0" cellpadding="0" style="margin-top: 24px;">
                      <tr>
                        <td align="center" style="background-color: #1e1b4b; border-radius: 12px; padding: 14px 32px;">
                          <a href="https://open-meteo.com" style="color: #ffffff; font-size: 14px; font-weight: 700; text-decoration: none; display: inline-block;">
                            Get Started &rarr;
                          </a>
                        </td>
                      </tr>
                    </table>

                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Section Divider Header -->
          <tr>
            <td align="center" style="padding: 10px 30px 24px 30px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td width="20%" style="border-bottom: 1px solid #e2e8f0;"></td>
                  <td align="center" style="font-size: 16px; font-weight: 700; color: #4c1d95; padding: 0 12px;">
                    Let's get your weather started
                  </td>
                  <td width="20%" style="border-bottom: 1px solid #e2e8f0;"></td>
                </tr>
              </table>
              <p style="margin: 8px 0 0 0; font-size: 13px; color: #64748b;">
                Here are a few metrics tracked to set you up for success today.
              </p>
            </td>
          </tr>

          <!-- 4 Feature Cards Grid (2x2 Layout) -->
          <tr>
            <td style="padding: 0 24px 20px 24px;">
              
              <!-- Row 1 Cards -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 16px;">
                <tr>
                  <!-- Card 1: Temperature -->
                  <td width="48%" style="background-color: #ffffff; border-radius: 20px; padding: 22px 18px; border: 1px solid #f1f5f9; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); vertical-align: top;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                      <tr>
                        <td align="center">
                          <div style="background-color: #f3e8ff; width: 44px; height: 44px; border-radius: 50%; display: table; text-align: center;">
                            <span style="display: table-cell; vertical-align: middle; font-size: 22px;">🌡️</span>
                          </div>
                          <div style="font-size: 14px; font-weight: 700; color: #6b21a8; margin-top: 14px;">1. Air Temperature</div>
                          <p style="font-size: 12px; color: #64748b; margin: 6px 0 14px 0; line-height: 1.4;">Current temperature reading in Celsius for Chennai.</p>
                          <div style="background-color: #1e1b4b; color: #ffffff; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 700; display: inline-block;">
                            {temp} °C
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                  
                  <td width="4%"></td>

                  <!-- Card 2: Humidity -->
                  <td width="48%" style="background-color: #ffffff; border-radius: 20px; padding: 22px 18px; border: 1px solid #f1f5f9; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); vertical-align: top;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                      <tr>
                        <td align="center">
                          <div style="background-color: #f3e8ff; width: 44px; height: 44px; border-radius: 50%; display: table; text-align: center;">
                            <span style="display: table-cell; vertical-align: middle; font-size: 22px;">💧</span>
                          </div>
                          <div style="font-size: 14px; font-weight: 700; color: #6b21a8; margin-top: 14px;">2. Humidity Level</div>
                          <p style="font-size: 12px; color: #64748b; margin: 6px 0 14px 0; line-height: 1.4;">Relative moisture content in the atmosphere.</p>
                          <div style="background-color: #1e1b4b; color: #ffffff; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 700; display: inline-block;">
                            {humidity} %
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Row 2 Cards -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 24px;">
                <tr>
                  <!-- Card 3: Wind Speed -->
                  <td width="48%" style="background-color: #ffffff; border-radius: 20px; padding: 22px 18px; border: 1px solid #f1f5f9; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); vertical-align: top;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                      <tr>
                        <td align="center">
                          <div style="background-color: #f3e8ff; width: 44px; height: 44px; border-radius: 50%; display: table; text-align: center;">
                            <span style="display: table-cell; vertical-align: middle; font-size: 22px;">💨</span>
                          </div>
                          <div style="font-size: 14px; font-weight: 700; color: #6b21a8; margin-top: 14px;">3. Wind Speed</div>
                          <p style="font-size: 12px; color: #64748b; margin: 6px 0 14px 0; line-height: 1.4;">Surface wind speed measured at 10 meters altitude.</p>
                          <div style="background-color: #1e1b4b; color: #ffffff; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 700; display: inline-block;">
                            {wind} km/h
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>

                  <td width="4%"></td>

                  <!-- Card 4: Live Condition -->
                  <td width="48%" style="background-color: #ffffff; border-radius: 20px; padding: 22px 18px; border: 1px solid #f1f5f9; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); vertical-align: top;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                      <tr>
                        <td align="center">
                          <div style="background-color: #f3e8ff; width: 44px; height: 44px; border-radius: 50%; display: table; text-align: center;">
                            <span style="display: table-cell; vertical-align: middle; font-size: 22px;">{condition_emoji}</span>
                          </div>
                          <div style="font-size: 14px; font-weight: 700; color: #6b21a8; margin-top: 14px;">4. Sky Condition</div>
                          <p style="font-size: 12px; color: #64748b; margin: 6px 0 14px 0; line-height: 1.4;">Real-time WMO weather condition code interpretation.</p>
                          <div style="background-color: #1e1b4b; color: #ffffff; border-radius: 8px; padding: 8px 16px; font-size: 12px; font-weight: 700; display: inline-block;">
                            {condition_text}
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Dark Navy Highlight Banner -->
          <tr>
            <td style="padding: 0 24px 24px 24px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #1e1b4b; border-radius: 22px; padding: 28px 24px; color: #ffffff;">
                <tr>
                  <td>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                      <tr>
                        <td width="54" style="vertical-align: top;">
                          <div style="background-color: #312e81; width: 44px; height: 44px; border-radius: 50%; text-align: center; display: table;">
                            <span style="display: table-cell; vertical-align: middle; font-size: 22px;">🚀</span>
                          </div>
                        </td>
                        <td>
                          <h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #ffffff;">Built to help you stay smarter</h3>
                          <p style="margin: 6px 0 14px 0; font-size: 12px; color: #c7d2fe; line-height: 1.4;">
                            Automated weather intelligence pipeline delivering real-time forecasts directly to your inbox.
                          </p>
                          <div style="background-color: #c084fc; color: #1e1b4b; font-size: 11px; font-weight: 700; padding: 6px 14px; border-radius: 6px; display: inline-block;">
                            Live Forecast Active &rarr;
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Support Bar -->
          <tr>
            <td style="padding: 0 24px 30px 24px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f5f3ff; border-radius: 14px; padding: 14px 20px;">
                <tr>
                  <td width="28" style="font-size: 18px;">🎧</td>
                  <td style="font-size: 13px; font-weight: 600; color: #5b21b6;">Need help getting started?</td>
                  <td align="right" style="font-size: 12px; font-weight: 700; color: #7c3aed;">
                    Visit Help Center &rarr;
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="background-color: #faf5ff; padding: 28px 24px; border-top: 1px solid #f3e8ff; color: #7e22ce; font-size: 12px;">
              <div style="font-size: 16px; font-weight: 800; color: #1e1b4b; margin-bottom: 8px;">🌤️ WeatherPulse</div>
              <p style="margin: 0 0 8px 0; color: #6b21a8;">© 2026 WeatherPulse Inc. All rights reserved. Chennai, Tamil Nadu, India</p>
              <p style="margin: 0; color: #a855f7; font-size: 11px;">You are receiving this email because you signed up for live weather reports.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL

    # Attach both plain text (for old email clients) and HTML text
    part1 = MIMEText(plain_body, "plain", "utf-8")
    part2 = MIMEText(html_body, "html", "utf-8")
    message.attach(part1)
    message.attach(part2)

    return message


# =========================================================
# STEP 3: Send the email
# =========================================================
def send_email(message):
    """
    Connects to Gmail's SMTP server, logs in, sends the email,
    and closes the connection. Never prints the app password.
    """
    server = None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())

    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "Gmail login failed. Please check that SENDER_EMAIL and "
            "SENDER_APP_PASSWORD are correct. (Remember: use a Gmail "
            "App Password, not your normal password.)"
        )
    except smtplib.SMTPConnectError:
        raise RuntimeError("Could not connect to the Gmail SMTP server. Check your internet connection.")
    except smtplib.SMTPException as error:
        raise RuntimeError(f"Something went wrong while sending the email: {error}")
    except OSError:
        raise RuntimeError("Network error while trying to send the email. Please check your connection.")
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass


# =========================================================
# STEP 4: Main program
# =========================================================
def main():
    try:
        # 1. Get the weather
        weather_data = get_weather()
        code = weather_data.get("weather_code", 0)
        cond_text, cond_emoji = get_weather_info(code)
        print("Weather data fetched successfully.")
        print("📍 Chennai, Tamil Nadu")
        print(f"🌡️ Temperature: {weather_data['temperature']} °C")
        print(f"💧 Humidity: {weather_data['humidity']} %")
        print(f"🌤️ Condition: {cond_text} {cond_emoji}")
        print(f"💨 Wind Speed: {weather_data['wind_speed']} km/h")

        # 2. Create the email
        message = create_email(weather_data)

        # 3. Send the email
        send_email(message)
        print("📧 Email sent successfully!")

    except RuntimeError as error:
        # Friendly, beginner-readable error messages
        print(f"❌ Error: {error}")
    except Exception as error:
        # Catch-all for anything unexpected, without ever showing the password
        print(f"❌ An unexpected error occurred: {error}")


if __name__ == "__main__":
    main()

