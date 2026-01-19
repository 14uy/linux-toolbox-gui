#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Linux 全能工具箱 - 带自动自检修复功能
import sys
import os
import re
import shutil
import subprocess
import json
import time
import threading
from datetime import datetime
from pathlib import Path

# ====================== 自动自检修复模块 ======================
def auto_fix_current_script():
    """自动检测并修复当前脚本的常见问题"""
    script_path = os.path.abspath(__file__)
    backup_path = f"{script_path}.auto_fix.bak"

    # 1. 备份原文件（仅当备份不存在时）
    if not os.path.exists(backup_path):
        shutil.copy2(script_path, backup_path)
        print(f"🔧 自动修复：已备份原脚本到 {backup_path}")

    # 2. 读取脚本内容
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. 修复问题1：替换所有 `addWidget(` 为 `addWidget(`
    original_count = content.count("addWidget(")
    content = re.sub(r'addWidgets\(', 'addWidget(', content)
    if original_count > 0:
        print(f"🔧 自动修复：替换了 {original_count} 处 `addWidget(` → `addWidget(`")

    # 4. 修复问题2：简化字体设置代码
    font_pattern = re.compile(
        r'font = QFont\(\)\s*'
        r'font.setFamily\("Noto Sans CJK SC" if "Noto Sans CJK SC" in QFontDatabase\(\).families\(.*?\) else "Arial"\)'
    )
    if font_pattern.search(content):
        content = font_pattern.sub(r'font = QFont("Arial", 10)', content)
        print("🔧 自动修复：字体设置已简化为直接指定 Arial 字体")

    # 5. 修复问题3：清理无用的 QFontDatabase 导入
    if "from PyQt6.QtGui import QFontDatabase" in content:
        content = content.replace("from PyQt6.QtGui import QFontDatabase\n", "")
        print("🔧 自动修复：已清理无用的 QFontDatabase 导入")

    # 6. 保存修复后的内容
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 自动修复完成，继续启动程序...\n")

# ====================== 启动时自动执行修复 ======================
if __name__ == "__main__":
    auto_fix_current_script()

# PyQt6 导入
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

# ========== 跨系统兼容核心配置 ==========
class SystemDetector:
    def __init__(self):
        self.os_info = self.detect_os()
        self.pkg_manager = self.get_package_manager()
        self.commands = self.get_compatible_commands()

    def detect_os(self):
        """检测系统发行版"""
        os_info = {"id": "unknown", "name": "Unknown Linux"}
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        os_info["id"] = line.strip().split("=")[1].strip('"')
                    elif line.startswith("NAME="):
                        os_info["name"] = line.strip().split("=")[1].strip('"')
        except:
            pass
        return os_info

    def get_package_manager(self):
        """获取系统包管理器"""
        os_id = self.os_info["id"]
        pkg_map = {
            "arch": "pacman",
            "debian": "apt",
            "ubuntu": "apt",
            "centos": "dnf",
            "rhel": "dnf",
            "fedora": "dnf",
            "opensuse-leap": "zypper",
            "opensuse-tumbleweed": "zypper"
        }
        return pkg_map.get(os_id, "unknown")

    def get_compatible_commands(self):
        """生成跨系统兼容命令映射"""
        pm = self.pkg_manager
        commands = {
            # 系统更新
            "update_system": {
                "pacman": "sudo pacman -Syu --noconfirm",
                "apt": "sudo apt update && sudo apt upgrade -y",
                "dnf": "sudo dnf update -y",
                "zypper": "sudo zypper refresh && sudo zypper update -y"
            },
            "update_keyring": {
                "pacman": "sudo pacman -S archlinux-keyring --noconfirm",
                "apt": "sudo apt install --reinstall apt-key -y",
                "dnf": "sudo dnf reinstall -y rpm",
                "zypper": "sudo zypper refresh --force"
            },
            "clean_cache": {
                "pacman": "sudo pacman -Sc --noconfirm",
                "apt": "sudo apt clean && sudo apt autoclean",
                "dnf": "sudo dnf clean all",
                "zypper": "sudo zypper clean -a"
            },
            # 软件管理
            "install_pkg": {
                "pacman": "sudo pacman -S {pkg} --noconfirm",
                "apt": "sudo apt install {pkg} -y",
                "dnf": "sudo dnf install {pkg} -y",
                "zypper": "sudo zypper install {pkg} -y"
            },
            "remove_pkg": {
                "pacman": "sudo pacman -R {pkg} --noconfirm",
                "apt": "sudo apt remove {pkg} -y",
                "dnf": "sudo dnf remove {pkg} -y",
                "zypper": "sudo zypper remove {pkg} -y"
            },
            "search_pkg": {
                "pacman": "pacman -Ss {pkg}",
                "apt": "apt search {pkg}",
                "dnf": "dnf search {pkg}",
                "zypper": "zypper search {pkg}"
            },
            "list_installed": {
                "pacman": "pacman -Q",
                "apt": "apt list --installed",
                "dnf": "dnf list installed",
                "zypper": "zypper list installed"
            },
            # 系统优化
            "clean_orphans": {
                "pacman": "sudo pacman -Rns $(pacman -Qdtq) --noconfirm 2>/dev/null || echo '无孤儿包'",
                "apt": "sudo apt autoremove -y",
                "dnf": "sudo dnf autoremove -y",
                "zypper": "sudo zypper remove --clean-deps -y"
            },
            "trim_ssd": {
                "pacman": "sudo systemctl enable fstrim.timer && sudo fstrim -av",
                "apt": "sudo systemctl enable fstrim.timer && sudo fstrim -av",
                "dnf": "sudo systemctl enable fstrim.timer && sudo fstrim -av",
                "zypper": "sudo systemctl enable fstrim.timer && sudo fstrim -av"
            }
        }
        return commands

    def get_command(self, cmd_type, **kwargs):
        """获取适配当前系统的命令"""
        cmd = self.commands.get(cmd_type, {}).get(self.pkg_manager, f"echo 不支持的系统: {self.os_info['name']}")
        return cmd.format(**kwargs) if kwargs else cmd

