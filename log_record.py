#! /usr/bin/env python3
import atexit
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import datetime

# 获取当前脚本所在的目录
current_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
log_directory = os.path.join(current_directory, "logs")  # 日志文件夹路径

if not os.path.exists(log_directory):
    os.makedirs(log_directory)  # 如果文件夹不存在，创建它

class Logger:
    _instances = {}

    def __new__(cls, task_name, debug_enabled=False):
        """保证同一 task_name 只有一个 Logger 实例"""
        if task_name not in cls._instances:
            cls._instances[task_name] = super().__new__(cls)
        return cls._instances[task_name]

    def __init__(self, task_name, debug_enabled=False):
        # 防止重复初始化
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.logger = logging.getLogger(f"Debug_{task_name}")
        self.logger.setLevel(logging.DEBUG)
        self.name = f"{task_name}_{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
        self.debug_log_file = os.path.join(log_directory, self.name)
        self.debug_enabled = debug_enabled

        # 检查是否已经存在相同 handler，避免重复添加
        if not any(isinstance(h, TimedRotatingFileHandler) and h.baseFilename == self.debug_log_file
                   for h in self.logger.handlers):
            file_handler = TimedRotatingFileHandler(
                self.debug_log_file, when='midnight', interval=1, backupCount=5)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        atexit.register(self.close_logger)

    def log(self, message):
        self.logger.debug(message)

    def space(self):
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.stream.write('\n')

    def close_logger(self):
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.stream.write('\n' + '-' * 50 + ' End of Log ' + '-' * 50 + '\n')
                handler.flush()
                handler.close()
                self.logger.removeHandler(handler)
