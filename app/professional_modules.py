from __future__ import annotations
from datetime import date
from typing import Any
from PySide6.QtWidgets import QDialog,QDialogButtonBox,QFormLayout,QHBoxLayout,QLabel,QLineEdit,QMessageBox,QPushButton,QTableWidget,QTableWidgetItem,QVBoxLayout,QWidget
from sqlalchemy import select
from .authorization import ROLE_PERMISSIONS
from .database import User, hash_password
from .models_extended import AttendanceRecord,Certificate,ClassRoom,Communication,DisciplineCase,DocumentRecord,Employee,Exam,Expense,HealthRecord,InventoryItem,LibraryBook,LibraryIssue,Mark,Parent,SchoolEvent,Section,Subject,TimetableEntry,Vehicle

MODULES={
"academics":("Academics",ClassRoom,["code","name","grade","academic_year","status"]),
"classes":("Classes & Sections",Section,["code","name","class_name","room","capacity"]),
"subjects":("Subjects",Subject,["code","name","grade","teacher","weekly_periods"]),
"timetable":("Timetable",TimetableEntry,["day","class_name","subject","teacher","start_time","end_time","room"]),
"attendance":("Attendance",AttendanceRecord,["student_code","student_name","class_name","attendance_date","status","note"]),
"exams":("Exams",Exam,["code","name","exam_type","class_name","start_date","status"]),
"results":("Results / Marks",Mark,["exam_code","student_code","subject","marks","total_marks","grade"]),
"hr":("HR / Employees",Employee,["employee_code","name","department","position","phone","salary","status"]),
"library":("Library Books",LibraryBook,["accession_no","title","author","category","quantity","available"]),
"library_issues":("Library Issue / Return",LibraryIssue,["accession_no","borrower","issue_date","due_date","return_date","status"]),
"transport":("Transport",Vehicle,["vehicle_no","driver","route","capacity","status"]),
"inventory":("Inventory / Store",InventoryItem,["item_code","name","category","quantity","minimum_stock","unit","supplier"]),
"expenses":("Expenses",Expense,["expense_code","category","amount","expense_date","paid_to","note"]),
"parents":("Parents / Guardians",Parent,["parent_code","name","relationship","phone","student_codes"]),
"communication":("Communication",Communication,["channel","audience","subject","message","sent_at","status"]),
"events":("Events / Calendar",SchoolEvent,["title","event_date","event_type","location","description"]),
"discipline":("Discipline",DisciplineCase,["student_code","incident_date","category","description","action_taken","status"]),
"health":("Health / Medical",HealthRecord,["student_code","blood_group","allergy","condition","emergency_contact","note"]),
"documents":("Documents",DocumentRecord,["document_no","document_type","owner","file_path","status"]),
"certificates":("Certificates",Certificate,["certificate_no","student_code","certificate_type","issue_date","status"]),}

def can(role,module,action):
    return role=="Super Admin" or action in ROLE_PERMISSIONS.get(role,{}).get(module,set())

class RecordDialog(QDialog):
    def __init__(self,db,model,fields,title,existing=None,parent=None):
        super().__init__(parent); self.db=db; self.model=model; self.fields=fields; self.existing=existing; self.inputs={}; self.setWindowTitle(title); self.setMinimumWidth(560)
        form=QFormLayout(self)
        for field in fields:
            edit=QLineEdit("" if existing is None else str(getattr(existing,field,""))); self.inputs[field]=edit; form.addRow(field.replace("_"," ").title(),edit)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(self.save); buttons.rejected.connect(self.reject); form.addRow(buttons)
    def save(self):
        try:
            with self.db.Session.begin() as session:
                record=session.get(self.model,self.existing.id) if self.existing else self.model()
                for field,edit in self.inputs.items():
                    raw=edit.text().strip(); typ=getattr(getattr(self.model,field).property.columns[0].type,"python_type",str)
                    value=int(raw or 0) if typ is int else float(raw or 0) if typ is float else date.fromisoformat(raw) if typ is date and raw else date.today() if typ is date else raw
                    setattr(record,field,value)
                if not self.existing: session.add(record)
                self.db.log(session,"UPDATE" if self.existing else "CREATE",self.model.__tablename__,f"Record saved in {self.model.__tablename__}")
            self.accept()
        except Exception as exc: QMessageBox.warning(self,"Could not save",str(exc))

