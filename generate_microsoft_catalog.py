import os
import re
from datetime import datetime

def extract_frontmatter_fields(file_path):
    """从markdown文件中提取frontmatter信息"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取frontmatter部分
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return None
    
    frontmatter_text = frontmatter_match.group(1)
    
    # 使用正则表达式提取各个字段
    title_match = re.search(r'title:\s*(.*?)$', frontmatter_text, re.MULTILINE)
    date_match = re.search(r'date:\s*(.*?)$', frontmatter_text, re.MULTILINE)
    permalink_match = re.search(r'permalink:\s*(.*?)$', frontmatter_text, re.MULTILINE)
    
    if not (title_match and date_match and permalink_match):
        return None
    
    title = title_match.group(1).strip()
    date_str = date_match.group(1).strip()
    permalink = permalink_match.group(1).strip()
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"文件 {file_path} 的日期格式错误: {date_str}")
        return None
    
    return {
        'title': title,
        'date': date,
        'permalink': permalink
    }

def generate_catalog():
    """生成微软文章目录"""
    # 获取microsoft路径下的所有markdown文件
    microsoft_path = os.path.join("source", "microsoft")
    if not os.path.exists(microsoft_path):
        print(f"路径 {microsoft_path} 不存在")
        return
    
    # 获取所有markdown文件
    markdown_files = []
    for file in os.listdir(microsoft_path):
        if file.endswith(".md"):
            file_path = os.path.join(microsoft_path, file)
            markdown_files.append(file_path)
    
    print(f"找到 {len(markdown_files)} 个markdown文件")
    
    # 提取文件信息
    articles = []
    for file_path in markdown_files:
        frontmatter = extract_frontmatter_fields(file_path)
        if frontmatter:
            title = frontmatter['title']
            date = frontmatter['date']
            permalink = frontmatter['permalink']
            
            # 提取permalink最后一部分作为url
            if isinstance(permalink, str) and '/' in permalink:
                url = permalink.split('/')[-1]
            else:
                url = permalink
            
            articles.append({
                'title': title,
                'date': date,
                'url': url,
                'file_path': file_path
            })
    
    # 按日期倒序排序
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    # 生成目录
    catalog = []
    for i, article in enumerate(articles, 1):
        date_str = article['date'].strftime("%Y-%m-%d")
        catalog.append(f"{i}、[{date_str}] [{article['title']}]({article['url']})")
    
    # 写入文件
    catalog_text = "\n".join(catalog)
    output_path = "微软文章目录.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 微软文章目录\n\n")
        f.write(catalog_text)
    
    print(f"目录已生成至 {output_path}")

if __name__ == "__main__":
    generate_catalog() 