from flask import Flask, request, jsonify
import requests
import os
from dotenv import dotenv_values

# ==========================================
# BACA .ENV SECARA LANGSUNG
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

ENV = dotenv_values(ENV_FILE)

BOT_TOKEN = ENV.get("BOT_TOKEN")
CHAT_ID = ENV.get("CHAT_ID")

# ==========================================
# DEBUG
# ==========================================

print("========================================")
print("     SERVER TRACKING MOTOR")
print("========================================")
print("FILE ENV :", ENV_FILE)
print("ENV ADA  :", os.path.exists(ENV_FILE))
print("BOT ADA  :", bool(BOT_TOKEN))
print("CHAT ADA :", bool(CHAT_ID))
print("========================================")

# ==========================================
# FLASK
# ==========================================

app = Flask(__name__)


# ==========================================
# TEST HALAMAN UTAMA
# ==========================================

@app.route("/")
def home():
    return "SERVER TRACKING MOTOR AKTIF"


# ==========================================
# TEST TELEGRAM
# ==========================================

@app.route("/test-telegram")
def test_telegram():

    if not BOT_TOKEN:
        return jsonify({
            "status": "error",
            "message": "BOT_TOKEN tidak terbaca"
        })

    if not CHAT_ID:
        return jsonify({
            "status": "error",
            "message": "CHAT_ID tidak terbaca"
        })

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": "TEST SERVER TRACKING MOTOR BERHASIL"
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=15
        )

        print("Telegram HTTP:", response.status_code)
        print("Telegram Response:", response.text)

        return jsonify({
            "status": "success" if response.ok else "error",
            "telegram_http": response.status_code
        })

    except Exception as e:

        print("ERROR TELEGRAM:", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        })


# ==========================================
# DATA DARI ESP32
# ==========================================

@app.route("/data", methods=["POST"])
def terima_data():

    try:

        data = request.get_json()

        print("")
        print("========================================")
        print("DATA DITERIMA DARI ESP32")
        print("========================================")
        print(data)

        if not data:

            return jsonify({
                "status": "error",
                "message": "Data kosong"
            }), 400

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is None or longitude is None:

            return jsonify({
                "status": "error",
                "message": "Latitude/longitude tidak ada"
            }), 400

        maps = f"https://www.google.com/maps?q={latitude},{longitude}"

        pesan = (
            "🚨 TRACKING MOTOR\n\n"
            "📍 Lokasi Motor\n"
            f"Latitude : {latitude}\n"
            f"Longitude: {longitude}\n\n"
            "🌐 Google Maps:\n"
            f"{maps}"
        )

        # ------------------------------------------
        # KIRIM TELEGRAM
        # ------------------------------------------

        if not BOT_TOKEN or not CHAT_ID:

            print("Telegram belum dikonfigurasi")

            telegram_ok = False

        else:

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            telegram_data = {
                "chat_id": CHAT_ID,
                "text": pesan
            }

            response = requests.post(
                url,
                data=telegram_data,
                timeout=15
            )

            print("Telegram HTTP:", response.status_code)
            print("Telegram Response:", response.text)

            telegram_ok = response.ok

        return jsonify({

            "status": "success",
            "telegram": telegram_ok,
            "latitude": latitude,
            "longitude": longitude,
            "maps": maps

        })

    except Exception as e:

        print("ERROR SERVER:", e)

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500


# ==========================================
# JALANKAN SERVER
# ==========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    print("")
    print("SERVER TRACKING MOTOR AKTIF")
    print("PORT:", port)

    app.run(
        host="0.0.0.0",
        port=port
    )