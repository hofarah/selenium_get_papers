import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import numpy as np
from selenium.common.exceptions import NoSuchElementException


def check_exists(dr, by, value):
    try:
        dr.find_element(by, value)
    except NoSuchElementException:
        return False
    return True


def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    return webdriver.Chrome('chromedriver', options=chrome_options)


def fetch_data(dr, name, url):
    wait = WebDriverWait(driver, 20)
    dr.get(url)
    related_topics = wait.until(EC.presence_of_element_located((By.ID, 'gsc_prf_int')))
    docs = wait.until(EC.presence_of_element_located((By.ID, 'gsc_a_b')))
    show_more_button = wait.until(EC.presence_of_element_located((By.ID, 'gsc_bpf_more')))

    while not show_more_button.get_property('disabled'):
        show_more_button.click()
        show_more_button = wait.until(EC.presence_of_element_located((By.ID, 'gsc_bpf_more')))
        time.sleep(1)

    user_categories = []
    all_children_by_css = related_topics.find_elements(By.CSS_SELECTOR, '*')
    for i in all_children_by_css:
        user_categories.append(i.text)

    doc_names = []
    doc_urls = []
    all_docs_children_by_css = docs.find_elements(By.TAG_NAME, 'tr')
    for i in all_docs_children_by_css:
        child_wait = WebDriverWait(i, 20)
        doc_details = child_wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        doc_names.append(doc_details.text)
        doc_urls.append(doc_details.get_property('href'))

    doc_descriptions = []

    for i in tqdm(range(len(doc_urls))):
        dr.get(doc_urls[i])
        if check_exists(dr, By.CLASS_NAME, 'gsh_csp'):
            description = dr.find_element(By.CLASS_NAME, 'gsh_csp')
            doc_descriptions.append(description.text)

        if check_exists(dr, By.CLASS_NAME, 'gsh_small'):
            description = dr.find_element(By.CLASS_NAME, 'gsh_small')
            doc_descriptions.append(description.text)
    dataset = [[] for _ in range(len(doc_names))]
    for i in range(len(doc_names)):
        dataset[i].append(doc_names[i])
        dataset[i].append(doc_names[i]+" "+doc_names[i]+" "+doc_descriptions[i])
    os.mkdir('./Data/'+name)
    np.save('./Data/' + name + '/dataset.npy', dataset)
    np.save('./Data/' + name + '/categories.npy', user_categories)


if __name__ == '__main__':
    driver = get_driver()
    fetch_data(driver, 'kahani', "https://scholar.google.com/citations?view_op=list_works&hl=en&hl=en&user=27QQkc8AAAAJ")
