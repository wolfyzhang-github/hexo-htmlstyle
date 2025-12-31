import os
import requests
import json
from datetime import datetime, timedelta
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import feedparser
import re
from urllib.parse import quote

# Azure OpenAI API配置
API_KEY = "dc37e43fbe4b4fb4aed7fb117e58afe8"  # 请替换为你的API密钥
ENDPOINT = "https://ghzhang-eastus2.openai.azure.com/"  # 请替换为你的API终结点
API_VERSION = "2025-01-01-preview"

def get_random_date():
    """生成2024年7月3日到2025年2月28日之间的随机日期和时间"""
    start_date = datetime(2024, 7, 3)
    end_date = datetime(2025, 2, 28)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    
    # 添加随机时分秒
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    return random_date.replace(hour=random_hour, minute=random_minute, second=random_second)

def get_paper_info():
    """从arXiv获取LLM相关的热门论文"""
    # arXiv API搜索URL
    # 使用更广泛的搜索条件，并按引用次数排序
    search_query = "cat:cs.CL AND (large language model OR LLM OR GPT OR transformer OR attention)"
    url = f"http://export.arxiv.org/api/query?search_query={quote(search_query)}&sortBy=relevance&sortOrder=descending&max_results=100"
    
    # 获取论文信息
    response = requests.get(url)
    feed = feedparser.parse(response.content)
    
    papers = []
    cutoff_date = datetime(2024, 7, 1)  # 设置截止日期
    
    for entry in feed.entries:
        # 检查论文发表时间
        published_date = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
        if published_date >= cutoff_date:
            continue
            
        # 提取论文信息
        title = entry.title.replace('\n', ' ').strip()
        abstract = entry.summary.replace('\n', ' ').strip()
        pdf_url = None
        for link in entry.links:
            if link.type == 'application/pdf':
                pdf_url = link.href
                break
        
        # 获取论文的引用信息（通过Semantic Scholar API）
        try:
            # 使用论文标题搜索Semantic Scholar
            ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote(title)}&limit=1"
            ss_response = requests.get(ss_url)
            if ss_response.status_code == 200:
                ss_data = ss_response.json()
                if ss_data['total'] > 0:
                    paper_id = ss_data['data'][0]['paperId']
                    # 获取论文详情
                    paper_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,citationCount"
                    paper_response = requests.get(paper_url)
                    if paper_response.status_code == 200:
                        paper_data = paper_response.json()
                        citation_count = paper_data.get('citationCount', 0)
                    else:
                        citation_count = 0
                else:
                    citation_count = 0
            else:
                citation_count = 0
        except Exception as e:
            print(f"获取论文 {title} 的引用信息时出错: {str(e)}")
            citation_count = 0
        
        papers.append({
            'title': title,
            'abstract': abstract,
            'pdf_url': pdf_url,
            'citation_count': citation_count,
            'published_date': published_date
        })
    
    # 按引用次数排序
    papers.sort(key=lambda x: x['citation_count'], reverse=True)
    
    # 返回前21篇最有影响力的论文
    return papers[:21]

def generate_article(paper, max_retries=3):
    """使用Azure OpenAI生成论文解读文章"""
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    
    prompt = f"""请根据以下论文信息，用中文详细解读这篇论文的工作：

论文标题：{paper['title']}
论文摘要：{paper['abstract']}

要求：
1. 使用Markdown格式
2. 文章结构清晰，包含以下部分：
   - 论文背景
   - 主要贡献
   - 技术细节
   - 实验结果
   - 创新点
   - 实际应用
3. 内容专业且详细，需要包含大量的技术细节
4. 语言流畅自然
5. 字数在3000字左右
6. 适当使用标题、列表、代码块等Markdown元素

请开始生成文章："""

    data = {
        "messages": [
            {"role": "system", "content": "你是一个专业的AI研究专家，擅长解读和讲解技术论文。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000,  # 减少token数量
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{ENDPOINT}/openai/deployments/gpt-4/chat/completions?api-version={API_VERSION}",
                headers=headers,
                json=data,
                timeout=60  # 添加超时设置
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code == 429:  # 频率限制
                wait_time = (attempt + 1) * 10  # 递增等待时间
                print(f"遇到频率限制，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"API请求失败 (状态码: {response.status_code}): {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # 其他错误等待5秒后重试
                else:
                    raise Exception(f"API请求失败: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise

    raise Exception("达到最大重试次数")

def create_blog_post(paper, content, index):
    """创建博客文章文件"""
    try:
        # 生成标题
        title = f"论文解读：{paper['title']}"
        
        # 生成permalink（使用论文标题的拼音）
        permalink = '-'.join(re.findall(r'[\w]+', paper['title'].lower()))
        
        # 生成随机日期和时间
        random_date = get_random_date()
        date_str = random_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # 生成YAML front matter
        front_matter = f"""---
title: {title}
date: {date_str}
updated: {date_str}
permalink: microsoft/{permalink}
pinned:
abstract:
password:
message:
key: 微软
---

"""
        
        # 使用论文编号作为文件名
        file_path = os.path.join("source", "microsoft", f"paper-{index+1:03d}.md")
        
        # 处理软链接
        if os.path.islink("source"):
            # 获取软链接指向的实际路径
            real_path = os.path.realpath("source")
            file_path = os.path.join(real_path, "microsoft", f"paper-{index+1:03d}.md")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(front_matter)
            f.write(content)
            
        print(f"成功创建文件: {file_path}")
        return True
    except Exception as e:
        print(f"创建文件时出错: {str(e)}")
        return False

def process_paper(paper, index):
    """处理单篇论文的生成任务"""
    try:
        print(f"正在处理第 {index+1} 篇论文: {paper['title']}")
        print(f"论文发表时间: {paper['published_date'].strftime('%Y-%m-%d')}")
        print(f"引用次数: {paper['citation_count']}")
        
        content = generate_article(paper)
        if create_blog_post(paper, content, index):
            print(f"论文解读 {paper['title']} 生成成功")
        else:
            print(f"论文解读 {paper['title']} 生成失败")
        
        # 添加处理间隔，避免频率限制
        time.sleep(10)  # 增加等待时间
        return True
    except Exception as e:
        print(f"处理论文 {paper['title']} 时出错: {str(e)}")
        return False

def main():
    # 确保目录存在
    os.makedirs(os.path.join("source", "microsoft"), exist_ok=True)
    
    # 获取论文信息
    print("正在从arXiv获取论文信息...")
    papers = get_paper_info()
    print(f"成功获取 {len(papers)} 篇论文信息")
    
    # 使用线程池进行并发处理
    # 减少并发数，避免频率限制
    with ThreadPoolExecutor(max_workers=1) as executor:  # 改为单线程处理
        # 提交所有任务
        future_to_paper = {
            executor.submit(process_paper, paper, i): paper 
            for i, paper in enumerate(papers)
        }
        
        # 等待所有任务完成
        for future in as_completed(future_to_paper):
            paper = future_to_paper[future]
            try:
                future.result()
            except Exception as e:
                print(f"处理论文 {paper['title']} 时发生错误: {str(e)}")

if __name__ == "__main__":
    main() 