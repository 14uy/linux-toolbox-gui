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
### 方法 1：一键运行（适合快速体验）
```bash
# 一键运行（跳过 SSL 验证，适配网络环境受限的情况）
python3 <(curl -sSLk https://raw.githubusercontent.com/14uy/linux-toolbox-gui/main/linux-toolbox.py)
方法 1 补充：更稳妥的“下载后运行”（推荐）
 
避免管道执行导致的命名管道问题，先下载到本地再运行：
# 1. 下载脚本到本地（跳过 SSL 验证）
curl -sSLk https://raw.githubusercontent.com/14uy/linux-toolbox-gui/main/linux-toolbox.py > linux-toolbox.py

# 2. 赋予执行权限（可选，方便后续直接运行）
chmod +x linux-toolbox.py

# 3. 启动 GUI 程序
python3 linux-toolbox.py

方法 2：克隆仓库（适合开发/修改）
# 克隆仓库
git clone https://github.com/14uy/linux-toolbox-gui.git
cd linux-toolbox-gui

# 安装依赖（含 GUI 库 Tkinter）
sudo apt update && sudo apt install -y python3-pip python3-tk git
pip3 install -r requirements.txt

# 启动 GUI 程序
python3 linux-toolbox.py
