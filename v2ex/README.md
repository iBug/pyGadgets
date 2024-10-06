# V2EX 自动签到脚本

其中 `v2ex.py` 修改自 [lord63/v2ex_daily_mission](https://github.com/lord63/v2ex_daily_mission/blob/master/v2ex_daily_mission/v2ex.py)。

## 使用方法

将 V2EX 的 cookie 写入同目录下的 `cookie.txt`，然后在 crontab 中加入配置：

```shell
1 8 * * * ~/path/to/v2ex/main.py sign
```
