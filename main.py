from os import _AddedDllDirectory
from queue import Empty
import pymssql
import time
import datetime
import configparser
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as font
import re
from datetime import datetime
# select a.holderID,b.name,b.unit,a.salesVolume from table_record a inner join table_holder_info b on a.holderID = b.id
#pyinstaller --onefile --noconsole your_script.py
# 表名
default_server = "."
table_record = "table_record"
table_operator = "table_operator"
table_holder_info = "table_holder_info"
table_permission_log = "table_permission_log"
table_permission_sign = "table_permission_sign"
num_standerd = 65


class permission:
    permission = []
    #key:table名
    #value:权限名
    permission_table = {table_permission_log:"登记",table_permission_sign:"签约"}
    permission_unit = ""

class database:
    def __init__(self,server=default_server,username='sa',password='Jjrjj3545',database='DBtest'):

        self.server = server
        self.username = username
        self.password = password
        self.database = database
        self.conn = self.get_connection()
        if not self.conn:
            return
    
    #链接数据库
    def get_connection(self):
        """创建数据库连接"""
        try:
            conn = pymssql.connect(
                server=self.server,
                user=self.username,
                password=self.password,
                database=self.database
            )
            print("连接 SQL Server 成功！")
            return conn
        except Exception as e:
            print(f"连接失败：{str(e)}")
            return None

    def create_record(self,table,holderID,salesVolume, recorder, recordDate,operator,operateDate,remark,has_equity_certificate,has_receipt,has_commitment_letter,is_entrusted):

        if not self.conn:
            print("数据库连接失败")
            return
        """新增记录"""
        try:
            cursor = self.conn.cursor()
            # 插入数据
            sql = f"""
            INSERT INTO {table} (
            holderID,salesVolume, recorder, recordDate,operator,operateDate,remark,has_equity_certificate,has_receipt,has_commitment_letter,is_entrusted
            )VALUES (%s,  %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)
            """
            cursor.execute(sql, (holderID,salesVolume, recorder, recordDate,operator,operateDate,remark,
            has_equity_certificate,has_receipt,has_commitment_letter,is_entrusted)) 
            self.conn.commit()
            print("记录插入成功")
        except Exception as e:
            print(f"记录插入失败：{str(e)}")
            self.conn.rollback()
        
    def read_records(self,table,condition=None):
        if not self.conn:
            return
        """查询记录"""
        try:
            cursor = self.conn.cursor()
            # 查询数据
            sql = f"""SELECT * FROM {table}"""
            if condition:
                sql += f" WHERE {condition}"
            
            cursor.execute(sql)
            # 获取列名
            columns = [column[0] for column in cursor.description]
            # 获取数据
            records = []
            for row in cursor.fetchall():
                records.append(dict(zip(columns, row)))
            
            print(f"read：查询到 {len(records)} 条记录")
            return records
        except Exception as e:
            print(f"read：查询失败：{str(e)}")
            return []
        
    def delete_record(self,table,ID):
        if not self.conn:
            return
        #安全验证
        if not table or not ID:
            print("表格名或ID不能为空")
            return
        
        """删除记录"""
        try:
            cursor = self.conn.cursor()
            # 删除数据
            sql = f"""DELETE FROM {table} WHERE ID = {ID}"""
            cursor.execute(sql)
            self.conn.commit()
            print("记录删除成功")
        except Exception as e:
            print(f"删除失败：{str(e)}")
            self.conn.rollback()
        
    def clear_table(self,table):
        if not self.conn:
            return
        #清空表
        try:
            cursor = self.conn.cursor()
            # 清空数据
            sql = f"""TRUNCATE TABLE {table}"""
            cursor.execute(sql)
            self.conn.commit()
            print("表格清空成功")
        except Exception as e:
            print(f"清空失败：{str(e)}")
            self.conn.rollback()
    #在某列寻找
    def search_records(self,table,column,target):
        if not self.conn:
            return
        """查询记录"""
        try:
            cursor = self.conn.cursor()
            # 查询数据
            sql = f"""SELECT * FROM {table} WHERE {column} LIKE '%{target}%' """
            cursor.execute(sql)
            # 获取列名
            columns = [column[0] for column in cursor.description]
            # 获取数据
            ans = []
            for row in cursor.fetchall():
                ans.append(dict(zip(columns, row)))
            
            print(f"search：查询到 {len(ans)} 条记录")
            return ans

        except Exception as e:
            print(f"search：查询失败：{str(e)}")
            return []

    def count_data(self):
        """执行股东统计存储过程并显示结果"""
        # 检查数据库连接是否有效
        if not self.conn:
            messagebox.showerror("错误", "数据库连接失败")
            return
        
        try:
            # 创建统计报表窗口（顶级窗口，独立于主窗口）
            report_window = tk.Toplevel()
            report_window.title("股权回购汇总表")  # 设置窗口标题
            report_window.geometry("1200x700")  # 设置窗口初始大小（宽x高）

            # 顶部框架：用于显示时间和百分比信息
            top_frame = tk.Frame(report_window)
            top_frame.pack(fill="x", padx=10, pady=5)  # 水平方向填满，设置内边距
            
            # 添加当前统计时间（左对齐）
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 格式化当前时间
            time_label = tk.Label(top_frame, text=f"统计时间: {current_time}", font=("SimHei", 10))
            time_label.pack(side="left")  # 左对齐放置

            # 百分比显示框架（居中对齐）
            percentage_frame = tk.Frame(top_frame)
            # 水平填充并占满剩余空间，实现居中效果
            percentage_frame.pack(side="left", fill="x", expand=True)
            
            # 百分比显示标签（数据加载时会更新）
            total_equity_label = tk.Label(percentage_frame, text="总股权: --", font=("SimHei", 12))
            total_equity_label.pack(side="left", padx=20)  # 左侧间距20像素
            
            # 收购股权占比标签（加粗显示）
            self.percentage_label = tk.Label(percentage_frame, text="收购股权占比: --%", 
                                            font=("SimHei", 12, "bold"))
            self.percentage_label.pack(side="left", padx=20)  # 左侧间距20像素

            # 创建用于显示数据的树状视图（表格形式）
            columns = ("单位", "股东数", "股权总数", "签约人数", "签约股数")
            # 仅显示列标题，不显示首列（默认的树形结构列）
            tree = ttk.Treeview(report_window, columns=columns, show="headings")

            # 配置列标题和宽度
            for col in columns:
                tree.heading(col, text=col)  # 设置列标题文本
                tree.column(col, width=150, anchor='center')  # 列宽150，内容居中

            # 添加垂直滚动条（当数据超出窗口时可滚动）
            scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)  # 关联滚动条与树状视图

            # 布局树状视图和滚动条
            tree.pack(side="left", fill="both", expand=True)  # 填满空间并可扩展
            scrollbar.pack(side="right", fill="y")  # 垂直方向填满

            # 搜索框架（用于单位筛选）
            search_frame = tk.Frame(report_window)
            search_frame.pack(pady=10, fill="x")  # 水平填满，上下间距10像素

            # 搜索标签和输入框
            tk.Label(search_frame, text="单位筛选:").pack(side="left")
            search_entry = tk.Entry(search_frame)
            # 可扩展并填满水平空间，左侧间距5像素
            search_entry.pack(side="left", padx=5, expand=True, fill="x")

            
            def load_data(unit='%'):
                """
                加载指定单位的数据并计算总计和百分比
                参数: unit - 单位名称，默认为'%'表示查询所有单位（SQL通配符）
                """
                # 清空现有数据
                for item in tree.get_children():
                    tree.delete(item)
                
                # 初始化总计变量
                total_shareholders = 0  # 总股东数
                total_equity = 0        # 总股权数
                total_signed_people = 0 # 总签约人数
                total_signed_shares = 0 # 总签约股数
                
                # 执行存储过程查询数据
                cursor = self.conn.cursor()
                # 调用存储过程，传入单位参数（支持模糊查询）
                cursor.execute("EXEC [dbo].[SYS_P_shareholderTotal] %s", (unit,))
                
                # 遍历查询结果并显示
                for row in cursor.fetchall():
                    tree.insert("", tk.END, values=row)  # 在表格末尾插入行
                    
                    # 累加总计（假设结果集中第1-4列是数值型）
                    try:
                        # 安全转换为整数，空值则视为0
                        total_shareholders += int(row[1]) if row[1] else 0
                        total_equity += int(row[2]) if row[2] else 0
                        total_signed_people += int(row[3]) if row[3] else 0
                        total_signed_shares += int(row[4]) if row[4] else 0
                    except (ValueError, TypeError):
                        # 优雅处理非数值类型数据（不累计，避免程序崩溃）
                        pass
                
                cursor.close()  # 关闭游标
                
                # 更新总股权显示
                total_equity_label.config(text=f"总股权: {total_equity}")
                
                # 计算并更新收购股权占比
                if total_equity > 0:
                    # 计算占比（签约股数/总股权数 * 100%）
                    percentage = (total_signed_shares / total_equity) * 100
                    percentage_text = f"收购股权占比: {percentage:.2f}%"  # 保留两位小数
                    
                    # 根据百分比设置不同颜色（≥65%显示红色，否则绿色）
                    if percentage >= num_standerd:
                        self.percentage_label.config(text=percentage_text, fg="red")
                    else:
                        self.percentage_label.config(text=percentage_text, fg="green")
                else:
                    # 总股权为0时显示0%，黑色文字
                    self.percentage_label.config(text="收购股权占比: 0%", fg="black")
                
                # 添加总计行并设置特殊样式（仅当有数据时）
                if tree.get_children():
                    total_item = tree.insert("", tk.END, values=(
                        "总计", 
                        total_shareholders, 
                        total_equity, 
                        total_signed_people, 
                        total_signed_shares
                    ))
                    # 设置总计行样式（灰色背景，加粗字体）
                    tree.item(total_item, tags=('total',))
                    tree.tag_configure('total', background='#f0f0f0', font=('SimHei', 10, 'bold'))
            
            def on_search():
                """处理查询按钮点击事件"""
                unit = search_entry.get().strip()  # 获取输入的单位名称
                # 若输入为空则查询所有单位（使用'%'通配符），否则按输入筛选
                load_data(unit if unit else '%')
                

            if permission.permission_unit == "管理员":
                # 查询按钮
                search_btn = tk.Button(search_frame, text="查询", command=on_search)
                search_btn.pack(side="left")
            
            if permission.permission_unit == "管理员":
                # 加载初始数据（管理员默认查询所有单位）
                load_data()
            else:
                load_data(permission.permission_unit)

            
        except Exception as e:
            # 捕获并显示异常信息
            messagebox.showerror("错误", f"执行统计失败: {str(e)}")

    def check_in_table(self, table, target_id):
        try:
            cursor = self.conn.cursor()
            # 使用参数化查询，防止SQL注入
            sql = f"SELECT * FROM {table} WHERE id = %s"
            cursor.execute(sql, (target_id,))
            
            # 获取列名
            columns = [column[0] for column in cursor.description]
            # 获取查询结果
            row = cursor.fetchone()
            
            if row:
                return True
            else:
                print(f"在表 {table} 的id列中未找到 {target_id}")
                return False
                
        except Exception as e:
            print(f"查询失败：{str(e)}")
            return None


