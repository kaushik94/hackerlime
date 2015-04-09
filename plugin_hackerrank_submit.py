import sublime, sublime_plugin
import urllib2, httplib, urllib
import json as JSON

import base64
import time

master_url = 'https://www.hackerrank.com/rest/contests/'


lang = {'py':'python', 'java':'java', 'c':'c', 'cpp':'cpp'}

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

class SubmitCodeCommand(sublime_plugin.TextCommand):
   
   def run(self, edit):

   	  status, username, password = self.get_credentials()
   	  if not status:
   	  	print "\n\nenter your credentials in your home directory in a file '.hrconfig.txt' \n\n"
   	  	return
	  payload, url, code = self.get_params()

	  sock = urllib2.Request(url+'submissions/', urllib.urlencode(payload))
	  resp = urllib2.urlopen(sock)
	  header = resp.read()
	  # print header
	  header_ = JSON.loads(header)
	  id_ =  header_['model']['id']

	  sock = urllib2.Request(url+'submissions/'+str(id_)+'?')
	  
	  jsoned = 'NULL'
	  while True:
	  	resp = urllib2.urlopen(sock)
	  	jsoned = JSON.loads(resp.read())
	  	if len(jsoned['model']['testcase_message']) is not 0:
	  		break
	  	else:
	  		time.sleep(1)
	  self.pretty_print(id_, code, jsoned)

   def get_credentials(self):
   	  from os.path import expanduser
   	  import os
	  home = expanduser("~")+'/'

	  try:
	  	f = open(home+'.hrconfig.txt', 'r')
	  except IOError:
	  	return None, None, None
	  lines = f.readlines()
	  return True, lines[0], lines[1]

   def get_params(self):

	  auth_handler = CustomBasicAuthHandler()
	  auth_handler.add_password( realm=None, uri=master_url, user=username, passwd=password)
	  opener = urllib2.build_opener(auth_handler)
	  urllib2.install_opener(opener)

	  language, code, child_url = self.get_file_info()
	  custom_testcase = None
	  if custom_testcase is None:
		payload = {'code':code, 'language':language}
	  return payload, master_url+child_url, code

   def get_file_info(self):
	  ffname = self.view.file_name()
	  file_name = ffname.split('/')[-1]
	  extension = file_name.split('.')[-1]
	  language = lang[extension]

	  code, custom_testcase = self.get_code()
	  juice = code.split('\n')[-1] 	  
	  contester = map(str, juice.split('/')[4:])
	  # print contester
	  if contester[1] == 'challenges':
		child_url = "master/challenges/"+contester[-1]+"/"
	  else:
		child_url = contester[2]+"/challenges/"+contester[-1]+"/"
	  return language, code, child_url

   def get_code(self):

	  content = self.view.substr(sublime.Region(0, self.view.size()))
	  return content, None

   def pretty_print(self, id_, code, result):

	  try:
		import tkinter as tk
		from tkinter import ttk
		tk_available = True
	  except ImportError:
		tk_available = False
	  
	  print "\n"+'SUBMISSION ID:', str(id_)+"\n"
	  print "YOUR CODE"+"\n"
	  print code+"\n"
	  print "RESULT:" 
	  result_list = result['model']['testcase_message']
	  # print result
	  print ''.join('	TESTCASE '+str(index+1)+": "+str(each)+'\n' for index, each in enumerate(result_list))

	  if tk_available:
		self.popup()

   def popup(self):
	  pass

