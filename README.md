# linux-toolbox-gui 🛠️
可视化 Linux 系统管理工具箱，让复杂的命令行操作变得简单直观

## ✨ 核心功能
- 📊 **系统监控**：实时查看 CPU、内存、磁盘、网络占用情况
- 🧹 **系统清理**：一键清理缓存、日志、冗余文件
- ⚡ **性能优化**：自动调整内核参数、关闭无用服务
- 📝 **日志分析**：可视化展示系统关键日志，快速定位问题
- 🔒 **安全加固**：检查系统漏洞、配置防火墙规则
- 📦 **软件管理**：一键安装/卸载常用工具，支持批量操作

## 🚀 快速安装
### 方法 1：一键脚本（推荐）
执行一键安装脚本（自动处理依赖+激活 GUI）
```bash
bash <(curl -sSL https://raw.githubusercontent.com/14uy/linux-toolbox-gui/main/linux-toolbox.py)
方法 2：克隆仓库
git clone https://github.com/14uy/linux-toolbox-gui.git
cd linux-toolbox-gui

# 安装依赖（含 GUI 库 Tkinter）
sudo apt update && sudo apt install -y python3-pip python3-tk git
pip3 install -r requirements.txt

# 启动 GUI 程序
python3 linux-toolbox.py