class ManagementApp:
    def __init__(self, root):
        server = default_server

        try:
            conf = configparser.ConfigParser()

            conf.read("config.ini")
            server = conf.get("dbconfig", "serverIP")
            # 创建数据库对象
            
        except Exception as e:
            print(f"数据库连接登录界面失败：{str(e)}")
        print(server)
        self.db = database(server = server)


        if self.db:
            print("数据库连接登录界面成功")
        else:
            print("数据库连接登录界面失败")

        self.root = root
        self.root.title("数据管理系统")
        self.root.geometry("1200x600")
        # 设置窗口最小大小为800x600
        self.root.minsize(1500, 800)
        self.root.resizable(True, True)

        # 设置中文字体支持
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="SimHei", size=10)
        self.root.option_add("*Font", self.default_font)
        
        # 从数据库获取的用户列表
        self.operator_list = self.get_users_from_database()
        #操作员名
        self.name = "NONE"
        self.jobType = "登记"
        #所选条的信息
        self.selected_shareholder = "NONE"
        self.selected_shareholderID = None
        self.selected_shareholderHasNum = 0
        self.selected_shareholders_remark = "NONE"
        self.selected_record_time = "NONE"
        self.selected_operate_time = "NONE"
        self.selected_recorder = "NONE"
        self.selected_operator = "NONE"

        #提示
        self.hint ="新建记录预览 ==> "
        #当前时间
        self.time = "NONE"

        # 添加自动刷新定时器
        self.auto_refresh_interval = 30000  # 30秒自动刷新
        
        # 创建登录界面
        self.create_login_frame()
        
    def get_users_from_database(self):
        res = []
        operatorArr = self.db.read_records(table_operator)
        if operatorArr:
            print("数据库operator查询成功")
        else:
            print("数据库operator查询失败")

        print(operatorArr)
        for _  in operatorArr:
            res.append(_["operator"])

        return res
    
    def create_login_frame(self):
        # 登录界面框架
        self.login_frame = tk.Frame(self.root, padx=50, pady=50)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(self.login_frame, text="核弹管理系统", font=("SimHei", 24, "bold"))
        title_label.pack(pady=30)
        
        # 表单框架
        form_frame = tk.Frame(self.login_frame)
        form_frame.pack(pady=20)
        
        # 姓名输入 - 使用Combobox实现联想功能
        tk.Label(form_frame, text="姓名:", font=("SimHei", 12)).grid(row=0, column=0, padx=10, pady=15, sticky="e")
        
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Combobox(
            form_frame, 
            textvariable=self.name_var,
            width=28, 
            font=("SimHei", 12),
            state="normal"
        )
        self.name_entry.grid(row=0, column=1, padx=10, pady=15)
        self.name_entry.bind("<KeyRelease>", self.update_name_suggestions)
        self.name_entry.bind("<Button-1>", self.show_matched_names)
        
        # 密码输入
        tk.Label(form_frame, text="密码:", font=("SimHei", 12)).grid(row=1, column=0, padx=10, pady=15, sticky="e")
        self.password_entry = tk.Entry(form_frame, width=30, show="*", font=("SimHei", 12))
        self.password_entry.grid(row=1, column=1, padx=10, pady=15)
        
        # 按钮框架
        button_frame = tk.Frame(self.login_frame)
        button_frame.pack(pady=10)
        
        # 登录按钮
        login_btn = tk.Button(
            button_frame, 
            text="登录", 
            command=self.login,
            width=15,
            height=2,
            bg="#3B82F6",
            fg="white",
            font=("SimHei", 12, "bold")
        )
        login_btn.pack(side=tk.LEFT, padx=10)
        
        # 修改密码按钮
        change_pwd_btn = tk.Button(
            button_frame, 
            text="修改密码", 
            command=self.show_change_password_dialog,
            width=15,
            height=2,
            bg="#10B981",
            fg="white",
            font=("SimHei", 12, "bold")
        )
        change_pwd_btn.pack(side=tk.LEFT, padx=10)
        
    def show_change_password_dialog(self):
        """显示修改密码对话框"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "请先输入用户名")
            return
            
        if name not in self.operator_list:
            messagebox.showerror("错误", "该用户不存在")
            return
            
        # 创建修改密码对话框
        self.change_pwd_dialog = tk.Toplevel(self.root)
        self.change_pwd_dialog.title("修改密码")
        self.change_pwd_dialog.geometry("400x300")
        self.change_pwd_dialog.resizable(False, False)
        
        # 对话框内容
        tk.Label(self.change_pwd_dialog, text=f"用户: {name}", font=("SimHei", 12)).pack(pady=10)
        
        # 原密码
        tk.Label(self.change_pwd_dialog, text="原密码:", font=("SimHei", 12)).pack()
        self.old_pwd_entry = tk.Entry(self.change_pwd_dialog, show="*", font=("SimHei", 12), width=25)
        self.old_pwd_entry.pack(pady=5)
        
        # 新密码
        tk.Label(self.change_pwd_dialog, text="新密码:", font=("SimHei", 12)).pack()
        self.new_pwd_entry = tk.Entry(self.change_pwd_dialog, show="*", font=("SimHei", 12), width=25)
        self.new_pwd_entry.pack(pady=5)
        
        # 确认新密码
        tk.Label(self.change_pwd_dialog, text="确认新密码:", font=("SimHei", 12)).pack()
        self.confirm_pwd_entry = tk.Entry(self.change_pwd_dialog, show="*", font=("SimHei", 12), width=25)
        self.confirm_pwd_entry.pack(pady=5)
        
        # 修改按钮
        change_btn = tk.Button(
            self.change_pwd_dialog, 
            text="确认修改", 
            command=self.change_password,
            width=15,
            height=1,
            bg="#10B981",
            fg="white",
            font=("SimHei", 12, "bold")
        )
        change_btn.pack(pady=15)
        
    def change_password(self):
        """执行密码修改操作"""
        name = self.name_var.get().strip()
        old_pwd = self.old_pwd_entry.get()
        new_pwd = self.new_pwd_entry.get()
        confirm_pwd = self.confirm_pwd_entry.get()
        
        # 验证输入
        if not old_pwd or not new_pwd or not confirm_pwd:
            messagebox.showerror("错误", "请填写所有密码字段")
            return
            
        if new_pwd != confirm_pwd:
            messagebox.showerror("错误", "两次输入的新密码不一致")
            return
            
        # 验证原密码是否正确
        correct_password = self.db.read_records(table_operator, f"operator='{name}'")[0]["password"]
        if str(correct_password) != old_pwd:
            messagebox.showerror("错误", "原密码不正确")
            return
            
        # 更新数据库中的密码
        try:
            
            # 更新数据库
            cursor = self.db.conn.cursor()
            update_sql = f"""
            UPDATE {table_operator} 
            SET password='{new_pwd}'
            WHERE operator='{name}'
            """
            cursor.execute(update_sql)
            self.db.conn.commit()
            
            messagebox.showinfo("成功", "密码修改成功")
            self.change_pwd_dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"密码修改失败: {str(e)}")
            

    def show_matched_names(self, event):
        """点击下拉框时显示匹配当前输入的用户名"""
        current_input = self.name_var.get().strip()
        
        if current_input:
            # 过滤匹配的姓名
            matching_names = [name for name in self.operator_list if current_input in name]
            
            if matching_names:
                self.name_entry['values'] = matching_names
            else:
                self.name_entry['values'] = ["未搜索到用户"]
        else:
            # 如果输入为空，显示所有用户
            self.name_entry['values'] = self.operator_list

    def update_name_suggestions(self, event):
        """根据输入更新姓名建议列表"""
        current_input = self.name_var.get().strip()
        
        # 如果输入为空，不显示建议
        if not current_input:
            self.name_entry['values'] = []
            return
        
        # 过滤匹配的姓名
        matching_names = [name for name in self.operator_list if current_input in name]
        
        # 更新下拉列表
        self.name_entry['values'] = matching_names
        
        # 如果只有一个匹配项，自动完成
        if len(matching_names) == 1:
            self.name_var.set(matching_names[0])
            # 选中自动补全的部分，方便用户修改
            self.name_entry.icursor(len(current_input))
            self.name_entry.select_range(len(current_input), tk.END)
    
    def show_all_names(self, event):
        """显示所有姓名（点击输入框时）"""
        self.name_entry['values'] = self.operator_list
    
    def login(self):
        # 获取输入的姓名和密码
        name = self.name_var.get().strip()
        password = self.password_entry.get().strip()
        self.name = name
        if my_input(name) == "ERROR":
            return
        if my_input(password) == "ERROR":
            return

        # 简单验证
        if not name or not password:
            messagebox.showerror("错误", "请输入姓名和密码")
            return
        
        
        # 检查姓名是否在数据库中存在
        # # print(name)
        if name not in self.operator_list:
            messagebox.showerror("错误", "该用户不存在")
            return
        correct_password = self.db.read_records(table_operator, f"operator='{name}'")[0]["password"]
        operatorID = self.db.read_records(table_operator, f"operator='{name}'")[0]["ID"]
        permission.permission_unit = str(self.db.read_records(table_operator, f"operator='{name}'")[0]["unit"] ).strip()

        for _ in permission.permission_table.keys():
            if self.db.check_in_table(_,operatorID):
                permission.permission.append(permission.permission_table[_])

        #测试登录信息获取
        # print(permission.permission)
        # print(correct_password)
        # print(operatorID)

        correct_password = str(correct_password)
        if correct_password != password:
            messagebox.showerror("错误", "密码错误")
            return
        
        
        


        # 销毁登录界面，创建主界面
        self.login_frame.destroy()
        self.create_main_frame()
         
    def update_main_time(self):
        """更新主界面的时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time = current_time
        self.main_time_label.config(text=f"{current_time}")
        # 每隔1秒更新一次时间
        self.root.after(1000, self.update_main_time)