# ========== 主程序 ==========
# 配置路径
HOME = str(Path.home())
CONFIG_DIR = os.path.join(HOME, '.config', 'linux-toolbox')
LOG_DIR = os.path.join(HOME, '.local', 'share', 'linux-toolbox', 'logs')

# 确保目录存在
for directory in [CONFIG_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# 主题配置
THEMES = {
    "light": {
        "bg_primary": "#f8f9fa",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#e9ecef",
        "text_primary": "#212529",
        "text_secondary": "#6c757d",
        "accent": "#0d6efd",
        "accent_hover": "#0b5ed7",
        "success": "#198754",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "border": "#dee2e6",
        "shadow": "rgba(0,0,0,0.08)"
    },
    "dark": {
        "bg_primary": "#121212",
        "bg_secondary": "#1e1e1e",
        "bg_tertiary": "#2d2d2d",
        "text_primary": "#f8f9fa",
        "text_secondary": "#adb5bd",
        "accent": "#0d6efd",
        "accent_hover": "#3d8bfd",
        "success": "#198754",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "border": "#495057",
        "shadow": "rgba(0,0,0,0.3)"
    }
}

class LinuxToolboxApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化系统兼容层
        self.system = SystemDetector()
        self.current_theme = "light"
        self.theme = THEMES[self.current_theme]
        self.config_file = os.path.join(CONFIG_DIR, "config.json")
        self.load_config()
        self.init_ui()

    def load_config(self):
        """加载配置文件"""
        default_config = {
            "theme": "light",
            "window_size": [1200, 800],
            "auto_check_updates": True,
            "notifications": True
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # 合并默认配置
                for key in default_config:
                    if key not in self.config:
                        self.config[key] = default_config[key]
            except:
                self.config = default_config
        else:
            self.config = default_config

        self.current_theme = self.config.get("theme", "light")
        self.theme = THEMES[self.current_theme]

    def save_config(self):
        """保存配置文件"""
        self.config["theme"] = self.current_theme
        self.config["window_size"] = [self.width(), self.height()]

        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def run_command(self, command, title="执行命令", need_sudo=False):
        """跨系统命令运行器"""
        if need_sudo and "sudo" not in command:
            command = f"sudo {command}"

        try:
            # 自动检测终端模拟器
            terminals = ["konsole", "gnome-terminal", "xfce4-terminal", "xterm", "alacritty", "kitty"]
            terminal = None

            for term in terminals:
                try:
                    subprocess.run(f"which {term}", shell=True, check=True, capture_output=True)
                    terminal = term
                    break
                except:
                    continue

            if terminal:
                if terminal == "xterm":
                    full_cmd = f"{terminal} -e 'bash -c \"{command}; echo; echo 按Enter退出...; read\"'"
                else:
                    full_cmd = f"{terminal} -e 'bash -c \"{command}; echo; read -p \\\"按Enter退出...\\\"\"'"

                subprocess.Popen(full_cmd, shell=True)
                return True, f"[{self.system.os_info['name']}] 命令正在终端执行..."
            else:
                # 无终端时后台执行
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    return True, f"执行成功\n输出:\n{result.stdout[:500]}"
                else:
                    return False, f"执行失败\n错误:\n{result.stderr[:500]}"

        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except subprocess.CalledProcessError as e:
            return False, f"错误代码: {e.returncode}\n错误信息:\n{e.stderr[:500]}"
        except Exception as e:
            return False, f"执行异常: {str(e)}"

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f"Linux 全能工具箱 - [{self.system.os_info['name']}]")
        self.setMinimumSize(1000, 700)
        self.apply_theme()

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        self.create_title_bar(main_layout)

        # 主体内容
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 左侧导航
        self.create_sidebar(content_layout)

        # 右侧内容栈
        self.content_stack = QStackedWidget()
        self.create_content_pages()
        content_layout.addWidget(self.content_stack)

        main_layout.addWidget(content_widget)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"就绪 | 当前系统: {self.system.os_info['name']} | 包管理器: {self.system.pkg_manager}")

        # 恢复窗口大小
        if "window_size" in self.config:
            self.resize(self.config["window_size"][0], self.config["window_size"][1])

    def create_title_bar(self, parent_layout):
        """标题栏"""
        title_bar = QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)

        icon_label = QLabel("🐧")
        icon_label.setStyleSheet("font-size: 20px;")
        title_layout.addWidget(icon_label)

        title_label = QLabel("Linux 全能工具箱")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {self.theme['text_primary']};")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # 主题切换
        self.theme_btn = QPushButton("🌙" if self.current_theme == "light" else "☀️")
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setToolTip("切换主题")
        title_layout.addWidget(self.theme_btn)

        # 窗口控制
        min_btn = QPushButton("─")
        min_btn.setFixedSize(36, 36)
        min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        parent_layout.addWidget(title_bar)

    def create_sidebar(self, parent_layout):
        """左侧导航栏"""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)

        # 导航按钮
        nav_buttons = [
            ("📊 系统监控", self.show_system_monitor),
            ("🔄 系统更新", self.show_system_update),
            ("⚡ 系统优化", self.show_system_optimize),
            ("📦 软件管理", self.show_package_manager),
            ("🌐 网络工具", self.show_network_tools),
            ("🤖 AI助手", self.show_ai_assistant),
            ("⚙️ 系统设置", self.show_system_settings),
        ]

        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # 系统信息卡片
        sys_info = QWidget()
        sys_layout = QVBoxLayout(sys_info)
        sys_layout.setContentsMargins(15, 15, 15, 15)

        sys_label = QLabel("系统信息")
        sys_label.setStyleSheet(f"font-weight: bold; color: {self.theme['text_secondary']};")
        sys_layout.addWidget(sys_label)

        self.sys_info_label = QLabel(f"""
        系统: {self.system.os_info['name']}
        包管理器: {self.system.pkg_manager}
        内核: {subprocess.run('uname -r', shell=True, capture_output=True, text=True).stdout.strip()}
        """)
        self.sys_info_label.setWordWrap(True)
        sys_layout.addWidget(self.sys_info_label)

        sidebar_layout.addWidget(sys_info)
        parent_layout.addWidget(sidebar)

        # 定时更新系统信息
        QTimer.singleShot(1000, self.update_system_info)

    def create_content_pages(self):
        """创建所有功能页面"""
        self.content_stack.addWidget(self.create_system_monitor_page())
        self.content_stack.addWidget(self.create_system_update_page())
        self.content_stack.addWidget(self.create_system_optimize_page())
        self.content_stack.addWidget(self.create_package_manager_page())
        self.content_stack.addWidget(self.create_network_tools_page())
        self.content_stack.addWidget(self.create_ai_assistant_page())
        self.content_stack.addWidget(self.create_system_settings_page())

    def apply_theme(self):
        """应用主题样式"""
        theme = self.theme
        style = f"""
        QMainWindow {{
            background-color: {theme['bg_primary']};
        }}
        #titleBar {{
            background-color: {theme['bg_secondary']};
            border-bottom: 1px solid {theme['border']};
        }}
        #sidebar {{
            background-color: {theme['bg_secondary']};
            border-right: 1px solid {theme['border']};
        }}
        QPushButton {{
            background-color: {theme['bg_tertiary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 10px 15px;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {theme['accent']};
            color: white;
        }}
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {theme['border']};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            color: {theme['text_primary']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
        }}
        QLineEdit, QTextEdit {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
        }}
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        QStatusBar {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_secondary']};
            border-top: 1px solid {theme['border']};
        }}
        """
        self.setStyleSheet(style)

    def toggle_theme(self):
        """切换明暗主题"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.theme = THEMES[self.current_theme]
        self.apply_theme()
        self.theme_btn.setText("🌙" if self.current_theme == "light" else "☀️")
        self.theme_combo.setCurrentText("浅色主题" if self.current_theme == "light" else "深色主题")

    # ========== 页面切换函数 ==========
    def show_system_monitor(self): self.content_stack.setCurrentIndex(0); self.update_system_monitor()
    def show_system_update(self): self.content_stack.setCurrentIndex(1)
    def show_system_optimize(self): self.content_stack.setCurrentIndex(2)
    def show_package_manager(self): self.content_stack.setCurrentIndex(3)
    def show_network_tools(self): self.content_stack.setCurrentIndex(4); self.check_network_status()
    def show_ai_assistant(self): self.content_stack.setCurrentIndex(5)
    def show_system_settings(self): self.content_stack.setCurrentIndex(6)

    # ========== 系统监控页面 ==========
    def create_system_monitor_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("📊 系统监控")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme['text_primary']}; margin: 20px;")
        layout.addWidget(title)

        # 系统概览
        info_card = QGroupBox("系统概览")
        info_layout = QVBoxLayout()
        self.sys_monitor_label = QLabel("正在获取信息...")
        info_layout.addWidget(self.sys_monitor_label)
        refresh_btn = QPushButton("刷新信息")
        refresh_btn.clicked.connect(self.update_system_monitor)
        info_layout.addWidget(refresh_btn)
        info_card.setLayout(info_layout)
        layout.addWidget(info_card)

        # 进程管理
        proc_card = QGroupBox("进程管理")
        proc_layout = QVBoxLayout()
        self.process_text = QTextEdit()
        self.process_text.setReadOnly(True)
        self.process_text.setMaximumHeight(200)
        proc_layout.addWidget(self.process_text)
        proc_btn_layout = QHBoxLayout()
        refresh_proc_btn = QPushButton("刷新进程")
        refresh_proc_btn.clicked.connect(self.refresh_process_list)
        proc_btn_layout.addWidget(refresh_proc_btn)

        kill_proc_btn = QPushButton("结束进程")
        kill_proc_btn.clicked.connect(self.kill_process_dialog)
        proc_btn_layout.addWidget(kill_proc_btn)

        proc_layout.addLayout(proc_btn_layout)
        proc_card.setLayout(proc_layout)
        layout.addWidget(proc_card)

        layout.addStretch()
        self.update_system_monitor()
        return widget

    def update_system_monitor(self):
        try:
            mem = subprocess.run("free -h | grep Mem", shell=True, capture_output=True, text=True).stdout.strip()
            disk = subprocess.run("df -h / | tail -1", shell=True, capture_output=True, text=True).stdout.strip()
            load = subprocess.run("cat /proc/loadavg", shell=True, capture_output=True, text=True).stdout.strip()
            self.sys_monitor_label.setText(f"""
            <b>内存使用:</b><br>{mem}<br><br>
            <b>磁盘使用:</b><br>{disk}<br><br>
            <b>系统负载:</b><br>{load}
            """)
            self.refresh_process_list()
        except Exception as e:
            self.sys_monitor_label.setText(f"获取信息失败: {str(e)}")

    def refresh_process_list(self):
        try:
            result = subprocess.run("ps aux --sort=-%cpu | head -20", shell=True, capture_output=True, text=True)
            self.process_text.setPlainText(result.stdout)
        except Exception as e:
            self.process_text.setPlainText(f"失败: {str(e)}")

    def kill_process_dialog(self):
        pid, ok = QInputDialog.getText(self, "结束进程", "输入PID:")
        if ok and pid:
            success, msg = self.run_command(f"kill -9 {pid}", "结束进程")
            QMessageBox.information(self, "成功" if success else "失败", msg)
            self.refresh_process_list()

    # ========== 系统更新页面 ==========
    def create_system_update_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("🔄 系统更新")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme['text_primary']}; margin: 20px;")
        layout.addWidget(title)

        # 更新状态
        status_card = QGroupBox("更新状态")
        status_layout = QVBoxLayout()
        self.update_status_label = QLabel("点击检查更新")
        status_layout.addWidget(self.update_status_label)
        check_btn = QPushButton("检查更新")
        check_btn.clicked.connect(self.check_system_updates)
        status_layout.addWidget(check_btn)
        status_card.setLayout(status_layout)
        layout.addWidget(status_card)

        # 跨系统更新操作
        update_card = QGroupBox("更新操作")
        update_layout = QVBoxLayout()
        buttons = [
            ("完整系统更新", lambda: self.run_command(self.system.get_command("update_system"), "系统更新", True)),
            ("更新密钥/签名", lambda: self.run_command(self.system.get_command("update_keyring"), "更新密钥", True)),
            ("清理包缓存", lambda: self.run_command(self.system.get_command("clean_cache"), "清理缓存", True)),
        ]
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            update_layout.addWidget(btn)
        update_card.setLayout(update_layout)
        layout.addWidget(update_card)

        # Arch专属镜像源优化
        if self.system.pkg_manager == "pacman":
            mirror_card = QGroupBox("镜像源优化 (Arch专属)")
            mirror_layout = QVBoxLayout()
            mirror_btn = QPushButton("优化国内镜像源")
            mirror_btn.clicked.connect(lambda: self.run_command("sudo reflector --country China --latest 10 --sort rate --save /etc/pacman.d/mirrorlist && sudo pacman -Syy", "镜像源优化", True))
            mirror_layout.addWidget(mirror_btn)
            mirror_card.setLayout(mirror_layout)
            layout.addWidget(mirror_card)

        layout.addStretch()
        return widget

    def check_system_updates(self):
        self.status_bar.showMessage("正在检查更新...")
        try:
            if self.system.pkg_manager == "pacman":
                result = subprocess.run("pacman -Qu", shell=True, capture_output=True, text=True)
                updates = len(result.stdout.strip().split('\n')) if result.stdout else 0
                self.update_status_label.setText(f"发现 {updates} 个更新" if updates else "系统已是最新")
            else:
                self.update_status_label.setText(f"[{self.system.os_info['name']}] 请点击更新按钮执行更新")
            self.status_bar.showMessage("检查完成")
        except Exception as e:
            self.update_status_label.setText(f"检查失败: {str(e)}")

    # ========== 系统优化页面 ==========
    def create_system_optimize_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("⚡ 系统优化")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme['text_primary']}; margin: 20px;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 清理功能
        clean_group = QGroupBox("🧹 清理功能")
        clean_layout = QVBoxLayout()
        clean_buttons = [
            ("深度清理缓存", self.system.get_command("clean_cache")),
            ("清理孤儿包", self.system.get_command("clean_orphans")),
            ("清理旧日志", "sudo journalctl --vacuum-time=7d"),
            ("清理浏览器缓存", "rm -rf ~/.cache/*/Cache/* ~/.cache/*/cache2/* 2>/dev/null || true")
        ]
        for text, cmd in clean_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, c=cmd: self.run_command(c, text, "sudo" in c))
            clean_layout.addWidget(btn)
        clean_group.setLayout(clean_layout)
        scroll_layout.addWidget(clean_group)

        # 性能优化
        perf_group = QGroupBox("🚀 性能优化")
        perf_layout = QVBoxLayout()
        perf_buttons = [
            ("SSD TRIM优化", self.system.get_command("trim_ssd")),
            ("优化Swappiness", "echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.d/99-swappiness.conf && sudo sysctl -p"),
            ("重建字体缓存", "sudo fc-cache -fv"),
            ("更新系统数据库", "sudo updatedb")
        ]
        for text, cmd in perf_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, c=cmd: self.run_command(c, text, True))
            perf_layout.addWidget(btn)
        perf_group.setLayout(perf_layout)
        scroll_layout.addWidget(perf_group)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        return widget

    # ========== 软件管理页面 ==========
    def create_package_manager_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("📦 软件管理")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme['text_primary']}; margin: 20px;")
        layout.addWidget(title)

        # 搜索功能
        search_card = QGroupBox("搜索软件包")
        search_layout = QVBoxLayout()
        search_box = QHBoxLayout()
        self.pkg_search_input = QLineEdit()
        self.pkg_search_input.setPlaceholderText("输入包名...")
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search_packages)
        search_box.addWidget(self.pkg_search_input)
        search_box.addWidget(search_btn)
        search_layout.addLayout(search_box)
        search_card.setLayout(search_layout)
        layout.addWidget(search_card)

        # 快速操作
        quick_card = QGroupBox("快速操作")
        quick_layout = QVBoxLayout()
        quick_buttons = [
            ("安装软件包", self.install_package_dialog),
            ("卸载软件包", self.remove_package_dialog),
            ("查看已安装包", lambda: self.run_command(self.system.get_command("list_installed"), "已安装包列表")),
        ]
        for text, func in quick_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            quick_layout.addWidget(btn)
        quick_card.setLayout(quick_layout)
        layout.addWidget(quick_card)

        layout.addStretch()
        return widget

    def search_packages(self):
        pkg = self.pkg_search_input.text().strip()
        if not pkg:
            QMessageBox.warning(self, "提示", "请输入包名")
            return
        success, msg = self.run_command(self.system.get_command("search_pkg", pkg=pkg), f"搜索 {pkg}")
        dialog = QDialog(self)
        dialog.setWindowTitle(f"搜索结果: {pkg}")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setPlainText(msg)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        dialog.exec()

    def install_package_dialog(self):
        pkg, ok = QInputDialog.getText(self, "安装软件包", "输入包名:")
        if ok and pkg:
            success, msg = self.run_command(self.system.get_command("install_pkg", pkg=pkg), f"安装 {pkg}", True)
            QMessageBox.information(self, "成功" if success else "失败", msg)

    def remove_package_dialog(self):
        pkg, ok = QInputDialog.getText(self, "卸载软件包", "输入包名:")
        if ok and pkg:
            success, msg = self.run_command(self.system.get_command("remove_pkg", pkg=pkg), f"卸载 {pkg}", True)
            QMessageBox.information(self, "成功" if success else "失败", msg)

    # ========== 网络工具页面 ==========
    def create_network_tools_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("🌐 网络工具")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme['text_primary']}; margin: 20px;")
        layout.addWidget(title)

        # 网络状态
        status_card = QGroupBox("网络状态")
        status_layout = QVBoxLayout()
        self.net_status_label = QLabel("正在获取状态...")
        status_layout.addWidget(self.net_status_label)
        refresh_btn = QPushButton("刷新状态")
        refresh_btn.clicked.connect(self.check_network_status)
        status_layout.addWidget(refresh_btn)
        status_card.setLayout(status_layout)
        layout.addWidget(status_card)

        # 网络诊断
        diag_card = QGroupBox("网络诊断")
        diag_layout = QVBoxLayout()
        diag_buttons = [
            ("Ping测试", "ping -c 4 8.8.8.8"),
            ("DNS测试", "nslookup google.com 8.8.8.8"),
            ("路由跟踪", "traceroute 8.8.8.8"),
            ("查看连接", "ss -tulpn")
        ]
        for text, cmd in diag_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, c=cmd: self.run_command(c, text))
            diag_layout.addWidget(btn)
        diag_card.setLayout(diag_layout)
        layout.addWidget(diag_card)

        layout.addStretch()
        return widget

    def check_network_status(self):
        try:
            ping = subprocess.run("ping -c 1 -W 1 8.8.8.8", shell=True, capture_output=True)
            online = ping.returncode == 0
            ip = subprocess.run("ip addr show | grep 'inet ' | grep -v '127.0.0.1'", shell=True, capture_output=True, text=True).stdout.strip()
            self.net_status_label.setText(f"状态: {'✅ 在线' if online else '❌ 离线'}\n\nIP地址:\n{ip[:200]}")
        except Exception as e:
            self.net_status_label.setText(f"获取失败: {str(e)}")

    # ========== AI助手页面 ==========
    def create_ai_assistant_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("🤖 AI助手")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme['text_primary']}; margin: 20px;")
        layout.addWidget(title)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(300)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("输入问题，按Enter发送...")
        self.chat_input.returnPressed.connect(self.send_ai_message)
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self.send_ai_message)
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

        # 快捷问题
        quick_layout = QHBoxLayout()
        quick_questions = ["系统更新慢", "清理缓存", "网络问题", "安装软件"]
        for q in quick_questions:
            btn = QPushButton(q)
            btn.clicked.connect(lambda checked, q=q: self.ask_quick_question(q))
            quick_layout.addWidget(btn)
        layout.addLayout(quick_layout)

        # 欢迎语
        welcome = f"""
        <div style='color: {self.theme['accent']}; font-weight: bold;'>Linux AI助手</div>
        <div style='color: {self.theme['text_secondary']}; margin-top: 10px;'>
        支持 {self.system.os_info['name']} 系统问题解答，输入问题即可查询！
        </div>
        """
        self.chat_display.setHtml(welcome)
        return widget

    def send_ai_message(self):
        question = self.chat_input.text().strip()
        if not question:
            return
        self.add_chat_message("user", question)
        self.chat_input.clear()
        self.process_ai_reply(question)

    def ask_quick_question(self, q):
        self.chat_input.setText(q)
        self.send_ai_message()

    def add_chat_message(self, sender, msg):
        ts = datetime.now().strftime("%H:%M")
        if sender == "user":
            color, align, name = self.theme['accent'], "right", "你"
        else:
            color, align, name = self.theme['bg_tertiary'], "left", "AI助手"

        html = f"""
        <div style='margin:10px 0; text-align:{align};'>
            <div style='display:inline-block; max-width:80%;'>
                <div style='font-size:12px; color:{self.theme['text_secondary']}; margin-bottom:2px;'>
                    {name} · {ts}
                </div>
                <div style='background:{color}; color:{self.theme['text_primary'] if sender!="user" else "white"}; padding:10px 15px; border-radius:18px; word-wrap:break-word;'>
                    {msg.replace(chr(10), '<br>')}
                </div>
            </div>
        </div>
        """
        self.chat_display.setHtml(self.chat_display.toHtml() + html)
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def process_ai_reply(self, question):
        rules = {
            "系统更新慢": f"[{self.system.os_info['name']}] 尝试清理缓存后重试更新，或更换官方镜像源。",
            "清理缓存": f"执行【系统优化】中的深度清理缓存功能，命令: {self.system.get_command('clean_cache')}",
            "网络问题": "尝试重启网络服务: sudo systemctl restart NetworkManager，或检查DNS配置。",
            "安装软件": f"使用【软件管理】页面安装，或命令: {self.system.get_command('install_pkg', pkg='软件名')}"
        }
        reply = rules.get(question, "可查询系统更新、清理缓存、网络问题、软件安装等内容，尝试更具体的问题。")
        self.add_chat_message("ai", reply)

    # ========== 系统设置页面 ==========
    def create_system_settings_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("⚙️ 系统设置")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme['text_primary']}; margin: 20px;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 外观设置
        appearance_card = QGroupBox("外观设置")
        appearance_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题"])
        self.theme_combo.setCurrentText("浅色主题" if self.current_theme == "light" else "深色主题")
        self.theme_combo.currentTextChanged.connect(lambda t: self.change_theme_setting(t))
        appearance_layout.addWidget(QLabel("主题:"))
        appearance_layout.addWidget(self.theme_combo)
        appearance_card.setLayout(appearance_layout)
        scroll_layout.addWidget(appearance_card)

        # 工具箱设置
        toolbox_card = QGroupBox("工具箱设置")
        toolbox_layout = QVBoxLayout()
        self.auto_update_check = QCheckBox("启动时自动检查更新")
        self.auto_update_check.setChecked(self.config.get("auto_check_updates", True))
        self.auto_update_check.stateChanged.connect(lambda s: self.config.update({"auto_check_updates": s==Qt.CheckState.Checked.value}))
        toolbox_layout.addWidget(self.auto_update_check)
        toolbox_card.setLayout(toolbox_layout)
        scroll_layout.addWidget(toolbox_card)

        # 系统工具
        system_card = QGroupBox("系统工具")
        system_layout = QVBoxLayout()
        system_buttons = [
            ("查看系统日志", lambda: self.run_command("journalctl -n 50 --no-pager", "系统日志", True)),
            ("清理工具箱缓存", self.clean_toolbox_cache),
            ("重置工具箱设置", self.reset_toolbox_settings),
        ]
        for text, func in system_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            system_layout.addWidget(btn)
        system_card.setLayout(system_layout)
        scroll_layout.addWidget(system_card)

        # 关于
        about_card = QGroupBox("关于")
        about_layout = QVBoxLayout()
        about_layout.addWidget(QLabel(f"""
        <b>Linux 全能工具箱</b><br>
        版本: 3.0<br>
        兼容系统: Arch/Debian/Ubuntu/CentOS/Fedora/openSUSE<br>
        当前运行: {self.system.os_info['name']}
        """))
        about_card.setLayout(about_layout)
        scroll_layout.addWidget(about_card)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        return widget

    def change_theme_setting(self, theme_text):
        self.current_theme = "light" if "浅色" in theme_text else "dark"
        self.theme = THEMES[self.current_theme]
        self.apply_theme()
        self.theme_btn.setText("🌙" if self.current_theme == "light" else "☀️")

    def clean_toolbox_cache(self):
        try:
            import shutil
            shutil.rmtree(os.path.join(HOME, '.cache', 'linux-toolbox'), ignore_errors=True)
            QMessageBox.information(self, "成功", "缓存已清理")
        except Exception as e:
            QMessageBox.critical(self, "失败", f"错误: {str(e)}")

    def reset_toolbox_settings(self):
        if QMessageBox.question(self, "确认", "是否重置所有设置？") == QMessageBox.StandardButton.Yes:
            os.remove(self.config_file) if os.path.exists(self.config_file) else None
            self.config = {"theme": "light", "auto_check_updates": True}
            self.current_theme = "light"
            self.apply_theme()
            QMessageBox.information(self, "成功", "设置已重置")

    # ========== 通用函数 ==========
    def update_system_info(self):
        try:
            uptime = subprocess.run("uptime -p", shell=True, capture_output=True, text=True).stdout.strip()
            self.sys_info_label.setText(f"""
            系统: {self.system.os_info['name']}
            包管理器: {self.system.pkg_manager}
            内核: {subprocess.run('uname -r', shell=True, capture_output=True, text=True).stdout.strip()}
            运行时间: {uptime}
            """)
        except:
            pass

    def closeEvent(self, event):
        self.save_config()
        event.accept()

# ========== 启动程序 ==========
def main():
    if sys.version_info < (3, 6):
        print("需要Python 3.6+")
        return

    app = QApplication(sys.argv)
    app.setApplicationName("Linux Toolbox")

    # 简化字体设置
    font = QFont("Arial", 10)
    app.setFont(font)

    # 创建并显示窗口
    window = LinuxToolboxApp()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
