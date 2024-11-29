from flask import Flask, request, jsonify, render_template
from datetime import datetime
import requests

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")
@app.route("/getUserRatings", methods=["GET"])
def get_user_ratings():
    handle = request.args.get("handle", "")
    if not handle:
        return jsonify({"success": False, "message": "No handle provided"}), 400
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
                    "ratingUpdatedAt": contest["ratingUpdateTimeSeconds"],
                    "oldRating": contest["oldRating"],
                    "newRating": contest["newRating"]
                })
            # 转换时间
            for result in formatted_results:
                result["ratingUpdatedAt"] = (
                    datetime.utcfromtimestamp(result["ratingUpdatedAt"]).strftime('%Y-%m-%dT%H:%M:%S%z')
                )
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
            #解析
            data = response.json()
            if data["status"] == "OK":
                user_data = data["result"][0]
                if "rating" in user_data:
                    results.append({
                        "success": True,
                        "result": {
                            "handle": user_data["handle"],
                            "rating": user_data["rating"],
                            "rank": user_data["rank"]
                        }
                    })
                else:
                    results.append({
                        "success": True,
                        "result": {"handle": user_data["handle"]}
                    })
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
    app.run(host="127.0.0.1", port=2333,debug=True)
