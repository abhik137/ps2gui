#!/usr/bin/env python

##Authored by Phani Kumar. Dated: 28/04/2014

from PyQt4 import QtGui, QtCore, QtWebKit
import sys, sqlite3, os
import app_routines

class MyTableWidgetItem(QtGui.QTableWidgetItem):
    def __init__(self, number):
        QtGui.QTableWidgetItem.__init__(self, number, QtGui.QTableWidgetItem.UserType)
        self.__number = number

    def __lt__(self, other):
        return int(self.__number) < int(other.__number)

class app_window(QtGui.QWidget):
	def __init__(self):
		""" Init block. Nothing interesting here."""
		QtGui.QWidget.__init__(self)
		## Make sure the database file exists so that we can go ahead and populate the tablewidget.
		app_routines.check_create_database(app_routines.db_file)
		self.setWindowTitle("PS2 APP")
		self.layout=QtGui.QGridLayout(self)
		self.table = QtGui.QTableWidget(self)
		self.table.setColumnCount(5)
		self.table.setMinimumWidth(573)
		## check for the number of entries and make enough rows for them


		self.table.setWordWrap(True)
		self.table.setSortingEnabled(True)
		self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.table.setHorizontalHeaderLabels(["S.no","Name","Location","Pref","Notes"])
		self.table.verticalHeader().setVisible(False)

		self.pbar = QtGui.QProgressBar()
		self.webView = QtWebKit.QWebView(loadProgress = self.pbar.setValue)
		self.checkbox = QtGui.QCheckBox("Load webpage when clicked",self)
		self.checkbox.setChecked(True)

		self.simplelabel = QtGui.QLabel("",self)
		self.upgrade_button = QtGui.QPushButton("Update PS lists",self)

		self.layout.addWidget(self.table,1,0)
		self.layout.addWidget(self.webView,1,1)
		self.layout.addWidget(self.checkbox,2,0)
		self.layout.addWidget(self.pbar,2,1)
		self.layout.addWidget(self.simplelabel,3,0)
		self.layout.addWidget(self.upgrade_button,3,1,QtCore.Qt.AlignRight)

		self.basic_chores()
		self.table.setColumnWidth(0,35)
		self.table.setColumnWidth(1,240)
		self.table.setColumnWidth(2,80)
		self.table.setColumnWidth(3,50)
		self.table.setColumnWidth(4,150)
		self.table.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
		self.upgrade_button.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Maximum)
		self.table.setAlternatingRowColors(True)
		self.table.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents);

		self.table.itemClicked.connect(self.fetch_and_set_url)
		self.table.itemChanged.connect(self.save_changes)
		self.checkbox.stateChanged.connect(self.set_blank)
		self.upgrade_button.pressed.connect(self.upgrade_handler)
		self.webView.loadFinished.connect(self.sane_scroll)

		self.show()

	def sane_scroll(self):
		self.webView.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, self.webView.page().mainFrame().scrollBarMaximum(QtCore.Qt.Vertical)/2)
		self.webView.page().mainFrame().setScrollBarValue(QtCore.Qt.Horizontal, self.webView.page().mainFrame().scrollBarMaximum(QtCore.Qt.Horizontal)/2)

	def basic_chores(self):
		self.prefnums=[]
		self.update_pref_list()
		conn=sqlite3.connect(app_routines.db_file)
		cur=conn.execute('SELECT COUNT(*) FROM info')
		self.count=cur.fetchone()
		conn.close()
		self.table.setRowCount(self.count[0])
		self.populate_window()
		self.table.resizeColumnsToContents()
		self.simplelabel.setText("Loading complete.")



	def fetch_and_set_url(self,item):
		""" Fetches the url from the info file and sets it to the QWebView if the checkbox is checked"""
		if self.checkbox.isChecked():
			irow=item.row()
			# When sorted the rows might get mangled.
			irowactual= int(self.table.item(irow,0).text())

			conn=sqlite3.connect(app_routines.db_file)
			cur=conn.execute("SELECT url FROM info WHERE sno=(?)", (irowactual,))
			urltup=cur.fetchone()
			conn.close()

			urlstring = "http://www.bits-pilani.ac.in:12355/"+urltup[0].encode('ascii','ignore')
			# http://www.bits-pilani.ac.in:12355/
			self.webView.setUrl(QtCore.QUrl(urlstring))
			
	def populate_window(self):
		""" Reads contents from the ps info file and populates the QTableWidget"""
		conn = sqlite3.connect(app_routines.db_file)
		cur = conn.execute("SELECT * FROM info;")
		contents = cur.fetchall()
		conn.close()

		counter=0
		for tup in contents:
			sitem=QtGui.QTableWidgetItem(str(tup[0]))
			sitem.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
			self.table.setItem(counter,0,sitem)

			nameitem = QtGui.QTableWidgetItem(str(tup[1]))
			nameitem.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
			self.table.setItem(counter,1,nameitem)

			locitem = QtGui.QTableWidgetItem(str(tup[2]))
			locitem.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
			self.table.setItem(counter,2,locitem)

			self.table.setItem(counter,3,MyTableWidgetItem(str(tup[4])))

			self.table.setItem(counter,4,QtGui.QTableWidgetItem(str(tup[5])))

			counter=counter+1



	def save_changes(self, item):
		""" Writes changes made to the pref and notes column to the database"""
		columnchanged = item.column()
		conn=sqlite3.connect(app_routines.db_file)

		if columnchanged == 3:
			irow=item.row()
			irowactual= int(self.table.item(irow,0).text())

			try:
				data = int(item.text())
				if not data < 1 and not data > self.count[0] and data not in self.prefnums:
					conn.execute("UPDATE info SET pref=(?) WHERE sno=(?)", (data,irowactual,) )
					conn.commit()
					conn.close()
					self.simplelabel.setText("<b>Preference updated.</b>")
				elif data == 0:
					pass
				else:
					takenby = conn.execute("SELECT name FROM info where pref=(?)", (data,)).fetchone()[0]
					self.simplelabel.setText("<b>The preference has already been taken by %s. Reverting</b>" % takenby)
					item.setText("0")
					data = 0
					conn.execute("UPDATE info SET pref=(?) WHERE sno=(?)", (data,irowactual,) )
					conn.commit()
					conn.close()
			except:
				self.simplelabel.setText("<b>Please enter a numeric value</b>")
				item.setText("0")
				data = 0
				conn.execute("UPDATE info SET pref=(?) WHERE sno=(?)", (data,irowactual,) )
				conn.commit()
				conn.close()
				

			self.update_pref_list()

		elif columnchanged == 4:
			irow=item.row()
			irowactual= int(self.table.item(irow,0).text())
			data = str(item.text())
			conn.execute("UPDATE info SET notes=(?) WHERE sno=(?)", (data,irowactual,) )
			conn.commit()
			conn.close()
			self.simplelabel.setText("Note updated.")

	def set_blank(self,state):
		""" Sets the QWebView to a blank web page"""
		if not self.checkbox.isChecked():
			self.webView.setUrl(QtCore.QUrl('about:blank'))
		else:
			pass

	def update_pref_list(self):
		""" Updates the temporary preference list used to ignore duplicates"""
		conn=sqlite3.connect(app_routines.db_file)
		cur=conn.execute("SELECT pref from info")
		tempdata=cur.fetchall()
		conn.close()

		self.prefnums=[]

		for tup in tempdata:
			if int(tup[0]) != 0:
				self.prefnums.append(tup[0])

	def remove_all_rows(self):
		while self.table.rowCount() > 0:
			self.table.removeRow(0)

	def upgrade_handler(self):
		tempdatabase = app_routines.app_home + "/tempdatabase.db"
		app_routines.check_create_database(tempdatabase)
		if app_routines.migrate_database(app_routines.db_file,tempdatabase):
			self.remove_all_rows()
			print "This might take some time. Stand by."
			self.basic_chores()
			self.simplelabel.setText("<b>PS database updated</b>")

		


def main():
	app_loop = QtGui.QApplication(sys.argv)
	run_window = app_window()
	sys.exit(app_loop.exec_())

if __name__=='__main__':
	main()