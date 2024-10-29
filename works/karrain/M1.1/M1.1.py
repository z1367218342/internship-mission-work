import sys
import requests
from lxml import etree
import json

def solve(username):
    url = 'https://codeforces.com/profile/{}/'.format(username)
    response = requests.get(url)
    if response.status_code == 200:
        html = response.content.decode('utf-8')
        root = etree.HTML(html)
        now_rating = root.xpath("//div[@class='info']/ul[1]/li[1]/span[1]/text()")
        max_rating = root.xpath("//div[@class='info']/ul[1]/li[1]//span[@class='smaller']//span[2]/text()")
        contribution = root.xpath("//div[@class='info']//ul/li[2]/span/text()")
        if contribution == []:
            contribution = root.xpath("//div[@class='info']//li[1]/span")
            # 这个用户不存在
            if contribution == []:
                sys.stderr.write("no such handle\n")
                sys.exit(1)
        flag = 0
        #标记用户是否有分数
        # 如果为空不存在
        if max_rating == []:
            flag = 1
        else:
            rank = root.xpath("//div[@class='user-rank']//span/text()")
        # 无rating
        if flag == 1:
            data = {
                "name": username
            }
        else:
            data = {
                "name": username,
                "rating": int(now_rating[0]),
                # 去空格
                "rank": rank[0].strip()
            }
        data_json = json.dumps(data)
        sys.stdout.write(data_json + "\n")
        sys.exit(0)


def main():
  #读参数
    username = sys.argv[1:][0]
    solve(username)


if __name__ == '__main__':
    main()
