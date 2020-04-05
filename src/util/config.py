# -*- coding: UTF-8 -*

config = {
    # Bmob 配置
    'bmob': {
        'APP_ID': '366372322020724a39d8de5ccd61eeaa',
        'REST_API_KEY': '40de9f3e91287703e695fe1f6b94393a',
    },
    # 微博配置
    'weibo': {
        # Cookie 获取方法：前往 m.weibo.cn，打开一条评论较多的微博全文，往下翻几页
        # 这时 Chrome 的 Network 界面的 request headers 就会有 Cookie 信息了
        # 注意: m.weibo.cn 比较特殊，查看微博并不需要登录，而看评论确实是需要的
        # 比如直接进这个网址 https://m.weibo.cn/detail/4461449911415808   //https://m.weibo.cn/detail/4389138709375153，往后多翻几条评论在 Network 的 XHR 里面可以看到 request headers 的 Cookie
        'COOKIE': 'ALF=1587886750; _T_WM=25387770715; WEIBOCN_FROM=1110006030; MLOGIN=1; XSRF-TOKEN=388e38; SCF=As_-yP-N2m2DH5s6zfyeGjQhu-krcrxuROefVtbVdJ6GKkNRYiwiGQ7mkPAbSZQLEZ0jcEhvrmrx1pFe_-p7sqY.; SUB=_2A25zjdHsDeRhGeRG7lQX-S3EyT6IHXVRcf-krDV6PUJbktAKLVetkW1NUgT7I10jpUYOX8eGJDI2LB4dTSNL2d9g; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhJ93aWUjl1S51Bx.3w6qpi5JpX5K-hUgL.FozRSKqc1KeReoz2dJLoI7LKIgUV9sHX9get; SUHB=010XaB3uzecqOf; SSOLoginState=1586078140; M_WEIBOCN_PARAMS=oid%3D4389138709375153%26lfid%3D2304132803301701_-_WEIBO_SECOND_PROFILE_WEIBO%26luicode%3D20000174%26uicode%3D20000174%26fid%3D102803
    },
    
    
    'mysql': {
        'CONNECTION': {
            'host': "localhost",
            'user': 'upupming',
            'charset': 'utf8mb4'
        }
    },
    'crawl': {
        # 用来初始化爬取队列
        'START_USER': '2803301701',
        # 每两次请求之间等待 PERIOD 秒
        'PERIOD': 4,
        # 被封之后等待 5 分钟再次请求
        'FORBID_PAUSE': 300
    }
}
