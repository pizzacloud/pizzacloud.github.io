# IPTV直播地址验证工具

这个工具可以自动验证你的IPTV直播地址是否可用，并生成清理后的播放列表。

## 📁 文件说明

- `iptv_validator.py` - 完整版验证工具（详细报告）
- `quick_validate.py` - 快速验证工具（简化版）
- `IPTV.txt` - 你的IPTV播放列表文件
- `IPTV_clean_*.txt` - 验证后生成的可用频道文件

## 🚀 使用方法

### 方法1: 快速验证（推荐）
```bash
python3 quick_validate.py
```

### 方法2: 详细验证
```bash
python3 iptv_validator.py
```

## 📊 验证结果

根据最新验证结果（2025-09-29）：

- **总频道数**: 206个
- **可用频道**: 77个 (37.4%)
- **警告频道**: 42个 (20.4%) 
- **无效频道**: 87个 (42.2%)

### ✅ 主要可用频道类别：

**4K频道**:
- CCTV4K
- 北京卫视4K
- CCTV4K(备用)

**卫视频道**:
- 重庆卫视、河北卫视、广东卫视
- 山东卫视、河南卫视、东南卫视
- 甘肃卫视、青海卫视、陕西卫视
- 西藏卫视、吉林卫视、内蒙古卫视

**国际频道**:
- CGTN News、CGTN Español、CGTN Français
- DW、Bloomberg、Russia Today
- Global News、SABC News

**法语频道**:
- ICI RDI、ICI Télé HD、ICI Montreal
- CPAC、BX1比利时、Chamber TV 卢森堡

**西班牙语频道**:
- Net TV 阿根廷、UCV Televisión智利
- El Trece 阿根廷

## 🔧 工具特性

### 完整版工具 (`iptv_validator.py`)
- ✅ 并发验证（20个线程）
- ✅ 详细错误报告
- ✅ 响应时间统计
- ✅ 按分类组织结果
- ✅ 生成详细报告文件
- ✅ 生成清理后的IPTV文件

### 快速版工具 (`quick_validate.py`)
- ✅ 超快验证（30个线程）
- ✅ 简单结果展示
- ✅ 生成可用频道文件
- ✅ 适合日常使用

## 📝 输出文件

### 验证报告
- `iptv_validation_report_YYYYMMDD_HHMMSS.txt` - 详细验证报告

### 清理后的播放列表
- `IPTV_clean_YYYYMMDD_HHMMSS.txt` - 只包含可用频道
- `IPTV_valid_YYYYMMDD_HHMMSS.txt` - 快速版生成的可用频道

## 🛠️ 自定义配置

你可以修改脚本中的参数：

```python
# 超时时间（秒）
timeout = 10

# 并发线程数
max_workers = 20

# 验证方法
# HEAD请求 - 快速但可能不准确
# GET请求 - 慢但更准确
```

## 📋 常见问题

### Q: 为什么有些频道显示"Content-Type可能不正确"？
A: 这些频道可能仍然可用，但服务器返回的Content-Type不是标准的视频类型。

### Q: 如何提高验证准确性？
A: 可以修改脚本使用GET请求而不是HEAD请求，但会显著增加验证时间。

### Q: 验证结果多久会过期？
A: IPTV地址可能会随时变化，建议定期（如每周）重新验证。

## 🔄 定期维护建议

1. **每周运行一次验证**
2. **及时更新失效的地址**
3. **备份可用的播放列表**
4. **关注新增的频道源**

## 📞 技术支持

如果遇到问题，可以：
1. 检查网络连接
2. 确认IPTV.txt文件格式正确
3. 尝试减少并发线程数
4. 增加超时时间

---

*最后更新: 2025-09-29*
