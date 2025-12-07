# ===================================================
# 作者: 鲁智勇
# 日期: 2025-12-06
# 功能: 个人资金管理工具
# ===================================================

import re
import yaml
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

SYSTEM_KEYS = {
    "balance-all",
    "history",
    "Default_consumption",
    "Default_income",
    "Default_salary",
}

# ------------------ 读取数据 ------------------
def read_data(yaml_path, logger=None):
    if not yaml_path.exists():
        if logger: logger.log(f"{yaml_path} 不存在")
        return None
    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        if data:
            data = normalize_data(data)
        if logger: logger.log(f"读取 YAML 文件: {yaml_path}")
        return data if data else None

def normalize_data(data):
    for key, value in data.items():
        if key in ("history", "Default_consumption", "Default_income", "Default_salary"):
            continue
        if value is None:
            continue
        data[key] = Decimal(str(value))
    return data

# ------------------ 写入数据 ------------------
def write_data(data, yaml_path, logger=None):
    safe_data = to_yaml_safe(data)

    tmp_path = yaml_path.with_suffix(".tmp")

    with tmp_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            safe_data,
            f,
            allow_unicode=True,
            sort_keys=False
        )

    tmp_path.replace(yaml_path)

    if logger:
        logger.log(f"写入 YAML 文件: {yaml_path}")

