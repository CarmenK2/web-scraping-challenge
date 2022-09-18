from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    Output_H, Output_P = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": Output_H,
        "news_paragraph": Output_P,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'Output_H'
        Output_H = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        Output_P = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return Output_H, Output_P



def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    button = browser.find_by_tag('button')[1]
    button.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # find the relative image url
         areas_to_search_image=soup.find('a',class_='showimg fancybox-thumbs')
         href=areas_to_search_image['href']


    except AttributeError:
        return None
    
     # Use the base url to create an absolute url
    image_url = f'https://spaceimages-mars.com/{href}'

    return image_url


def mars_facts():
    # Add try/except for error handling
    try:
        # use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Give the new table name 
    Mars_Earth_comparision_df=df[0]
    #Take the first row to be the new header
    new_header =Mars_Earth_comparision_df.iloc[0]
    #Take the data less the header row
    MARS_EARTH_df=Mars_Earth_comparision_df[1:]
    #Set the header row as the df header
    MARS_EARTH_df.columns=new_header

  

    # Convert dataframe into HTML format, add bootstrap
    return MARS_EARTH_df.to_html(classes="table table-striped")


def hemispheres(browser):
    url_hem = 'https://marshemispheres.com/'

    browser.visit(url_hem + 'index.html')

    hemisphere_count =browser.find_by_css('a.product-item img')

    hemisphere_image_urls=[]

    for count in range(len(hemisphere_count)):
        #create a dictionary to hold the all the data output
        hemisphere={}

        #Look for the image, then click the image to get the sample image and the link
        browser.find_by_css('a.product-item img')[count].click()

        #Look for the Sample image and get the link
        sample_link=browser.links.find_by_text('Sample').first
        hemisphere['img_url']=sample_link['href']

         #Look for the title
        hemisphere['title']=browser.find_by_css('h2.title').text

        #append result to the list
        hemisphere_image_urls.append(hemisphere)

        #get the broswer to go back and repeat step above
        browser.back()

    return hemisphere_image_urls



def scrape_hemisphere(html_text):
    # parse html text
    hemi_soup = soup(html_text, "html.parser")

    # adding try/except for error handling
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:
        # Image error will return None, for better front-end handling
        title_elem = None
        sample_elem = None

    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemispheres


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())


