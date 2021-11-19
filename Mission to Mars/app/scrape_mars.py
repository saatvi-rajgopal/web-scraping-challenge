# Import Splinter, BeautifulSoup, and Pandas

from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():

    # Initiate headless driver for deployment

    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary

    news_data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data

    browser.quit()
    return news_data

# Scrape Mars News

def mars_news(browser):

    # Visit the mars nasa news site

    mars_url = 'https://redplanetscience.com/'
    browser.visit(mars_url)

    # Optional delay for loading the page

    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object

    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling

    try:
        slide_element = news_soup.select_one('div.list_text')

        # Use the parent element to find the first 'a' tag and save it as 'news_title'

        news_title = slide_element.find("div", class_="content_title").get_text()

        # Use the parent element to find the paragraph text

        news_paragraph = slide_element.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_paragraph


def featured_image(browser):

    # Visit space URL

    space_url = 'https://spaceimages-mars.com'
    browser.visit(space_url)

    # Find/click the full image button

    full_image_element = browser.find_by_tag('button')[1]
    full_image_element.click()

    # Parse html results with soup

    html = browser.html
    soup_img = soup(html, 'html.parser')

    # Add try/except for error handling

    try:

        # find the relative image url

        relative_img_url = soup_img.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url

    img_url = f'https://spaceimages-mars.com/{relative_img_url}'

    return img_url


def mars_facts():

    # Add try/except for error handling

    try:

        # use 'read_html' to scrape the facts table into a dataframe

        spacefacts_df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Create defined columns and show new dataframe

    spacefacts_df.columns = ['Description', 'Mars', 'Earth']
    spacefacts_df.set_index('Description', inplace=True)

    # Convert dataframe to html

    return spacefacts_df.to_html(classes="table table-striped")

    # Visit hemisphere URL
def hemispheres(browser):
    hemisphere_url = 'https://marshemispheres.com/'

    browser.visit(hemisphere_url + 'index.html')

    # Click the link, find the sample anchor, return the href

    hemisphere_img_urls = []
    for i in range(4):

        # Find the elements on each loop to avoid a stale element exception

        browser.find_by_css("a.product-item img")[i].click()
        hemisphere_data = scrape_hemisphere(browser.html)
        hemisphere_data['img_url'] = hemisphere_url + hemisphere_data['img_url']
        # Append hemisphere object to list

        hemisphere_img_urls.append(hemisphere_data)

        # Navigate backwards
        
        browser.back()

    return hemisphere_img_urls


def scrape_hemisphere(html_text):

    # parse html text

    hemisphere_soup = soup(html_text, "html.parser")

    # Add try/except for error handling

    try:
        title_element = hemisphere_soup.find("h2", class_="title").get_text()
        sample_element = hemisphere_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error will return None, for better front-end handling

        title_element = None
        sample_element = None

    hemispheres = {
        "title": title_element,
        "img_url": sample_element
    }

    return hemispheres


if __name__ == "__main__":

    # If running as script, print scraped data

    print(scrape_all())
