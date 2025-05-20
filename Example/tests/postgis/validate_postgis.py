import psycopg2
import json
from dateutil import parser as dateparser
import argparse
from shapely.wkb import loads as load_wkb
import binascii
import ast

def load_test_spec(path):
    with open(path) as f:
        return json.load(f)

def convert_row(row, colnames):
    result = {}
    for i, value in enumerate(row):
        key = colnames[i]
        result[key] = value  # We do not convert timestamps to epoch millis
    return result

def compare_row(expected, actual):
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        
        # Convert binary geometry (WKB) to WKT text if a string like "POINT (...)" is expected
        if key in ("location", "polygon") and isinstance(expected_value, str):
            try:
                if actual_value is not None and not isinstance(actual_value, str):
                    # Just in case, for previous cases
                    actual_geom = load_wkb(bytes(actual_value))
                else:
                    # Hex string case
                    actual_geom = load_wkb(binascii.unhexlify(actual_value))
                actual_value = actual_geom.wkt
            except Exception as e:
                print(f"⚠️ Error converting '{key}' from WKB to WKT: {e}")
                return False            

        # If it's a timestamp in ISO string format, parse it to datetime
        if key in ("timeinstant", "recvtime") and isinstance(expected_value, str):
            expected_value = dateparser.isoparse(expected_value)

        # Normalize float to int
        if isinstance(expected_value, int) and isinstance(actual_value, float):
            actual_value = int(actual_value)

        if isinstance(expected_value, dict):
            for op, val in expected_value.items():
                if op == "gte" and not (actual_value >= val):
                    return False
                elif op == "lte" and not (actual_value <= val):
                    return False
                elif op == "gt" and not (actual_value > val):
                    return False
                elif op == "lt" and not (actual_value < val):
                    return False
                elif op == "eq" and actual_value != val:
                    return False
        else:
            # We need to cover when expected_value is a json
            if isinstance(expected_value, str):
                try:
                    parsed_expected = json.loads(expected_value)
                    expected_value = parsed_expected
                except (ValueError, json.JSONDecodeError):
                    pass  # No json, keep going

            # In case of json, actual_value should already be a dictionary, just in case
            if isinstance(actual_value, str):
                try:
                    parsed_actual = json.loads(actual_value)
                    actual_value = parsed_actual
                except (ValueError, json.JSONDecodeError):
                    pass

            # Final comparation
            if actual_value != expected_value:
                #print(f"🔎 Mismatch in '{key}': expected {expected_value}, got {actual_value}")
                return False
    return True

def validate_data(test_spec):
    conn_info = test_spec["connection"]
    table = test_spec["table"]
    conditions = test_spec["conditions"]

    conn = psycopg2.connect(
        host=conn_info["host"],
        port=conn_info.get("port", 5432),
        dbname=conn_info["dbname"],
        user=conn_info["user"],
        password=conn_info["password"]
    )

    with conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table}")
            colnames = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

    matched = 0
    for expected_row in conditions:
        match_found = False
        for row in rows:
            actual_row = convert_row(row, colnames)
            if compare_row(expected_row, actual_row):
                match_found = True
                break
        if match_found:
            matched += 1
        else:
            print(f"❌ No matching row found for: {expected_row}")

    if matched == len(conditions):
        print(f"✅ All checks ({matched}) passed successfully.")
    else:
        print(f"⚠️ Only {matched}/{len(conditions)} rows matched the expectations.")

def main():
    parser = argparse.ArgumentParser(description="Validate PostGIS content against a JSON test specification.")
    parser.add_argument("--test", required=True, help="JSON file with the test specification.")
    args = parser.parse_args()

    test_spec = load_test_spec(args.test)
    validate_data(test_spec)

if __name__ == "__main__":
    main()
