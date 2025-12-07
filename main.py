# ===================================================
# 作者: 鲁智勇
# 日期: 2025-12-06
# 功能: 个人资金管理工具
# ===================================================

import argparse
from pathlib import Path
from log_record import Logger
import finance_funcs as ff
import traceback

# 版本号
version = '1.0.0'

# ------------------ 辅助函数 ------------------
def Initialize(yaml_path, logger):
    try:
        return ff.initialize(yaml_path, logger)
    except Exception as e:
        print(f"初始化账户失败: {e}")
        if logger:
            logger.log(f"初始化账户失败: {e}")
            logger.log(traceback.format_exc())
        return None

def Expense_Mode(data, yaml_path, logger):
    try:
        ff.expense_mode(data, yaml_path, logger)
    except Exception as e:
        print(f"消费模式执行失败: {e}")
        if logger:
            logger.log(f"消费模式执行失败: {e}")
            logger.log(traceback.format_exc())

def Income_Mode(data, yaml_path, logger):
    try:
        ff.income_mode(data, yaml_path, logger)
    except Exception as e:
        print(f"工资模式执行失败: {e}")
        if logger:
            logger.log(f"工资模式执行失败: {e}")
            logger.log(traceback.format_exc())

def Income_Extra_Mode(data, yaml_path, logger):
    try:
        ff.income_extra_mode(data, yaml_path, logger)
    except Exception as e:
        print(f"收入模式执行失败: {e}")
        if logger:
            logger.log(f"收入模式执行失败: {e}")
            logger.log(traceback.format_exc())

def Add_Account(data, yaml_path, logger):
    try:
        ff.add_account(data, yaml_path, logger)
    except Exception as e:
        print(f"新增账户失败: {e}")
        if logger:
            logger.log(f"新增账户失败: {e}")
            logger.log(traceback.format_exc())

def Remove_Account(data, yaml_path, logger):
    try:
        ff.remove_account(data, yaml_path, logger)
    except Exception as e:
        print(f"删除账户失败: {e}")
        if logger:
            logger.log(f"删除账户失败: {e}")
            logger.log(traceback.format_exc())

def Query_Accounts(data, logger):
    try:
        ff.query_accounts(data, logger)
    except Exception as e:
        print(f"查询账户信息失败: {e}")
        if logger:
            logger.log(f"查询账户信息失败: {e}")
            logger.log(traceback.format_exc())

def Show_Version(version, logger):
    try:
        ff.show_version(version, logger)
    except Exception as e:
        print(f"显示版本失败: {e}")
        if logger:
            logger.log(f"显示版本失败: {e}")
            logger.log(traceback.format_exc())

def Backup_Yaml(yaml_path, logger):
    try:
        ff.backup_yaml(yaml_path, logger)
    except Exception as e:
        print(f"备份失败: {e}")
        if logger:
            logger.log(f"备份失败: {e}")
            logger.log(traceback.format_exc())

# ------------------ 主函数 ------------------
def main():
    try:
        parser = argparse.ArgumentParser(
            description="个人资金管理工具",
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument("-x", "--expense", action="store_true", help="消费模式")
        parser.add_argument("-g", "--salary", action="store_true", help="工资模式")
        parser.add_argument("-s", "--income", action="store_true", help="收入模式")
        parser.add_argument("-i", "--init", action="store_true", help="初始化账户")
        parser.add_argument("-a", "--add", action="store_true", help="新增账户")
        parser.add_argument("-r", "--remove", action="store_true", help="删除账户")
        parser.add_argument("-q", "--query", action="store_true", help="查询账户信息")
        parser.add_argument("-v", "--version", action="store_true", help="显示版本号")
        parser.add_argument("-f", "--file", type=str, default=None, help="指定 YAML 文件路径(默认工具所在路径)")

        args = parser.parse_args()

        # YAML 文件路径
        yaml_path = Path(args.file).expanduser().resolve() if args.file else Path("balance.yaml").resolve()
        
        # 初始化日志
        global logger
        if 'logger' not in globals():
            logger = Logger("finance")
            
        # 检查 YAML 文件
        data = ff.read_data(yaml_path, logger)
        if data is None:
            logger.log(f"{yaml_path} 不存在，进入初始化流程")
            data = Initialize(yaml_path, logger)
            
        if args.version:
            Show_Version(version, logger)
        elif args.query:
            Query_Accounts(data, logger)
        elif args.init:
            data = Initialize(yaml_path, logger)
        else:
            # 执行备份
            Backup_Yaml(yaml_path, logger)

            # 功能分发
            if args.expense:
                Expense_Mode(data, yaml_path, logger)
            elif args.salary:
                Income_Mode(data, yaml_path, logger)
            elif args.income:
                Income_Extra_Mode(data, yaml_path, logger)
            elif args.add:
                Add_Account(data, yaml_path, logger)
            elif args.remove:
                Remove_Account(data, yaml_path, logger)
            else:
                parser.print_help()
    except Exception as e:
        print(f"程序出现异常: {e}")
        logger.log(f"程序出现异常: {e}")
        logger.log(traceback.format_exc())

# ------------------ 启动 ------------------
if __name__ == "__main__":
    main()
