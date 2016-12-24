#!/usr/bin/python
# coding:utf-8

import base64
import json
import re
import requests
import random
import time
import cookies_new
import weibo_postMessage
import filterStr
import proxyHandler

requests.adapters.DEFAULT_RETRIES = 5
class Weibo(object):
    def __init__(self, username, password, proxy):
        self.username = username
        self.password = password
        self.session = None
        self.user_agent = None
        self.proxy = proxy
        self.login(self.username, self.password)

    def login(self, username, password):
        username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
        data = {
            "entry": "sso",
            "gateway": "1",
            "from": "null",
            "savestate": "30",
            "useticket": "0",
            "pagerefer": "",
            "vsnf": "1",
            "su": username,
            "service": "sso",
            "sp": password,
            "sr": "1440*900",
            "encoding": "UTF-8",
            "cdult": "3",
            "domain": "sina.com.cn",
            "prelt": "0",
            "returntype": "TEXT",
        }
        login_url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        session = requests.Session()
        res = session.post(login_url, proxies=self.proxy, data=data)
        print res
        json_str = res.content.decode('gbk')
        info = json.loads(json_str)
        if info["retcode"] == "0":
            cookies = session.cookies.get_dict()
            cookies = [key + "=" + value for key, value in cookies.items()]
            cookies = "; ".join(cookies)
            session.headers["cookie"] = cookies
        else:
            print info['reason']
            raise Exception("login fail:%s" % info['reason'])

        self.session = session

    # 发新微博
    def post_new(self, content):
        st = re.findall(r'"st":"(\w+)"', self.session.get(r"https://m.weibo.cn/mblog").text)
        addurl = "https://m.weibo.cn/mblogDeal/addAMblog"
        data = {'content': content, 'st': st, }
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://m.weibo.cn/mblog",
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(addurl, data, proxies=self.proxy, headers=headers)
        print res.status_code
        return res.status_code

    # 转发
    def repost(self, content, uid, repost_id):
        repost_page_url = r"http://m.weibo.cn/repost?id=%s" % repost_id
        st = re.findall(r'"st":"(\w+)"', self.session.get(repost_page_url).text)
        data = {
            'annotations': '',
            'content': content,
            'id': repost_id,
            'rtcomment': uid,
            'st': st[0]
        }
        repost_url = 'http://m.weibo.cn/mblogDeal/rtMblog'
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://m.weibo.cn/repost?id=%s" % repost_id,
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(repost_url, data, headers=headers)
        return res.status_code

    # 评论别人的微博
    def comment(self, content, post_id):
        comment_page_url = r"http://m.weibo.cn/comment?id=%s" % post_id
        st = re.findall(r'"st":"(\w+)"', self.session.get(comment_page_url).text)
        data = {
            'content': content,
            'id': post_id,
            'st': st[0]
        }
        comment_url = 'http://m.weibo.cn/commentDeal/addCmt'
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://m.weibo.cn/comment?id=%s" % post_id,
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(comment_url, data, headers=headers)
        return res.status_code

    def follow(self, uid):
        follow_page_url = r"http://m.weibo.cn/u/%s" % uid
        st = re.findall(r'st: \'(\w+)\'', self.session.get(follow_page_url).text)
        follow_url = 'http://m.weibo.cn/api/friendships/create?st=%s&uid=%s' % (st[0], uid)
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://m.weibo.cn/u/%s" % uid,
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(follow_url, headers=headers)
        return res.status_code

    def unfollow(self, uid):
        follow_page_url = r"http://m.weibo.cn/u/%s" % uid
        st = re.findall(r'st: \'(\w+)\'', self.session.get(follow_page_url).text)
        unfollow_url = 'http://m.weibo.cn/api/friendships/destory'
        data = {
            'uid': uid,
            'st': st[0]
        }
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://m.weibo.cn/u/%s" % uid,
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(unfollow_url, data, headers=headers)
        return res.status_code

    def like_post(self, uid, post_id):
        like_page_url = r"http://m.weibo.cn/repost?id=%s" % post_id
        st = re.findall(r'"st":"(\w+)"', self.session.get(like_page_url).text)
        data = {
            'attitude': 'heart',
            'id': post_id,
            'st': st[0]
        }
        like_url = 'http://m.weibo.cn/attitudesDeal/add'
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://m.weibo.cn/%s/%s" % (uid, post_id),
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(like_url, data, headers=headers)
        return res.status_code

    def unlike_post(self, uid, post_id):
        unlike_page_url = r"http://m.weibo.cn/repost?id=%s" % post_id
        st = re.findall(r'"st":"(\w+)"', self.session.get(unlike_page_url).text)
        data = {
            'id': post_id,
            'st': st[0]
        }
        unlike_url = 'http://m.weibo.cn/attitudesDeal/delete'
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://m.weibo.cn/%s/%s" % (uid, post_id),
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(unlike_url, data, headers=headers)
        return res.status_code

    # 每天浏览
    def daily_refresh(self):
        post_list = []
        content = self.session.get('http://m.weibo.cn/index/feed?format=cards').text
        json_data = json.loads(content)
        for card in json_data[0]["card_group"]:
            post_list.append(str(card["mblog"]["user"]["id"]) + '/' + str(card["mblog"]["id"]))

        content = self.session.get('http://m.weibo.cn/index/feed?format=cards&page=2').text
        json_data = json.loads(content)
        for card in json_data[0]["card_group"]:
            post_list.append(str(card["mblog"]["user"]["id"]) + '/' + str(card["mblog"]["id"]))

        content = self.session.get('http://m.weibo.cn/index/feed?format=cards&page=3').text
        json_data = json.loads(content)
        for card in json_data[0]["card_group"]:
            post_list.append(str(card["mblog"]["user"]["id"]) + '/' + str(card["mblog"]["id"]))

        content = self.session.get('http://m.weibo.cn/index/feed?format=cards&page=4').text
        json_data = json.loads(content)
        for card in json_data[0]["card_group"]:
            post_list.append(str(card["mblog"]["user"]["id"]) + '/' + str(card["mblog"]["id"]))

        random_num = random.randint(0, len(post_list))
        self.like_post(post_list[random_num].split('/')[0], post_list[random_num].split('/')[1])
        time.sleep(random_num)

        random_num = random.randint(0, len(post_list))
        self.like_post(post_list[random_num].split('/')[0], post_list[random_num].split('/')[1])
        time.sleep(random_num)

        random_num = random.randint(0, len(post_list))
        self.like_post(post_list[random_num].split('/')[0], post_list[random_num].split('/')[1])
        time.sleep(random_num)

        random_num = random.randint(0, len(post_list))
        self.repost('', post_list[random_num].split('/')[0], post_list[random_num].split('/')[1])
        time.sleep(random_num)
        random_num = random.randint(0, len(post_list))
        self.repost('', post_list[random_num].split('/')[0], post_list[random_num].split('/')[1])

        random_num = random.randint(0, len(post_list))
        self.repost('', post_list[random_num].split('/')[0], post_list[random_num].split('/')[1])
        time.sleep(random_num)

    # Todo 转发话题
    def topic_repost(self, topic):
        print 'topic'

    # Todo 关注列表
    def get_followers(self):
        followers_list = []

        followers_url = 'http://m.weibo.cn/container/getSecond?containerid=1005051850082763_-_FOLLOWERS'
        content = self.session.get(followers_url).text
        json_data = json.loads(content)
        print json_data['cards']
        for card in json_data['cards']:
            followers_list.append(card['user']['id'])

        followers_url = 'http://m.weibo.cn/container/getSecond?containerid=1005053674263332_-_FOLLOWERS&page=2'
        content = self.session.get(followers_url).text
        json_data = json.loads(content)
        print json_data['cards']
        for card in json_data['cards']:
            followers_list.append(card['user']['id'])

        followers_url = 'http://m.weibo.cn/container/getSecond?containerid=1005053674263332_-_FOLLOWERS&page=2'
        content = self.session.get(followers_url).text
        json_data = json.loads(content)
        print json_data['cards']
        for card in json_data['cards']:
            followers_list.append(card['user']['id'])

        for key in followers_list:
            print key

    # Todo
    def get_fans(self):
        print 'get fans'

    def like_comment(self, uid, post_id, comment_id):
        print 'like comment'
        like_comment_url = 'http://m.weibo.cn/comment/like?id=%s' % comment_id
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://m.weibo.cn/%s/%s" % (uid, post_id),
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(like_comment_url, headers=headers)
        print res.status_code
        return res.status_code

    def dislike_comment(self, uid, post_id, comment_id):
        print 'dislike'
        dislike_comment_url = 'http://m.weibo.cn/comment/dislike?id=%s' % comment_id
        headers = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://m.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://m.weibo.cn/%s/%s" % (uid, post_id),
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        res = self.session.post(dislike_comment_url, headers=headers)
        print res.status_code
        return res.status_code


