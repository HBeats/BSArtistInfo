#!/usr/bin/python3
# BSArtistInfo.py - Allows pasting of db page, will extract
# artist name and url and output hyperlinks

import urllib.request
from bs4 import BeautifulSoup   
import pyperclip
import sys  # Used for closing the window when quit is called
import pygame  # Used for playing sound
import os  # Used for finding the music
import re  # Used for finding the digits to be used in start and end count

list_of_links = []
start_count = 0
count = start_count
post_count = start_count
want_count = 10
intro_done = False
no_small = False
list_of_unfiltered_links = []  # raw db links
list_of_filtered_links = []  # filtered, specific links
available_sites = ["twitter", "pixiv", "nicovideo", "deviantart"]

test_pix = "http://danbooru.donmai.us/posts/2436830"
test_twit = "http://danbooru.donmai.us/posts/2445622"
test_tumblr = "http://danbooru.donmai.us/posts/2439983?tags=slugbox"
test_nico = "http://danbooru.donmai.us/posts/2372797"
test_da = "http://danbooru.donmai.us/posts/2452709?tags=oxykoma"
hyperlink = '<a href="{link}">{text}</a><br>\n'

output = '<p><h2></h2>\n<blockquote><div><b></b><br>\n<a href="hntaibeatx.tumblr.com/">Click here for more hentai! Feel free to request for sets like this one!</a></div></blockquote>\nSources!<br>\n'

pygame.mixer.init()
music = os.path.join("resources", "tuturu.mp3")

def intro():
    global intro_done
    global want_count
    global start_count
    global output
    global no_small
    if intro_done is False:
        print("Enter a link, or type done for output")
        intro_done = True
        intro()
    elif intro_done is True:
        choice = input(">")
        if "paste" in choice:
            choice = pyperclip.paste()  # Expects a link or "done"
            check_choice(choice)
            intro()
        elif choice == "test":
            choice = test_pix
            check_choice(choice)
            intro()
        elif choice == "twitter test":
            choice = test_twit
            check_choice(choice)
            intro()
        elif choice == "nico test": 
            choice = test_nico
            check_choice(choice)
            intro()
        elif choice == "da test":
            choice = test_da
            check_choice(choice)
            intro()
        elif choice == "tumblr test":
            choice = test_tumblr
            check_choice(choice)
            intro()
        elif choice == "clear":
            intro()
        elif choice == "num":
            print(count)
            intro()
        elif choice == "check":
            print(pyperclip.paste())
            intro()
        elif "end" in choice:
            mo = re.search(r"\d+", choice)
            mo = mo.group()
            want_count = int(mo)
            print("Changed count to " + str(want_count))
            intro()
        elif "start" in choice:
            mo = re.search(r"\d+", choice)
            mo = mo.group()
            start_count = int(mo) - 1
            print("Changed starting count to " + str(start_count + 1))
            update_count()
            output = ""
            no_small = True
            intro()
        elif choice == "exit" or choice == "quit":
            sys.exit()
        else:
            check_choice(choice)

def update_count():
    global post_count
    global count
    global start_count
    count = start_count
    post_count = start_count

def check_choice(choice):  # Checks if input is a link or not
    global count
    if "danbooru" in choice:
        if choice not in list_of_unfiltered_links:
            list_of_unfiltered_links.append(choice)
            count += 1
            print("Added post #" + str(count), choice)
            if count == want_count:
                filter_links(list_of_unfiltered_links)
            else:
                intro()
        elif choice in list_of_unfiltered_links:
            print("Please enter a new link")
            intro()
    elif "done" in choice:
        filter_links(list_of_unfiltered_links)
    else:
        print("Please enter a proper link")
        intro()

def play_notif():
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(0, 0.0)

def filter_links(unfiltered_links):  # For db links only
    global post_count
    global list_of_unfiltered_links
    for i in unfiltered_links:  # Gets the BS url so it can be checked
        soup = get_bs_link(i)
        raw_link = soup.find("section", attrs = {"id": "post-information"})
        list_of_links = raw_link.select("li > a")
        if "tumblr" in str(list_of_links) or "tmblr" in str(list_of_links):
            post_count += 1
            print("Warning! Post " + str(post_count) + " is a tumblr page!")
            sys.exit(0)
        if "pixiv.net" in str(list_of_links) or "twitter.com" in str(list_of_links) or "nicovideo" in str(list_of_links) \
            or "deviantart" in str(list_of_links):
            for link in list_of_links:
                str_link = str(link)
                if "pixiv.net/" in str_link:
                    post_count += 1
                    get_pixiv_info(str_link, post_count)
                elif "twitter" in str_link:
                    post_count += 1
                    get_twitter_info(str_link, post_count)
                elif "nicovideo" in str_link:
                    post_count += 1
                    get_nico_info(str_link, post_count)
                elif "deviantart" in str_link:
                    post_count += 1
                    get_da_info(str_link, post_count)
        else:
            post_count += 1
            insert_url(post_count)


