from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests


# 启动浏览器
def setup_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式（可选）
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    return driver


# 在Pixabay搜索图片
def search_images(keyword: str, num_images: int, retries_num: int = 3) -> None:
    driver = setup_driver()

    # 打开Pixabay首页
    driver.get('https://www.hippopx.com/')

    # 使用WebDriverWait等待搜索框加载
    wait = WebDriverWait(driver, 5)
    print("Waiting for search box...")
    search_box = wait.until(EC.presence_of_element_located((By.NAME, 'q')))
    print("Search box found!")
    # 输入关键词并按回车键
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)

    # 等待搜索结果加载
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img')))

    # # 滑动页面以加载更多图片
    # scrolls = 5  # 控制滑动到底部的次数
    # for _ in range(scrolls):
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     time.sleep(5)  # 等待页面加载新内容

    # 获取所有图片的元素
    image_elements = driver.find_elements(By.CSS_SELECTOR, 'img[itemprop="contentUrl"]')

    # 创建一个以关键词命名的文件夹
    save_directory = os.path.join(os.getcwd(), keyword)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # 下载前 num_images 张图片
    downloaded_images = 0
    for idx, image_element in enumerate(image_elements):
        if downloaded_images >= num_images:
            break
        try:
            image_url = image_element.get_attribute('src')
            if image_url:
                # 确定图片的保存路径
                file_path = os.path.join(save_directory, f'{keyword}_{idx}.jpg')
                download_image(image_url, file_path,retries = retries_num)
                downloaded_images += 1
        except Exception as e:
            print(f"Error downloading image {idx}: {e}")

    driver.quit()


# 下载图片到本地
def download_image(url: str, file_name: str, retries: int) -> None:
    headers = {
        'User-Agent': 'Mozilla/5.0 ...'
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded {file_name}")
                return  # 成功后退出
            else:
                print(f"Failed to download {file_name}, status code {response.status_code}")
        except Exception as e:
            print(f"Error: {e} on attempt {attempt + 1}")
    print(f"All attempts failed for {file_name}")


if __name__ == "__main__":
    keyword = input("Enter the search keyword: ")
    search_images(keyword,num_images=50)
