#
#   Copyright (c) 2012-2013 Canonical Ltd.
#
#   This file is part of: SST (selenium-simple-test)
#   https://launchpad.net/selenium-simple-test
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#


import codecs
import json
import urllib2


class BrowserMobProxy:

    def __init__(self, host, command_port):
        self.host = host
        self.command_port = command_port
        self.command_url = 'http://%s:%s' % (self.host, self.command_port)
        content = self.__request('%s/proxy' % self.command_url, 'POST')
        jcontent = json.loads(content)
        self.listen_port = jcontent['port']
        self.url = 'http://%s:%s' % (self.host, self.listen_port)

    @property
    def har(self):
        url = '%s/proxy/%s/har' % (self.command_url, self.listen_port)
        content = self.__request(url)
        return json.loads(content)

    def __request(self, url, method='GET'):
        req = urllib2.Request(url)
        if method == 'POST':
            req = urllib2.Request(url, '')
        req.get_method = lambda: method
        try:
            resp = urllib2.urlopen(req)
            content = resp.read()
        except urllib2.URLError:
            raise ProxyError('Error: can not connect to proxy')
        return content

    def close(self):
        url = '%s/proxy/%s' % (self.command_url, self.listen_port)
        self.__request(url, method='DELETE')

    def new_har(self):
        url = '%s/proxy/%s/har' % (self.command_url, self.listen_port)
        self.__request(url, method='PUT')

    def save_har(self, file_name='out.har'):
        with codecs.open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.har))


class ProxyError(Exception):
    pass
