from pprint import pprint
import psycopg2
from abstract.crawler import AbstractCrawler
from db import psql_db
from crawler.tracks import TracksParser
from models import Setlist, Track_Setlist_Link

#The purpose of this class is to scrape data from a MixesDB setlist url page in order to generate a data
#structure that can be used to seed or update the PostgresSQL database
class SetlistCrawler(AbstractCrawler):
    def __init__(self):
        AbstractCrawler.__init__(self)
        self.no_comments_selector = "not(contains(@class,'commenttextfield'))"
        return

    def crawl(self):
        conn, cursor = psql_db.connect()
        cursor.execute("SELECT * FROM dj")
        dj_rows = cursor.fetchmany(100)
        while len(dj_rows):
            for dj_row in dj_rows:
                self.dj_search_keyphrase = dj_row[1].split("(")[0].strip()
                setlist_urls = self.get_setlist_urls(dj_row[2])
                for setlist_url in setlist_urls:
                    track_texts = self.scrape_setlist_page_for_tracks(setlist_url)
                    track_nodes = self.parse_tracks(track_texts)
            dj_rows = cursor.fetchmany(100)
        self.log_time()

    def get_setlist_urls(self, dj_url):
        while dj_url != False:
            dj_tree = self.get_tree(dj_url)
            scraped_setlist_urls = dj_tree.xpath('//ul[@id="catMixesList"]/li/a/@href')
            more_results_url = dj_tree.xpath("//div[@class='listPagination'][1]/a[contains(text(), 'next')]/@href")
            dj_url = self.base_url + more_results_url[0] if len(more_results_url) else False
        scraped_setlist_urls = list(map(lambda url: self.base_url + url, scraped_setlist_urls))
        return scraped_setlist_urls

    def scrape_setlist_page_for_tracks(self, setlist_url):
        self.setlist_page_tree = self.get_tree(setlist_url)
        headers_xpath = "//dl[parent::div[" + self.no_comments_selector + " and (child::ol or child::div)]]/dt/text()"
        headers_before_tracklist = self.setlist_page_tree.xpath(headers_xpath)
        #If there are headers before tracklists, evaluate whether or not they
        for header in headers_before_tracklist:
            lowercase_header = header.lower()
            if "version" in lowercase_header:
                return self.get_tracks_for_setlist_with_one_dj()
            elif self.dj_search_keyphrase.lower() in lowercase_header:
                return self.get_tracks_for_setlist_with_multiple_djs()
        return self.get_tracks_for_setlist_with_one_dj()

    def parse_tracks(self, track_texts):
        tparser = TracksParser(track_texts)
        tparser.build_tracklist_data()
        return tparser.tracks_info
        # if self.save:
        #     tparser.save_to_db()
        # else:
        #     pprint(tparser.tracks_info)
        # self.track_ids = tparser.setlist_trackids

    def get_tracks_for_setlist_with_one_dj(self):
        track_texts = self.setlist_page_tree.xpath("//ol[parent::*[" + self.no_comments_selector + "]]/li//text()")
        track_texts.extend(self.setlist_page_tree.xpath("//div[parent::*[" + self.no_comments_selector + "] and @class='list']/div[contains(@class, 'list-track')]//text()"))
        return track_texts

    def get_tracks_for_setlist_with_multiple_djs(self):
        '''TODO: not working for DJ's with apostrophes/single quotes in name due to xpath'''
        belongs_to_dj_selector = "preceding-sibling::*[1]/dt[contains(text(), '" + self.dj_search_keyphrase + "')]"
        tracklist_condition = self.no_comments_selector + "] and " + belongs_to_dj_selector
        if not "'" in self.dj_search_keyphrase:
            track_texts = self.setlist_page_tree.xpath("//ol[parent::*[" + tracklist_condition + "]/li//text()")
            track_texts.extend(self.setlist_page_tree.xpath("//div[parent::*[" + tracklist_condition + " and @class='list']/div[contains(@class, 'list-track')]//text()"))
        # pprint(self.track_texts)
        return track_texts

    def get_page_mod_time(self):
        page_mod_time = self.tree.xpath("//li[@id='lastmod']/text()") #should be using PHP API to get the eexact
        if len(page_mod_time) > 1:
            page_mod_time = page_mod_time[1].strip()
        elif  len(page_mod_time) == 1:
            page_mod_time = page_mod_time[0]
        else:
            page_mod_time = "2010 Jan 1"
        return page_mod_time
