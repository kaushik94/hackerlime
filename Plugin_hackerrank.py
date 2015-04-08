import sublime, sublime_plugin
import urllib2, httplib


class OpenBrowserCommand(sublime_plugin.TextCommand):
   
   def run(self,edit):
      url = 'https://www.hackerrank.com/rest/contests/master/challenges/solve-me-first/compile_tests'
      payload = {'code':'def solveMeFirst(a,b):\nreturn a+b\n\nnum1 = input()\num2 = input()\nres = solveMeFirst(num1,num2)\nprint res\n', 'customtestcase': 'false', 'language':'python'}
      sock = self.URLRequest(url, payload, method = 'POST')
      resp = urllib2.urlopen(sock)
      print resp.read()

      
   def URLRequest(self, url, params, method="GET"):
    if method == "POST":
        return urllib2.Request(url, data=urllib.urlencode(params))
    else:
        return urllib2.Request(url + "?" + urllib.urlencode(params))