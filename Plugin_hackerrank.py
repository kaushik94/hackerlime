import sublime, sublime_plugin
import urllib2, httplib, urllib
import json as JSON

import base64

username = 'kaushik_varanasi'
password = 'hackerrank'
master_url = 'https://www.hackerrank.com/rest/contests/'


lang = {'py':'python', 'java':'java', 'c':'c'}

class CustomBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
	'''
	Preemptive basic auth.

	Instead of waiting for a 403 to then retry with the credentials,
	send the credentials if the url is handled by any password manager.
	Note: please use realm=None when calling add_password.

	'''
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

class RunCodeCommand(sublime_plugin.TextCommand):
   
   def run(self, edit):

	  payload, url, code = self.get_params()

	  # print url
	  sock = urllib2.Request(url+'compile_tests', urllib.urlencode(payload))
	  resp = urllib2.urlopen(sock)
	  header = resp.read()
	  # print header
	  header_ = JSON.loads(header)
	  id_ =  header_['model']['id']
	  sock = urllib2.Request(url+'compile_tests/'+str(id_)+'?')
	  resp = urllib2.urlopen(sock)
	  self.pretty_print(id_, code, JSON.loads(resp.read()))

   def get_params(self):

	  auth_handler = CustomBasicAuthHandler()
	  auth_handler.add_password( realm=None, uri=master_url, user=username, passwd=password)
	  opener = urllib2.build_opener(auth_handler)
	  urllib2.install_opener(opener)

	  language, code, custom_testcase, child_url = self.get_file_info()
	  if custom_testcase is None:
		payload = {'code':code, 'customtestcase': 'false', 'language':language}
	  return payload, master_url+child_url, code

   def get_file_info(self):
	  ffname = self.view.file_name()
	  file_name = ffname.split('/')[-1]
	  extension = file_name.split('.')[-1]
	  language = lang[extension]

	  code, custom_testcase = self.get_code()
	  juice = code.split('\n')[-1] 	  
	  contester = map(str, juice.split('/')[3:])
	  # print contester
	  if contester[0] == 'challenges':
		child_url = "master/challenges/"+contester[-1]+"/"
	  else:
		child_url = contester[1]+"/challenges/"+contester[-1]+"/"
	  return language, code, custom_testcase, child_url

   def get_code(self):

	  content = self.view.substr(sublime.Region(0, self.view.size()))
	  return content, None

   def pretty_print(self, id_, code, result):

	  try:
		import tkinter as tk
		from tkinter import ttk
		tk_available = True
	  except ImportError:
	  	print "unavail"
		tk_available = False
	  
	  print "\n"+'SUBMISSION ID:', str(id_)+"\n"
	  print "YOUR CODE"+"\n"
	  print code+"\n"
	  print "RESULT:" 
	  result_list = result['model']['testcase_message']
	  print ''.join('	TESTCASE '+str(index+1)+": "+str(each)+'\n' for index, each in enumerate(result_list))

	  if tk_available:
		self.popup()

   def popup(self):
	  pass

