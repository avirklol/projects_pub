import re
import time
import random
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScraperObject:
    def __init__(self, **kwargs: dict):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        attrs = ',\n'.join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}(\n{attrs}\n)"



def run(scraper_object, num_posts) -> list:

    # Initialize Chrom WebDriver:
    driver = webdriver.Chrome()

    # Intialize ActionChains:
    action = ActionChains(driver)

    # Initialize WebDriverWait:
    wait = WebDriverWait(driver, 30)

    # Load URL:
    driver.get(scraper_object.url)

    # List to store dictionaries of post title & URL data {title, url}:
    post_titles = []

    # List to store dictionaries of complete post data {title, url, body}:
    posts = []

    # Post Amount Target:
    n = num_posts

    # Classes:
    post_title_class = scraper_object.post_title_class
    post_body_class = scraper_object.post_body_class
    avoid_class = scraper_object.avoid_class

    # Input Related:
    actions = scraper_object.actions
    repeated_input_type = scraper_object.repeated_input_type
    repeated_click_xpath = scraper_object.repeated_click_xpath
    paginated = scraper_object.paginated

    # NESTED FUNCTIONS BEGIN

    # Sroll Page Function:
    def scroll_down_page(scroll_pause_time=1, scroll_increment=400):

        # Get the initial scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down by a certain amount
            try:
                driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_increment)

                # Wait to load the page
                time.sleep(scroll_pause_time)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # If heights are the same, break the loop
                    break
                last_height = new_height
            except Exception as e:
                print(f'Error: {e}')
                os.system('say "Error occured during scrolling."')
                sys.exit(1)

    # Post Title & URL Scrape Function:
    def post_scrape() -> list:

        nonlocal post_titles, posts

        if avoid_class != None:
            post_titles = [post for post in driver.find_elements(By.CLASS_NAME, post_title_class) if avoid_class not in post.get_attribute('class')]
        else:
            post_titles = [post for post in driver.find_elements(By.CLASS_NAME, post_title_class)]

        def scrape(post_titles):

            nonlocal posts

            for post in post_titles:
                post_data = {}
                title = post.find_element(By.TAG_NAME, 'a').get_attribute('title')
                if title != '':
                    post_data['title'] = title
                else:
                    post_data['title'] = post.find_element(By.TAG_NAME, 'a').text
                post_data['url'] = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
                posts.append(post_data)

            return posts

        if paginated:
            posts = scrape(post_titles)
        else:
            posts = scrape(post_titles[len(posts):])

        return posts

    # NESTED FUNCTIONS END

    # Intial Input Actions:
    if bool(actions):
        for action_name, action_selector in actions.items():
            if 'click' in action_name:
                try:
                    input = wait.until(EC.element_to_be_clickable((By.XPATH, action_selector)))
                    input.click()
                except Exception as e:
                    print(f'Error: {e}')
                    os.system('say "Error occured during initial input actions."')
                    sys.exit(1)
            else:
                try:
                    input.send_keys(action_selector)
                except Exception as e:
                    print(f'Error: {e}')
                    os.system('say "Error occured during initial input actions."')
                    sys.exit(1)

    # Repeated Input and Scraping of Post Titles & URLs:
    while len(posts) < n:
        try:
            if repeated_input_type == 'Click':
                try:
                    posts = post_scrape()
                    if len(posts) >= n:
                        break
                    else:
                        input = wait.until(EC.element_to_be_clickable((By.XPATH, repeated_click_xpath)))
                        input.click()
                except Exception as e:
                    print(f'Error: {e}')
                    os.system('say "Error occured during repeated input actions."')
                    sys.exit(1)

            else:
                try:
                    posts = post_scrape()
                    if len(posts) >= n:
                        break
                    else:
                        scroll_down_page()
                except Exception as e:
                    print(f'Error: {e}')
                    os.system('say "Error occured during repeated input actions."')
                    sys.exit(1)
        except Exception as e:
            print(f'Error: {e}')
            os.system('say "Error occured during repeated input actions."')
            sys.exit(1)

    # Fetch Post Bodies:
    for post in posts[:n]:
        try:
            driver.get(post['url'])
            post['body'] = driver.find_element(By.CLASS_NAME, post_body_class).text
        except Exception as e:
            print(f'Error: {e}')
            os.system('say "Error occured during post body fetch."')
            sys.exit(1)

    os.system('say "Scraping complete, ready for L L M filtering."')
    return posts[:n]