#======================主界面====================
    def create_main_frame(self):
        # 主界面框架
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 时间显示 - 顶部居中
        self.main_time_label = tk.Label(
            self.main_frame, 
            text="", 
            font=("SimHei", 20),
            anchor="center"
        )
        self.main_time_label.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.update_main_time()  # 启动主界面的时间更新
        
        # 上半部分框架
        upper_frame = tk.Frame(self.main_frame)
        upper_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # =======================================上半部分的左侧 - 列表区域==============================================
        list_frame = tk.Frame(upper_frame, borderwidth=2, relief="groove")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 列表区域的顶部控制栏
        list_control_frame = tk.Frame(list_frame)
        list_control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 刷新按钮
        refresh_btn = tk.Button(
            list_control_frame, 
            text="刷新", 
            command=self.refresh_data,
            bg="#3B82F6",
            fg="white",
            padx=10
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 统计按钮
        refresh_btn = tk.Button(
            list_control_frame, 
            text="统计", 
            command=self.count_data,
            bg="#3B82F6",
            fg="white",
            padx=10
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 列表搜索框
        self.list_search_entry = tk.Entry(list_control_frame, width=30, font=("SimHei", 10))
        self.list_search_entry.pack(side=tk.RIGHT, padx=(0, 5))
        

        self.list_search_entry.bind('<Return>', self.list_search_enter)

        list_search_btn = tk.Button(
            list_control_frame, 
            text="搜索", 
            command=self.search_list_data,
            bg="#3B82F6",
            fg="white",
            padx=10
        )
        list_search_btn.pack(side=tk.RIGHT)
        
        # 创建列表（Treeview）
        columns = ("售股人", "回购数量", "登记人", "登记时间", "签约人", "签约时间", "状态")
        self.data_tree = ttk.Treeview(
            list_frame, 
            columns=columns + ("record_id",),  # 添加隐藏列
            show="headings"
        )

        # 隐藏record_id列
        self.data_tree.column("record_id", width=0, stretch=False)
        self.data_tree.heading("record_id", text="", anchor="center")

        # 设置列标题
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=150, anchor="center")
        
        # 绑定选择事件
        self.data_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # 添加数据
        # 在 create_main_frame 方法中找到这部分代码
        self.data_tree.tag_configure("logined_tag", foreground="blue")  # 设置颜色
        self.data_tree.tag_configure("finished_tag", foreground="black")  # 设置颜色
        self.data_tree.tag_configure("verified_tag", foreground="green")  # 已审验标签颜色

        record_data = self.db.read_records(table_record)
        for _ in record_data:
            #筛选
            # print(permission.permission_unit,self.db.search_records(table_holder_info, "id", _["holderID"])[0]["unit"])
            # print(permission.permission_unit!= "管理员" and self.db.search_records(table_holder_info, "id", _["holderID"])[0]["unit"] != permission.permission_unit)
            if permission.permission_unit!= "管理员" and self.db.search_records(table_holder_info, "id", _["holderID"])[0]["unit"] != permission.permission_unit:
                continue
            name = self.db.search_records(table_holder_info, "id", _["holderID"])[0]["name"]
            row_id = self.data_tree.insert("", tk.END, values=(name,_["salesVolume"],_["recorder"],_["recordDate"],_["operator"],_["operateDate"],_["remark"]))
            self.data_tree.set(row_id, "record_id", _["id"])
            #记录信息1
            # print(_["operator"])
            # print(_["id"])
            # 设置标签颜色
            if str(_["remark"]).strip() == "已审验":
                current_tags = self.data_tree.item(row_id, "tags")
                new_tags = current_tags + ("verified_tag",) if current_tags else ("verified_tag",)
                self.data_tree.item(row_id, tags=new_tags)
            elif str(_["remark"]).strip() == "已登记":
                current_tags = self.data_tree.item(row_id, "tags")
                new_tags = current_tags + ("logined_tag",) if current_tags else ("logined_tag",)
                self.data_tree.item(row_id, tags=new_tags)
            elif str(_["remark"]).strip() == "已签约":
                current_tags = self.data_tree.item(row_id, "tags")
                new_tags = current_tags + ("finished_tag",) if current_tags else ("finished_tag",)
                self.data_tree.item(row_id, tags=new_tags)
        # 自动刷新
        self.setup_auto_refresh()

        # 添加滚动条
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscroll=list_scrollbar.set)
        
        # 布局列表和滚动条
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # =====================================上半部分的右侧 - 信息框区域 ===================================
        info_frame = tk.Frame(upper_frame, borderwidth=2, relief="groove", width=350, height=400)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        info_frame.pack_propagate(False)  # 固定大小

        info_control_frame = tk.Frame(info_frame)
        info_control_frame.pack(fill=tk.X, pady=(0, 5))

        if "登记" in permission.permission:
            # 信息搜索框
            self.info_search_entry = tk.Entry(info_control_frame, width=30, font=("SimHei", 10))
            self.info_search_entry.pack(side=tk.RIGHT, padx=(0, 5))
            
            self.info_search_entry.bind('<Return>', self.handle_search_enter)
            # 新增处理回车搜索的方法
            
            search_btn = tk.Button(
                info_control_frame, 
                text="搜索", 
                command=self.search_info_data,
                bg="#3B82F6",
                fg="white",
                padx=10
            )
            search_btn.pack(side=tk.RIGHT)
        
        # 信息标题
        info_title = tk.Label(info_control_frame, text="详细信息", font=("SimHei", 12, "bold"))
        info_title.pack(pady=5)
        
        # 创建多个文本框用于显示不同信息
        info_labels = ["持股人:", "手机号:", "身份证号:", "持股数:", "单位:",
                       "是否有股权证:", "是否有收据:", "是否有承诺书:", "是否委托:" ]
        self.info_texts = []
        
        for label in info_labels:
            frame = tk.Frame(info_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(frame, text=label, width=8, anchor="e").pack(side=tk.LEFT)
            text = tk.Entry(frame, state='readonly', readonlybackground='white', 
                          font=("SimHei", 15), relief="flat")
            text.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.info_texts.append(text)
        
        # 下半部分框架
        lower_frame = tk.Frame(self.main_frame)
        lower_frame.pack(fill=tk.BOTH, expand=True)
        
        # =======================================下半部分的左侧 - 预览框==============================================

        input_frame = tk.Frame(lower_frame, borderwidth=2, relief="groove")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 动态文本显示
        self.hint = "当前记录查看 ==> "
        self.dynamic_text = tk.StringVar()
        self.dynamic_text.set(f"{self.hint}持股人：____  售卖数额：____ 万元  状态：____") 

        title_label = tk.Label(
            input_frame, 
            textvariable=self.dynamic_text, 
            font=("SimHei", 12, "bold"),
            pady=10
        )
        title_label.pack(fill=tk.X)
        
        # 数字输入框
        self.number_entry = tk.Entry(
            input_frame,
            font=("SimHei", 14),
            width=10
        )
        self.number_entry.pack(pady=10)
        self.number_entry.bind("<KeyRelease>", self.on_entry_change)
        
        # ========================================下半部分的右侧 - 操作区域==================================
        action_frame = tk.Frame(lower_frame, borderwidth=2, relief="groove", width=350)
        action_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        action_frame.pack_propagate(False)  # 禁止自动调整大小
        
        # 复选框区域
        checkbox_frame = tk.Frame(action_frame)
        checkbox_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.check_vars = []
        check_labels = ["是否有股权证", "是否有收据", "是否有承诺书", "是否委托"]

        for i in range(4):
            var = tk.IntVar()
            self.check_vars.append(var)
            check = tk.Checkbutton(
                checkbox_frame, 
                text=check_labels[i], #是否有股权证,是否有收据,是否有承诺书,是否委托
                variable=var,
                font=("SimHei", 10)
            )
            check.pack(anchor="w", pady=2)
        
        # 按钮区域
        button_frame = tk.Frame(action_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        if "登记" in permission.permission:

            # 保存按钮

            self.root.bind('<Control-s>', self.save_data_cs)
            save_btn = tk.Button(
                button_frame, 
                text="保存", 
                command=self.save_data,
                bg="#10B981",
                fg="white",
                padx=15,
                pady=5,
                width=7
            )
            save_btn.pack(side=tk.LEFT, padx=5)
            
            # 删除按钮
            delete_btn = tk.Button(
                button_frame, 
                text="删除", 
                command=self.delete_data,
                bg="#EF4444",
                fg="white",
                padx=15,
                pady=5,
                width=7
            )
            delete_btn.pack(side=tk.LEFT, padx=5)
            
            # 审验按钮
            verify_btn = tk.Button(
                button_frame, 
                text="审验", 
                command=self.verify_data,
                bg="#F59E0B",
                fg="white",
                padx=15,
                pady=5,
                width=7
            )
            verify_btn.pack(side=tk.LEFT, padx=5)


        
        if "签约" in permission.permission:
            # 签约按钮
            sign_btn = tk.Button(
                button_frame, 
                text="签约", 
                command=self.sign_data,
                bg="#3B82F6",
                fg="white",
                padx=15,
                pady=5,
                width=7
            )
            sign_btn.pack(side=tk.LEFT, padx=5)
    
    def on_tree_select(self, event):
        selected_item = self.data_tree.focus()
        if selected_item:
            item_data = self.data_tree.item(selected_item)
            values = item_data['values']
            record_id = self.data_tree.set(selected_item, "record_id")

            if len(values) >= 7:  # 7列对应索引0-6
                self.selected_shareholder = values[0]  # 持股人（索引0）
                self.selected_salesVolume = values[1]  # 回购数量（索引1）
                self.selected_recorder = values[2]     # 登记人（索引2）
                self.selected_record_time = values[3]  # 登记时间（索引3）
                self.selected_operator = values[4]     # 办理人（索引4）
                self.selected_operate_time = values[5] # 办理时间（索引5）
                self.selected_shareholders_remark = values[6]  # 状态（索引6）
                
                record_info = self.db.search_records(table_record,"id",record_id)[0]
                self.selected_shareholderID= record_info["holderID"]

                holder_info = self.db.search_records(table_holder_info,"id",record_info["holderID"])[0]
                self.refresh_infobox(holder_info,record_info)

                self.hint = "当前记录查看 ==> "
                self.dynamic_text.set(
                    f"{self.hint}持股人：{self.selected_shareholder} "
                    f"售卖数额：{self.selected_salesVolume}万元 "
                    f"状态：{self.selected_shareholders_remark}"
                )
        
    def on_entry_change(self, event):
        """输入框内容变化时的处理"""
        self.hint = "新建记录预览 ==> "

        content = self.number_entry.get()
        # 简单过滤非数字字符
        filtered = ''.join(filter(str.isdigit, content))
        if content != filtered:
            self.number_entry.delete(0, tk.END)
            self.number_entry.insert(0, filtered)
        
        # 更新显示文本，移除登记人和登记时间
        if filtered and self.selected_shareholder!="NONE":
            if self.selected_shareholders_remark == "已登记":
                self.dynamic_text.set(f"""{self.hint}持股人：{self.selected_shareholder} 售卖数额：{filtered}万元 状态：{self.selected_shareholders_remark}""")

            elif self.selected_shareholders_remark == "已签约":
                self.dynamic_text.set(f"""{self.hint}持股人：{self.selected_shareholder} 售卖数额：{self.selected_salesVolume}万元 状态：{self.selected_shareholders_remark}""")
            
            else:
                self.dynamic_text.set(
                    f"{self.hint}持股人：{self.selected_shareholder} "
                    f"售卖数额：{filtered if filtered else '____'} 万元 "
                    f"状态：未登记"
                )

        else:
            self.hint = "当前记录查看 ==> "
            self.dynamic_text.set(f"""{self.hint}持股人：____ 售卖数额：{filtered}万元 状态：____""")

    def refresh_infobox(self,holder_info, record_info = None):
        """刷新信息框"""
        # if self.selected_shareholderID:
            #holder_info = self.db.search_records(table_holder_info, "id", self.selected_shareholderID)[0]
        if record_info ==None:
            info_values = [
                holder_info.get("name", ""),    # 持股人
                holder_info.get("phone", ""),   # 手机号
                holder_info.get("idcard", ""),  # 身份证号
                holder_info.get("holdVolums", ""),  # 持股数
                holder_info.get("unit", ""),     # 单位
                " ",
                " ",
                " ",
                " "
                ]
        else:
            info_values = [
                holder_info.get("name", ""),    # 持股人
                holder_info.get("phone", ""),   # 手机号
                holder_info.get("idcard", ""),  # 身份证号
                holder_info.get("holdVolums", ""),  # 持股数
                holder_info.get("unit", ""),     # 单位
                record_info.get("has_equity_certificate", ""),   # 是否有股权证
                record_info.get("has_receipt", ""),  # 是否有收据
                record_info.get("has_commitment_letter", ""),  # 是否有承诺书
                record_info.get("is_entrusted", "")     # 是否委托
                ]
            

        for i in range(min(len(self.info_texts), len(info_values))):
            self.info_texts[i].config(state='normal')
            self.info_texts[i].delete(0, tk.END)
            self.info_texts[i].insert(0, str(info_values[i]))
            self.info_texts[i].config(state='readonly')

    def save_data(self):
        """保存数据的方法"""
        check_status = []
        for _ in self.check_vars:
            check_status.append(_.get())
        if check_status[2]!=1:
            if check_status[0]!=1 or check_status[0]!=1:
                messagebox.showerror("错误", "请选择是否有股权证或收据")
                return

        num = self.number_entry.get()
        if num and int(num)!=0:
            if self.selected_shareholder!="NONE":
                
                #判断是否已登记过
                record_info = self.db.search_records(table_record,"holderID",self.selected_shareholderID)
                if record_info:
                    messagebox.showerror("错误", "该持股人已登记")
                    return

                #print(f"保存数量：{num}")
                if self.jobType == "登记":
                    #计算剩余股数
                    left_num = self.selected_shareholderHasNum - int(num)
                    if left_num<0:
                        messagebox.showerror("错误", "持股数不足")
                        return


                    #判断是否超售
                    if  self.has_reached_num_standerd(num):
                        messagebox.showerror("错误", "超售！")
                        return
                    
                    #保证只有一个登记记录
                    if self.db.search_records(table_record,"remark","已登记"):
                        messagebox.showerror("错误", "有为审验的记录,请先审验！")
                        return

                    #没问题之后保存
                    check_status = ["Y" if _==1 else "N" for _ in check_status]
                    # 获取当前时间作为记录时间
                    record_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # 创建记录并获取新记录的ID
                    #print(self.selected_shareholderID)
                    self.db.create_record(table_record, self.selected_shareholderID, num, 
                                        self.name, record_time, None, None, "已登记",
                                        check_status[0], check_status[1], check_status[2], check_status[3])
                    # 获取最新创建的记录ID
                    latest_record = self.db.read_records(table_record, 
                                                    f"recorder='{self.name}' AND recordDate='{record_time}'")
                    if latest_record:
                        latest_id = latest_record[-1]["id"]  # 获取最后一条记录的ID
                        #print("登记成功，记录ID:", latest_id)

                        messagebox.showinfo("提示", "登记成功！")
                        self.number_entry.delete(0, tk.END)
                        # 刷新数据并自动选中新记录
                        self.refresh_data(select_record_id=latest_id)
            else:
                messagebox.showerror("错误", "选择持股人")

        else:
            messagebox.showerror("错误", "请输入有效数字")
    
    def delete_data(self):
        """删除记录"""
        selected_item = self.data_tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        record_id = self.data_tree.set(selected_item, "record_id")
        current_status = str(self.data_tree.set(selected_item, column=6)).strip()  # 获取当前状态

        
        if current_status == "已审验":
            messagebox.showwarning("警告", "已审验记录不能被删除")
            return
        elif current_status == "已签约":
            messagebox.showwarning("警告", "已签约记录不能被删除")
            return
        elif current_status != "已登记":
            messagebox.showwarning("警告", "只能删除已登记状态的记录")
            return
        
        # 确认删除操作
        if messagebox.askyesno("确认", "确定要删除这条记录吗？"):
            try:
                # 从数据库删除
                self.db.delete_record(table_record, record_id)

                #计算剩余股数
                new_num = self.selected_shareholderHasNum+int(self.selected_salesVolume)
                
                # 刷新数据
                self.refresh_data()
                messagebox.showinfo("成功", "记录已删除")
                
                # 清空选择和信息显示
                self.selected_shareholder = "NONE"
                self.selected_shareholderID = None
                self.selected_shareholders_remark = "NONE"
                self.dynamic_text.set(f"{self.hint}持股人：____  售卖数额：____ 万元  状态：____")
                
                # 清空信息框
                for text_entry in self.info_texts:
                    text_entry.config(state='normal')
                    text_entry.delete(0, tk.END)
                    text_entry.config(state='readonly')
                    
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
    
    def verify_data(self):
        """审验数据"""
        selected_item = self.data_tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        record_id = self.data_tree.set(selected_item, "record_id")
        current_status = str(self.data_tree.set(selected_item, column=6)).strip() # 获取当前状态
        # 获取当前状态
        # print(current_status)

        if current_status == "已审验":
            messagebox.showinfo("提示", "该记录已审验，无需重复操作")
            return
        elif current_status == "已签约":
            messagebox.showwarning("警告", "已签约记录不能进行审验操作")
            return
        elif current_status != "已登记":
            messagebox.showwarning("警告", "只能审验已登记状态的记录")
            return
        
        # 确认审验操作
        if messagebox.askyesno("确认", "确定要审验这条记录吗？"):
            try:
                # 更新数据库
                cursor = self.db.conn.cursor()
                update_sql = f"""
                UPDATE {table_record} 
                SET remark='已审验'
                WHERE id={record_id}
                """
                cursor.execute(update_sql)
                self.db.conn.commit()
                
                # 刷新数据并保持选中状态
                self.refresh_data(select_record_id=record_id)
                messagebox.showinfo("成功", "记录已审验")
            except Exception as e:
                messagebox.showerror("错误", f"审验失败: {str(e)}")
                self.db.conn.rollback()

    def sign_data(self):
        """完成数据"""
        selected_item = self.data_tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        record_id = self.data_tree.set(selected_item, "record_id")
        current_status = str(self.data_tree.set(selected_item, column=6)).strip() # 获取当前状态
        # 获取当前状态
        # print(current_status)

        if current_status == "已签约":
            messagebox.showinfo("提示", "该记录已签约，无需重复操作")
            return
        elif current_status == "已登记":
            messagebox.showwarning("警告", "该记录还未审验,请联系登记员审验！")
            return
        elif current_status != "已审验":
            messagebox.showwarning("警告", "只能签约已审验状态的记录")
            return
        
        # 确认签约操作
        if messagebox.askyesno("确认", "确定要签约这条记录吗？"):
            try:
                # 更新数据库
                cursor = self.db.conn.cursor()
                update_sql = f"""
                UPDATE {table_record} 
                SET remark='已签约',
                    operateDate='{self.time}',  
                    operator='{self.name}'
                WHERE id={record_id}
                """
                cursor.execute(update_sql)
                self.db.conn.commit()
                
                # 刷新数据并保持选中状态
                self.refresh_data(select_record_id=record_id)
                messagebox.showinfo("成功", "记录已签约")
            except Exception as e:
                messagebox.showerror("错误", f"签约失败: {str(e)}")
                self.db.conn.rollback()

    def list_search_enter(self, event):
            """处理搜索框的回车事件，执行搜索后跳转焦点"""
            # 调用搜索功能
            res = self.search_list_data()

    def handle_search_enter(self, event):
            """处理搜索框的回车事件，执行搜索后跳转焦点"""
            # 调用搜索功能
            res = self.search_info_data()
            if res != -1:
                self.number_entry.focus_set()  # 设置焦点到数字输入框

    def save_data_cs(self,event):
        self.save_data()

    def search_list_data(self):
        """Search records by name, time or sales volume with fuzzy matching"""
        search_text = self.list_search_entry.get().strip()
        if not search_text:
            messagebox.showwarning("提示", "请输入搜索内容")
            return
        
        # Clear current selection
        self.data_tree.selection_remove(self.data_tree.selection())
        
        # Get all items in the tree
        all_items = self.data_tree.get_children()
        
        # Try to match the search text in different columns
        matched_items = []
        for item in all_items:
            # Get all column values for this item
            values = self.data_tree.item(item, 'values')
            
            # Check if search text matches in any of these columns:
            # 0: name (持股人), 1: sales volume (回购数量), 3: record time (登记时间), 5: operate time (办理时间)
            if (search_text in str(values[0]) or  # Name
                search_text in str(values[1]) or  # Sales volume
                search_text in str(values[3]) or  # Record time
                search_text in str(values[5])):  # Operate time
                matched_items.append(item)
        
        if matched_items:
            # Highlight all matched items
            for item in matched_items:
                self.data_tree.selection_add(item)
            
            # Scroll to the first matched item
            first_item = matched_items[0]
            self.data_tree.focus(first_item)
            self.data_tree.see(first_item)
            
            # Update the info box with the first matched item
            self.data_tree.selection_set(first_item)
            self.on_tree_select(None)  # Trigger the selection event
            
            messagebox.showinfo("搜索结果", f"找到{len(matched_items)}条匹配记录")
        else:
            messagebox.showinfo("搜索结果", "没有找到匹配的记录")

    def search_info_data(self):
        """搜索信息并更新信息框显示"""
        search_text = self.info_search_entry.get().strip().lower()
        if not search_text:
            messagebox.showinfo("提示", "请输入搜索内容")
            return -1
        
        info_data = []
        if self.db.search_records(table_holder_info, "name", search_text):
            info_data = self.db.search_records(table_holder_info, "name", search_text)
        elif self.db.search_records(table_holder_info, "phone", search_text):
            info_data = self.db.search_records(table_holder_info, "phone", search_text)
        elif self.db.search_records(table_holder_info, "idcard", search_text):
            info_data = self.db.search_records(table_holder_info, "idcard", search_text)

        # 清空现有信息框内容
        for text_entry in self.info_texts:
            text_entry.config(state='normal')
            text_entry.delete(0, tk.END)
            text_entry.config(state='readonly')

        if info_data:
            if len(info_data) != 1:
                messagebox.showerror("抱歉～", "有同名的持股人存在，请通过手机号,身份证号等条件搜索！")
                return -1
            # 提取数据并更新信息框（根据实际字段名调整）
            record = info_data[0]
            # print(666)
            # print(permission.permission_unit)
            if permission.permission_unit != "管理员" and permission.permission_unit != record.get("unit"):
                messagebox.showerror("注意！", "有此持股人存在，但不在您的单位！如有需要,请联系管理员.")
                return -1   


            self.refresh_infobox(record)
            # 同时更新选中状态
            self.selected_shareholder = record.get("name", "NONE")
            self.selected_shareholderID = record.get("id", "NONE")
            self.selected_shareholderHasNum = record.get("holdVolums", "NONE")
            self.hint = "新建记录预览 ==> "

            current_num = self.number_entry.get()  # 获取当前输入的数字
            self.dynamic_text.set(
                f"{self.hint}持股人：{self.selected_shareholder} "
                f"售卖数额：{current_num if current_num else '____'} 万元 "
                f"状态：未登记"
            )

        else:
            messagebox.showinfo("提示", "未找到匹配数据")
            return -1

    def has_reached_num_standerd(self,num):
        recorded_num = 0

        record = self.db.read_records(table_record)
        for _ in record:
            recorded_num += int(_["salesVolume"])
        added_num = recorded_num+int(num)
        # 执行存储过程查询数据
        cursor = self.db.conn.cursor()
        # 调用存储过程，传入单位参数（支持模糊查询）
        unit='%'
        cursor.execute("EXEC [dbo].[SYS_P_shareholderTotal] %s", (unit,))
        total_num = 0 

        for row in cursor.fetchall():
            total_num += int(row[2]) if row[2] else 0
        print(added_num,total_num,float(added_num/total_num)*100)
        if float(added_num/total_num)*100 > num_standerd:
            messagebox.showerror("注意！", "当前持股人已超售，无法继续售卖！")
            return True
        else:
            return False


    #==列表刷新函数组==
    def refresh_data(self, select_record_id=None):
        # 清空现有数据
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # 重新加载数据并按规则排序
        record_data = self.db.read_records(table_record)
        
        # 将数据分成三类
        verified_records = []  # 已审验
        registered_records = []  # 已登记
        completed_records = []  # 已签约
        
        for record in record_data:
            if str(record["remark"]).strip() == "已审验":
                verified_records.append(record)
            elif str(record["remark"]).strip() == "已登记":
                registered_records.append(record)
            elif str(record["remark"]).strip() == "已签约":
                completed_records.append(record)
        
        # 对每类记录按时间降序排序（最新的在最前面）
        verified_records.sort(key=lambda x: x["recordDate"], reverse=True)
        registered_records.sort(key=lambda x: x["recordDate"], reverse=True)
        completed_records.sort(key=lambda x: x["recordDate"], reverse=True)
        
        # 按顺序插入数据：已审验 -> 已登记 -> 已签约
        for records in [verified_records, registered_records, completed_records]:
            for _ in records:
                #筛选
                # print(permission.permission_unit,self.db.search_records(table_holder_info, "id", _["holderID"])[0]["unit"])
                # print(permission.permission_unit!= "管理员" and self.db.search_records(table_holder_info, "id", _["holderID"])[0]["unit"] != permission.permission_unit)
                if permission.permission_unit!= "管理员" and self.db.search_records(table_holder_info, "id", _["holderID"])[0]["unit"] != permission.permission_unit:
                    continue
                name = self.db.search_records(table_holder_info, "id", _["holderID"])[0]["name"]
                row_id = self.data_tree.insert("", tk.END, values=(
                    name,
                    _["salesVolume"],
                    _["recorder"],
                    _["recordDate"],
                    _["operator"] if _["operator"] is not None else ""
                        ,
                    _["operateDate"] if _["operateDate"] is not None else ""
                        ,
                    _["remark"]
                ))
                
                self.data_tree.set(row_id, "record_id", _["id"])
                
                # 设置标签颜色
                if str(_["remark"]).strip() == "已审验":
                    current_tags = self.data_tree.item(row_id, "tags")
                    new_tags = current_tags + ("verified_tag",) if current_tags else ("verified_tag",)
                    self.data_tree.item(row_id, tags=new_tags)
                elif str(_["remark"]).strip() == "已登记":
                    current_tags = self.data_tree.item(row_id, "tags")
                    new_tags = current_tags + ("logined_tag",) if current_tags else ("logined_tag",)
                    self.data_tree.item(row_id, tags=new_tags)
                elif str(_["remark"]).strip() == "已签约":
                    current_tags = self.data_tree.item(row_id, "tags")
                    new_tags = current_tags + ("finished_tag",) if current_tags else ("finished_tag",)
                    self.data_tree.item(row_id, tags=new_tags)
        
        # 如果有指定要选中的记录ID，则自动选中
        if select_record_id:
            for child in self.data_tree.get_children():
                if self.data_tree.set(child, "record_id") == str(select_record_id):
                    self.data_tree.selection_set(child)
                    self.data_tree.focus(child)
                    self.data_tree.see(child)  # 确保记录可见
                    break
    def count_data(self):
        self.db.count_data()
    def setup_auto_refresh(self):
        """设置自动刷新定时器"""
        if hasattr(self, 'data_tree'):
            self.refresh_data()
            self.root.after(self.auto_refresh_interval, self.auto_refresh)    
    def auto_refresh(self):
        """自动刷新函数"""
        # 获取当前选中的记录ID（如果有）
        selected_item = self.data_tree.focus()
        selected_id = self.data_tree.set(selected_item, "record_id") if selected_item else None
        
        self.refresh_data(select_record_id=selected_id)
        self.root.after(self.auto_refresh_interval, self.auto_refresh)
    #================


def my_input(input_str):
    # if not input_str or not isinstance(input_str, str):
    #     return False
    
    # # 转换为小写以便不区分大小写检测
    # lower_str = input_str.lower()
    
    # # 常见的SQL注入关键字和模式
    # sql_patterns = [
    #     # SQL关键字
    #     r'\b(select|insert|update|delete|drop|alter|create|truncate|exec|union|join|where|from|and|or)\b',
    #     # 注释符号
    #     r'--|#|/\*',
    #     # 引号和转义字符
    #     r'\'|\"|\\',
    #     # 逻辑操作符
    #     r'\b(and|or)\b\s*=\s*\d+',
    #     # 通配符
    #     r'%',
    #     # 执行命令
    #     r'exec\(|xp_cmdshell|sp_executesql',
    #     # 其他常见注入模式
    #     r'\b(1=1|0=0)\b',
    #     r'union\s+all\s+select',
    #     r'char\(|ascii\(|hex\('
    # ]
    
    # # 检查是否匹配任何模式
    # for pattern in sql_patterns:
    #     if re.search(pattern, lower_str):
    #         messagebox.showerror("警告！", "您的输入包含潜在的风险!\n请避免使用特殊字符。")
    #         return "ERROR"
    # return input_str
    pass
    
# 示例用法
if __name__ == "__main__":
    root = tk.Tk()
    app = ManagementApp(root)
    root.mainloop()
