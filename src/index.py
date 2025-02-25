import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time, re
import datetime

TIME_SET = 0.01
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


def retry_operation(operation, max_attempts=50, delay=TIME_SET):
    """작업을 재시도하는 함수"""
    time.sleep(TIME_SET * 10)
    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            print(f"오류 발생: {str(e)}. {attempt + 1}번째 재시도...")
            time.sleep(delay)


def main():
    # Chrome 드라이버 설치 및 설정
    driver = webdriver.Chrome()

    # 웹사이트 열기
    url = "https://sillok.history.go.kr/main/main.do"
    driver.get(url)

    # 웹사이트 로딩 대기
    time.sleep(TIME_SET)

    first_links = driver.find_elements(By.CSS_SELECTOR, "#m_cont_list a")  # 모든 <a> 태그 가져오기
    data = []
    print("@@ START CRAWLER @@")
    for index in range(len(first_links) - START_KING):
        data = []
        currentData = {
            "name": "",
            "number": "",
            "date": "",
            "content": "",
            "title": "",
        }
        print(f"- {index + START_KING}/{len(first_links)}번째 실록")

        # 첫번째 링크 클릭 재시도
        def click_first():
            links = driver.find_elements(By.CSS_SELECTOR, "#m_cont_list a")
            links[index + START_KING].click()
        retry_operation(click_first)
        time.sleep(TIME_SET)
        second_links = driver.find_elements(By.CSS_SELECTOR, ".king_year2.clear2 ul.clear2 a")
        for index in range(len(second_links)- START_YEARS):
            print(f"-- {index + START_YEARS}/{len(second_links)}번째 권")
            # 두번째 링크 클릭 재시도
            def click_second():
                links = driver.find_elements(By.CSS_SELECTOR, ".king_year2.clear2 ul.clear2 a")
                links[index + START_YEARS].click()
            retry_operation(click_second)
            time.sleep(TIME_SET)
            thrid_links = driver.find_elements(By.CSS_SELECTOR, ".ins_list_main li a")
            for index in range(len(thrid_links)):
                print(f"--- {index + 1}/{len(thrid_links)}번째 기사")
                # 세번째 링크 클릭 재시도
                def click_third():
                    links = driver.find_elements(By.CSS_SELECTOR, ".ins_list_main li a")
                    links[index].click()
                retry_operation(click_third)
                time.sleep(TIME_SET) 
                # scrape_page 함수가 정상동작하지 않을 경우 재실행하는 로직
                result = retry_operation(lambda: scrape_page(driver))
                currentData = result
                data.append(result)
                driver.back()
                time.sleep(TIME_SET)
            driver.back()
            time.sleep(TIME_SET)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f'{currentData["name"]}_{currentData["number"]}_{timestamp}.json', 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            data = []
            print(f'### {currentData["name"]}_{currentData["number"]}_{timestamp}.json 저장 완료')
            time.sleep(TIME_SET)
        driver.back()
        time.sleep(TIME_SET)
    
        

    # 수집한 데이터를 JSON 형태로 저장
    with open('error_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    # 작업이 끝난 후 브라우저 종료
    driver.quit()

    print("데이터가 JSON 파일로 저장되었습니다.")


if __name__ == "__main__":
    main()
