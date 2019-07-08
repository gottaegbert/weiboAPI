# -*- coding: UTF-8 -*

import os, logging, time
from util.table import *
from util.Bmob import *
from collections import deque
from lxml import etree

BmobSDK.setup(config["bmob"]["APP_ID"], config["bmob"]["REST_API_KEY"])

# 用来获取 containerid
INFO_URL = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}'
# 注意不同人的微博 containerid 是不同的
WEIBO_URL = 'https://m.weibo.cn/api/container/getIndex?containerid={}&page={}'
LONG_WEIBO_URL = 'https://m.weibo.cn/statuses/extend?id={}'
COMMENT_URL = 'https://m.weibo.cn/api/comments/show?id={}&page={}'
FOLLOWING_URL = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{}&page={}'


class WBSpider():

    def init_logging(name='testname', log_level=logging.INFO):
        file_dir = os.path.dirname(os.path.realpath('__file__')) + "/log"
        # 没有目录的时候自动创建
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        fileh = logging.FileHandler(file_dir+f'/{name}-{logging.getLevelName(log_level)}.log', 'w', encoding='utf-8')
        formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")
        fileh.setFormatter(formatter)

        log = logging.getLogger()  # root logger
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fileh)      # set the new handler
        log.setLevel(log_level)

        return fileh

    def init_crawl_from_bmob(self):
        # 待爬取队列，采用广度优先搜索
        self.crawling = deque(Crawling().query().exec_query())
        self.crawled = deque(Crawled().query().exec_query())
    def save_crawl_to_bmob(self):
        for crawling_item in self.crawling:
            crawling_item.save()
        for crawled_item in crawled:
            crawled_item.save()

    def init_session(self):
        self.session = requests.Session()
        cookies_dict = dict([l.split("=", 1) for l in config['weibo']['COOKIE'].split("; ")])
        # https://blog.csdn.net/mgxcool/article/details/52663382
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies_dict)

    def __init__(self):
        self.init_logging()
        self.init_crawl_from_bmob()
        self.init_session()
    
    def get_data(self, url):
        # 每次请求之前等待 0.5 秒，防止因为速度过快被封
        time.sleep(0.5)
        return self.session.get(url).json()
    
    def crawl_user_following(self, uid):
        """
        返回此用户的所有 following 的 (uid, uname)（字典）
        """
        # 特殊情况，是从 1 开始索引的
        try:
            result = []
            cur_page = 1
            while True:
                logging.info(f'正在爬取 {uid} 的第 {cur_page} 页的 following')
                # https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_1669879400&page=0
                url = FOLLOWING_URL.format(uid, cur_page)
                data = self.get_data(url)
                if len(data['data']['cards']) == 0:
                    logging.info(f'用户 {uid} 的 following 爬取完毕')
                    return
                
                for card in data['data']['cards']:
                    for card_group_item in card['card_group']:
                        # 只有类型为 10 才是真正的关注列表
                        if card_group_item['card_type'] != 10:
                            continue
                        result.append({'uid': card_group_item['user']['id'], 'uname': card_group_item['user']['screen_name']})
            logging.info(f'将新增加 {len(result)} 个 following 到队列中')
            return result
        except:
            return []
        
    def get_weibo_containerid(self, uid):
        try:
            # https://m.weibo.cn/api/container/getIndex?type=uid&value=1669879400
            url = INFO_URL.format(uid)
            data = self.get_data(url)
            return data['data']['tabsInfo']['tabs'][1]['containerid'] 
        except:
            print(data)
    def crawl_user_weibo(self, uid):
        """
        将所有的微博爬取到，并存储到 Weibo 表中
        """
        try:
            containerid = self.get_weibo_containerid(uid)
            cur_page = 0
            while True:
                logging.info(f'正在爬取 {uid} 的第 {cur_page+1} 页微博')
                # https://m.weibo.cn/api/container/getIndex?containerid=1076031669879400&page=0
                url = WEIBO_URL.format(containerid, cur_page)
                data = self.get_data(url)
                if len(data['data']['cards']) == 0:
                    logging.info(f'用户 {uid} 爬取完毕')
                    return

                for card in data['data']['cards']:
                    # 忽略广告等其他卡片
                    if card["card_type"] != 9:
                        continue
                    mblog = card["mblog"]
                    # 如果是转发微博的话，忽略
                    if "retweeted_status" in mblog:
                        continue
                    
                    selector = etree.HTML(mblog["text"])
                    a_text = selector.xpath("//a/text()")
                    # 将 HTML 转换为 txt
                    # 参考 https://www.zybuluo.com/Alston/note/778377
                    text = etree.tostring(selector, method="text", encoding="UTF-8").decode('utf-8')
                    img_emoji = selector.xpath("//span/img/@alt")
                    
                    weibo = Weibo(text=text, mid=mblog['mid'], img_emoji=img_emoji)
                    weibo.save()
                
                # 抓取评论
                self.crawl_weibo_comments(mblog['mid'])

                cur_page += 1
        except:
            print(data)
        
    def crawl_weibo_comments(self, mid, max=10):
        """
        将某一篇微博的评论爬取 200 篇，并存储到 Comment 表中，将 mid（博文唯一标识）设置为传入的 mid
        """
        try:
            cur_page = 0
            for i in range(max):
                logging.info(f'正在抓取 {mid} 的第 {cur_page+1} 页评论')
                # https://m.weibo.cn/api/comments/show?id=4384122253963002&page=0
                url = COMMENT_URL.format(mid, cur_page)
                data = self.get_data(url)
                if data['msg'] == '暂无数据':
                    break
                for comment in data['data']['data']:
                    selector = etree.HTML(comment["text"])
                    cid = comment["id"]
                    text = etree.tostring(selector, method="text", encoding="UTF-8").decode('utf-8')
                    img_emoji = selector.xpath("//span/img/@alt")
                    
                    comment = Comment(cid=cid, mid=mid, text=text, img_emoji=img_emoji)
                    comment.save()

                cur_page += 1
            logging.info(f'微博 {mid} 爬取完毕')
        except:
            print(data)

    def crawl(self, uid):
        """
        爬取 uid 所代表的用户
        结束之后返回此用户的所有 following 的 (uid, uname)（字典）
        """
        self.crawl_user_weibo(uid)
        return self.crawl_user_following(uid)

    def startBFS(self):
        """
        开始爬取（BFS 搜索）
        """
        # 理论上会结束，实际上并不会结束
        while len(self.crawling) > 0:
            crawling_user = self.crawling.popleft()
            for v in self.crawl(crawling_user.uid):
                self.crawling.append(Crawling(uid=v.uid, uname=v.uname))
            self.crawled.append(Crawled(crawling_user.uid, crawling_user.uname))
        
if __name__ == "__main__":    
    spider = WBSpider()
    spider.startBFS()