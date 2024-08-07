import re
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScraperObjects:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        attrs = ',\n'.join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}(\n{attrs}\n)"

def post_scrape(driver, posts, post_titles):

    for post in post_titles[len(posts):]:
        post_data = {}
        post_data['title'] = post.find_element(By.TAG_NAME, 'a').get_attribute('title')
        post_data['url'] = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
        posts.append(post_data)

    return posts

def scroll_down_page(driver, scroll_pause_time=1, scroll_increment=400):

    # Get the initial scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down by a certain amount
        driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_increment)

        # Wait to load the page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same, break the loop
            break
        last_height = new_height

def run(scraper_object):

    # Initialize Chrom WebDriver:
    driver = webdriver.Chrome()

    # Intialize ActionChains:
    action = ActionChains(driver)

    # Initialize WebDriverWait:
    wait = WebDriverWait(driver, 30)

    # Load URL:
    driver.get(scraper_object.url)

    # List to store dictionaries of posts {title, url, body}:
    posts = []

    # Post Amount Target:
    n = scraper_object.num_posts

    # Classes:
    post_title_class = scraper_object.post_title_class
    post_body_class = scraper_object.post_body_class
    avoid_class = scraper_object.avoid_class

    # Input Related:
    repeated_input_type = scraper_object.repeated_input_type
    repeated_click_xpath = scraper_object.repeated_click_xpath
    actions = scraper_object.actions

    # Intial Input Actions:
    for action_name, action_selector in actions.items():
        if 'click' in action_name:
            try:
                input = wait.until(EC.element_to_be_clickable((By.XPATH, action_selector)))
                input.click()
            except Exception as e:
                print(f'Error: {e}')
        else:
            try:
                input.send_keys(action_selector)
            except Exception as e:
                print(f'Error: {e}')

    # Repeated Input and Scraping of Post Titles & URLs:
    while len(posts) < n:
        try:
            if repeated_input_type == 'Click':
                try:
                    if avoid_class != None:
                        post_titles = [post for post in driver.find_elements(By.CLASS_NAME, post_title_class) if avoid_class not in post.get_attribute('class')]
                        posts = post_scrape(driver, posts, post_titles)
                        if posts >= n:
                            break
                        else:
                            input = wait.until(EC.element_to_be_clickable((By.XPATH, repeated_click_xpath)))
                            input.click()
                    else:
                        post_titles = [post for post in driver.find_elements(By.CLASS_NAME, post_title_class)]
                        posts = post_scrape(driver, posts, post_titles)
                        if posts >= n:
                            break
                        else:
                            input = wait.until(EC.element_to_be_clickable((By.XPATH, repeated_click_xpath)))
                            input.click()
                except Exception as e:
                    print(f'Error: {e}')
            else:
                try:
                    if avoid_class != None:
                        post_titles = [post for post in driver.find_elements(By.CLASS_NAME, post_title_class) if avoid_class not in post.get_attribute('class')]
                        posts = post_scrape(driver, posts, post_titles)
                        if len(posts) >= n:
                            break
                        else:
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    else:
                        post_titles = [post for post in driver.find_elements(By.CLASS_NAME, post_title_class)]
                        posts = post_scrape(driver, posts, post_titles)
                        if posts >= n:
                            break
                        else:
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                except Exception as e:
                    print(f'Error: {e}')
        except Exception as e:
            print(f'Error: {e}')

    # Fetch Post Bodies:
    for post in posts[:n]:
        try:
            driver.get(post['url'])
            post['body'] = driver.find_element(By.CLASS_NAME, post_body_class).text
        except Exception as e:
            print(f'Error: {e}')

    return posts[:n]
