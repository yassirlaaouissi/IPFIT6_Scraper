## Made by Yassir Laaouissi || 01-10-2020 ##
import os
import twint
import csv
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from translate import Translator
from datetime import datetime
from item import Item
import json
from gmaps_scraper import scraper, settings

#####
#####
#####
#####   TWITTER
#####
#####   It is kinda broken, no time to fix
#####

def twitter():

    total_tweets = []
    inputfile = open("Zoektermen/keywords_base - Copy.txt", "r")
    for word in inputfile:
        word = word.replace("\n", "")
        print('\33[33m' + "Het woord is nu: " + word + '\33[0m')
        if "amsterdam" in word:
            c = twint.Config()
            c.Search = str(word)
            c.Profile_full = True

            # use this for initialscrape
            c.Since = "2020-01-01 00:00:01"
            c.Until = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.Store_object = True
            c.Limit = 1
            twint.run.Search(c)
            tlist = c.search_tweet_list
            total_tweets.append(tlist)

        else:
            c = twint.Config()
            c.Search = str(word)
            c.Geo = "52.378909,4.900244,25km"

            # use this for initialscrape
            c.Since = "2020-01-01 00:00:01"
            c.Until = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.Store_object = True
            c.Limit = 1
            c.Profile_full = True
            twint.run.Search(c)
            tlist = c.search_tweet_list
            total_tweets.append(tlist)


    #print(total_tweets)
    filename_json = f"Output/Twitter/Export_" + datetime.now().strftime("%Y-%m-%d--%H-%M") + ".json"
    file = open(filename_json, 'w')
    json.dump(total_tweets, file)


#####
#####
#####
#####   MARKTPLAATS
#####
#####
#####

def translate(textoToTranslate):
    translator = Translator(from_lang="dutch", to_lang="english")
    translation = translator.translate(textoToTranslate)
    return translation


