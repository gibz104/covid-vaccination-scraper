import pandas
from html.parser import HTMLParser
from urllib.request import urlopen, urljoin, Request
import re

# GLOBAL VARIABLES
url = 'http://www.usnews.com/news/best-states/articles/covid-19-vaccine-eligibility-by-state'
target_file = "state_vaccine_eligibility.csv"
delimiter = "|"
state_list = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida',
              'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
              'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana',
              'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina',
              'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
              'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
              'Wisconsin', 'Wyoming']


class WebScraper(HTMLParser):
    def __init__(self, url):
        """given a URL will scrape all links and state covid vaccine eligibility text"""
        HTMLParser.__init__(self)
        self.url = url  # store url
        self.HTMLcontent = self.retrieveHTML()  # store contents of HTML content
        self.links = []  # list accumulator for links
        self.site_updated_date = []  # date website was last updated
        self.state_eligibility = {}  # dictionary with current and next phase eligibility by state

    def retrieveHTML(self):
        """when called, will retrieve HTML content from url"""
        user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"  # sets user agent
        request = Request(self.url)  # creates request
        request.add_header("User-Agent", user_agent)  # adds header to request
        content = urlopen(request).read().decode()  # open url and get HTML content
        return content  # return HTML content

    def handle_starttag(self, tag, attrs):
        """extends original function in HTMLParser to look for all ancher tabs and find links as href attributes"""
        if tag == 'a':  # if tag is an anchor tag
            for attr in attrs:  # for each attribute in this anchor tags list of attributes
                if attr[0] == 'href':  # if the attribute is href (attribute that contains hyperlink)
                    absolute = urljoin(self.url, attr[1])  # combines relative reference with original url
                    if absolute[:4] == 'http':  # if link is http
                        if absolute.find('?') != -1:  # chop off specific search queries at end of link (this prevents duplicate pages accessed from different links)
                            absolute = absolute[:absolute.find('?')]  # changes link to exclude search query
                        self.links.append(absolute)  # adds link to list of links created earlier

    def handle_data(self, data):
        """extends original function from HTMLParser to collect text from HTML content"""
        for item in re.findall('"dateModified":"([0-9]{4}-[0-9]{2}-[0-9]{2})T', data.strip()):  # find last update date
            self.site_updated_date.append(item)  # append update date to list
        for state in state_list:  # for each state
            current_phase = re.findall(f"{state} Vaccine Eligibility(?::)?\s?Current Phase(?::)?\s?([\w+\s\.,!\-']+)(?:(?:Next Phase)|(?:More information))", data.strip())  # get current phase eligibility
            next_phase = re.findall(f"{state} Vaccine Eligibility(?::)?\s?Current Phase(?::)?\s?[\w+\s\.,!\-']+\s?Next Phase(?::)?\s?([\w+\s\.,!\-']+)(?:More information)", data.strip())  # get next phase eligibility
            if state not in self.state_eligibility:  # if state is not already included in dict
                self.state_eligibility[state] = {"current_phase": "", "next_Phase": "", "last_update": ""}  # add to dict
            if len(current_phase) > 0:  # if current phase text found
                self.state_eligibility[state]["current_phase"] = current_phase[0]  # add to dict
            if len(next_phase) > 0:  # if next phase text found
                self.state_eligibility[state]["next_phase"] = next_phase[0]  # add to dict
            if len(self.site_updated_date) > 0:  # if site updated was found
                self.state_eligibility[state]["last_update"] = self.site_updated_date[0]  # add to dict

    def getLinks(self):
        """when called, will return a list of links that are contained on the current website"""
        return self.links  # return links list

    def getStateEligibility(self):
        """when called will return a list of all the words/text that are on the current website"""
        df = pandas.DataFrame.from_dict(self.state_eligibility, orient="index", columns=['current_phase', 'next_phase', 'last_update'])  # convert dict to dataframe
        df.index.name = "state"  # name the index of the data frame
        return df  # return the data frame with state eligibility

    def getHTML(self):
        """when called, will return the HTML content frim the url"""
        return self.HTMLcontent


def main():
    """when called, will scrape website and save state vaccine eligibility to csv with specified delimiter"""
    scraper = WebScraper(url)  # create scraper obj
    scraper.feed(scraper.getHTML())  # feed HTML file to scraper obj
    data = scraper.getStateEligibility()  # get state eligibility text
    data.to_csv(target_file, sep=delimiter, quoting=0)  # save dataframe to csv


if __name__ == "__main__":
    main()
