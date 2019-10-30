import logging
#import time
#import datetime
import requests
import json,os
import voluptuous as vol
#import sys

from homeassistant.components.notify import (
    ATTR_MESSAGE, ATTR_TITLE, ATTR_DATA, ATTR_TARGET, PLATFORM_SCHEMA, BaseNotificationService)
import homeassistant.helpers.config_validation as cv
#以上照抄

_LOGGER = logging.getLogger(__name__)

CONF_CORPID = 'corpid'
CONF_AGENTID = 'agentId'
CONF_SECRET = 'secret'
CONF_TOUSER = 'touser'
CONF_HAURL = 'ha_url'
#定义配置文件参数变量
ATTR_PHOTO = 'photo'
ATTR_VIDEO = 'video'
ATTR_FILE = 'file'

def get_service(hass, config, discovery_info=None):
    corpid = config.get(CONF_CORPID)
    agentId = config.get(CONF_AGENTID)
    secret = config.get(CONF_SECRET)
    touser = config.get(CONF_TOUSER)
    ha_url = config.get(CONF_HAURL)
    return QiyeweichatNotificationService(hass, corpid, agentId, secret, touser, ha_url)
#从配置文件获取参数

class QiyeweichatNotificationService(BaseNotificationService):

    def __init__(self, hass, corpid, agentId, secret, touser, ha_url):
        self.CORPID = corpid
        self.CORPSECRET = secret
        self.AGENTID = agentId
        self.TOUSER = touser
        self.HAURL = ha_url
    #将参数赋予到变量

    def _get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]
    #获取token

    def get_access_token(self):
        access_token = self._get_access_token()
        return access_token
    #将token赋值到变量

    def send_message(self, message='', **kwargs):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        data = kwargs.get(ATTR_DATA)
        message = '{}'.format(message)
        title = kwargs.get(ATTR_TITLE)
        if data is None: #当data为空时，根据是否有标题发送文本或文本卡片
            if title:
                msgtype = "textcard"
                content = '{"title": "%s", "description": "%s", "url": "%s"}' % (title, message, self.HAURL)
            else:
                msgtype = "text"
                content = '{"content": "%s"}' % message
        else:
            if ATTR_VIDEO in data:
                path = data.get(ATTR_VIDEO, None)
                print(path)
                curl = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=' + self.get_access_token() + '&type=video'
                files = {'video': open(path, 'rb')}
                r = requests.post(curl, files=files)
                print(r.text)
                re = json.loads(r.text)
                ree = re['media_id']
                media_id = str(ree)
                if title is None:
                    content = '{"media_id":"%s", "description":"%s"}' % (media_id, message)
                else:
                    content = '{"media_id":"%s", "title":"%s", "description":"%s"}' % (media_id, title, message)
                msgtype = "video"
            if ATTR_PHOTO in data and title is not None:
                path = data.get(ATTR_PHOTO, None)
                print(path)
                curl = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=' + self.get_access_token() + '&type=video'
                files = {'image': open(path, 'rb')}
                r = requests.post(curl, files=files)
                print(r.text)
                re = json.loads(r.text)
                ree = re['media_id']
                media_id = str(ree)
                content = '{"articles":[{"title":"%s","thumb_media_id":"%s","digest":"%s"}]}' % (title, media_id, message)
                msgtype = "mpnews"
            if ATTR_PHOTO in data and title is None:
                _LOGGER.error("使用企业微信发送图片时必须有title")
            if ATTR_FILE in data:
                path = data.get(ATTR_FILE, None)
                print(path)
                curl = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=' + self.get_access_token() + '&type=video'
                files = {'file': open(path, 'rb')}
                r = requests.post(curl, files=files)
                print(r.text)
                re = json.loads(r.text)
                ree = re['media_id']
                media_id = str(ree)
                send_file = '{"touser":"%s","msgtype":"file","agentid":%s,"file":{"media_id":"%s"}}' % (self.TOUSER,self.AGENTID,media_id)
                send_file8 = send_file.encode('utf-8')
                response = requests.post(send_url,send_file8)
                print(send_file8)
                print(response.text)
                if title:
                    msgtype = "textcard"
                    content = '{"title": "%s", "description": "%s", "url": "%s"}' % (title, message, self.HAURL)
                else:
                    msgtype = "text"
                    content = '{"content": "%s"}' % message
        send_data = '{"touser": "%s","msgtype": "%s","agentid": %s,"%s":%s}' % (self.TOUSER,msgtype,self.AGENTID,msgtype,content)
        send_data8 = send_data.encode('utf-8')
        response = requests.post(send_url,send_data8)
        print(send_data)
        print(response.text)
