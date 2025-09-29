#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速IPTV验证工具 - 简化版
使用方法: python3 quick_validate.py
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def validate_url(url, timeout=5):
    """快速验证单个URL"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def quick_validate():
    """快速验证IPTV文件"""
    print("🔍 快速IPTV地址验证工具")
    print("=" * 40)
    
    # 读取IPTV文件
    try:
        with open('IPTV.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("❌ 找不到IPTV.txt文件")
        return
    
    # 提取URL
    urls = []
    for line in lines:
        line = line.strip()
        if ',' in line and ('http://' in line or 'https://' in line):
            parts = line.split(',', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                url = parts[1].strip()
                urls.append((name, url))
    
    print(f"📺 找到 {len(urls)} 个频道")
    print("🚀 开始验证...")
    
    # 并发验证
    valid_count = 0
    invalid_count = 0
    valid_channels = []
    
    with ThreadPoolExecutor(max_workers=30) as executor:
        future_to_channel = {
            executor.submit(validate_url, url): (name, url) 
            for name, url in urls
        }
        
        for i, future in enumerate(as_completed(future_to_channel), 1):
            name, url = future_to_channel[future]
            is_valid = future.result()
            
            if is_valid:
                valid_count += 1
                valid_channels.append((name, url))
                print(f"[{i}/{len(urls)}] ✅ {name}")
            else:
                invalid_count += 1
                print(f"[{i}/{len(urls)}] ❌ {name}")
    
    # 生成结果
    print("\n" + "=" * 40)
    print("📊 验证结果:")
    print(f"✅ 可用频道: {valid_count} ({valid_count/len(urls)*100:.1f}%)")
    print(f"❌ 无效频道: {invalid_count} ({invalid_count/len(urls)*100:.1f}%)")
    
    # 生成清理后的文件
    if valid_channels:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        clean_file = f"IPTV_valid_{timestamp}.txt"
        
        with open(clean_file, 'w', encoding='utf-8') as f:
            f.write("4K,#genre#\n")
            for name, url in valid_channels:
                f.write(f"{name},{url}\n")
        
        print(f"💾 可用频道已保存到: {clean_file}")
    
    print("✨ 验证完成!")

if __name__ == "__main__":
    quick_validate()
