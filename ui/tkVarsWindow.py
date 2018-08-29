from Tkinter import *
import tkFileDialog
import ScrolledText
import os


class FileBrowser:
	def __init__(self,varsWindow,variableName):
		self.varsWindow=varsWindow
		self.variableName=variableName
		
	def onDialog(self):
		# TODO: assign file types based on constraints in Variable object
		filetypes=(("all files","*.*"))
		filename=tkFileDialog.askopenfilename()#filetypes=filetypes)
		print 'chose',self.variableName,self.varsWindow.tkVars[self.variableName],filename
		self.varsWindow.tkVars[self.variableName]=filename

		
class ToolTip:
	def __init__(self,bindToControl,text):
		self.text=text
		self.control=bindToControl
		bindToControl.bind("<Enter>",self.onMouseEnter)
		bindToControl.bind("<Leave>",self.onMouseExit)
		bindToControl.bind("<ButtonPress>",self.onMouseExit)
		self.timerId=None
		self.tipWindow=None

	def onMouseEnter(self,event=None):
		self.startHoverTimer()

	def onMouseExit(self,event=None):
		self.stopHoverTimer()
		self.hideTip()

	def startHoverTimer(self):
		self.stopHoverTimer()
		self.timerId=self.control.after(1500,self.showTip)

	def stopHoverTimer(self):
		if self.timerId!=None:
			self.control.after_cancel(self.timerId)
			self.timerId=None

	def showTip(self):
		if self.tipWindow!=None:
			return
		# The tip window must be completely outside the control;
		# otherwise when the mouse enters the tip window we get
		# a leave event and it disappears, and then we get an enter
		# event and it reappears, and so on forever :-(
		x = self.control.winfo_rootx() + 20
		y = self.control.winfo_rooty() + self.control.winfo_height() + 1
		self.tipWindow = tw = Toplevel(self.control)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))
		label=Label(self.tipWindow,text=self.text,justify=LEFT,background="#ffffe0",relief=SOLID,borderwidth=1)
		label.pack()
		
	def hideTip(self):
		if self.tipWindow!=None:
			self.tipWindow.destroy()
			self.tipWindow=None
		
		
