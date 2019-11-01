import logging
import time
import datetime
import requests
import json,os
import voluptuous as vol
import sys

from requests.exceptions import Timeout

from homeassistant.components.notify import (
    ATTR_MESSAGE, ATTR_TITLE, ATTR_DATA, ATTR_TARGET, PLATFORM_SCHEMA, BaseNotificationService)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_CORPID = 'corpid'
CONF_AGENTID = 'agentId'
CONF_SECRET = 'secret'
CONF_TOUSER = 'touser'
CONF_HAURL = 'ha_url'
ATTR_PHOTO = 'photo'
ATTR_IMAGE = 'image'
ATTR_VIDEO = 'video'
ATTR_FILE = 'file'

def get_service(hass, config, discovery_info=None):
    corpid = config.get(CONF_CORPID)
    agentId = config.get(CONF_AGENTID)
    secret = config.get(CONF_SECRET)
    touser = config.get(CONF_TOUSER)
    ha_url = config.get(CONF_HAURL)
    return QiyeweichatNotificationService(hass, corpid, agentId, secret, touser, ha_url)

class QiyeweichatNotificationService(BaseNotificationService):

    def __init__(self, hass, corpid, agentId, secret, touser, ha_url):
        self.CORPID = corpid
        self.CORPSECRET = secret
        self.AGENTID = agentId
        self.TOUSER = touser
        self.HAURL = ha_url

    def _get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def get_access_token(self):
        access_token = self._get_access_token()
        return access_token

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
        else: #当data不为空时，上传文件并获取media_id
            if ATTR_VIDEO in data:
                path = data.get(ATTR_VIDEO, None)
                media_type = "video"
                msgtype = "video"                
            if ATTR_PHOTO in data:
                path = data.get(ATTR_PHOTO, None)
                media_type = "image"
                msgtype = "mpnews"
                if title is None:
                    title = message
            if ATTR_IMAGE in data:
                path = data.get(ATTR_IMAGE, None)
                media_type = "image"
                msgtype = "mpnews"
                if title is None:
                    title = message
            if ATTR_FILE in data:
                path = data.get(ATTR_FILE, None)
                media_type = "file"
                msgtype = "file"
            try:
                curl = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=' + self.get_access_token() + '&type=' + media_type
                files = {media_type: open(path, 'rb')}
                _LOGGER.debug("Uploading media " + path + " to WeChat servicers")
                r = requests.post(curl, files=files, timeout=(20,180))
            except requests.Timeout: 
                _LOGGER.error("File upload timeout, please try again later.")
                return
            else:
                pass
            if int(json.loads(r.text)['errcode']) != 0:
                _LOGGER.error("Upload failed. Error Code " + str(json.loads(r.text)['errcode']) + ". " + str(json.loads(r.text)['errmsg']))
                return
            media_id = str(json.loads(r.text)['media_id'])
            if int(json.loads(r.text)['errcode']) == 0:
                _LOGGER.debug("Upload completed! media_id is "+media_id)
            if media_type == "video":
                if title is None:
                    content = '{"media_id":"%s", "description":"%s"}' % (media_id, message)
                else:
                    content = '{"media_id":"%s", "title":"%s", "description":"%s"}' % (media_id, title, message)
            if media_type == "image":
                if title is None:
                    title = message
                content = '{"articles":[{"title":"%s","thumb_media_id":"%s","digest":"%s"}]}' % (title, media_id, message)
            if media_type == "file":
                send_file = '{"touser":"%s","msgtype":"file","agentid":%s,"file":{"media_id":"%s"}}' % (self.TOUSER,self.AGENTID,media_id)
                send_file8 = send_file.encode('utf-8')
                response = requests.post(send_url,send_file8)
                if int(json.loads(response.text)['errcode']) == 0:
                    _LOGGER.debug("File sent successfully")
                else:
                    _LOGGER.error("File failed to send. Error code " + str(json.loads(response.text)['errcode']) + ". " + str(json.loads(response.text)['errmsg']))
                if title:
                    msgtype = "textcard"
                    content = '{"title": "%s", "description": "%s", "url": "%s"}' % (title, message, self.HAURL)
                else:
                    msgtype = "text"
                    content = '{"content": "%s"}' % message
        send_data = '{"touser": "%s","msgtype": "%s","agentid": %s,"%s":%s}' % (self.TOUSER,msgtype,self.AGENTID,msgtype,content)
        send_data8 = send_data.encode('utf-8')
        response = requests.post(send_url,send_data8)
        if int(json.loads(response.text)['errcode']) == 0:
            _LOGGER.debug("Message sent successfully")
        else:
            _LOGGER.error("Message failed to send. Error code " + str(json.loads(response.text)['errcode']) + ". " + str(json.loads(response.text)['errmsg']))