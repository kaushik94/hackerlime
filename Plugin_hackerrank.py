import sublime, sublime_plugin
import urllib2, httplib, urllib
import json as JSON

import base64

username = 'kaushik_varanasi'
password = 'hackerrank'
url = 'https://www.hackerrank.com/rest/contests/master/challenges/solve-me-first/'

code = """

def solveMeFirst(a,b):
  return a+b


num1 = input()
num2 = input()
res = solveMeFirst(num1,num2)
print res

"""

class CustomBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
    '''Preemptive basic auth.

    Instead of waiting for a 403 to then retry with the credentials,
    send the credentials if the url is handled by any password manager.
    Note: please use realm=None when calling add_password.'''
    def http_request(self, req):
        url = req.get_full_url()
        realm = None
        # this is very similar to the code from retry_http_basic_auth()
        # but returns a request object.
        user, pw = self.passwd.find_user_password(realm, url)
        if pw:
            raw = "%s:%s" % (user, pw)
            auth = 'Basic %s' % base64.b64encode(raw).strip()
            req.add_unredirected_header(self.auth_header, auth)
        return req

    https_request = http_request

class OpenBrowserCommand(sublime_plugin.TextCommand):
   
   def run(self,edit):

      auth_handler = CustomBasicAuthHandler()
      auth_handler.add_password( realm=None, uri=url, user=username, passwd=password)
      opener = urllib2.build_opener(auth_handler)
      urllib2.install_opener(opener)

      payload = {'code':code, 'customtestcase': 'false', 'language':'python'}
      sock = urllib2.Request(url+'compile_tests', urllib.urlencode(payload))
      resp = urllib2.urlopen(sock)
      header = resp.read()
      header_ = JSON.loads(header)
      id_ =  header_['model']['id']
      print id_
      sock = urllib2.Request(url+'compile_tests/'+str(id_)+'?')
      resp = urllib2.urlopen(sock)
      print resp.read()
