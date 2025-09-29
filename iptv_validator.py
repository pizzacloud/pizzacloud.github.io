#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV直播地址验证工具
自动检查IPTV.txt文件中的直播链接是否可用
"""

import requests
import time
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime

class IPTVValidator:
    def __init__(self, timeout=10, max_workers=20):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def parse_iptv_file(self, filename):
        """解析IPTV文件，提取频道名称和URL"""
        channels = []
        current_genre = ""
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 检查是否是分类行
                    if line.endswith(',#genre#'):
                        current_genre = line.replace(',#genre#', '')
                        continue
                    
                    # 检查是否是频道行
                    if ',' in line and ('http://' in line or 'https://' in line):
                        parts = line.split(',', 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            url = parts[1].strip()
                            channels.append({
                                'line_num': line_num,
                                'name': name,
                                'url': url,
                                'genre': current_genre
                            })
        except Exception as e:
            print(f"解析文件时出错: {e}")
            return []
        
        return channels
    
    def validate_url(self, channel):
        """验证单个URL是否可用"""
        url = channel['url']
        name = channel['name']
        
        try:
            # 对于m3u8文件，使用HEAD请求检查
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            
            # 检查状态码
            if response.status_code == 200:
                # 检查Content-Type
                content_type = response.headers.get('Content-Type', '').lower()
                if 'video' in content_type or 'application' in content_type or 'text' in content_type:
                    return {
                        'status': 'success',
                        'channel': channel,
                        'response_time': response.elapsed.total_seconds(),
                        'status_code': response.status_code,
                        'content_type': content_type
                    }
                else:
                    return {
                        'status': 'warning',
                        'channel': channel,
                        'response_time': response.elapsed.total_seconds(),
                        'status_code': response.status_code,
                        'content_type': content_type,
                        'message': 'Content-Type可能不正确'
                    }
            else:
                return {
                    'status': 'error',
                    'channel': channel,
                    'status_code': response.status_code,
                    'message': f'HTTP {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'error',
                'channel': channel,
                'message': '连接超时'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'error',
                'channel': channel,
                'message': '连接错误'
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'channel': channel,
                'message': f'请求错误: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'channel': channel,
                'message': f'未知错误: {str(e)}'
            }
    
    def validate_all(self, channels):
        """并发验证所有频道"""
        results = []
        print(f"开始验证 {len(channels)} 个频道...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_channel = {
                executor.submit(self.validate_url, channel): channel 
                for channel in channels
            }
            
            # 收集结果
            for i, future in enumerate(as_completed(future_to_channel), 1):
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 显示进度
                    if result['status'] == 'success':
                        print(f"[{i}/{len(channels)}] ✅ {result['channel']['name']}")
                    elif result['status'] == 'warning':
                        print(f"[{i}/{len(channels)}] ⚠️  {result['channel']['name']} - {result.get('message', '')}")
                    else:
                        print(f"[{i}/{len(channels)}] ❌ {result['channel']['name']} - {result.get('message', '')}")
                        
                except Exception as e:
                    channel = future_to_channel[future]
                    results.append({
                        'status': 'error',
                        'channel': channel,
                        'message': f'验证异常: {str(e)}'
                    })
                    print(f"[{i}/{len(channels)}] ❌ {channel['name']} - 验证异常")
        
        return results
    
    def generate_report(self, results, output_file=None):
        """生成验证报告"""
        # 统计结果
        total = len(results)
        success = len([r for r in results if r['status'] == 'success'])
        warning = len([r for r in results if r['status'] == 'warning'])
        error = len([r for r in results if r['status'] == 'error'])
        
        # 按状态分组
        success_channels = [r for r in results if r['status'] == 'success']
        warning_channels = [r for r in results if r['status'] == 'warning']
        error_channels = [r for r in results if r['status'] == 'error']
        
        # 生成报告
        report = []
        report.append("=" * 60)
        report.append("IPTV直播地址验证报告")
        report.append("=" * 60)
        report.append(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"总频道数: {total}")
        report.append(f"可用频道: {success} ({success/total*100:.1f}%)")
        report.append(f"警告频道: {warning} ({warning/total*100:.1f}%)")
        report.append(f"无效频道: {error} ({error/total*100:.1f}%)")
        report.append("")
        
        # 详细结果
        if error_channels:
            report.append("❌ 无效频道列表:")
            report.append("-" * 40)
            for result in error_channels:
                channel = result['channel']
                report.append(f"• {channel['name']} ({channel['genre']})")
                report.append(f"  URL: {channel['url']}")
                report.append(f"  错误: {result.get('message', '未知错误')}")
                report.append(f"  行号: {channel['line_num']}")
                report.append("")
        
        if warning_channels:
            report.append("⚠️  警告频道列表:")
            report.append("-" * 40)
            for result in warning_channels:
                channel = result['channel']
                report.append(f"• {channel['name']} ({channel['genre']})")
                report.append(f"  URL: {channel['url']}")
                report.append(f"  警告: {result.get('message', '')}")
                report.append(f"  行号: {channel['line_num']}")
                report.append("")
        
        if success_channels:
            report.append("✅ 可用频道列表:")
            report.append("-" * 40)
            for result in success_channels:
                channel = result['channel']
                response_time = result.get('response_time', 0)
                report.append(f"• {channel['name']} ({channel['genre']}) - {response_time:.2f}s")
        
        report_text = "\n".join(report)
        
        # 输出到控制台
        print("\n" + report_text)
        
        # 保存到文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"\n报告已保存到: {output_file}")
            except Exception as e:
                print(f"保存报告时出错: {e}")
        
        return report_text
    
    def generate_clean_iptv(self, results, output_file=None):
        """生成清理后的IPTV文件（只包含可用频道）"""
        success_results = [r for r in results if r['status'] == 'success']
        
        if not success_results:
            print("没有可用的频道，无法生成清理后的文件")
            return
        
        # 按分类组织频道
        genres = {}
        for result in success_results:
            channel = result['channel']
            genre = channel['genre']
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(channel)
        
        # 生成新文件内容
        lines = []
        for genre, channels in genres.items():
            lines.append(f"{genre},#genre#")
            for channel in channels:
                lines.append(f"{channel['name']},{channel['url']}")
            lines.append("")  # 空行分隔
        
        content = "\n".join(lines)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"清理后的IPTV文件已保存到: {output_file}")
            except Exception as e:
                print(f"保存清理文件时出错: {e}")
        
        return content

def main():
    """主函数"""
    print("IPTV直播地址验证工具")
    print("=" * 40)
    
    # 创建验证器
    validator = IPTVValidator(timeout=10, max_workers=20)
    
    # 解析IPTV文件
    iptv_file = "IPTV.txt"
    print(f"正在解析文件: {iptv_file}")
    channels = validator.parse_iptv_file(iptv_file)
    
    if not channels:
        print("没有找到有效的频道信息")
        return
    
    print(f"找到 {len(channels)} 个频道")
    
    # 验证所有频道
    results = validator.validate_all(channels)
    
    # 生成报告
    report_file = f"iptv_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    validator.generate_report(results, report_file)
    
    # 生成清理后的IPTV文件
    clean_file = f"IPTV_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    validator.generate_clean_iptv(results, clean_file)
    
    print("\n验证完成！")

if __name__ == "__main__":
    main()