class TkVariablesWindow(Frame):
	ICON_PATH=os.path.abspath(__file__).rsplit(os.sep,2)[0]+os.sep+'icon.ico'
	
	def __init__(self,name,variables,master=None):
		"""
		values={name:(value,desc)}
		
		TODO:
			1) Need text areas
			2) Needs validation like http://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter#4140988
			3) Could use date, time, color pickers
			4) Need to come up with some kind of constraints, be it number ranges or allowed file extensions
		"""
		self.variables=variables
		self.tkVars={}
		self.accepted=False
		self.tooltips=[]
		if master==None:
			master=Tk()
			master.wm_title(name)
			master.minsize(400,300)
			master.iconbitmap(default=self.ICON_PATH)
			#master.bind('<Return>',self.onEnterKey)			
		Frame.__init__(self, master)
		self.pack(fill=BOTH,expand=1)
		self.createWidgets()
		
	def onEnterKey(self,control):
		self.accepted=True
		self.quit()
		
	def onOk(self):
		self.accepted=True
		self.quit()
		
	def onCancel(self):
		self.accepted=False
		self.quit()
		
	def createWidgets(self):
		row=0
		control=None
		self.grid_columnconfigure(1,weight=1)
		for v in self.variables.values():
			if v.uitype=='checkbox':
				tkVar=IntVar()
				self.tkVars[v.name]=tkVar
				control=Checkbutton(self,text=v.name.replace('_',' '),variable=tkVar)
				if v.toBool():
					tkVar.set(1)
				else:
					tkVar.set(0)
				control.grid(row=row,column=0,columnspan=3,sticky="W")
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
			elif v.uitype=='color':
				# TODO: needs validation
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='date':
				# TODO: needs validation
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='datetime':
				# TODO: needs validation
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='datetime-local':
				# TODO: needs validation
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='email':
				# TODO: needs validation
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,columnspan=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='file':
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,sticky="EW")
				fb=FileBrowser(self,v.name)
				bn=Button(self,text='...',command=fb.onDialog)
				bn.grid(row=row,column=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
					self.tooltips.append(ToolTip(bn,v.description))
			elif v.uitype=='hidden':
				pass
			elif v.uitype=='image':
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1)
				fb=FileBrowser(self,v.name)
				bn=Button(self,text='...',command=fb.onDialog)
				bn.grid(row=row,column=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
					self.tooltips.append(ToolTip(bn,v.description))
			elif v.uitype=='month':
				# TODO: needs validation
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='number':
				# TODO: needs validation
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,columnspan=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='password':
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,show='*',textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,columnspan=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='radio':
				tkVar=IntVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,text=v.name.replace('_',' '),variable=tkVar)
				tkVar.set(v.value)
				value=v.value
				tkvar.set(value)
				control.grid(row=row,column=0,columnspan=3)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
			elif v.uitype=='range':
				# TODO: needs validation
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,columnspan=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='search':
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,columnspan=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='tel':
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,columnspan=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='text':
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,columnspan=2,sticky="WE")
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='textarea':
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				control=ScrolledText.ScrolledText(self,height=3)
				tkVar=control # In total breaking with TK's pattern, we have to get the data directly from the control!
				self.tkVars[v.name]=tkVar
				control.pack()
				control.delete('1.0',END)
				control.insert('insert',v.value)
				control.grid(row=row,column=1,columnspan=2,sticky="WE")
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			elif v.uitype=='time':
				pass
			elif v.uitype=='url':
				label=Label(self,text=v.name.replace('_',' '))
				label.grid(row=row,column=0)
				tkVar=StringVar()
				self.tkVars[v.name]=tkVar
				control=Entry(self,textvariable=tkVar)
				tkVar.set(v.value)
				control.grid(row=row,column=1,columnspan=2)
				if v.description!=None and v.description!='':
					self.tooltips.append(ToolTip(control,v.description))
					self.tooltips.append(ToolTip(label,v.description))
			else:
				print 'ERR: Unknown or inconclusive variable type -',v.uitype
				raise Exception()
			if control!=None:
				if row==0:
					control.focus_set()
				row=row+1
		self.grid_rowconfigure(row,weight=5)
		row=row+1
		buttonPanel=Frame(self)
		buttonPanel.grid(columnspan=3,sticky='EWS')
		buttonPanel.grid_columnconfigure(0,weight=1)
		buttonPanel.grid_columnconfigure(1,weight=5)
		buttonPanel.grid_columnconfigure(2,weight=1)
		buttonPanel.grid_columnconfigure(3,weight=5)
		buttonPanel.grid_columnconfigure(4,weight=1)
		okButton=Button(buttonPanel,text='OK',default='active',command=self.onOk)
		okButton.grid(row=0,column=1,sticky='EWS')
		cancelButton=Button(buttonPanel,text='Cancel',command=self.onCancel)
		cancelButton.grid(row=0,column=3,sticky='EWS')
			
	def run(self):
		self.mainloop()
		for k,v in self.variables.items():
			if k in self.tkVars: # need to check since hidden ones aren't in there!
				tkVar=self.tkVars[k]
				if type(tkVar) in [str,unicode]:
					self.variables[k].value=tkVar
				elif tkVar.__class__==StringVar:
					self.variables[k].value=tkVar.get().strip()
				else:
					self.variables[k].value=tkVar.get(1.0,END).strip()
		try:
			self.master.destroy()
		except:
			pass
		return self.accepted
		
		
def runVarsWindow(variables,title):
	"""
	takes an array of variable objects to edit
	
	returns [new variables], or None if cancelled
	"""
	app=TkVariablesWindow(title,variables)
	return app.run()


if __name__ == '__main__':
	vals={
		'filename':('default text','the name of the file'),
		'puppies':('3','how many puppies to kick')
	}
	app=TkVariablesWindow("Edit Stuff",vals)
	vals2=app.run()
	print vals2