if __name__ == '__main__':
    users = cookies_new.getUser("users.txt")
    #proxy = proxyHandler.getProxy()
    #print proxy
    for username in users:
        print username
        print users[username]
        proxies = {
            "https": "http://180.153.87.22:18080"
        }
        print proxies
        # uid = mlogin(username, users[username])
        # print uid
        res=requests.get("https://icanhazip.com/",proxies=proxies,timeout=3)
        print res.content
        weibo = Weibo(username, users[username], proxies)
        uid = weibo.login(username, users[username])
        print uid
        msg = weibo_postMessage.reandomMessage('weiboText/weibo.txt')
        while filterStr.filterStr(msg):
            msg = weibo_postMessage.reandomMessage('weiboText/weibo.txt')
        print msg
        weibo.post_new(msg)
        # time.sleep(30)
        # weibo.like_comment('1403915120', 'EmusLdjBy', '4053627523776987')
        # weibo.random_repost()
        # weibo.like_post('1990309453', '4054100666534879')
        # weibo.unlike_post('1990309453', '4054100666534879')
        # weibo.post_new('想妈妈了!!')
        # weibo.comment('赢得不轻松啊', '4054100666534879')
        # weibo.follow('1990309453')
        # weibo.repost('C罗好帅!!', '1990309453', '4054100666534879')
        # weibo.unfollow('1990309453')
        # with open('./id.txt') as f:
        #     content = f.readlines()
        #     for line in content:
        #         username = line.strip('\n').split('----')[0]
        #         password = line.strip('\n').split('----')[1]
        #         print str(username) + '\t' + str(password)
        #         weibo = Weibo(username, password)
        #         weibo.daily_refresh()