"""AI Agent Pre-flight Verification & Deploy Trigger Script

Usage:
  python scripts/deploy_check.py                  # Run checks only
  python scripts/deploy_check.py --trigger-render # Run checks and trigger Render deploy hook
"""
import argparse
import os
import sqlite3
import sys
import urllib.request
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

# Ensure root directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def check_env():
    print("[1/4] Checking Environment Variables...")
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        print("❌ FAIL: CWA_API_KEY is not set in environment or .env!")
        return False
    print("✅ PASS: CWA_API_KEY is configured.")
    return True


def test_pipeline():
    print("[2/4] Testing Data Pipeline (fetch -> parse -> database)...")
    try:
        import fetch_weather
        import parse_weather
        import database

        fetch_weather.main()
        parse_weather.parse_weather()
        conn = database.init_db()
        database.populate_db(conn)
        conn.close()

        # Check DB records
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            count = cursor.execute("SELECT COUNT(*) FROM TemperatureForecasts").fetchone()[0]
            if count != 42:
                print(f"❌ FAIL: Expected 42 records in data.db, got {count}!")
                return False
        print(f"✅ PASS: Pipeline executed successfully, data.db contains {count} records.")
        return True
    except Exception as e:
        print(f"❌ FAIL: Pipeline execution threw error: {e}")
        return False


def check_git_secrets():
    print("[3/4] Checking Git Secrets Protection...")
    if os.path.exists(".git"):
        import subprocess

        res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        tracked_files = res.stdout.splitlines()
        for line in tracked_files:
            if ".env" in line and not ".env.example" in line:
                print("❌ FAIL: .env file is being tracked by Git!")
                return False
    print("✅ PASS: No secrets found in tracked Git files.")
    return True


def trigger_render():
    print("[4/4] Triggering Render Deployment Hook...")
    hook_url = os.getenv("RENDER_DEPLOY_HOOK_URL")
    if not hook_url:
        print("⚠️ SKIP: RENDER_DEPLOY_HOOK_URL is not set in .env.")
        return True

    try:
        req = urllib.request.Request(hook_url, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"✅ PASS: Deploy hook triggered successfully! (Status: {resp.status})")
            return True
    except Exception as e:
        print(f"❌ FAIL: Failed to trigger Render deploy hook: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="AI Agent Pre-flight & Deploy Script")
    parser.add_argument("--trigger-render", action="store_true", help="Trigger Render Deploy Hook if configured")
    args = parser.parse_args()

    print("=" * 60)
    print("🤖 AI Agent Pre-flight Inspection")
    print("=" * 60)

    ok1 = check_env()
    ok2 = test_pipeline()
    ok3 = check_git_secrets()

    if not (ok1 and ok2 and ok3):
        print("\n❌ PRE-FLIGHT CHECK FAILED. Deployment aborted.")
        sys.exit(1)

    print("\n🎉 ALL PRE-FLIGHT CHECKS PASSED!")

    if args.trigger_render:
        ok4 = trigger_render()
        if not ok4:
            sys.exit(1)


if __name__ == "__main__":
    main()
