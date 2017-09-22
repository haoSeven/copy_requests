# -*- coding: utf-8 -*-
"""
    学习requests
"""
import urllib
import urllib2


AUTOAUTHS = []


class _Request(urllib2.Request):

    def __init__(self, url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None):
        urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
        self.method = method

    def get_method(self):
        if self.method:
            return self.method

        return urllib2.Request.get_method(self)


class Request(object):

    _METHODS = ('GET', 'PUT', 'DELETE', 'HEAD', 'POST')

    def __init__(self):
        self.url = None
        self.headers = dict()
        self.method = None
        self.params = dict()
        self.data = dict()
        self.response = Response()
        self.auth = None
        self.sent = False

    def __repr__(self):
        try:
            repr = '<Response [%s]>' % self.method
        except:
            repr = '<Response object>'
        return repr

    def __setattr__(self, name, value):
        if name == 'method' and value:
            if value not in self._METHODS:
                raise InvalidMethod()

        object.__setattr__(self, name, value)

    def _checks(self):

        if not self.url:
            raise UrlRequired

    def _get_opener(self):
        """为urllib2创建适当的开启对象"""
        if self.auth:
            author = urllib2.HTTPPasswordMgrWithDefaultRealm()

            author.add_password(None, self.url, self.auth.username, self.auth.password)
            handler = urllib2.HTTPBasicAuthHandler(author)
            opener = urllib2.build_opener(handler)

            return opener.open
        else:
            return urllib2.urlopen

    def send(self, anyway=False):
        """发送请求 返回True的successfull，如果不是，则返回false。
             如果传输过程中出现HTTPError，
             self.response.status_code将包含HTTPError代码。

             一旦请求成功发送，`sent`将等于True。

             ：param anyway：如果为True，请求将被发送，即使它
             已经发送
        """

        self._checks()

        success = False

        if self.method in ('GET', 'HEAD', 'DELETE'):
            if (not self.sent) or anyway:
                # url encode GET params if it's a dict
                if isinstance(self.params, dict):
                    params = urllib.urlencode(self.params)
                else:
                    params = self.params

                req = _Request(("%s?%s" % (self.url, params)), method=self.method)

                if self.headers:
                    req.headers = self.headers

                opener = self._get_opener()

                try:
                    resp = opener(req)
                    self.response.status_code = resp.code
                    self.response.headers = resp.info().dict
                    if self.method.lower() == 'get':
                        self.response.content = resp.read()

                    success = True
                except urllib2.HTTPError as why:
                    self.response.status_code = why.code

        elif self.method == 'POST':
            if (not self.sent) or anyway:
                req = _Request(self.url, method='POST')

                if self.headers:
                    req.headers = self.headers

                if isinstance(self.data, dict):
                    req.data = urllib.urlencode(self.data)
                else:
                    req.data = self.data

                try:
                    opener = self._get_opener()
                    resp = opener(req)
                    self.response.status_code = resp.code
                    self.response.headers = resp.info().dict
                    self.response.content = resp.read()

                    success = True
                except urllib2.HTTPError as why:
                    self.response.status_code = why.code

        self.sent = True if success else False

        return success


class Response(object):

    def __init__(self):
        self.content = None
        self.status_code = None
        self.headers = dict()

    def __repr__(self):
        try:
            repr = '<Response [%s]>' % self.status_code
        except:
            repr = '<Response object>'

        return repr


def get(url, params={}, headers={}, auth=None):
    """
    发送GET请求， 返回Response 对象
    :param url:
    :param params:（可选）GET字符串要发送的参数：class：`Request`。
    :param headers:
    :param auth:（可选）AuthObject启用基本HTTP验证
    :return:返回Response 对象
    """

    r = Request()
    r.method = 'GET'
    r.url = url
    r.params = params
    r.headers = headers
    r.auth = _detect_auth(url, auth)

    r.send()

    return r.response


def post(url, params={}, headers={}, auth=None):

    r = Request()
    r.url = url
    r.params = params
    r.headers = headers
    r.auth = _detect_auth(url, auth)

    r.send()

    return r.response


def _detect_auth(url, auth):
    """返回给定URL的注册AuthObject（如果可用），默认为给定的AuthObject。"""

    return _get_autoauth(url) if not auth else auth


def _get_autoauth(url):

    for autoauth_url, auth in AUTOAUTHS:
        if autoauth_url in url:
            return auth

    return None


class RequestException(Exception):
    """处理您的请求时发生了一个模糊异常。"""


class UrlRequired(RequestException):
    """需要一个有效的URL才能发出请求"""


class InvalidMethod(RequestException):
    """尝试了不适当的方法。"""
