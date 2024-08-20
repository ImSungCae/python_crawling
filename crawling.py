import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import time

# 설정
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-cache")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

url = 'https://boottent.com/camps'  # 이 부분을 실제 URL로 변경하세요
driver.get(url)

try:
    wait = WebDriverWait(driver, 10)  
    categoryList = wait.until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/main/section/div[1]/div/ul/li')))
    categoryList[1].click()
    
    while True:
        try:
            load_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/section/div[7]/div/section/div[3]/div/button')))
            load_more_button.send_keys(Keys.ENTER)
            time.sleep(1)
        except (NoSuchElementException, TimeoutException):
            print("더 이상 버튼이 없습니다. 루프 종료.")
            break

    time.sleep(2)
    # 모든 데이터가 로드된 후 리스트 아이템을 선택하여 상세 페이지로 이동
    list_items = wait.until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/main/section/div[7]/div/section/div[2]/div[2]/table/tbody/tr')))
    original_tab = driver.current_window_handle  # 현재 탭 저장
    
    for index in range(len(list_items)):
        try:
            # 각 리스트 아이템을 클릭하여 상세 페이지로 이동
            item = list_items[index].find_element(By.XPATH,'th//a')
            item.send_keys(Keys.ENTER)

            # 새 탭으로 전환
            WebDriverWait(driver, 10).until(EC.new_window_is_opened)
            new_tab = [tab for tab in driver.window_handles if tab != original_tab][0]
            driver.switch_to.window(new_tab)
            
            # 페이지가 로드될 때까지 대기
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//body')))  # 적절한 요소로 변경 필요
            
            # 모든 데이터가 로드된 후 페이지 소스 가져오기
            page_source = driver.page_source

            # BeautifulSoup로 HTML 파싱
            soup = BeautifulSoup(page_source, 'html.parser')

            educational_name = soup.select_one('body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.flex.w-full.flex-col.items-start.text-semibold18.md\:text-bold24 > div:nth-child(2)').text
            curriculum_name = soup.select_one('body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.flex.w-full.flex-col.items-start.text-semibold18.md\:text-bold24 > div:nth-child(3)').text
            keyword = [key.text for key in soup.select('body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(1) > div > div.flex.w-full.flex-col.gap-\[10px\].text-semibold14.text-grey-400.md\:text-semibold16 > div.rounded-\[10px\].bg-grey-100.p-4.md\:p-5.mt-5.flex.flex-col.gap-2\.5.text-grey-800 > ul > li')]
            image_selector = [
                "body > main > section > header > div.relative.grid.aspect-video.w-full.grow-0.border.border-grey-200.sm\:aspect-\[3\/1\].lg\:aspect-\[10\/3\].grid-cols-1.lg\:grid-cols-\[4\.7fr_4fr\].gap-1.overflow-hidden.rounded-none.md\:gap-2.lg\:gap-2\.5.lg\:rounded-\[10px\] > div.relative.flex.h-full.w-full.items-center.justify-center.overflow-hidden > button > img",
                "body > main > section > header > div.relative.grid.aspect-video.w-full.grow-0.border.border-grey-200.sm\:aspect-\[3\/1\].lg\:aspect-\[10\/3\].grid-cols-1.gap-1.overflow-hidden.rounded-none.md\:gap-2.lg\:gap-2\.5.lg\:rounded-\[10px\] > div > img"
            ]
            bootcamp_image_url = None
            for selector in image_selector:
                image_element = soup.select_one(selector)
                if image_element:
                    bootcamp_image_url = image_element['src']
                    break
                
            recruitment_end_date = soup.select_one('body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(3) > div > ul > li:nth-child(1) > div > ul > li:nth-child(2) > div > div > div:nth-child(1)').text
            study_date = soup.select_one("body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(3) > div > ul > li:nth-child(1) > div > ul > li:nth-child(4) > div > div").text.split(' ~ ')
            study_start_date = study_date[0]
            study_end_date = study_date[1].split(' ')[0]
            day_time = soup.select_one("body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(3) > div > ul > li:nth-child(1) > div > ul > li:nth-child(6) > div > ul > li > p").text
            recruitment_quota = soup.select_one("body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(3) > div > ul > li:nth-child(1) > div > ul > li:nth-child(8) > div > div").text
            class_method = soup.select_one("body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(3) > div > ul > li:nth-child(2) > div > ul > li:nth-child(2) > div > div > div").text
            learning_equipment = soup.select_one("body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(3) > div > ul > li:nth-child(2) > div > ul > li:nth-child(4) > div > div").text
            class_type = soup.select_one("body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(3) > div > ul > li:nth-child(2) > div > ul > li:nth-child(6) > div > div > div").text
            if class_type == "온라인":
                study_place = None
            else:
                study_place = soup.select_one("body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(1) > ul > li:nth-child(3) > div > ul > li:nth-child(2) > div > ul > li:nth-child(8) > div > ul > div").text    
            target_cost = soup.find('div', text=lambda t: t and "수강료 & 지원금" in t)
            if target_cost:
                parent_cost = target_cost.parent
                cost = parent_cost.select_one("ul > li > div > ul > li:nth-child(2) > div > div").text
                tomorrow_learning_card = parent_cost.select_one("ul > li > div > ul > li:nth-child(4) > div > span > span").text
                subsidyList = parent_cost.select("ul > li > div > ul > li:nth-child(6) > div > div > div")
                subsidy = []
                for subsidyElement in subsidyList:
                    subsidy.append(subsidyElement.text)
            else:
                print("해당 텍스트를 포함하는 div를 찾을 수 없습니다.")
                
            curriculum_map = []
            # targer_curriculum = soup.select_one("body > main > section > section > div.w-full.lg\:w-\[calc\(100\%-345px\)\].xl\:w-\[calc\(100\%-385px\)\] > div.relative.flex.w-full.flex-col.items-start.gap-\[30px\] > ul > li:nth-child(3) > ul > li > div > div.flex.flex-col.gap-10.text-base.font-normal.md\:gap-20 > div.markdown.prose.mx-auto.w-full.max-w-none.overflow-hidden.break-words.text-regular14.text-grey-600.prose-h1\:text-grey-800.prose-h2\:text-grey-800.prose-h3\:text-grey-800.md\:text-regular16")
            # if targer_curriculum:
            #     parent_curriculum = targer_curriculum
            #     next_curriculum = parent_curriculum.select_one("div > div:nth-child(2) > div:nth-child(1) > h3")
                # h3_elements = next_curriculum.select_one('div:nth-child(2)').text
                # h3_elements = targer_curriculum.select('div:nth-child(2) > div:nth-child(1) > h3')
                # for h3_next_elements in h3_elements:
                #     div_elements = h3_next_elements.next_sibling
                #     curriculum_map[h3_next_elements.text] = [li.text for li in div_elements.select('ul > li')]
                    
            
            
            
            
            # 추출된 데이터 출력
            print("educationalName :", educational_name)
            print("curriculumName :", curriculum_name)
            print("keyword :", keyword)
            print("bootCampImageUrl :", bootcamp_image_url)
            print("recruitmentEndDate :", recruitment_end_date)
            print("studyStartDate :", study_start_date)
            print("studyEndDate :", study_end_date)
            print("dayTime :", day_time)
            print("recruitmentQuota :", recruitment_quota)
            print("classMethod :", class_method)
            print("learningEquipment :", learning_equipment)
            print("classType :", class_type)
            print("studyPlace :", study_place)
            print("cost :", cost)
            print("tomorrowLearningCard :", tomorrow_learning_card)
            print("subsidy :", subsidy)
            # print("curriculumMap :", targer_curriculum)
            # print("curriculumMap :", parent_curriculum)
            # print("curriculumMap :", next_curriculum)

            
            
        except StaleElementReferenceException:
            print("StaleElementReferenceException 발생 - 요소를 다시 찾습니다.")
            list_items = wait.until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/main/section/div[7]/div/section/div[2]/div[2]/table/tbody/tr')))
            item = list_items[index]
            item.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"상세 페이지 크롤링 중 오류 발생: {e}")
            traceback.print_exc() # 전체 스택 트레이스 출력
        finally:
            # 탭 닫기 및 원래 탭으로 전환
            driver.close()    
            driver.switch_to.window(original_tab)
            time.sleep(1.5)  # 잠시 대기 후 다음 아이템 처리

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")
finally:
    driver.quit()  # 드라이버 종료
