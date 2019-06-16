# weiboAPI

正在收集微博 API 爬取微博用于自然语言处理...

## CDN

```js
<script src='https://cdn.jsdelivr.net/gh/upupming/weiboAPI/response.js'></script>

<div id="userInfo"></div>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/renderjson@1.4.0/renderjson.js"></script>
<script>
    renderjson.set_show_to_level(2);
    document.getElementById("userInfo").appendChild(
        renderjson(userInfo)
    );
</script>
```

## Spider

修复[输出重定向错误](http://blog.mathieu-leplatre.info/python-utf-8-print-fails-when-redirecting-stdout.html)：

```pwsh
$env:PYTHONIOENCODING = "utf_8"
```

运行（无需 Cookie）：

```pwsh
python.exe .\spider.py
```
