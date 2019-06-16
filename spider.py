# -*- coding: UTF-8 -*-
import settings, requests, sys, traceback, json, os, time, random, csv, tqdm
from lxml import etree

INFO_URL = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}'
WEIBO_URL = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid={}&page={}'


class WBSpider():
    def __init__(self, user_id, filter=0, pic_download=0):
        """Weibo类初始化"""
        if not isinstance(user_id, int):
            sys.exit(u"user_id值应为一串数字形式,请重新输入")
        if filter != 0 and filter != 1:
            sys.exit(u"filter值应为0或1,请重新输入")
        if pic_download != 0 and pic_download != 1:
            sys.exit(u"pic_download值应为0或1,请重新输入")
        self.user_id = user_id  # 用户id,即需要我们输入的数字,如昵称为"Dear-迪丽热巴"的id为1669879400
        self.filter = filter  # 取值范围为0、1,程序默认值为0,代表要爬取用户的全部微博,1代表只爬取用户的原创微博
        self.pic_download = pic_download  # 取值范围为0、1,程序默认值为0,代表不下载微博原始图片,1代表下载
        # 根据抓取信息赋值
        self.userInfo = None
        self.weobo_containerid = None
        self.total_pages = 0
        self.all_cards = []
        self.got_num = 0

    def request_data(self, url):
        try:
            data = requests.get(url, headers=settings.DEFAULT_REQUEST_HEADERS).json()
            assert data["ok"] == 1
            return data["data"]
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def save_json(self, data, type='userinfo.json'):
        json_path = self.get_filepath(type)
        with open(json_path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)

    def start(self):
        """运行爬虫"""
        try:
            self.get_user_info()
            self.get_all_weibo()
            print(u"信息抓取完毕")
            print("*" * 100)
            if self.pic_download == 1:
                self.download_pictures()
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_user_info(self):
        """获取用户信息"""
        try:
            url = INFO_URL.format(self.user_id)
            data = self.request_data(url)
            self.userInfo = data["userInfo"]
            self.weobo_containerid = data["tabsInfo"]["tabs"][1]["containerid"]
            self.save_json(data)

        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_all_weibo(self):
        """获取用户信息"""
        try:
            url = WEIBO_URL.format(self.user_id, self.weobo_containerid, 1)
            data = self.request_data(url)
            self.total_pages = data['cardlistInfo']['total'] 
            self.save_json(data, type='cards1.json')

            page1  = 0
            random_pages = random.randint(1, 5)
            wrote_num = 0
            for i in tqdm.tqdm(range(self.total_pages), desc=u"进度"):
                page = i+1
                url = WEIBO_URL.format(self.user_id, self.weobo_containerid, page)
                data = self.request_data(url)
                self.all_cards += data['cards']
                self.got_num += len(data['cards'])

                if page % 2 == 0:  # 每爬20页写入一次文件
                    # 写文件
                    if self.got_num > wrote_num:
                        self.write_txt(wrote_num)
                    wrote_num = self.got_num

                # 通过加入随机等待避免被限制。爬虫速度过快容易被系统限制(一段时间后限
                # 制会自动解除)，加入随机等待模拟人的操作，可降低被系统限制的风险。默
                # 认是每爬取1到5页随机等待6到10秒，如果仍然被限，可适当增加sleep时间
                if page - page1 == random_pages:
                    time.sleep(random.randint(6, 10))
                    page1 = page
                    random_pages = random.randint(1, 5)

        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def write_txt(self, wrote_num):
        """将爬取的信息写入txt文件"""
        try:
            temp_result = []
            if wrote_num == 0:
                if self.filter:
                    result_header = u"\n\n原创微博内容: \n"
                else:
                    result_header = u"\n\n微博内容: \n"
                userInfo = self.userInfo
                result_header = (u"用户信息\n用户昵称：" + userInfo["screen_name"] + u"\n用户id: " +
                                 str(self.user_id) + u"\n微博数: " +
                                 str(userInfo["statuses_count"]) + u"\n关注数: " +
                                 str(userInfo["follow_count"]) + u"\n粉丝数: " +
                                 str(userInfo["followers_count"]) + result_header)
                temp_result.append(result_header)
            for i, w in enumerate(self.all_cards[wrote_num:]):
                print(w)
                w = w["mblog"]
                temp_result.append(
                    str(wrote_num + i + 1) + ":" + w["text"] + "\n" +
                    u"发布时间: " +
                    w["created_at"] + "\n" + u"点赞数: " + str(w["attitudes_count"]) +
                    u"   转发数: " + str(w["reposts_count"]) + u"   评论数: " +
                    str(w["reposts_count"]) + "\n" + u"发布工具: " +
                    w["source"] + "\n\n")
            result = "".join(temp_result)
            with open(self.get_filepath("txt"), "ab") as f:
                f.write(result.encode(sys.stdout.encoding))
            print(u"%d条微博写入txt文件完毕,保存路径:" % self.got_num)
            print(self.get_filepath("txt"))
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def download_pictures(self):
        pass

    def get_filepath(self, type):
        """获取结果文件路径"""
        try:
            file_dir = os.path.split(os.path.realpath(
                __file__))[0] + os.sep + "weibo" + os.sep + self.userInfo["screen_name"]
            # 图片的话就是 'img' 目录
            if type == "img":
                file_dir = file_dir + os.sep + "img"
            # 没有目录的时候自动创建
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            if type == "img":
                return file_dir
            # 其他类型的话，直接返回 user_id.csv
            file_path = file_dir + os.sep + "%d" % self.user_id + "." + type
            return file_path
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

if __name__ == "__main__":
    # 使用实例,输入一个用户id，所有信息都会存储在wb实例中
    user_id = 1669879400  # 可以改成任意合法的用户id（爬虫的微博id除外）
    filter = 0  # 值为0表示爬取全部微博（原创微博+转发微博），值为1表示只爬取原创微博
    pic_download = 0  # 值为0代表不下载微博原始图片,1代表下载微博原始图片
    wb = WBSpider(user_id, filter, pic_download)  # 调用Weibo类，创建微博实例wb
    wb.start()  # 爬取微博信息
