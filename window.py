import pymssql
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class PermissionManager:
    def __init__(self, root):
        self.root = root
        self.root.title("权限管理系统")
        self.root.geometry("1000x700")  # 增大窗口尺寸
        self.root.minsize(950, 650)    # 设置最小尺寸
        self.unit_all = {
            "娄底": "娄底",
            "涟源": "涟源",
            "新化": "新化"
        }
        # 数据库连接信息
        self.db_config = {
            'server': '.',
            'user': 'sa',
            'password': 'Jjrjj3545',
            'database': 'DBtest'
        }
        
        # 表名定义
        self.operator_table = "table_operator"
        self.permission1_table = "table_permission_log"
        self.permission2_table = "table_permission_sign"

        # 创建UI
        self.create_ui()
        
        # 加载数据
        self.load_operators()
        self.load_permission1()
        self.load_permission2()
    
    def get_db_connection(self):
        """获取数据库连接"""
        try:
            conn = pymssql.connect(
                server=self.db_config['server'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            return conn
        except Exception as e:
            messagebox.showerror("数据库连接错误", f"无法连接到数据库: {str(e)}")
            return None
    
    def create_ui(self):
        """创建用户界面"""
        # 设置样式
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("SimHei", 10, "bold"))
        style.configure("Treeview", font=("SimHei", 10), rowheight=25)
        style.configure("TLabel", font=("SimHei", 10))
        style.configure("TButton", font=("SimHei", 10))
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)  # 操作员列表
        main_frame.columnconfigure(1, weight=0)  # 按钮区域
        main_frame.columnconfigure(2, weight=1)  # 权限列表
        main_frame.rowconfigure(0, weight=0)    # 标题行
        main_frame.rowconfigure(1, weight=1)    # 主要内容行
        main_frame.rowconfigure(2, weight=0)    # 权限标题行
        main_frame.rowconfigure(3, weight=1)    # 权限内容行
        main_frame.rowconfigure(4, weight=0)    # 详情区域
        
        # 左侧操作员列表
        operator_header = ttk.Frame(main_frame)
        operator_header.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(operator_header, text="操作员列表", font=("SimHei", 12, "bold")).pack(side=tk.LEFT)
        
        operator_frame = ttk.Frame(main_frame)
        operator_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.operator_tree = ttk.Treeview(
            operator_frame, 
            columns=("ID", "name", "Unit"), 
            show="headings", 
            height=25
        )
        self.operator_tree.heading("ID", text="操作员ID", anchor="center")
        self.operator_tree.heading("name", text="操作员姓名", anchor="center")
        self.operator_tree.heading("Unit", text="所属单位", anchor="center")
        self.operator_tree.column("ID", width=100, anchor="center")
        self.operator_tree.column("name", width=120, anchor="center")
        self.operator_tree.column("Unit", width=120, anchor="center")
        
        operator_scrollbar = ttk.Scrollbar(operator_frame, orient="vertical", command=self.operator_tree.yview)
        operator_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.operator_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.operator_tree.configure(yscrollcommand=operator_scrollbar.set)
        
        # 绑定操作员选择事件
        self.operator_tree.bind("<<TreeviewSelect>>", self.on_operator_select)
        
        # 中间按钮区域
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ns")
        
        ttk.Button(button_frame, text="添加操作员", command=self.add_operator).pack(fill=tk.X, pady=8)
        ttk.Button(button_frame, text="修改所属单位", command=self.edit_operator_unit).pack(fill=tk.X, pady=8)
        ttk.Button(button_frame, text="删除操作员", command=self.delete_operator).pack(fill=tk.X, pady=8)
        ttk.Separator(button_frame, orient="horizontal").pack(fill=tk.X, pady=15)
        ttk.Button(button_frame, text="刷新所有数据", command=self.refresh_all).pack(fill=tk.X, pady=8)
        
        # 右侧权限列表
        perm_header_frame = ttk.Frame(main_frame)
        perm_header_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Label(perm_header_frame, text="权限列表", font=("SimHei", 12, "bold")).pack(side=tk.LEFT)
        
        # 权限列表容器
        perm_container = ttk.Frame(main_frame)
        perm_container.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        perm_container.columnconfigure(0, weight=1)
        perm_container.rowconfigure(0, weight=1)
        perm_container.rowconfigure(1, weight=1)
        
        # 登记权限列表
        perm1_frame = ttk.LabelFrame(perm_container, text="登记权限列表", padding="5")
        perm1_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.perm1_tree = ttk.Treeview(
            perm1_frame, 
            columns=("ID", "name"), 
            show="headings", 
            height=10
        )
        self.perm1_tree.heading("ID", text="操作员ID", anchor="center")
        self.perm1_tree.heading("name", text="操作员姓名", anchor="center")
        self.perm1_tree.column("ID", width=100, anchor="center")
        self.perm1_tree.column("name", width=120, anchor="center")
        
        perm1_scrollbar = ttk.Scrollbar(perm1_frame, orient="vertical", command=self.perm1_tree.yview)
        perm1_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.perm1_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.perm1_tree.configure(yscrollcommand=perm1_scrollbar.set)
        
        # 签约权限列表
        perm2_frame = ttk.LabelFrame(perm_container, text="签约权限列表", padding="5")
        perm2_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.perm2_tree = ttk.Treeview(
            perm2_frame, 
            columns=("ID", "name"), 
            show="headings", 
            height=10
        )
        self.perm2_tree.heading("ID", text="操作员ID", anchor="center")
        self.perm2_tree.heading("name", text="操作员姓名", anchor="center")
        self.perm2_tree.column("ID", width=100, anchor="center")
        self.perm2_tree.column("name", width=120, anchor="center")
        
        perm2_scrollbar = ttk.Scrollbar(perm2_frame, orient="vertical", command=self.perm2_tree.yview)
        perm2_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.perm2_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.perm2_tree.configure(yscrollcommand=perm2_scrollbar.set)
        
        # 绑定权限选择事件
        self.perm1_tree.bind("<<TreeviewSelect>>", self.on_permission_select)
        self.perm2_tree.bind("<<TreeviewSelect>>", self.on_permission_select)
        
        # 操作员详情区域
        detail_header = ttk.Frame(main_frame)
        detail_header.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Label(detail_header, text="操作员详情", font=("SimHei", 12, "bold")).pack(side=tk.LEFT)
        
        self.detail_frame = ttk.LabelFrame(main_frame, text="详细信息", padding="15")
        self.detail_frame.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        # 详情区域网格布局
        self.detail_frame.columnconfigure(0, weight=0)
        self.detail_frame.columnconfigure(1, weight=1)
        self.detail_frame.columnconfigure(2, weight=0)
        self.detail_frame.columnconfigure(3, weight=1)
        
        # 操作员ID
        ttk.Label(self.detail_frame, text="操作员ID:").grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.id_label = ttk.Label(self.detail_frame, text="", font=("SimHei", 10, "bold"))
        self.id_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        # 操作员姓名
        ttk.Label(self.detail_frame, text="操作员姓名:").grid(row=0, column=2, padx=5, pady=10, sticky="e")
        self.name_label = ttk.Label(self.detail_frame, text="", font=("SimHei", 10, "bold"))
        self.name_label.grid(row=0, column=3, padx=5, pady=10, sticky="w")
        
        # 所属单位
        ttk.Label(self.detail_frame, text="所属单位:").grid(row=1, column=0, padx=5, pady=10, sticky="e")
        self.unit_label = ttk.Label(self.detail_frame, text="", font=("SimHei", 10, "bold"))
        self.unit_label.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        
        # 拥有权限
        ttk.Label(self.detail_frame, text="拥有权限:").grid(row=2, column=0, padx=5, pady=10, sticky="ne")
        
        # 权限复选框框架
        self.permissions_frame = ttk.Frame(self.detail_frame)
        self.permissions_frame.grid(row=2, column=1, columnspan=3, padx=5, pady=10, sticky="w")
        
        # 权限复选框
        self.perm1_var = tk.BooleanVar()
        self.perm1_check = ttk.Checkbutton(
            self.permissions_frame, 
            text="登记权限", 
            variable=self.perm1_var, 
            command=lambda: self.toggle_permission(1, self.perm1_var.get())
        )
        self.perm1_check.pack(side=tk.LEFT, padx=20, pady=5)
        
        self.perm2_var = tk.BooleanVar()
        self.perm2_check = ttk.Checkbutton(
            self.permissions_frame, 
            text="签约权限", 
            variable=self.perm2_var,
            command=lambda: self.toggle_permission(2, self.perm2_var.get())
        )
        self.perm2_check.pack(side=tk.LEFT, padx=20, pady=5)
    
    def load_operators(self):
        """加载所有操作员"""
        # 清空现有数据
        for item in self.operator_tree.get_children():
            self.operator_tree.delete(item)
        
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT ID, operator, Unit FROM {self.operator_table} ORDER BY ID")
            
            for row in cursor.fetchall():
                self.operator_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("加载错误", f"加载操作员时出错: {str(e)}")
        finally:
            conn.close()
    
    def load_permission1(self):
        """加载拥有权限1(日志权限)的操作员"""
        # 清空现有数据
        for item in self.perm1_tree.get_children():
            self.perm1_tree.delete(item)
        
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT p.ID, o.operator 
                FROM {self.permission1_table} p
                JOIN {self.operator_table} o ON p.ID = o.ID
                ORDER BY p.ID
            """)
            
            for row in cursor.fetchall():
                self.perm1_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("加载错误", f"加载日志权限时出错: {str(e)}")
        finally:
            conn.close()
    
    def load_permission2(self):
        """加载拥有权限2(签到权限)的操作员"""
        # 清空现有数据
        for item in self.perm2_tree.get_children():
            self.perm2_tree.delete(item)
        
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT p.ID, o.operator 
                FROM {self.permission2_table} p
                JOIN {self.operator_table} o ON p.ID = o.ID
                ORDER BY p.ID
            """)
            
            for row in cursor.fetchall():
                self.perm2_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("加载错误", f"加载签到权限时出错: {str(e)}")
        finally:
            conn.close()
    
    def on_operator_select(self, event):
        """处理操作员选择事件，显示其权限信息"""
        selected_items = self.operator_tree.selection()
        if not selected_items:
            return
            
        # 获取选中的操作员信息
        selected_item = selected_items[0]
        operator_id, operator_name, unit = self.operator_tree.item(selected_item, "values")
        
        # 更新详情区域
        self.id_label.config(text=operator_id)
        self.name_label.config(text=operator_name)
        self.unit_label.config(text=unit)
        
        # 检查权限
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # 检查日志权限
            cursor.execute(f"SELECT COUNT(*) FROM {self.permission1_table} WHERE ID = %s", (operator_id,))
            has_perm1 = cursor.fetchone()[0] > 0
            self.perm1_var.set(has_perm1)
            
            # 检查签到权限
            cursor.execute(f"SELECT COUNT(*) FROM {self.permission2_table} WHERE ID = %s", (operator_id,))
            has_perm2 = cursor.fetchone()[0] > 0
            self.perm2_var.set(has_perm2)
            
        except Exception as e:
            messagebox.showerror("查询错误", f"查询权限时出错: {str(e)}")
        finally:
            conn.close()
    
    def on_permission_select(self, event):
        """处理权限选择事件，在操作员列表中定位该操作员"""
        # 获取触发事件的控件
        tree = event.widget
        
        selected_items = tree.selection()
        if not selected_items:
            return
            
        # 获取选中的操作员ID
        selected_item = selected_items[0]
        operator_id = tree.item(selected_item, "values")[0]
        
        # 在操作员列表中找到并选中该操作员
        for item in self.operator_tree.get_children():
            if self.operator_tree.item(item, "values")[0] == operator_id:
                self.operator_tree.selection_set(item)
                self.operator_tree.focus(item)
                self.operator_tree.see(item)
                # 触发详情显示
                self.on_operator_select(None)
                break
    
    def toggle_permission(self, permission_num, grant):
        """授予或撤销操作员的权限"""
        operator_id = self.id_label["text"]
        if not operator_id:
            messagebox.showwarning("警告", "请先从左侧列表选择一个操作员")
            return
            
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            table_name = self.permission1_table if permission_num == 1 else self.permission2_table
            permission_name = "日志权限" if permission_num == 1 else "签到权限"
            
            if grant:
                # 授予权限 - 插入记录
                cursor.execute(f"INSERT INTO {table_name} (ID) VALUES (%s)", (operator_id,))
            else:
                # 撤销权限 - 删除记录
                cursor.execute(f"DELETE FROM {table_name} WHERE ID = %s", (operator_id,))
                
            conn.commit()
            messagebox.showinfo("成功", f"{permission_name}已{'授予' if grant else '撤销'}")
            
            # 刷新权限列表
            if permission_num == 1:
                self.load_permission1()
            else:
                self.load_permission2()
                
        except Exception as e:
            messagebox.showerror("权限修改错误", f"修改权限时出错: {str(e)}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_operator(self):
        """添加新操作员"""
        # 获取ID和姓名
        id_str = simpledialog.askstring("添加操作员", "请输入操作员ID:")
        if not id_str or not id_str.isdigit():
            messagebox.showerror("输入错误", "请输入有效的数字ID")
            return
            
        operator_id = int(id_str)
        
        operator_name = simpledialog.askstring("添加操作员", "请输入操作员姓名:")
        if not operator_name:
            messagebox.showerror("输入错误", "请输入操作员姓名")
            return
        
        # 选择Unit
        unit_window = tk.Toplevel(self.root)
        unit_window.title("选择所属单位")
        unit_window.geometry("300x200")
        unit_window.transient(self.root)
        unit_window.grab_set()
        unit_window.resizable(False, False)
        
        ttk.Label(unit_window, text="请选择操作员的所属单位:").pack(pady=20)
        
        unit_var = tk.StringVar(value="娄底")  # 默认选择第一个
        
        frame = ttk.Frame(unit_window)
        frame.pack(pady=10)
        
        for unit in self.unit_all.keys():
            ttk.Radiobutton(
                frame, 
                text=unit, 
                variable=unit_var, 
                value=self.unit_all[unit]
            ).pack(side=tk.LEFT, padx=10)
        
        def save_unit():
            unit = unit_var.get()
            unit_window.destroy()
            
            conn = self.get_db_connection()
            if not conn:
                return
                
            try:
                cursor = conn.cursor()
                # 检查ID是否已存在
                cursor.execute(f"SELECT COUNT(*) FROM {self.operator_table} WHERE ID = %s", (operator_id,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("错误", f"ID为{operator_id}的操作员已存在")
                    return
                    
                # 插入新操作员
                cursor.execute(
                    f"INSERT INTO {self.operator_table} (ID, operator, Unit) VALUES (%s, %s, %s)", 
                    (operator_id, operator_name, unit)
                )
                conn.commit()
                
                messagebox.showinfo("成功", f"操作员 {operator_id} 添加成功")
                self.load_operators()
                
            except Exception as e:
                messagebox.showerror("添加错误", f"添加操作员时出错: {str(e)}")
                conn.rollback()
            finally:
                conn.close()
        
        ttk.Button(unit_window, text="确定", command=save_unit).pack(pady=20)
    
    def edit_operator_unit(self):
        """修改操作员的Unit"""
        selected_items = self.operator_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择一个操作员")
            return
            
        selected_item = selected_items[0]
        operator_id, operator_name, current_unit = self.operator_tree.item(selected_item, "values")
        
        # 选择新的Unit
        unit_window = tk.Toplevel(self.root)
        unit_window.title("修改所属单位")
        unit_window.geometry("300x200")
        unit_window.transient(self.root)
        unit_window.grab_set()
        unit_window.resizable(False, False)
        
        ttk.Label(unit_window, text="请选择新的所属单位:").pack(pady=20)
        
        unit_var = tk.StringVar(value=current_unit)
        
        frame = ttk.Frame(unit_window)
        frame.pack(pady=10)
        for unit in self.unit_all.keys():
            ttk.Radiobutton(
                frame, 
                text=unit, 
                variable=unit_var, 
                value=self.unit_all[unit]
            ).pack(side=tk.LEFT, padx=10)
        
        def save_new_unit():
            new_unit = unit_var.get()
            unit_window.destroy()
            
            conn = self.get_db_connection()
            if not conn:
                return
                
            try:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE {self.operator_table} SET Unit = %s WHERE ID = %s", 
                    (new_unit, operator_id)
                )
                conn.commit()
                
                messagebox.showinfo("成功", f"操作员 {operator_id} 的所属单位已更新为 {new_unit}")
                self.load_operators()
                self.on_operator_select(None)  # 刷新详情
                
            except Exception as e:
                messagebox.showerror("修改错误", f"修改所属单位时出错: {str(e)}")
                conn.rollback()
            finally:
                conn.close()
        
        ttk.Button(unit_window, text="确定", command=save_new_unit).pack(pady=20)
    
    def delete_operator(self):
        """删除操作员"""
        selected_items = self.operator_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择一个操作员")
            return
            
        selected_item = selected_items[0]
        operator_id, operator_name, unit = self.operator_tree.item(selected_item, "values")
        
        if messagebox.askyesno(
            "确认删除", 
            f"确定要删除操作员 {operator_id}({operator_name}) 吗？\n这将同时删除该操作员的所有权限。"
        ):
            conn = self.get_db_connection()
            if not conn:
                return
                
            try:
                cursor = conn.cursor()
                
                # 删除权限记录
                cursor.execute(f"DELETE FROM {self.permission1_table} WHERE ID = %s", (operator_id,))
                cursor.execute(f"DELETE FROM {self.permission2_table} WHERE ID = %s", (operator_id,))
                
                # 删除操作员记录
                cursor.execute(f"DELETE FROM {self.operator_table} WHERE ID = %s", (operator_id,))
                
                conn.commit()
                messagebox.showinfo("成功", f"操作员 {operator_id} 已删除")
                
                # 刷新所有数据
                self.refresh_all()
                
                # 清空详情区域
                self.id_label.config(text="")
                self.name_label.config(text="")
                self.unit_label.config(text="")
                self.perm1_var.set(False)
                self.perm2_var.set(False)
                
            except Exception as e:
                messagebox.showerror("删除错误", f"删除操作员时出错: {str(e)}")
                conn.rollback()
            finally:
                conn.close()
    
    def refresh_all(self):
        """刷新所有数据"""
        self.load_operators()
        self.load_permission1()
        self.load_permission2()

if __name__ == "__main__":
    root = tk.Tk()
    # 设置中文字体支持
    root.option_add("*Font", "SimHei 10")
    app = PermissionManager(root)
    root.mainloop()