import pandas as pd
import re
import time
import io

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains

chrome_options = webdriver.ChromeOptions()
prefs = {'profile.managed_default_content_settings.images': 2}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(
    executable_path="/usr/lib/chromium-browser/chromedriver", chrome_options=chrome_options)
driver.set_page_load_timeout(10)
ac = ActionChains(driver)


def get_coin_info(coin_name, bas_tarih, bit_tarih):  # 20170606 -- 20170906
    url = 'https://coinmarketcap.com/currencies/' + str(coin_name)
    try:
        driver.get(url)
    except TimeoutException:
        driver.execute_script("window.stop();")


    # <li id="ember1118" class="ember-view"><script id="metamorph-55-start">
    #  "//li[contains(@id,'ember')]//a[@title='Rugby League ']
    # //*[@id="highcharts-eei2u26-0"]/svg/g[20]/g[1]
    # //*[@id="highcharts-eei2u26-0"]/svg/g[20]/g[1]
    # <g class="highcharts-series highcharts-series-0 highcharts-line-series highcharts-color-undefined " transform="translate(82,87) scale(1 1)" clip-path="url(#highcharts-eei2u26-3)">
    # "//g[@class='highcharts-series highcharts-series-0 highcharts-line-series highcharts-color-undefined ']"
    #xpath = "//g[@class='highcharts-series highcharts-series-0 highcharts-line-series highcharts-color-undefined ']"
    #el = driver.find_elements_by_class_name("container")
    #print(By.CssSelector("svg")

    svg_parent = "/html/body/div[4]/div/div[1]/div[5]/div[2]//*[@id='charts']/div[2]/div[2]"
    rect_element = "%s/*[name()='svg']/*[name()='rect']" % svg_parent
    one_year_xpath = "%s/*[name()='svg']/*[name()='g']/*[name()='g'][2]" % svg_parent
    series_path = "%s/*[name()='svg']/*[name()='g' and @class='highcharts-series-group']" % svg_parent
    first_series = "%s/*[name()='g'][1]/*[name()='path']" % series_path

    
    #
    tooltip = "%s/*[name()='svg']/*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']/*[name()='text']" % svg_parent
    date = "%s/*[name()='tspan'][0]" % tooltip
 
    graph_elem = driver.find_element_by_xpath(rect_element)
    print(graph_elem.size)
    ac.move_to_element(graph_elem).click().perform()
    time.sleep(2)

    date_elem = driver.find_element_by_xpath(date)
    print(date_elem.text)

    #print(el)
    #print(el.get_attribute('d'))
    #ac.move_to_element(el).move_by_offset(346.69226327945, 288.403906662).click().perform()


get_coin_info("siacoin", "20170606", "20170906")
