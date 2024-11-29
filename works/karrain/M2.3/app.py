from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import requests
import logging
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
user_info_cache = {}
user_ratings_cache = {}
CACHE_EXPIRY_SECONDS = 15
def is_cache_valid(cache_entry):
    return cache_entry and datetime.utcnow() < cache_entry["expiry_time"]
#缓存是否有效
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")
@app.route("/getUserRatings", methods=["GET"])
def get_user_ratings():
    handle = request.args.get("handle", "")
    if not handle:
        return jsonify({"success": False, "message": "No handle provided"}), 400
    # 查询缓存
    if handle in user_ratings_cache and is_cache_valid(user_ratings_cache[handle]):
        return jsonify(user_ratings_cache[handle]["data"])

    try:
        api_url = f"https://codeforces.com/api/user.rating?handle={handle}"
        response = requests.get(api_url, timeout=5)
        if response.status_code != 200:
            return jsonify({"success": False, "message": f"HTTP {response.status_code}"}), response.status_code
        data = response.json()
        if data["status"] == "OK":
            formatted_results = []
            for contest in data["result"]:
                formatted_results.append({
                    "handle": handle,
                    "contestId": contest["contestId"],
                    "contestName": contest["contestName"],
                    "rank": contest["rank"],
                    "ratingUpdatedAt": datetime.utcfromtimestamp(contest["ratingUpdateTimeSeconds"]).strftime('%Y-%m-%dT%H:%M:%S%z'),
                    "oldRating": contest["oldRating"],
                    "newRating": contest["newRating"]
                })#renew
            user_ratings_cache[handle] = {
                "data": formatted_results,
                "expiry_time": datetime.utcnow() + timedelta(seconds=CACHE_EXPIRY_SECONDS)
            }
            return jsonify(formatted_results)
        else:
            return jsonify({"success": False, "message": "No such handle"}), 404
    except requests.RequestException as e:
        return jsonify({"success": False, "message": str(e)}), 500
@app.route("/query_handles", methods=["POST"])
def query_handles():
    handles = request.form.get("handles", "")
    if not handles:
        return jsonify([])
    handles_list = handles.split(",")
    results = []
    for handle in handles_list:
        #查
        if handle in user_info_cache and is_cache_valid(user_info_cache[handle]):
            results.append(user_info_cache[handle]["data"])
            continue
        try:
            api_url = f"https://codeforces.com/api/user.info?handles={handle}"
            response = requests.get(api_url, timeout=5)
            if response.status_code != 200:
                results.append({
                    "success": False,
                    "type": 2,
                    "message": f"HTTP response with code {response.status_code}",
                    "details": {"status": response.status_code}
                })
                continue
            data = response.json()
            if data["status"] == "OK":
                user_data = data["result"][0]
                if "rating" in user_data:
                    result = {
                        "success": True,
                        "result": {
                            "handle": user_data["handle"],
                            "rating": user_data["rating"],
                            "rank": user_data["rank"]
                        }
                    }
                else:
                    result = {
                        "success": True,
                        "result": {"handle": user_data["handle"]}
                    }
                #renew
                user_info_cache[handle] = {
                    "data": result,
                    "expiry_time": datetime.utcnow() + timedelta(seconds=CACHE_EXPIRY_SECONDS)
                }
                results.append(result)
            else:
                results.append({
                    "success": False,
                    "type": 1,
                    "message": "no such handle"
                })
        except requests.RequestException as e:
            results.append({
                "success": False,
                "type": 3,
                "message": str(e)
            })
        except Exception:
            results.append({
                "success": False,
                "type": 4,
                "message": "Internal Server Error"
            })
    return jsonify(results)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=2333, debug=True)
