import sys
import requests
import json
def solve(handle):
  url = f"https://codeforces.com/api/user.info?handles={handle}"
  try:
    response = requests.get(url)
    response.raise_for_status()  # 检查http响应状态
    data = response.json()
    if data['status'] != 'OK':
      sys.stderr.write(f"API 返回异常: {data.get('comment', '未知错误')}\n")
      sys.exit(1)
    user_info = data['result'][0]  #获取用户信息
    if 'rating' in user_info:
      result = {
        "handle": user_info['handle'],
        "rating": user_info['rating'],
        "rank": user_info['rank']
      }
    else:
      result = {
        "handle": user_info['handle']
      }

    # print
    result_json = json.dumps(result, ensure_ascii=False)
    sys.stdout.write(result_json + "\n")
    sys.exit(0)

  except requests.exceptions.RequestException as e:
    #选了三个我经常出现的错误
    sys.stderr.write(f"网络请求错误: {e}\n")
    sys.exit(1)
  except json.JSONDecodeError:
    sys.stderr.write("JSON解析错误\n")
    sys.exit(1)
  except KeyError:
    sys.stderr.write("KeyError\n")
    sys.exit(1)
def main():
  handle = sys.argv[1:][0]
  solve(handle)


if __name__ == "__main__":
  main()
