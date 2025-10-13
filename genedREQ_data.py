# complete_gened_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# 定义所有通识教育类别及其子类别
GENED_CATEGORIES = {
    'ACP': {
        'url': 'https://courses.illinois.edu/gened/2025/fall/ACP',
        'subcategories': []  # ACP没有子类别
    },
    'CS': {
        'url': 'https://courses.illinois.edu/gened/2025/fall/CS',
        'subcategories': ['US', 'NW', 'WCC']
    },
    'HUM': {
        'url': 'https://courses.illinois.edu/gened/2025/fall/HUM', 
        'subcategories': ['LA', 'HP']
    },
    'NAT': {
        'url': 'https://courses.illinois.edu/gened/2025/fall/NAT',
        'subcategories': ['LS', 'PS']
    },
    'QR': {
        'url': 'https://courses.illinois.edu/gened/2025/fall/QR',
        'subcategories': ['QR1', 'QR2']
    },
    'SBS': {
        'url': 'https://courses.illinois.edu/gened/2025/fall/SBS',
        'subcategories': ['BSC', 'SS']
    }
}

def setup_driver():
    """设置Chrome浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def scrape_gened_category(driver, category_name, category_info):
    """获取单个通识教育类别的数据"""
    
    url = category_info['url']
    subcategories = category_info['subcategories']
    
    print(f"\n📚 正在获取 {category_name} 类别的数据...")
    print(f"   网址: {url}")
    
    try:
        driver.get(url)
        time.sleep(5)  # 等待页面加载
        
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找数据表格
        table = soup.find('table', {'id': 'gened-dt'})
        if not table:
            print(f"   ❌ 未找到 {category_name} 的表格")
            return None
        
        # 提取表头
        headers = []
        header_row = table.find('thead').find('tr') if table.find('thead') else table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                header_text = th.get_text(strip=True)
                headers.append(header_text)
        
        print(f"   表头: {headers}")
        
        # 提取数据行
        data = []
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')[1:]
        
        print(f"   找到 {len(rows)} 行数据")
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 2:  # 至少需要课程代码和名称
                continue
                
            # 提取课程代码
            course_code = cells[0].get_text(strip=True)
            
            # 验证课程代码格式
            if re.match(r'^[A-Z]{2,4}\s\d+', course_code):
                course_data = {
                    'course_code': course_code,
                    'course_title': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                }
                
                # 添加主类别标记
                course_data[f'{category_name}_MAIN'] = 1
                
                # 处理子类别
                for subcat in subcategories:
                    course_data[f'{category_name}_{subcat}'] = 0
                
                # 检查每个单元格的内容，确定具体满足哪些子类别
                for j, cell in enumerate(cells):
                    if j < 2:  # 前两列是课程代码和名称
                        continue
                    
                    cell_text = cell.get_text(strip=True)
                    # 检查单元格内容是否匹配任何子类别
                    for subcat in subcategories:
                        if subcat in cell_text:
                            course_data[f'{category_name}_{subcat}'] = 1
                
                data.append(course_data)
        
        print(f"   ✅ 成功提取 {len(data)} 门课程")
        return data
        
    except Exception as e:
        print(f"   ❌ 获取 {category_name} 数据时出错: {e}")
        return None

def merge_all_data(all_category_data):
    """合并所有类别的数据"""
    
    # 创建主数据字典，以课程代码为键
    master_data = {}
    
    # 所有可能的列
    all_columns = ['course_code', 'course_title']
    
    # 添加所有类别和子类别的列
    for category_name, category_info in GENED_CATEGORIES.items():
        all_columns.append(f'{category_name}_MAIN')
        for subcat in category_info['subcategories']:
            all_columns.append(f'{category_name}_{subcat}')
    
    # 处理每个类别的数据
    for category_name, course_list in all_category_data.items():
        if course_list is None:
            continue
            
        for course in course_list:
            course_code = course['course_code']
            
            if course_code not in master_data:
                # 初始化新课程记录
                master_data[course_code] = {col: 0 for col in all_columns}
                master_data[course_code]['course_code'] = course_code
                master_data[course_code]['course_title'] = course.get('course_title', '')
            
            # 更新当前类别的数据
            for key, value in course.items():
                if key not in ['course_code', 'course_title']:
                    master_data[course_code][key] = value
    
    # 转换为列表
    merged_data = list(master_data.values())
    
    # 创建DataFrame，确保列顺序一致
    df = pd.DataFrame(merged_data, columns=all_columns)
    
    return df

def main():
    """主函数：获取所有通识教育类别的数据"""
    
    print("🚀 开始获取UIUC所有通识教育要求数据...")
    
    # 设置浏览器
    driver = setup_driver()
    
    all_category_data = {}
    
    try:
        # 获取每个类别的数据
        for category_name, category_info in GENED_CATEGORIES.items():
            data = scrape_gened_category(driver, category_name, category_info)
            all_category_data[category_name] = data
        
        # 合并所有数据
        print("\n🔄 正在合并所有类别的数据...")
        merged_df = merge_all_data(all_category_data)
        
        if not merged_df.empty:
            # 保存完整数据
            filename = 'uiuc_all_gened_requirements.csv'
            merged_df.to_csv(filename, index=False)
            print(f"\n✅ 成功保存 {len(merged_df)} 门课程数据到 {filename}")
            
            # 生成统计报告
            generate_statistics(merged_df)
            
            # 显示数据预览
            print("\n📊 完整数据预览 (前10行):")
            pd.set_option('display.max_columns', None)
            print(merged_df.head(10))
            
        else:
            print("❌ 没有合并到有效数据")
            
    except Exception as e:
        print(f"❌ 主程序错误: {e}")
    finally:
        driver.quit()

def generate_statistics(df):
    """生成数据统计报告"""
    
    print("\n📈 数据统计报告:")
    print("=" * 50)
    
    # 主类别统计
    print("\n主类别统计:")
    for category_name in GENED_CATEGORIES.keys():
        col_name = f'{category_name}_MAIN'
        if col_name in df.columns:
            count = df[col_name].sum()
            print(f"  {category_name}: {count} 门课程")
    
    # 子类别统计
    print("\n子类别统计:")
    for category_name, category_info in GENED_CATEGORIES.items():
        if category_info['subcategories']:
            print(f"\n  {category_name} 子类别:")
            for subcat in category_info['subcategories']:
                col_name = f'{category_name}_{subcat}'
                if col_name in df.columns:
                    count = df[col_name].sum()
                    print(f"    {subcat}: {count} 门课程")
    
    # 课程满足多个要求的统计
    print("\n课程满足要求数量统计:")
    requirement_cols = [col for col in df.columns if col.endswith('_MAIN')]
    df['total_requirements'] = df[requirement_cols].sum(axis=1)
    
    requirement_counts = df['total_requirements'].value_counts().sort_index()
    for count, num_courses in requirement_counts.items():
        print(f"  满足 {count} 个要求: {num_courses} 门课程")

if __name__ == "__main__":
    main()