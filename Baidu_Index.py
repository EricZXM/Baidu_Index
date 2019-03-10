import time
import datetime
import pandas as pd
from ast import literal_eval
from urllib.parse import quote
from selenium import webdriver
from setting import ChromePath, Keyword, province, city, startdate, enddate


browser = webdriver.Chrome(ChromePath)

def initialize_browser():

    browser.get('https://index.baidu.com/#/')
    browser.set_window_size(1500, 900)
    browser.delete_all_cookies()
    cookies = open("cookies.txt", "r")
    for cookie in cookies:
        browser.add_cookie(literal_eval(cookie))
    cookies.close()
    time.sleep(1)
    browser.refresh()


def get_into_page(keyword):
    url = "https://index.baidu.com/v2/main/index.html#/trend/"+ quote(keyword)+"?words=" + quote(keyword)
    browser.get(url)

def set_region(province, city):
    browser.find_elements_by_xpath('//*[@class="index-region"]')[0].click()
    time.sleep(1)
    pro = "//span[text()='%s']"%province
    cit = "//span[text()='%s']"%city
    browser.find_elements_by_xpath(pro)[0].click()
    time.sleep(1)
    browser.find_elements_by_xpath(cit)[0].click()


def get_time_range_list(startdate, enddate):
    """
    max 6 months
    """
    date_range_list = []
    startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d')
    enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
    while True:
        tempdate = startdate + datetime.timedelta(days=300)
        if tempdate >= enddate:
            all_days = (enddate-startdate).days
            date_range_list.append((startdate, enddate, all_days+1))
            return date_range_list
        date_range_list.append((startdate, tempdate, 301))
        startdate = tempdate + datetime.timedelta(days=1)

def ignore_baidu_index_bug():
    """
        百度咨询指数，第一次点击时间会没有响应
    """
    time.sleep(1)
    browser.find_elements_by_xpath('//*[@class="index-date-range-picker"]')[1].click()
    base_node = browser.find_element_by_xpath('//*[contains(@class, "index-date-range-picker-overlay-box") and \
        contains(@class, "tether-enabled")]')
    time.sleep(1.5)
    base_node.find_element_by_xpath('.//*[@class="primary"]').click()

def adjust_time_range(startdate, enddate, kind):
    """
        ...
    """
    time.sleep(2)
    browser.find_elements_by_xpath('//*[@class="index-date-range-picker"]')[kind].click()
    base_node = browser.find_element_by_xpath('//*[contains(@class, "index-date-range-picker-overlay-box") and \
        contains(@class, "tether-enabled")]')
    select_date(base_node, startdate)
    end_date_button = base_node.find_elements_by_xpath('.//*[@class="date-panel-wrapper"]')[1]
    end_date_button.click()
    select_date(base_node, enddate)

    base_node.find_element_by_xpath('.//*[@class="primary"]').click()
    time.sleep(1)

def select_date(base_node, date):
    """
        select date
    """
    time.sleep(2.5)
    base_node = base_node.find_element_by_xpath('.//*[@class="right-wrapper" and not(contains(@style, "none"))]')
    next_year = base_node.find_element_by_xpath('.//*[@aria-label="下一年"]')
    pre_year = base_node.find_element_by_xpath('.//*[@aria-label="上一年"]')
    next_month = base_node.find_element_by_xpath('.//*[@aria-label="下个月"]')
    pre_month = base_node.find_element_by_xpath('.//*[@aria-label="上个月"]')
    cur_year = base_node.find_element_by_xpath('.//*[@class="veui-calendar-left"]//b').text
    cur_month = base_node.find_element_by_xpath('.//*[@class="veui-calendar-right"]//b').text
    diff_year = int(cur_year) - date.year
    diff_month = int(cur_month) - date.month
    if diff_year > 0:
        for _ in range(abs(diff_year)):
            pre_year.click()
    elif diff_year < 0:
        for _ in range(abs(diff_year)):
            next_year.click()

    if diff_month > 0:
        for _ in range(abs(diff_month)):
            pre_month.click()
    elif diff_month <0:
        for _ in range(abs(diff_month)):
            next_month.click()

    time.sleep(1)
    base_node.find_elements_by_xpath('.//table//*[contains(@class, "veui-calendar-day")]')[date.day-1].click()

def loop_move(all_days, keyword, kind):
    """
        to get the index by moving mouse
    """
    time.sleep(1)
    chart = browser.find_elements_by_xpath('//*[@class="index-trend-chart"]')[kind]
    chart_size = chart.size
    move_step = all_days - 1
    step_px = chart_size['width'] / move_step
    cur_offset = {
        'x': step_px,
        'y': chart_size['height'] - 50
    }

    webdriver.ActionChains(browser).move_to_element_with_offset(
        chart, 1, cur_offset['y']).perform()
    yield get_index(keyword, chart)

    for _ in range(all_days-1):
        time.sleep(0.05)
        webdriver.ActionChains(browser).move_to_element_with_offset(
            chart, int(cur_offset['x']), cur_offset['y']).perform()
        cur_offset['x'] += step_px
        yield get_index(keyword, chart)

def get_index(keyword, base_node):
    """
        get index datas by html
    """
    date = base_node.find_element_by_xpath('./div[2]/div[1]').text
    date = date.split(' ')[0]
    index = base_node.find_element_by_xpath('./div[2]/div[2]/div[2]').text
    index = index.replace(',', '').strip(' ')
    result = {
        'keyword': keyword,
        'date': date,
        'index': index,
    }
    return result

def main(keyword, province, city, startdate, enddate, kind=0):
    """
        :kind; int, 0:搜索指数, 1:咨询指数
        搜索指数最早的数据日期为2011-01-01
        咨询指数最早的数据日期为2017-07-03
    """
    initialize_browser()
    get_into_page(keyword)
    set_region(province, city)
    if kind == 1:
        ignore_baidu_index_bug()

    date_range_list = get_time_range_list(startdate, enddate)
    for startdate, enddate, all_days in date_range_list:
        adjust_time_range(startdate, enddate, kind)
        for data in loop_move(all_days, keyword, kind):
            yield data
    browser.quit()

if __name__ == '__main__':

    dataframe = {}
    dataframe[Keyword] = []
    dataframe['date'] = []

    for data in main(Keyword, province, city, startdate, enddate, 0):
        print(data)
        dataframe[Keyword].append(data['index'])
        dataframe['date'].append(data['date'])

    dataframe = pd.DataFrame(dataframe)
    dataframe.set_index('date',inplace=True)
    dataframe.to_csv("BaiduIndex.csv", encoding='utf_8_sig')