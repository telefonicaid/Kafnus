import os
import subprocess
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = CURRENT_DIR

def run_tests():
    for root, _, files in os.walk(TESTS_DIR):
        # Group by notification and expected
        notifications = [f for f in files if f.endswith("_notification.json")]
        expecteds = [f for f in files if f.endswith("_expected.json")]

        if not notifications or not expecteds:
            continue  # Nothing to do

        print(f"\n🧪 Running tests in: {root}")

        for notif_file in notifications:
            notif_path = os.path.join(root, notif_file)
            print(f"📤 Sending notification: {notif_path}")
            subprocess.run(["python3", "producer.py", notif_path], check=True)

        # Wait between send and check
        time.sleep(1)

        for expected_file in expecteds:
            expected_path = os.path.join(root, expected_file)
            print(f"🔍 Validating: {expected_path}")
            subprocess.run(["python3", "validate_postgis.py", "--test", expected_path], check=True)

if __name__ == "__main__":
    run_tests()
