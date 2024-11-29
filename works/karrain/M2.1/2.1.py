import sys
import requests
import json


def fetch_user_info(handle):
  api_url = f"https://codeforces.com/api/user.info?handles={handle}"

  try:
    response = requests.get(api_url)
    response_data = response.json()

    if response_data["status"] == "OK":
      user_data = response_data["result"][0]
      if "rating" in user_data:
        output = {
          "handle": user_data["handle"],
          "rating": user_data["rating"],
          "rank": user_data["rank"]
        }
      else:
        output = {"handle": user_data["handle"]}

      print(json.dumps(output, ensure_ascii=False))
      return 0
    else:
      sys.stderr.write("no such handle\n")
      return 1
  except requests.RequestException as e:
    sys.stderr.write(f"API request failed: {e}\n")
    return 1
  except KeyError:
    sys.stderr.write("Unexpected response structure\n")
    return 1


if __name__ == "__main__":
  if len(sys.argv) != 2:
    sys.stderr.write("Usage: python script.py <handle>\n")
    sys.exit(1)

  handle = sys.argv[1]
  exit_code = fetch_user_info(handle)
  sys.exit(exit_code)
