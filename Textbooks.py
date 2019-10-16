from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import os
import time
import csv
import re
import random
from datetime import datetime, date

def random_driver(loadstrat="normal",images=True,visible=True):
	caps = DesiredCapabilities().CHROME
	caps["pageLoadStrategy"] = loadstrat
	opts = Options()
	if not images:
		prefs = {"profile.managed_default_content_settings.images":2}
		opts.add_experimental_option("prefs",prefs)
	if not visible:
		opts.add_argument('headless')
		opts.add_argument('window-size=1200x600')
	useragent=random_user_agent()
	opts.add_argument("user-agent="+useragent)
	driver = webdriver.Chrome(desired_capabilities=caps, executable_path=local_directory+'/chromedriver',chrome_options=opts)
	return driver

def random_user_agent():
	with open(local_directory+'/useragents.txt') as file:
		raw_config = [line.rstrip('\n') for line in file] 
		weighted_agent_list=[]
		for agent in raw_config:
			for _ in range(int(float(agent.split('%')[0])*10)):
				weighted_agent_list.append(agent.split('%')[1])
	return random.choice(weighted_agent_list)

def get_isbn_list(url, driver):
	driver.get(url)
	while len(re.findall(r"ISBN:</span> \d{10,}",str(driver.page_source))) < 1:
		time.sleep(1)
	r1 = re.findall(r"ISBN:</span> \d{10,}",str(driver.page_source))
	return [isbn.split("ISBN:</span> ")[1] for isbn in r1]

def download_book(isbn, driver):
	driver.get('https://b-ok.cc')
	search=driver.find_element_by_id('searchFieldx')
	search.send_keys(isbn)
	search.submit()
	while 'nothing has been found' not in driver.page_source:
		for elem in driver.find_elements_by_tag_name('h3'):
			if elem.get_attribute("itemprop")=="name":
				elem.find_elements_by_tag_name('a')[0].click()
				break
		else:
			continue
		break
	if 'nothing has been found' in driver.page_source:
		return False
		print(2)
	while len(driver.find_elements_by_class_name('dlButton'))<1:
		time.sleep(1)
		print(1)
	driver.find_elements_by_class_name('dlButton')[0].click()
	time.sleep(5)
	return True


def main():
	with random_driver() as driver:
		while True:
			link=input('Paste the link to the book list or "q" to quit\n(Available in the course description in your Student Portal)\n     ->')
			if link=="q":
				break
			isbns=get_isbn_list(link, driver)
			if len(isbns)>0:
				print(str(len(isbns)) + ' isbn numbers found:')
				for i in range(len(isbns)):
					print('['+str(i+1)+'] '+isbns[i])
					print(('Not ' if not download_book(isbns[i],driver) else '')+'Downloaded.')
			else:
				print('No isbns found. Check the link or report a bug with the link included.')
				continue
		driver.quit()

local_directory=os.getcwd()
main()