class ProfessionalModulePage(QWidget):
    def __init__(self,db,main_window,key):
        super().__init__(); self.db=db; self.main_window=main_window; self.key=key; self.title_text,self.model,self.fields=MODULES[key]; self.role=str(main_window.current_user.get("role","Viewer")); self.build(); self.refresh()
    def build(self):
        layout=QVBoxLayout(self); head=QHBoxLayout(); title=QLabel(self.title_text); title.setObjectName("pageTitle"); head.addWidget(title); head.addStretch()
        add=QPushButton("＋  Add record"); add.setObjectName("primaryButton"); add.setEnabled(can(self.role,self.key,"create")); add.clicked.connect(self.add_record); head.addWidget(add); layout.addLayout(head)
        layout.addWidget(QLabel("Local SQLite · RBAC protected · Audit logged",objectName="muted")); tools=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText("Search records…"); self.search.textChanged.connect(self.refresh); tools.addWidget(self.search); ref=QPushButton("↻ Refresh"); ref.clicked.connect(self.refresh); tools.addWidget(ref); layout.addLayout(tools)
        self.table=QTableWidget(0,len(self.fields)+1); self.table.setHorizontalHeaderLabels(["ID"]+[f.replace("_"," ").title() for f in self.fields]); self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.table.horizontalHeader().setStretchLastSection(True); self.table.doubleClicked.connect(self.edit_selected); layout.addWidget(self.table)
        foot=QHBoxLayout(); self.edit=QPushButton("Edit"); self.edit.setEnabled(can(self.role,self.key,"edit")); self.edit.clicked.connect(self.edit_selected); self.delete=QPushButton("Delete"); self.delete.setEnabled(can(self.role,self.key,"delete")); self.delete.clicked.connect(self.delete_selected); foot.addWidget(QLabel(f"Role: {self.role}")); foot.addStretch(); foot.addWidget(self.edit); foot.addWidget(self.delete); layout.addLayout(foot)
    def refresh(self,*args):
        with self.db.Session() as session: records=session.scalars(select(self.model).order_by(self.model.id.desc())).all()
        q=self.search.text().strip().lower(); records=[r for r in records if not q or q in " ".join(str(getattr(r,f,"")) for f in self.fields).lower()]
        self.table.setRowCount(0)
        for row,r in enumerate(records):
            self.table.insertRow(row); self.table.setItem(row,0,QTableWidgetItem(str(r.id)))
            for col,f in enumerate(self.fields,1): self.table.setItem(row,col,QTableWidgetItem(str(getattr(r,f,""))))
    def selected_id(self):
        row=self.table.currentRow(); return int(self.table.item(row,0).text()) if row>=0 else None
    def add_record(self):
        if can(self.role,self.key,"create") and RecordDialog(self.db,self.model,self.fields,f"Add {self.title_text}",parent=self).exec()==QDialog.DialogCode.Accepted: self.refresh()
    def edit_selected(self,*args):
        ident=self.selected_id()
        if ident is None or not can(self.role,self.key,"edit"): return
        with self.db.Session() as session:
            r=session.get(self.model,ident); data={f:getattr(r,f) for f in self.fields} if r else None
        if data and RecordDialog(self.db,self.model,self.fields,f"Edit {self.title_text}",self.model(id=ident,**data),self).exec()==QDialog.DialogCode.Accepted: self.refresh()
    def delete_selected(self):
        ident=self.selected_id()
        if ident is None or not can(self.role,self.key,"delete"): return
        if QMessageBox.question(self,"Confirm deletion","Delete this record? This action will be audited.")!=QMessageBox.StandardButton.Yes:return
        with self.db.Session.begin() as session:
            r=session.get(self.model,ident)
            if r: session.delete(r); self.db.log(session,"DELETE",self.model.__tablename__,f"Record {ident} deleted")
        self.refresh()

class ProfessionalUsersPage(QWidget):
    def __init__(self,db,main_window):
        super().__init__(); self.db=db; layout=QVBoxLayout(self); t=QLabel("Users & Roles"); t.setObjectName("pageTitle"); layout.addWidget(t); layout.addWidget(QLabel("17 school roles with module/action permissions",objectName="muted")); self.table=QTableWidget(0,4); self.table.setHorizontalHeaderLabels(["ID","Name","Username","Role"]); self.table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.table); add=QPushButton("＋ Add user"); add.setObjectName("primaryButton"); add.clicked.connect(self.add_user); layout.addWidget(add); self.refresh()
    def refresh(self):
        with self.db.Session() as session: users=session.scalars(select(User).order_by(User.id)).all()
        self.table.setRowCount(0)
        for row,u in enumerate(users):
            self.table.insertRow(row)
            for col,v in enumerate([u.user_code,u.full_name,u.username,u.role]): self.table.setItem(row,col,QTableWidgetItem(str(v)))
    def add_user(self):
        d=QDialog(self); d.setWindowTitle("Create school user"); f=QFormLayout(d); name,user,pw,role=QLineEdit(),QLineEdit(),QLineEdit(),QLineEdit(); pw.setEchoMode(QLineEdit.EchoMode.Password); role.setPlaceholderText("Exact role name"); f.addRow("Full name",name); f.addRow("Username",user); f.addRow("Password",pw); f.addRow("Role",role); b=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel); f.addRow(b); b.accepted.connect(d.accept); b.rejected.connect(d.reject)
        if d.exec()!=QDialog.DialogCode.Accepted:return
        if len(pw.text())<8 or role.text().strip() not in ROLE_PERMISSIONS: QMessageBox.warning(self,"Invalid data","Password must be 8+ characters and role must match a defined school role."); return
        with self.db.Session.begin() as session:
            u=User(user_code=self.db.next_code(session,User,"user_code","USR"),username=user.text().strip(),full_name=name.text().strip(),password_hash=hash_password(pw.text()),role=role.text().strip()); session.add(u); self.db.log(session,"CREATE","Users",f"{u.username} created as {u.role}")
        self.refresh()
