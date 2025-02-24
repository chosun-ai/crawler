import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time, re


TIME_SET = 0.5
START_KING = 3 # 세종
START_YEARS = 232 # 
# START_YEARS = 282 # 

def convert_text(text):
    clean_text = " ".join(text.split())
    pattern = re.compile(r"(\w+실록)(\d+)권")
    pattern_2 = re.compile(r"(\d{4})년")
    pattern_3 = re.compile(r"(\d+)월 (\d+)일")

    matches = pattern.findall(clean_text)
    matches_2 = pattern_2.findall(clean_text)
    matches_3 = pattern_3.findall(clean_text)

    result = {
        "name": matches[0][0],
        "number": matches[0][1],
        "date": f"{matches_2[0]}-{matches_3[0][0]}-{matches_3[0][1]}"
    }
    return result


def scrape_page(driver):
    """현재 페이지에서 데이터를 수집하는 함수."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    history = soup.find('span', class_='tit_loc').text if soup.find('span', class_='tit_loc') else ''
    title = soup.find('h3', class_='search_tit').text if soup.find('h3', class_='search_tit') else ''
    content_list = soup.select('.ins_view_left .paragraph')
    content_all = '\n\n'.join(content.get_text(strip=True) for content in content_list)
    return {**convert_text(history), "content": content_all, "title": title}


def main():
    # Chrome 드라이버 설치 및 설정
    driver = webdriver.Chrome()

    # 웹사이트 열기
    url = "https://sillok.history.go.kr/main/main.do"
    driver.get(url)

    # 웹사이트 로딩 대기
    time.sleep(TIME_SET)  # 필요에 따라 시간 조정

    first_links = driver.find_elements(By.CSS_SELECTOR, "#m_cont_list a")  # 모든 <a> 태그 가져오기
    data = []
    print("@@ START CRAWLER @@")
    try:
        for index in range(len(first_links) - START_KING):
        # for index in range(1):
            data = []
            currentData = {
                "name": "",
                "number": "",
                "date": "",
                "content": "",
                "title": "",
            }
            print(f"- {index + START_KING}/{len(first_links)}번째 실록")
            links_first = driver.find_elements(By.CSS_SELECTOR, "#m_cont_list a")  # 모든 <a> 태그 가져오기
            links_first[index + START_KING].click()
            time.sleep(TIME_SET)  # 필요에 따라 시간 조정
            second_links = driver.find_elements(By.CSS_SELECTOR, ".king_year2.clear2 ul.clear2 a")  # 모든 <a> 태그 가져오기
            for index in range(len(second_links)- START_YEARS):
            # for index in range(1):
                print(f"-- {index + START_YEARS}/{len(second_links)}번째 권")
                links_sec = driver.find_elements(By.CSS_SELECTOR, ".king_year2.clear2 ul.clear2 a")  # 모든 <a> 태그 가져오기
                links_sec[index + START_YEARS].click()
                time.sleep(TIME_SET)  # 필요에 따라 시간 조정
                thrid_links = driver.find_elements(By.CSS_SELECTOR, ".ins_list_main li a")  # 모든 <a> 태그 가져오기
                for index in range(len(thrid_links)):
                # for index in range(2):
                    print(f"--- {index + 1}/{len(thrid_links)}번째 기사")
                    links_trd = driver.find_elements(By.CSS_SELECTOR, ".ins_list_main li a")  # 모든 <a> 태그 가져오기
                    links_trd[index].click()
                    time.sleep(TIME_SET)  # 필요에 따라 시간 조정
                    result = scrape_page(driver)
                    currentData = result
                    data.append(result)
                    driver.back()
                    time.sleep(TIME_SET)  # 필요에 따라 시간 조정
                driver.back()
                time.sleep(TIME_SET)  # 필요에 따라 시간 조정
            driver.back()
            time.sleep(TIME_SET)  # 필요에 따라 시간 조정
        # 수집한 데이터를 JSON 형태로 저장
        
        with open(f'{currentData["name"]}.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f'### {currentData["name"]}.json 저장 완료')
        time.sleep(TIME_SET)  # 필요에 따라 시간 조정

    except:
        print('@@ 에러 발생함 @@')
        data.append({
            "name" : currentData["name"],
            "number" : currentData["number"],
            "date" : "",
            "content" : "",
            "title" : "",
        })
        time.sleep(TIME_SET)  # 필요에 따라 시간 조정
        time.sleep(TIME_SET)  # 필요에 따라 시간 조정
        time.sleep(TIME_SET)  # 필요에 따라 시간 조정

    # 수집한 데이터를 JSON 형태로 저장
    with open('error_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    # 작업이 끝난 후 브라우저 종료
    driver.quit()

    print("데이터가 JSON 파일로 저장되었습니다.")


if __name__ == "__main__":
    main()
