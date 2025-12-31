import os
import requests
import json
from datetime import datetime, timedelta
import pypinyin
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Azure OpenAI API配置
API_KEY = "dc37e43fbe4b4fb4aed7fb117e58afe8"  # 请替换为你的API密钥
ENDPOINT = "https://ghzhang-eastus2.openai.azure.com/"  # 请替换为你的API终结点
API_VERSION = "2025-01-01-preview"

# 文章主题列表
TOPICS = [
    # 基础概念与概述
    "深入浅出：Azure OpenAI服务全解析",
    "解密大语言模型：从原理到应用",
    "Azure OpenAI vs ChatGPT：全面对比分析",
    "Azure OpenAI模型家族：从GPT到DALL-E",
    "一文读懂Azure OpenAI的API架构设计",
    
    # 使用技巧与实战
    "提示词工程：让Azure OpenAI发挥最大价值",
    "10个技巧：提升Azure OpenAI响应质量",
    "上下文管理：打造流畅的对话体验",
    "流式响应：实现实时交互的关键技术",
    "并发处理：如何优化Azure OpenAI的性能",
    "缓存策略：提升响应速度的实用指南",
    "速率限制：如何优雅地处理API限制",
    "错误处理：构建健壮的AI应用系统",
    "日志监控：全方位保障系统稳定性",
    "性能调优：从入门到精通",
    
    # 实际应用场景
    "从零开始：构建智能客服系统实战",
    "文档处理新范式：Azure OpenAI应用实践",
    "智能搜索：让信息获取更高效",
    "代码生成：提升开发效率的利器",
    "文本摘要：让信息处理更智能",
    "内容创作：AI辅助写作的实践指南",
    "智能问答：打造知识库的智能助手",
    "数据分析：AI驱动的数据洞察",
    "文本分类：自动化处理的新思路",
    "机器翻译：打破语言障碍的桥梁",
    
    # 高级功能与集成
    "模型微调：打造专属AI的秘诀",
    "嵌入模型：语义理解的核心技术",
    "向量数据库：构建智能搜索的基石",
    "RAG实现：知识增强的实践指南",
    "多模型协同：构建更强大的AI系统",
    "版本管理：确保模型更新的稳定性",
    "模型评估：如何衡量AI的性能",
    "部署策略：从开发到生产的最佳实践",
    "监控方案：全方位保障系统运行",
    "更新机制：保持系统与时俱进",
    
    # 安全与合规
    "安全特性：保护你的AI应用",
    "数据隐私：合规使用AI的关键",
    "访问控制：构建安全的权限体系",
    "内容审核：确保AI输出的安全性",
    "敏感信息：如何安全处理数据",
    "灾难恢复：保障业务连续性",
    "备份策略：数据安全的重要保障",
    "安全监控：实时防护的关键环节",
    
    # 行业应用案例（精选）
    "金融科技：Azure OpenAI在风控中的应用",
    "医疗健康：AI辅助诊断的实践探索",
    "教育创新：个性化学习的AI解决方案",
    "零售升级：智能客服的落地实践",
    
    # 未来展望（精选）
    "技术演进：Azure OpenAI的发展方向",
    "应用创新：AI技术的未来趋势",
    "生态建设：构建AI应用的新生态"
]

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

def get_pinyin(text):
    """将中文转换为拼音，用于生成permalink"""
    # 移除标题中的冒号和空格
    text = text.replace('：', '').replace(' ', '')
    pinyin_list = pypinyin.lazy_pinyin(text)
    return '-'.join(pinyin_list)

def generate_article(topic):
    """使用Azure OpenAI生成文章内容"""
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    
    prompt = f"""请以以下格式生成一篇关于{topic}的博客文章：

1. 使用Markdown格式
2. 文章结构清晰
3. 内容专业且详细，需要包含大量的技术细节
4. 包含实际应用场景和示例
5. 语言流畅自然
6. 字数在2000字左右

请开始生成文章："""

    data = {
        "messages": [
            {"role": "system", "content": "你是一个专业的Azure OpenAI技术专家，擅长撰写技术博客文章。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }

    response = requests.post(
        f"{ENDPOINT}/openai/deployments/gpt-4/chat/completions?api-version={API_VERSION}",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API请求失败: {response.status_code}")

def create_blog_post(topic, content):
    """创建博客文章文件"""
    # 生成permalink（使用拼音）
    permalink = get_pinyin(topic)
    
    # 生成随机日期和时间
    random_date = get_random_date()
    date_str = random_date.strftime("%Y-%m-%d %H:%M:%S")
    
    # 生成YAML front matter
    front_matter = f"""---
title: {topic}
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
    
    # 使用中文标题作为文件名，移除冒号
    safe_filename = topic.replace('：', '-')  # 将冒号替换为连字符
    file_path = os.path.join("source", "microsoft", f"{safe_filename}.md")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(front_matter)
        f.write(content)

def process_topic(topic, index):
    """处理单个主题的生成任务"""
    try:
        print(f"正在生成第 {index+1} 篇文章: {topic}")
        content = generate_article(topic)
        create_blog_post(topic, content)
        print(f"文章 {topic} 生成成功")
        return True
    except Exception as e:
        print(f"生成文章 {topic} 时出错: {str(e)}")
        return False

def main():
    # 确保目录存在
    os.makedirs(os.path.join("source", "microsoft"), exist_ok=True)
    
    # 使用线程池进行并发处理
    # 设置最大并发数为5，避免API限制
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务
        future_to_topic = {
            executor.submit(process_topic, topic, i): topic 
            for i, topic in enumerate(TOPICS)
        }
        
        # 等待所有任务完成
        for future in as_completed(future_to_topic):
            topic = future_to_topic[future]
            try:
                future.result()
            except Exception as e:
                print(f"处理主题 {topic} 时发生错误: {str(e)}")

if __name__ == "__main__":
    main() 