def insert_url(link_count):
    if post_count == len(list_of_unfiltered_links):
        play_notif()

    global output
    print("Post " + str(post_count) + " has no url.")
    hyper =  '<a href = "">{text}</a><br>\n'
    output = output + hyper.format(text = "[ " + str(link_count) + " -- " + " ]")
    check_done()

def get_bs_link(link):  # Will return a BeautifulSoup url
    try:
        with urllib.request.urlopen(link) as url:
            return BeautifulSoup(url, "html.parser")
    except urllib.error.HTTPError:
        print("Error with url of post", post_count)



def get_pixiv_info(link, link_count):
    if post_count == len(list_of_unfiltered_links):
        play_notif()

    global output
    global hyperlink
    try :
        link_end_index = link.index("\">")
        link_start_index = link.index("\"") + 1
        pix_link = link[link_start_index: link_end_index]  # gets url
        pix_bs = get_bs_link(pix_link)  # goes to the pix site
        name = pix_bs.find("div", attrs={"class": "userdata"}).select("h1")
        str_name = str(name)
        name_end_index = str_name.index("</h1>")
        name_start_index = str_name.index(">") + 1
        pix_name = str_name[name_start_index: name_end_index]  # gets the art name
        artist = pix_bs.find("div", attrs={"class": "userdata"}).select("a")
        str_artist = str(artist)
        artist_end_index = str_artist.index("</a>")
        artist_start_index = str_artist.index(">") + 1
    except (ValueError, AttributeError):
        print("Post " + str(post_count) + " has missing info")
        insert_url(post_count)
    else :
        pix_artist = str_artist[artist_start_index: artist_end_index]
        pix_info = "[ " + str(link_count) + " -- " + pix_name + " by " + pix_artist + " on pixiv" + " ]"
        hyper = hyperlink.format(link=pix_link, text=pix_info)
        output = output + hyper
        check_done()


def get_da_info(link, link_count):
    if post_count == len(list_of_unfiltered_links):
        play_notif()
    try:
        global output
        global hyperlink
        link_end_index = link.index("\">")
        link_start_index = link.index("\"") + 1
        da_link = str(link[link_start_index: link_end_index])
        artist_end_index = link.index(".deviantart")
        artist_start_index = link.index("//") + 2
        artist = str(link[artist_start_index: artist_end_index])
    except (ValueError, AttributeError):
        print("Post " + str(post_count) + " has missing info")
        insert_url(post_count)
    else:
        da_info = "[ " + str(link_count) + " -- " + artist + " on deviantart ]"
        hyper = hyperlink.format(link=da_link, text = da_info)
        output = output + hyper
        check_done()


def get_twitter_info(link, link_count):
    if post_count == len(list_of_unfiltered_links):
        play_notif()
    try:
        global output
        global hyperlink
        link_end_index = link.index("\">")
        link_start_index = link.index("\"") + 1
        twit_link = link[link_start_index: link_end_index]  # gets url
        twit_bs = get_bs_link(twit_link)  # goes to twit site
        artist = twit_bs.find("span", attrs={"class": "username js-action-profile-name"})
        str_artist = str(artist)
        artist_end_index = str_artist.index("</b>")
        artist_start_index = str_artist.index("<b>") + 3
    except (ValueError, AttributeError):
        print("Post " + str(post_count) + " has missing info")
        insert_url(post_count)
    else:
        twit_artist = str_artist[artist_start_index: artist_end_index]
        twit_info = "[ " + str(link_count) + " -- " + twit_artist + " on twitter" + " ]"
        hyper = hyperlink.format(link=twit_link, text=twit_info)
        output = output + hyper
        check_done()

def get_nico_info(link, link_count):
    if post_count == len(list_of_unfiltered_links):
        play_notif()
    try:
        global output
        global hyperlink
        link_end_index = link.index("\">")
        link_start_index = link.index("\"") + 1
        nico_link = link[link_start_index: link_end_index]
        nico_bs = get_bs_link(nico_link)
        artist = nico_bs.find("div", attrs={"class": "lg_txt_illust"}).select("strong")
        str_artist = str(artist)
        artist_end_index = str_artist.index("</strong>")
        artist_start_index = str_artist.index(">") + 1
    except (ValueError, AttributeError):
        print("Post " + str(post_count) + " has missing info")
        insert_url(post_count)
    else:
        nico_artist = str_artist[artist_start_index: artist_end_index]
        nico_info = "[ " + str(link_count) + " -- " + nico_artist + " on nicovideo" + " ]"
        hyper = hyperlink.format(link=nico_link, text=nico_info)
        output = output + hyper
        check_done()

def check_done():
    global post_count
    global count
    global output
    if post_count == count:
        if no_small == False:
            output = output + "<small>Set  on the blog</small></p>"
        pyperclip.copy(output)
        print("Done!")
        sys.exit(0)
    else:
        pass



intro()