def writetocsv(items, csvfilename):
    csv_file = open(csvfilename, 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Title', 'URL', 'Price', 'Summary', 'Seller name', 'Seller location', 'Seller link'])
    for item in items:
        csv_writer.writerow([item.title, item.url, item.price, item.summary, item.seller_name, item.seller_location, item.seller_link])
    csv_file.close()


def convert_csv_to_xsl(csvfilename, xlsxfilename):
    wb = Workbook()
    ws = wb.active

    with open(csvfilename, 'r') as f:
        for row in csv.reader(f):
            ws.append(row)
    wb.save(xlsxfilename)


def is_correct_response(response):
    """Check that the response returned 'success'"""
    return response == 'success'


def is_defined_item(element):
    if element is not None:
        return element
    else:
        return "not Available"



def marktplaats():
    inputfile = open("Zoektermen/keywords_base - Copy.txt", "r")
    wordlist = []

    for phrase in inputfile:
        phrase = phrase.replace("\n", "")
        wordlist.append(phrase)
    for word in wordlist:
        if "amsterdam" in word:
            #print("amsterdam")
            query = word
            url = 'https://www.marktplaats.nl/q/' + query + '/'
            print(str(url))
            source = requests.get(url)
            #print(source)
            marktplaats = BeautifulSoup(source.text, 'lxml')
            # body = marktplaats.find('div', class_='mp-Page-element--main')
            body = marktplaats.find('body')
            search_result = is_defined_item(body.find('ul', class_='mp-Listings--list-view'))
            # print(search_result)
            listOfArticles = []
            listOfArticles = []
            try:
                for article in search_result:
                    try:
                        # advertentieinformatie
                        title = is_defined_item(article.find('h3', class_="mp-Listing-title")).text
                        # print(title)

                        href1 = article.a['href']
                        href = "https://www.marktplaats.nl" + href1

                        summary_ = is_defined_item(article.find('p', class_='mp-text-paragraph')).text
                        # print(summary_)

                        price = is_defined_item(article.find('span', class_='mp-text-price-label')).text
                        price = price.replace("\xc2\xa0", " ")
                        # print(price)

                        # seller informatie
                        seller_name = is_defined_item(article.find('span', class_='mp-Listing-seller-name')).text
                        # print(seller_name)

                        seller_location = is_defined_item(article.find('span', class_='mp-Listing-location')).text
                        # print(seller_location)

                        seller_link = is_defined_item(article.find('a', class_='mp-TextLink'))['href']
                        if "/u/" in seller_link:
                            def_seller_link = "https://www.marktplaats.nl" + seller_link
                        else:
                            def_seller_link = seller_link

                        # ff al die advertentieinfo wegschrijven naar een object
                        myObj = Item()
                        myObj.title = title.encode("utf-8").strip()
                        myObj.url = href.encode("utf-8").strip()
                        myObj.price = price.encode("utf-8").strip()
                        myObj.summary = summary_.encode("utf-8").strip()
                        myObj.seller_name = seller_name.encode("utf-8").strip()
                        myObj.seller_location = seller_location.encode("utf-8").strip()
                        myObj.seller_link = def_seller_link.encode("utf-8").strip()
                        listOfArticles.append(myObj)
                    except Exception as e:
                        summary_ = "None"
                        title_ = "None"
                        href = "None"
                        price = "None"
                        seller_name = "None"
                        seller_location = "None"
                        seller_link = "None"
                        print(e)
            except Exception as e:
                print(e)

            timeofnow = datetime.now().strftime(f"%Y-%m-%d--%H-%M")
            smallertimeofnow = datetime.now().strftime(f"%Y-%m-%d")
            if not os.path.exists(f"Output/Marktplaats/{smallertimeofnow}"):
                os.mkdir(f"Output/Marktplaats/{smallertimeofnow}")
            csvfilename = f"Output/Marktplaats/{smallertimeofnow}/{word}_MP_{timeofnow}.csv"
            xlsxfilename = f"Output/Marktplaats/{smallertimeofnow}/{word}_MP_{timeofnow}.xlsx"
            writetocsv(listOfArticles, csvfilename)
            convert_csv_to_xsl(csvfilename, xlsxfilename)
        else:
            #print("not amsterdam")
            query = word
            postalcode = '1011ab'
            distance = '20000'

            url = 'https://www.marktplaats.nl/q/' + query + '/'
            url += '#distanceMeters:' + distance
            url += '|postcode:' + postalcode
            print(url)
            source = requests.get(url)
            #print(source)
            marktplaats = BeautifulSoup(source.text, 'lxml')
            # body = marktplaats.find('div', class_='mp-Page-element--main')
            body = marktplaats.find('body')
            search_result = is_defined_item(body.find('ul', class_='mp-Listings--list-view'))
            # print(search_result)
            listOfArticles = []
            try:
                for article in search_result:
                    try:
                        # advertentieinformatie
                        title = is_defined_item(article.find('h3', class_="mp-Listing-title")).text
                        # print(title)

                        href1 = article.a['href']
                        href = "https://www.marktplaats.nl" + href1

                        summary_ = is_defined_item(article.find('p', class_='mp-text-paragraph')).text
                        # print(summary_)

                        price = is_defined_item(article.find('span', class_='mp-text-price-label')).text
                        price = price.replace("\xc2\xa0", " ")
                        # print(price)

                        # seller informatie
                        seller_name = is_defined_item(article.find('span', class_='mp-Listing-seller-name')).text
                        # print(seller_name)

                        seller_location = is_defined_item(article.find('span', class_='mp-Listing-location')).text
                        # print(seller_location)

                        seller_link = is_defined_item(article.find('a', class_='mp-TextLink'))['href']
                        if "/u/" in seller_link:
                            def_seller_link = "https://www.marktplaats.nl" + seller_link
                        else:
                            def_seller_link = seller_link

                        # ff al die advertentieinfo wegschrijven naar een object
                        myObj = Item()
                        myObj.title = title.encode("utf-8").strip()
                        myObj.url = href.encode("utf-8").strip()
                        myObj.price = price.encode("utf-8").strip()
                        myObj.summary = summary_.encode("utf-8").strip()
                        myObj.seller_name = seller_name.encode("utf-8").strip()
                        myObj.seller_location = seller_location.encode("utf-8").strip()
                        myObj.seller_link = def_seller_link.encode("utf-8").strip()
                        listOfArticles.append(myObj)
                    except Exception as e:
                        summary_ = "None"
                        title_ = "None"
                        href = "None"
                        price = "None"
                        seller_name = "None"
                        seller_location = "None"
                        seller_link = "None"
                        print(e)
            except Exception as e:
                print(e)

            timeofnow = datetime.now().strftime(f"%Y-%m-%d--%H-%M")
            smallertimeofnow = datetime.now().strftime(f"%Y-%m-%d")
            if not os.path.exists(f"Output/Marktplaats/{smallertimeofnow}"):
                os.mkdir(f"Output/Marktplaats/{smallertimeofnow}")
            csvfilename = f"Output/Marktplaats/{smallertimeofnow}/{word}_MP_{timeofnow}.csv"
            xlsxfilename = f"Output/Marktplaats/{smallertimeofnow}/{word}_MP_{timeofnow}.xlsx"
            writetocsv(listOfArticles, csvfilename)
            convert_csv_to_xsl(csvfilename, xlsxfilename)

#####
#####
#####
#####   INSTAGRAM
#####
#####
#####

def instagram():
    inputfile = open("Zoektermen/keywords_base - Copy.txt", "r")
    wordlist = []
    for phrase in inputfile:
        phrase = phrase.replace("\n", "")
        wordlist.append(phrase)

    timeofnow = datetime.now().strftime(f"%Y-%m-%d--%H-%M")
    for word in wordlist:
        os.system(f'instagram-scraper -u="studenthsleiden" -p="Rolstoel31" --tag "{word}" --include-location --maximum 30 --comments --profile-metadata -d Output/Instagram/{timeofnow}/{word}')


#####
#####
#####
#####   GOOGLE MAPS
#####
#####
#####

def google_maps():
    inputfile = open("Zoektermen/keywords_base - Copy.txt", "r")
    #inputfile = open("Zoektermen/yeet.txt", "r")
    for word in inputfile:
        #print(word)
        word = word.replace("\n", "")
        settings.SETTINGS['BASE_QUERY'].append(str(word))
    scraper.scrape()


#####
#####
#####
#####   THE MAIN
#####
#####
#####

def main():
    ## Welcome message
    r = requests.get(f'http://artii.herokuapp.com/make?text={"Welcome  to  N2O - Scraper ! ! !"}')
    print('\33[33m' + r.text + '\33[0m' + "\n\n")

    ##keuze voor welke platformen gescraped moeten worden en gelijk checken of die platforms wel gescraped kunnen worden.
    WhatToScrape = input("What platforms do you want scraped? (Options and input structure: twitter, marktplaats, instagram, google maps): ")
    Platforms = ["twitter", "marktplaats", "instagram", "google maps"]
    x = WhatToScrape.split(", ")
    for SelectedPlatform in x:
        if not SelectedPlatform in Platforms:
            print('\33[31m' +"\nOne or more platforms you have given up are not available for scraping in this tool. Please try again with the available platforms." + '\33[0m')
            exit(-1)

    #De scrapers runnen op basis van SelectedPlatform in x
    for SelectedPlatform in x:
        if SelectedPlatform == "twitter":
            print('\33[33m' + "\nStarting twitter scraper" + '\33[0m')
            twitter()
        elif SelectedPlatform == "marktplaats":
            print('\33[33m' + "\nStarting marktplaats scraper" + '\33[0m')
            marktplaats()
        elif SelectedPlatform == "instagram":
            print('\33[33m' + "\nStarting instagram scraper" + '\33[0m')
            instagram()
        elif SelectedPlatform == "google maps":
            print('\33[33m' + "\nStarting google maps scraper" + '\33[0m')
            google_maps()

if __name__ == "__main__":
    main()