def to_yaml_safe(obj):
    from decimal import Decimal

    if isinstance(obj, Decimal):
        return format(obj.quantize(Decimal("0.01")), "f")

    if isinstance(obj, dict):
        return {k: to_yaml_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [to_yaml_safe(v) for v in obj]

    return obj

# ------------------ 初始化 --------------------
def initialize(yaml_path, logger=None):
    print("==== 初始化账户 ====")
    accounts_input = input("请输入账户名称，用空格分隔: ").strip()
    accounts = accounts_input.split()
    if not accounts:
        print("未输入账户，初始化失败")
        if logger: logger.log("初始化失败，未输入账户")
        exit(1)

    data = {"history": []}
    total = Decimal("0")   # ✅ 关键

    for acc in accounts:
        while True:
            amount_input = input(f"请输入账户 {acc} 的初始金额: ").strip()
            try:
                amount = Decimal(amount_input)
                break
            except:
                print("输入金额无效，请重新输入")

        data[acc] = amount
        total += amount     # ✅ 安全
    data["balance-all"] = total
    data["Default_consumption"] = None
    data["Default_income"] = None
    data["Default_salary"] = None
    # print(f"1111111: {data}")
    write_data(data, yaml_path, logger)
    print("初始化完成！")
    if logger: logger.log(f"初始化账户: {accounts}, 总资金: {total}")
    return data

# ---------------- 金额解析函数 -----------------
def parse_amount(text):
    """
    返回金额，或 None（非法）
    消费：-10 / 午饭-10
    收入：+50 / 工资5000
    """
    match = re.search(r"([+-])\s*(\d+(?:\.\d+)?)", text)
    if not match:
        return None

    sign, value = match.groups()
    amount = Decimal(value)
    return -amount if sign == "-" else amount

# ------------------ 选择账户 ------------------
def select_account(data, logger=None):
    accounts = [acc for acc in data.keys() if acc not in SYSTEM_KEYS]
    if not accounts:
        print("当前没有可用账户")
        return None
    print("请选择账户：")
    for i, acc in enumerate(accounts):
        print(f"{i+1}. {acc} (余额: {data[acc]})")
    while True:
        choice = input("输入数字选择账户: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(accounts):
            if logger: logger.log(f"选择账户: {accounts[int(choice)-1]}")
            return accounts[int(choice)-1]
        print("选择无效，请重新输入")

# ----------------- 输入功能信息 ----------------
def get_user_input(func_name, account):
    if func_name == "消费":
        user_input = input(f"输入'/切换', '/switch' 切换消费账户\n当前消费账户[{account}]: ").strip()
    elif func_name == "收入":
        user_input = input(f"输入'/切换', '/switch' 切换收入账户\n当前收入账户[{account}]: ").strip()
    elif func_name == "工资":
        user_input = input(f"输入'/切换', '/switch' 切换工资账户\n当前工资账户[{account}]: ").strip()
    return user_input

# ----------------- 智能选择账户 ----------------
def select_account_with_default(data, default_key, func_name, yaml_path, logger=None):
    accounts = [acc for acc in data.keys() if acc not in SYSTEM_KEYS]

    default_name = {"消费": "Default_consumption",
                    "收入": "Default_income",
                    "工资": "Default_salary"}
    if not accounts:
        print("当前没有可用账户")
        return None, None
    
    # print(f"default_key: {default_key}")
    default_account = data.get(default_key)
    # print(f"default_account: {default_account}")
    current_account = default_account if default_account in accounts else select_account(data, logger)

    print(f"输入格式为：\n  信息(+/-)数字\n  工资模式只需要输入数字\n  例如：午饭-10 或 朋友还钱+50\n")
        
    # ✅ 有默认账户，且账户仍存在
    while True:
        user_input = get_user_input(func_name, current_account)

        # ✅ 路径一：切换账户（循环）
        if user_input.lower() in ("/切换", "/switch"):
            current_account = select_account(data, logger)
            continue
        
        # ✅ 校验金额
        if func_name != "工资":
            amount = parse_amount(user_input)
            if amount is None:
                print("❌ 金额格式错误，请重新输入（如：午饭-10）")
                continue
        
        # ✅ 路径二：进入下一步（结束循环）
        if logger:
            logger.log(f"{func_name} - 使用账户: {current_account}")

        data[default_name[func_name]] = current_account
        write_data(data, yaml_path, logger)
            
        return current_account, user_input

# ------------------ 消费 ------------------
def expense_mode(data, yaml_path, logger=None):
    account, user_input = select_account_with_default(
        data, "Default_consumption", "消费", yaml_path, logger
    )
    
    amounts = re.findall(r"-\s*(\d+(?:\.\d+)?)", user_input)
    # print(f'account: {account}')
    if not amounts:
        print("未找到有效消费金额")
        if logger: logger.log("消费失败，未找到有效金额")
        return
    total_expense = sum(Decimal(x) for x in amounts).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    data[account] -= Decimal(total_expense)
    data["balance-all"] -= Decimal(total_expense)
    data["history"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "消费",
        "record": user_input,
        "expense": format(total_expense, "f"),
        "balance-all": data["balance-all"],
        account: data[account]
    })
    write_data(data, yaml_path, logger)
    print(f"消费成功！{account} 余额: {data[account]} , 总余额: {data['balance-all']}")
    if logger: logger.log(f"消费记录: {user_input}, 账户: {account}, 消费金额: {total_expense}")

# ------------------ 工资模式 ------------------
def income_mode(data, yaml_path, logger=None):
    account, user_input = select_account_with_default(
        data, "Default_salary", "工资", yaml_path, logger
    )
    try:
        salary = Decimal(user_input).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except:
        print("输入金额无效")
        if logger: logger.log("工资增加失败，输入金额无效")
        return
    data[account] += Decimal(salary)
    data["balance-all"] += Decimal(salary)
    data["history"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "工资",
        "salary": format(salary, "f"),
        "balance-all": data["balance-all"],
        account: data[account]
    })
    write_data(data, yaml_path, logger)
    print(f"工资增加成功！{account} 余额: {data[account]} , 总余额: {data['balance-all']}")
    if logger: logger.log(f"工资增加: {salary}, 账户: {account}")

# ------------------ 收入模式 ------------------
def income_extra_mode(data, yaml_path, logger=None):
    account, user_input = select_account_with_default(
        data, "Default_income", "收入", yaml_path, logger
    )

    amounts = re.findall(r"\+?\s*(\d+(?:\.\d+)?)", user_input)
    if not amounts:
        print("未找到有效收入金额")
        if logger: logger.log("收入记录失败，未找到有效金额")
        return
    total_income = sum(Decimal(x) for x in amounts).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    data[account] += Decimal(total_income)
    data["balance-all"] += Decimal(total_income)
    data["history"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "收入",
        "record": user_input,
        "income": format(total_income, "f"),
        "balance-all": data["balance-all"],
        account: data[account]
    })
    write_data(data, yaml_path, logger)
    print(f"收入成功！{account} 余额: {data[account]} , 总余额: {data['balance-all']}")
    if logger: logger.log(f"收入记录: {user_input}, 账户: {account}, 金额: {total_income}")

