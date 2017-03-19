#!/usr/bin/python3
from bs4 import BeautifulSoup
import pyperclip
import sys
import pygame
import os
import re
import grequests	
import requests

"""Test links for debugging"""
test_pixiv = "http://danbooru.donmai.us/posts/2436830"
test_twit = "http://danbooru.donmai.us/posts/2445622"
test_tumblr = "http://danbooru.donmai.us/posts/2439983?tags=slugbox"
test_nico = "http://danbooru.donmai.us/posts/2372797"
test_da = "http://danbooru.donmai.us/posts/2452709?tags=oxykoma"
test_blank = "http://danbooru.donmai.us/posts/2314172"
test_all = [
			"http://danbooru.donmai.us/posts/2436830",
			"http://danbooru.donmai.us/posts/2445622",
			"http://danbooru.donmai.us/posts/2439983?tags=slugbox",
			"http://danbooru.donmai.us/posts/2372797",
			"http://danbooru.donmai.us/posts/2452709?tags=oxykoma",
			"http://danbooru.donmai.us/posts/2314172"
			]

"""Text files to writing to and from"""

class example:
	def __init__(self):
		self.db_links = []
		self.link_count = 0
		self.total_count = 10
		self.available_sites = ["pixiv", "twitter", "deviantart", "nicovideo"]
		self.hyperlink = '<a href="{link}">{text}</a><br>\n'
		self.output = '<p><h2></h2>\n<blockquote><div><b></b><br>\n<a href="hentaibeatx.tumblr.com/">Click here for more hentai! Requests open!</a></div></blockquote>\nSources!<br>\n'
		print("Enter a link, or type done for output.")
		print("Type help for list of commands")

	def console(user_cmd = ""):
		"""
		Console acts as the UI and filters the user's input. 

		Parameters:
		user_cmd - What the user wants to do. Default blank string.
		"""
		pass

	def check_link(self, link):
		"""
		check_link checks a link if it's a db link, then converts the link.
		
		Parameters: 
		link - The link to be checked
		"""
		if "danbooru" in link and link not in self.db_links:
			self.db_links.append(link)
			self.link_count += 1
			print("Added post #{} {}".format(self.link_count, link))
		else: print("Please enter a new link.")
		if self.link_count == self.total_count:
			self.filter_db_links(self.db_links)
			#filter links here, get bs url, then segregate to respective
			#get_site_url 

	def filter_db_links(self, db_links_list):
		"""
		filter_db_links takes a list of db links and filters them.
		It finds the site url using the BeautifulSoup of the db link
		Then filters the links to their respective functions.

		Parameters:
		db_links_list - To ensure that link_count == total_count, takes a parameter instead of accessing the list instance
		"""
		skip_count = 0  # experimental. if this increments, keep filtering db links
		post_count = 0
		requests = grequests.map(grequests.get(link) for link in db_links_list)  # gets all the links so faster
		for request in requests:
			soup = BeautifulSoup(request.content, "lxml")
			# Save danbooru artist name in case of error
			artist = soup.find("section", attrs={"id": "tag-list"})
			artist = artist.find("a", attrs={"itemprop": "author"}).text
			post_info = soup.find("section", attrs = {"id": "post-information"})
			link_list = post_info.select("li > a")
			site_link = link_list[-1]["href"]
			if "tumblr" in site_link or "tmblr" in site_link:
				print("Warning! Post {} is a tumblr post.".format(post_count + 1))
				print("Replacing Post {}".format(post_count + 1))
				pass
			elif "pixiv.net/" in site_link:
				post_count += 1
				self.get_pixiv_info(site_link, post_count, artist)
			elif "twitter" in site_link:
				post_count += 1
				self.get_default_info(site_link, post_count, artist, "Twitter")
			elif "nicovideo" in site_link:
				post_count += 1
				self.get_default_info(site_link, post_count, artist, "NicoVideo")
			elif "deviantart" in site_link:
				post_count += 1
				self.get_default_info(site_link, post_count, artist, "DeviantArt")
			else:
				post_count += 1
				self.get_default_info("", post_count, artist)

	def get_bs_link(self, link):  
		"""Gets the BeautifulSoup of the passed link"""
		result = requests.get(link)
		result = result.content
		return BeautifulSoup(result, "html.parser")

	def get_pixiv_info(self, link, post_count, default_artist):
		if post_count == len(self.db_links):
			pass  # play notif
		try:
			pix_bs = self.get_bs_link(link)
			"""Getting the title"""
			title = str(pix_bs.find("div", attrs={"class": "userdata"}).select("h1"))
			title_start = title.index(">") + 1
			title_end = title.index("</h1>")
			title = title[title_start: title_end]
			""""""
			"""Getting the artist"""
			artist = str(pix_bs.find("div", attrs={"class": "userdata"}).select("a"))
			artist_start = artist.index(">") + 1
			artist_end = artist.index("</a>")
			artist = artist[artist_start: artist_end]
			""""""
			info = "[{} -- {} by {} on Pixiv]".format(post_count, title, artist)
			hyper = self.hyperlink.format(link = link, text = info)
			self.output += hyper
			print("Done with post {}".format(post_count))
		except (ValueError, AttributeError) as e:  # occurs when page not found
			print("Error on post #{}".format(post_count))
			get_default_info(self, post_count, default_artist, "Pixiv")

	def get_default_info(self, link, post_count, default_artist, platform=""):
		if platform == "":
			info = "[{} -- Art by {}]".format(post_count, default_artist)
		else:
			info = "[{} -- Art by {} on {}]".format(post_count, default_artist, platform)
		hyper = self.hyperlink.format(link = link, text = info)
		self.output += hyper
		
	def set_total_count(self, new_total_count):
		self.total_count = new_total_count
		print("Changed total count to %d" % new_total_count)

	def dbg_db_links(self):
		"""Debugging: Prints the db_links list"""
		print(self.db_links)

	def dbg_link_count(self):
		"""Debugging: Prints the link_count"""
		print(self.link_count)

	def dbg_done(self):
		"""Debugging: Done posting links before reaching total_count"""
		self.filter_db_link(self.db_links)

	def dbg_output(self):
		"""Debugging: Print the output html"""
		print(self.output)

if __name__ == '__main__':
	e = example()
	e.set_total_count(len(test_all))

	for link in test_all:
		e.check_link(link)
	e.dbg_output()
	# e.set_total_count(2)
	# e.check_link(test_pixiv)
	# e.check_link(test_twit)
	