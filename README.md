# home-assistant-wechatwork-notify

> 项目名称： home-assistant-wechatwork-notify
>
> github：<https://github.com/Chiunownow/home-assistant-wechatwork-notify>
>
> 本项目魔改自 @[81795791](https://bbs.hassbian.com/home.php?mod=space&uid=6080) （[原贴](https://bbs.hassbian.com/forum.php?mod=viewthread&tid=7128)）与 @[ck3](https://bbs.hassbian.com/home.php?mod=space&uid=19624) （[原贴](https://bbs.hassbian.com/forum.php?mod=viewthread&tid=7585)）的企业微信推送插件。感谢

组件下载 https://github.com/Chiunownow/home-assistant-wechatwork-notify/releases/latest



## 更新日志

2019年11月1日更新

1. ~~某鱼收了个 Kindle 看了几页书回来继续乱改惹~~
2. 修复发送图片时标题不能为空的bug
3. 现在推送图片，除了data-photo还允许使用data-image
4. 优化代码逻辑
5. 优化log输出

## 前言

本项目来自一个没学过 Python 的人（我）的瞎折腾。

为什么要改？

举个栗子，假设我要发一个推送，原先的企业微信插件使用方法大概是这样的：

````yaml
#原版企业微信文本推送
title: 这是推送标题
message: text|这是推送内容
#原版企业微信图片推送
title: 这是推送标题
message: image|这是图片描述|/path/to/photo.jpg
````

熟悉官方插件的人应该知道，大部分的推送服务应该是这样的

````yaml
#其他组件文本推送
title: 这是推送标题
message: 这是推送内容
#其他组件图片推送
title: 这是推送标题
message: 这是图片描述
data:
	photo: /path/to/photo.jpg
````

当一个信息要同时推送到多端（如 iOS，mobile_app，html5，telegram 等）时，就会受到限制，需要特地为他多写一次配置。本次修改就是为了解决这一问题。

## 插件介绍

1. 功能介绍

   1. 文本推送（带标题用文本卡片，不带标题直接发送文本消息）
   2. 图片推送（使用图文消息mpnews方式，文件上传到微信临时素材库）
   3. 视频推送（使用视频消息）
   4. 文件推送（使用文件消息，受限企业微信功能，文本与文件会拆两条消息推送。文本内容参考1）

   实现样式参考[企业微信API文档-发送应用消息](https://work.weixin.qq.com/api/doc#90000/90135/90236)

2. 特点

   1. 区别于各种 Pushbear 改版插件，可以无标题推送（受限企业微信API，图片推送除外（写到这里想起来可以把message当title多发一次嘛……））
   2. 使用 @[ck3](https://bbs.hassbian.com/home.php?mod=space&uid=19624) 提供的方法，将图片视频上传到企业微信临时素材库，避免直接暴露到公网
   3. 推送使用方式向其他 ha notify 组件靠拢

3. 配置方法

   ````yaml
   notify:
     - platform: wechatwork
       name: your_wechat #自定义推送服务名称，比如这里出来就是 notify.your_wechat
       corpid: !secret wxpusher_corpid #企业ID
       agentId: !secret wxpusher_agentId #应用ID
       secret: !secret wxpusher_secret #应用对应的密钥
       touser: '@all' #@all是向企业内所有人推送，亦可 UserID1|UserID2|UserID3
       ha_url: https://your.ha.url #你的HA链接，推送文本卡片时点击链接前往你的HA
       #以上项目均为必填
   ````

   几个 ID 和密钥的获取方式请见[[基础教程] 通过企业微信推送消息（暂时取代方糖）](https://bbs.hassbian.com/forum.php?mod=viewthread&tid=7128&highlight=%E4%BC%81%E4%B8%9A%E5%BE%AE%E4%BF%A1)

4. 使用方法

   ````yaml
   #文本不带标题
   message: 文本信息
   #文本带标题
   title: 标题
   message: 文本信息
   #图片
   title: 标题 #必填
   message: 图片描述
   data:
        photo: /path/to/photo.jpg #或image: 亦可
   #视频
   title: 标题 #选填
   message: 视频描述
   data:
        video: /path/to/video.mp4
   #文件
   title: 标题 #选填
   message: 文件描述
   data:
        file: /path/to/file.txt
   ````
   如碰到`voluptuous.error.MultipleInvalid: expected dict for dictionary value @ data['data']`请检查文件路径前是否有空格（需要空格）

   # 后续计划

   - [x] 实现图片推送免标题
   - [x] 让 log 正常一点
   - [ ] 上传文件超时正确输出 log
   - [ ] 实现 data_template
   - [ ] data后面的参数似乎对空格过于敏感？（放弃，应该是hass限制）

   项目公开在 github，欢迎~~吊锤~~鞭策。正好借此契机开始入门学习 Python。