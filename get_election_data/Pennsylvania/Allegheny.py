from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from get_election_data.Pennsylvania import general_parser

def download_data(url, year):

    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "/home/matt/GitRepos/ElectionData/get_election_data/Pennsylvania/data/raw_downloads/Allegheny"})
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=chrome_options)

    driver.get(url)

    election_select = driver.find_element_by_xpath("//*[@id=\"mainContainer\"]/div[2]/section/div[1]/div[2]/div/div/div[1]/div/div/table/tbody/tr[1]/td[2]/font/a")
    election_select.click()

    handles = driver.window_handles
    driver.switch_to.window(handles[1])
    WebDriverWait(driver, 30).until(ec.visibility_of_element_located((By.XPATH, "//*[@id=\"PRESIDENTIAL ELECTORS\"]/div[2]/div[1]")))
    election_results = driver.find_element_by_xpath("//*[@id=\"sidebar-list\"]/li[7]/reports-widget/div/div[5]/ul/li[2]/a")
    driver.execute_script("return arguments[0].scrollIntoView();", election_results)
    WebDriverWait(driver, 30).until(ec.visibility_of_element_located((By.XPATH, "//*[@id=\"sidebar-list\"]/li[7]/reports-widget/div/div[5]/ul/li[2]/a/span[1]")))
    election_results.click()


# download_data("http://www.alleghenycounty.us/elections/election-results.aspx", "")

parser = general_parser.PrecinctParser("/home/matt/Downloads/2015 Official General Election Precinct.pdf")
precinct_text = parser.pdf_to_txt()
parser.precinct_parser(precinct_text)
