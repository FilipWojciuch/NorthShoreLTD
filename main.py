import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pandas as pd
import random
from database_setup import database_run, execute_query
from security import verify_login, log_event


class NorthshoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Northshore Logistics Ltd - Centralised Management System")
        self.root.geometry("1200x850")

        self.current_user = None
        self.user_role = None

        database_run()
        self.show_login_screen()

    # --- UI UTILITIES ---
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # --- LOGIN SCREEN ---
    def show_login_screen(self):
        self.clear_window()
        frame = tk.Frame(self.root, padx=30, pady=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="NORTHSHORE LOGISTICS", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(frame, text="Username").pack()
        self.u_entry = tk.Entry(frame, width=30)
        self.u_entry.pack(pady=5)

        tk.Label(frame, text="Password").pack()
        self.p_entry = tk.Entry(frame, width=30, show="*")
        self.p_entry.pack(pady=5)

        tk.Button(frame, text="Login", bg="#27ae60", fg="white", width=20,
                  command=self.handle_login).pack(pady=20)

    def handle_login(self):
        u, p = self.u_entry.get(), self.p_entry.get()
        role = verify_login(u, p)
        if role:
            self.current_user, self.user_role = u, role
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    # --- DASHBOARD LAYOUT (RBAC INTEGRATED) ---
    def show_dashboard(self):
        self.clear_window()
        # Sidebar Navigation
        self.sidebar = tk.Frame(self.root, width=220, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")

        tk.Label(self.sidebar, text="LOGISTICS PANEL", fg="white", bg="#2c3e50", pady=20).pack()

        # RBAC Logic: Filter buttons based on user_role
        if self.user_role in ["Admin", "Shipment staff"]:
            tk.Button(self.sidebar, text="📦 View Shipments", command=self.view_shipments,
                      bg="#34495e", fg="white", relief="flat", pady=10, anchor="w", padx=15).pack(fill="x", pady=1)
            tk.Button(self.sidebar, text="➕ Register Shipment", command=self.add_shipment_form,
                      bg="#34495e", fg="white", relief="flat", pady=10, anchor="w", padx=15).pack(fill="x", pady=1)

        if self.user_role in ["Admin", "Shipment staff", "Drivers"]:
            tk.Button(self.sidebar, text="🔄 Update Delivery", command=self.update_delivery_form,
                      bg="#34495e", fg="white", relief="flat", pady=10, anchor="w", padx=15).pack(fill="x", pady=1)

        if self.user_role in ["Admin"]:
            tk.Button(self.sidebar, text="💰 Financial Report", command=self.view_financial_report,
                      bg="#34495e", fg="white", relief="flat", pady=10, anchor="w", padx=15).pack(fill="x", pady=1)

        if self.user_role in ["Admin", "Warehouse staff"]:
            tk.Button(self.sidebar, text="🏠 Inventory Mgmt", command=self.update_inventory_form,
                      bg="#34495e", fg="white", relief="flat", pady=10, anchor="w", padx=15).pack(fill="x", pady=1)
            tk.Button(self.sidebar, text="🚛 Fleet Mgmt", command=self.update_fleet_form,
                      bg="#34495e", fg="white", relief="flat", pady=10, anchor="w", padx=15).pack(fill="x", pady=1)

        if self.user_role == "Admin":
            tk.Button(self.sidebar, text="📜 Security logs", command=self.view_audit_logs,
                      bg="#c0392b", fg="white", relief="flat", pady=10, anchor="w", padx=15).pack(fill="x", pady=20)

        tk.Button(self.sidebar, text="🚪 Logout", command=self.show_login_screen).pack(side="bottom", fill="x", pady=10)

        # Dynamic Content Area
        self.content_area = tk.Frame(self.root, bg="#ecf0f1", padx=20, pady=20)
        self.content_area.pack(side="right", expand=True, fill="both")

        tk.Label(self.content_area, text=f"System Active: {self.current_user} ({self.user_role})",
                 font=("Arial", 12), bg="#ecf0f1").pack(anchor="ne")

    # --- VIEW COMPONENT (With Sliders/Scrollbars) ---
    def view_table_gui(self, table_name):
        self.clear_content()
        tk.Label(self.content_area, text=f"CURRENT {table_name.upper()} RECORDS",
                 font=("Arial", 16, "bold"), bg="#ecf0f1").pack(pady=10)

        container = tk.Frame(self.content_area)
        container.pack(expand=True, fill="both")

        sy = tk.Scrollbar(container, orient="vertical")
        sy.pack(side="right", fill="y")
        sx = tk.Scrollbar(container, orient="horizontal")
        sx.pack(side="bottom", fill="x")

        with sqlite3.connect('northshore.db') as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

        tree = ttk.Treeview(container, columns=list(df.columns), show='headings',
                            yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.config(command=tree.yview)
        sx.config(command=tree.xview)

        for col in df.columns:
            tree.heading(col, text=col.upper())
            tree.column(col, width=150)

        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
        tree.pack(expand=True, fill="both")

    def view_shipments(self):
        self.view_table_gui("shipments")

    # --- SHIPMENT OPERATIONS ---
    def add_shipment_form(self):
        self.clear_content()
        tk.Label(self.content_area, text="Register New Shipment", font=("Arial", 16, "bold"), bg="#ecf0f1").pack(
            pady=10)

        fields = ["ID", "Order Number", "Sender", "Receiver", "Base Cost (£)", "Vehicle ID"]
        entries = {}
        for f in fields:
            tk.Label(self.content_area, text=f, bg="#ecf0f1").pack()
            e = tk.Entry(self.content_area, width=40);
            e.pack(pady=2)
            entries[f] = e

        def save():
            status, sur = random.choice([("In Transit", 0.0), ("Delayed", 15.0), ("Damaged", 50.0), ("Rerouted", 12.0)])
            try:
                execute_query(
                    "INSERT INTO shipments (shipment_id, order_number, sender_details, receiver_details, cost, vehicle_id, status, surcharges) VALUES (?,?,?,?,?,?,?,?)",
                    (entries["ID"].get(), entries["Order Number"].get(), entries["Sender"].get(),
                     entries["Receiver"].get(), float(entries["Base Cost (£)"].get()), entries["Vehicle ID"].get(),
                     status, sur))
                messagebox.showinfo("Success", f"Shipment Registered.\nStatus: {status}\nSurcharge: £{sur}")
                self.view_shipments()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))

        tk.Button(self.content_area, text="Submit Shipment", bg="#27ae60", fg="white", command=save).pack(pady=20)

    def update_delivery_form(self):
        self.clear_content()
        tk.Label(self.content_area, text="Update Existing Delivery", font=("Arial", 16, "bold"), bg="#ecf0f1").pack(
            pady=10)

        fields = {"ID": "", "Status": "", "Driver": "", "Date": "", "Route": "", "Payment": ""}
        for f in fields:
            tk.Label(self.content_area, text=f, bg="#ecf0f1").pack()
            fields[f] = tk.Entry(self.content_area, width=40);
            fields[f].pack()

        def commit():
            with sqlite3.connect('northshore.db') as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE shipments SET status=?, driver_name=?, delivery_date=?, route_details=?, payment_status=? WHERE shipment_id=?",
                    (fields["Status"].get(), fields["Driver"].get(), fields["Date"].get(), fields["Route"].get(),
                     fields["Payment"].get(), fields["ID"].get()))
                if cur.rowcount == 0:
                    messagebox.showerror("Error", "Shipment ID not found!")
                else:
                    messagebox.showinfo("Success", "Delivery updated.")
                    if self.user_role in ["Admin", "Shipment staff"]:
                        self.view_shipments()

        tk.Button(self.content_area, text="Update Record", bg="#2980b9", fg="white", command=commit).pack(pady=15)

    # --- SMART INVENTORY & FLEET (Upsert Logic) ---
    def update_inventory_form(self):
        self.clear_content()
        tk.Label(self.content_area, text="Inventory Management", font=("Arial", 16, "bold"), bg="#ecf0f1").pack(pady=10)

        inputs = {"Name": "", "WH_ID": "", "Qty": "", "Level": ""}
        for i in inputs:
            tk.Label(self.content_area, text=i).pack()
            inputs[i] = tk.Entry(self.content_area);
            inputs[i].pack()

        def do_save():
            name = inputs["Name"].get()
            with sqlite3.connect('northshore.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT item_id FROM inventory WHERE item_name = ?", (name,))
                if cur.fetchone():
                    cur.execute("UPDATE inventory SET quantity=?, warehouse_id=?, reorder_level=? WHERE item_name=?",
                                (inputs["Qty"].get(), inputs["WH_ID"].get(), inputs["Level"].get(), name))
                    msg = "Stock Updated!"
                else:
                    cur.execute(
                        "INSERT INTO inventory (item_name, warehouse_id, quantity, reorder_level) VALUES (?,?,?,?)",
                        (name, inputs["WH_ID"].get(), inputs["Qty"].get(), inputs["Level"].get()))
                    msg = "New Item Added!"
                messagebox.showinfo("Success", msg)
                self.view_table_gui("inventory")

        tk.Button(self.content_area, text="Save / Update Item", bg="#27ae60", fg="white", command=do_save).pack(pady=10)
        tk.Button(self.content_area, text="View All Inventory", command=lambda: self.view_table_gui("inventory")).pack()

    def update_fleet_form(self):
        self.clear_content()
        tk.Label(self.content_area, text="Fleet Management", font=("Arial", 16, "bold"), bg="#ecf0f1").pack(pady=10)

        inputs = {"Vehicle ID": "", "Capacity": "", "Status": ""}
        for i in inputs:
            tk.Label(self.content_area, text=i).pack()
            inputs[i] = tk.Entry(self.content_area);
            inputs[i].pack()

        def do_save():
            v_id = inputs["Vehicle ID"].get()
            with sqlite3.connect('northshore.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT vehicle_id FROM vehicles WHERE vehicle_id = ?", (v_id,))
                if cur.fetchone():
                    cur.execute("UPDATE vehicles SET availability=?, capacity=? WHERE vehicle_id=?",
                                (inputs["Status"].get(), inputs["Capacity"].get(), v_id))
                    msg = "Vehicle Updated!"
                else:
                    cur.execute("INSERT INTO vehicles (vehicle_id, capacity, availability) VALUES (?,?,?)",
                                (v_id, inputs["Capacity"].get(), inputs["Status"].get()))
                    msg = "Vehicle Registered!"
                messagebox.showinfo("Success", msg)
                self.view_table_gui("vehicles")

        tk.Button(self.content_area, text="Save / Update Vehicle", bg="#f39c12", fg="white", command=do_save).pack(
            pady=10)
        tk.Button(self.content_area, text="View All Vehicles", command=lambda: self.view_table_gui("vehicles")).pack()

    def view_financial_report(self):
        self.clear_content()
        tk.Label(self.content_area, text="Financial & Surcharge Resolution", font=("Arial", 16, "bold"),
                 bg="#ecf0f1").pack(pady=10)
        with sqlite3.connect('northshore.db') as conn:
            df = pd.read_sql_query(
                "SELECT shipment_id, cost, surcharges, (cost+surcharges) as total, status FROM shipments", conn)

        tree = ttk.Treeview(self.content_area, columns=list(df.columns), show='headings')
        for col in df.columns: tree.heading(col, text=col.upper())
        for _, row in df.iterrows(): tree.insert("", "end", values=list(row))
        tree.pack(expand=True, fill="both")

    def view_audit_logs(self):
        self.clear_content()
        tk.Label(self.content_area, text="ADMIN ONLY: SECURITY AUDIT TRAIL", font=("Arial", 16, "bold"),
                 bg="#ecf0f1").pack(pady=10)
        t = tk.Text(self.content_area, height=30);
        t.pack(fill="both")
        try:
            with open('audit_log.txt', 'r') as f:
                t.insert("1.0", f.read())
        except:
            t.insert("1.0", "Logs empty.")


if __name__ == "__main__":
    root = tk.Tk()
    app = NorthshoreGUI(root)
    root.mainloop()