# ------------------ 增加账户 ------------------
def add_account(data, yaml_path, logger=None):
    new_acc = input("请输入要新增的账户名称: ").strip()
    if new_acc in data:
        print("该账户已存在！")
        if logger: logger.log(f"新增账户失败: {new_acc} 已存在")
        return
    while True:
        amount_input = input(f"请输入账户 {new_acc} 的初始金额: ").strip()
        try:
            amount = Decimal(amount_input)
            break
        except:
            print("输入金额无效，请重新输入")
    data[new_acc] = amount
    data["balance-all"] += amount
    write_data(data, yaml_path, logger)
    print(f"新增账户 {new_acc} 成功，初始金额 {amount}，总资金 {data['balance-all']}")
    if logger: logger.log(f"新增账户: {new_acc}, 初始金额: {amount}")

# ------------------ 查询账户信息 ------------------
def query_accounts(data, logger=None):
    print("==== 当前账户信息 ====")

    # ✅ 先打印总余额
    if "balance-all" in data:
        print(f"balance-all: {data['balance-all']}")

    # ✅ 再打印其他账户
    for acc, val in data.items():
        if acc in SYSTEM_KEYS:
            continue
        if acc == "balance-all":
            continue
        print(f"{acc}: {val}")

    print("======================")

    if logger:
        logger.log(
            f"查询账户信息: "
            f"{[f'{acc}:{val}' for acc, val in data.items() if acc != 'history']}"
        )

# ------------------ 显示版本 ------------------
def show_version(version, logger):
    print(f"版本：{version}")
    logger.log(f"查看版本: {version}")

# ------------------ 减少账户 ------------------
def remove_account(data, yaml_path, logger=None):
    # 过滤出可删除的账户
    accounts = [acc for acc in data.keys() if acc not in SYSTEM_KEYS]
    if not accounts:
        print("没有可删除的账户")
        if logger: logger.log("尝试删除账户，但无可删除账户")
        return

    print("可删除账户列表：")
    for i, acc in enumerate(accounts):
        print(f"{i+1}. {acc} (余额: {data[acc]})")

    while True:
        choice = input("请输入要删除的账户编号: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(accounts):
            acc_to_remove = accounts[int(choice)-1]
            break
        print("输入无效，请重新输入")

    # 二次确认
    confirm = input(f"确认删除账户 {acc_to_remove}？账户余额 {data[acc_to_remove]} 将从总资金中扣除！(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消删除操作")
        if logger: logger.log(f"取消删除账户: {acc_to_remove}")
        return

    # 从总资金 balance-all 减去该账户余额
    removed_amount = data.get(acc_to_remove, 0)
    data["balance-all"] -= removed_amount
    # 删除账户
    del data[acc_to_remove]

    # 写入 YAML
    write_data(data, yaml_path, logger)

    print(f"账户 {acc_to_remove} 已删除，总资金减少 {removed_amount}, 当前总资金 {data['balance-all']}")
    if logger: logger.log(f"删除账户: {acc_to_remove}, 扣除资金: {removed_amount}, 当前总资金: {data['balance-all']}")

# ------------------ 备份 YAML ------------------
def backup_yaml(yaml_path, logger=None):
    if not yaml_path.exists():
        if logger:
            logger.log(f"YAML 文件不存在，无法备份: {yaml_path}")
        return

    backup_path = yaml_path.with_suffix(yaml_path.suffix + ".bak")
    
    # 复制当前 YAML 到备份
    import shutil
    shutil.copy(yaml_path, backup_path)
    print(f"已备份 YAML 到: {backup_path}")
    if logger:
        logger.log(f"备份 YAML 文件: {backup_path}")