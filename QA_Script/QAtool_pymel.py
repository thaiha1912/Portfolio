"""QA Tool PyMEL Module

Author: Thai Ha Trieu (Hannah Trieu)
Studio: Vintata Animation Studio
Role: Rigger

Alternative PyMEL-based implementation of the QA Tool UI for
character and prop rig validation and cleanup.
"""

from pymel.core import *
from maya import OpenMayaUI as omui
from Qt import QtWidgets, QtCore, QtGui
import Qt
from functools import partial
import re
import os
from ngSkinTools.layerUtils import LayerUtils

if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
elif Qt.__binding__.startswith("PyQt"):
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal


def getMayaMainWindow():
    """Get Maya's main window as a Qt widget.
    
    Returns:
        QMainWindow: Maya main window widget
    """
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(int(win), QtWidgets.QMainWindow)
    return ptr


class QAtool(QtWidgets.QWidget):
    """PyMEL-based QA Tool UI class.
    
    Provides interface for rig validation and cleanup using PyMEL.
    """
    
    def __init__(self):
        """Initialize QA Tool UI."""
        try:
            deleteUI("qa_tool_ui")
        except NameError:
            pass
        parent = QtWidgets.QDialog(parent=getMayaMainWindow())
        parent.setObjectName("qa_tool_ui")
        layout = QtWidgets.QVBoxLayout(parent)
        super(QAtool, self).__init__(parent=parent)
        parent.setWindowTitle("QA Tool Python v01")
        self.topNode = None
        self.parent().layout().addWidget(self)
        self.buildUI()
        
        self.rigGrpName = None
        self.listAttrObj = None
        self.listRef = ls(references=True)
        self.numListRef = len(self.listRef)
        self.topNode = None
        parent.show()
    
    def buildUI(self):
        """Build the user interface components."""
        self.vLayout = QtWidgets.QVBoxLayout(self)
        dummy = QtWidgets.QWidget()
        
        layout = QtWidgets.QGridLayout(dummy)
        layout.setColumnMinimumWidth(0, 200)
        self.vLayout.addWidget(dummy)
        
        self.charTopnode = QtWidgets.QLineEdit()
        self.charTopnode.setPlaceholderText("Select character node")
        self.charTopnode.setReadOnly(1)
        layout.addWidget(self.charTopnode, 0, 0, 1, 2)

        self.selectBtn = QtWidgets.QPushButton("Select")
        self.selectBtn.clicked.connect(self.selBtnClicked)
        layout.addWidget(self.selectBtn, 0, 2)
        
        self.expDir = QtWidgets.QLineEdit()
        self.expDir.setPlaceholderText("File export directory")
        layout.addWidget(self.expDir, 1, 0, 1, 2)

        dirBtn = QtWidgets.QPushButton("Choose dir")
        layout.addWidget(dirBtn, 1, 2)	


	
		dummy2 = QtWidgets.QWidget()
        hLayout = QtWidgets.QHBoxLayout(dummy2)
        self.vLayout.addWidget(dummy2)
        
        self.maCheckBox = QtWidgets.QRadioButton(".ma")
        self.maCheckBox.setChecked(1)
        hLayout.addWidget(self.maCheckBox)

        self.mbCheckBox = QtWidgets.QRadioButton(".mb")
        hLayout.addWidget(self.mbCheckBox)
        
        self.openSButton = QtWidgets.QCheckBox("Open submit file after export")
        self.openSButton.setChecked(1)
        hLayout.addWidget(self.openSButton)
        
        self.note = QtWidgets.QLineEdit()
        self.note.setPlaceholderText("--- Nothing to warn you yet! ---")
        self.note.setReadOnly(1)
        self.vLayout.addWidget(self.note)
        
        self.fullQaBtn = QtWidgets.QPushButton("Full Rig Cleanup and Export")
        self.fullQaBtn.setFlat(True)
        self.fullQaBtn.clicked.connect(self.fullQa)
        self.vLayout.addWidget(self.fullQaBtn)
        
        self.faceQaBtn = QtWidgets.QPushButton("Facial Cleanup and Export")
        self.faceQaBtn.setFlat(True)
        self.faceQaBtn.setChecked(True)
        self.faceQaBtn.clicked.connect(partial(self.fullQa, option="face"))
        self.vLayout.addWidget(self.faceQaBtn)
		miscTool = QtWidgets.QWidget()
		mToolLayout = QtWidgets.QGridLayout(miscTool)
		self.Btn1 = QtWidgets.QPushButton("Toggle AnimMode")
		self.Btn1.setCheckable(True)
		self.Btn1.clicked.connect(partial (self.callFunc, funcName = "toggleAnimode"))
		self.Btn2 = QtWidgets.QPushButton("Toggle view")
		self.Btn2.setCheckable(True)
		self.Btn2.clicked.connect(partial (self.callFunc, funcName = "toggleView"))
		Btn3 = QtWidgets.QPushButton("Clear keys")
		Btn3.clicked.connect(partial (self.callFunc, funcName = "setCtrlZero"))
		Btn4 = QtWidgets.QPushButton("Close All Panel")
		Btn4.clicked.connect(partial (self.callFunc, funcName = "killAllWindow"))
#--
		self.creDir = QtWidgets.QLineEdit()
		self.creDir.setPlaceholderText("Paste directory you want to create here")
		mToolLayout.addWidget(self.creDir,2,0)

		creBtn = QtWidgets.QPushButton("Create dir")
		creBtn.clicked.connect(self.creUserDir)
		mToolLayout.addWidget(creBtn , 2 , 1 )	
#--		
		mToolLayout.addWidget(self.Btn1,0,0)
		mToolLayout.addWidget(self.Btn2,0,1)
		mToolLayout.addWidget(Btn3,1,0)
		mToolLayout.addWidget(Btn4,1,1)
		
		
		checkFacialFile  = self.checkfacial()
		stepByStep = QtWidgets.QWidget()
		stepByStepLayout = QtWidgets.QGridLayout(stepByStep)
		numRow = len(self.ALL_CMDS)/3
		count = 0
		outList = []
		for x in range (0,numRow):    
			for x in range (0,3):
				a =  str(count) + " " + str(x)
				outList.append(a)        
				if x == 2:
					count += 1

		for x in range(0,len(self.ALL_CMDS)):
			testBtn = QtWidgets.QPushButton(str(x) +"."+ self.ALL_CMDS[x])
			testBtn.clicked.connect(partial (self.callFunc, funcName = self.ALL_CMDS[x]))
			stepByStepLayout.addWidget(testBtn , int(outList[x][0]),int(outList[x][2]) )
			

		self.tabWidget = QtWidgets.QTabWidget()
		self.tabWidget.addTab(miscTool, "Misc Tools")
		self.tabWidget.addTab(stepByStep, "Clean up funcs")
		if checkFacialFile:
			self.tabWidget.setTabEnabled(1,1)
		else:
			self.tabWidget.setTabEnabled(1,0)
		self.vLayout.addWidget(self.tabWidget)

	def selBtnClicked(self):
		sel = ls(sl = True)
		if len(sel):
			self.charTopnode.setText(str(sel[0]))
			self.tabWidget.setTabEnabled(1,1)
			self.fullQaBtn.setFlat(False)
			self.topNode = self.charTopnode.text()		
			self.autoDir()
			self.checkAbcGeo()
		else:
			print ("I can't do it!")
		
	def fullQa(self, option = "body"): # body or face for option parameter
		if option == "body":
			condition = self.fullQaBtn.isFlat()
		else:
			condition = self.faceQaBtn.isFlat()
			
		if not condition and self.checkDeformer():

			cnt=len(self.ALL_CMDS) 
			for e in range(cnt):
				progressWindow(status="Running, running, running...", isInterruptable=True, minValue=0, maxValue=cnt, title="QA Tool Python v01")
				progressWindow(edit=1, progress=e, status=self.ALL_CMDS[e])
				cmd = self.ALL_CMDS[e]
				print "Step " + str(e) + "-"*5 + cmd + "-"*5 + "\n"
				
				try:
					cmds_list =  cmd.split()
					if len(cmds_list) == 1:
						eval("self."+cmd+"()")
					else:
						eval ("self."+cmds_list[0]+"({})".format(cmds_list[1]))
					
				except:
					print (cmd+" can not be executed")
					progressWindow(endProgress=1)
					break
				
				if progressWindow(query=1, isCancelled=1):
					break
 
				self.openS()
				
			progressWindow(edit=1, progress=cnt, status="MY JOB IS DONE!")
			progressWindow(endProgress=1)

		else:
			print "Stop QA process."
			
	def checkfacial(self): 	
		sceneName = cmds.file(q=1, loc=1, shn=1)
		if "facial"in sceneName.lower() :
			self.autoDir()
			self.faceQaBtn.setFlat(False)
			self.selectBtn.setFlat(True)
			self.ALL_CMDS = ["doOWrite", "setCtrlZero", "importRef abc=False", "deleteNg", "deleteDelLayer", "deleteAllLayer", "ctrlShapeAttrCheck", "checkHideJnt", "optimizeScn", "deleteAllNamespace", "smoothDiv", "convertMatrixNlock", "optiUnitNode", "removeUnknowPlugin", "autoExp expAll=True"]
			return 1
		else:
			self.ALL_CMDS = ["doOWrite", "setCtrlZero", "importRef", "deleteNg", "deleteDelLayer", "deleteAllLayer", "deleteDagNode", "turnAnimmode", "cleanCb", "ctrlShapeAttrCheck", "checkHideJnt", "optimizeScn", "deleteAllNamespace", "smoothDiv", "convertMatrixNlock", "optiUnitNode", "removeUnknowPlugin", "autoExp"]
			return 0
		
	def callFunc(self, funcName):
		cmds_list =  funcName.split()
		if len(cmds_list) == 1:
			eval("self."+funcName+"()")
		else:
			eval ("self."+cmds_list[0]+"({})".format(cmds_list[1]))	
					
	def creUserDir(self):
		dir = self.creDir.text()
		if "\\" in dir:
			dir.replace("\\", "/")
			os.makedirs(dir)
			print "Okay bye!"
		else:
			print "WTH , the directory you want isn't correct"
#--------------------------------
	def autoDir(self): #done
		if self.maCheckBox.isChecked():
			typExp=".ma"
		else:
			typExp = ".mb"
		sceneName= cmds.file(q=1, loc=1, shn=1)
		self.longSceneName = cmds.file(q=1, loc=1)
		if "wip" in self.longSceneName :
			self.longSceneName = self.longSceneName.replace("wip","submit")

		cutScene= re.search(r"^.*/", self.longSceneName)
		if not cutScene:
			raise RuntimeError(" File nay chua duoc luu!!!")
			return
		curVer= re.search(r"[0-9]+", sceneName)
		nameChar= re.search(r"^[^\.]*", sceneName)
		if not curVer:
			curVer = 000
		else:
			curVer = curVer.group()
			
		if not os.path.exists(self.longSceneName):	
			if not os.path.exists(cutScene.group()):
				os.makedirs(cutScene.group())	
			final = self.longSceneName
		else:
			confirm = confirmDialog(title="QA Tool Python v01", cancelButton="Ignore", defaultButton="Overwrite", button=["Overwrite", "Up version", "Eh!"], message="This file already exist! \n", dismissString="Ignore")
			if confirm == "Overwrite":
				self.note.setText("File existed! Overwrite")
				final = self.longSceneName
			elif confirm == "Up version":
				self.note.setText("File existed! Auto up number from %03d to %03d" %(int(curVer), int(curVer) + 1))
				final = (cutScene.group() + nameChar.group() + ".v%03d"   + typExp) %(int(curVer) +1)

			else: 
				self.note.setText("File existed! Save as auto backup!")
				final = (cutScene.group() + nameChar.group() + ".v%03d_QAauto"   + typExp) %(int(curVer))
		
		self.expDir.setText(final)
	
	def doOWrite(self): #done
	
		if "Overwrite" in self.note.text():
			try:
				os.remove(self.expDir.text())
			except:
				pass
		

	def importRef(self, abc = True): #done -- it will keep abc if == True
		self.dieu_kien_loop = 1
		countRefAbc = 0
		for x in range(0,self.numListRef):
			refName=self.listRef[x]
			try:
				dirName = referenceQuery(refName, f=1)
				if dirName:
					filepart= dirName.split("/")[-1]
					if abc :  
						if "abc" not in filepart:
							try:
								cmds.file(filepart, ir = True)
							except:
								pass	
						elif "abc" in filepart:
							# self.dieu_kien_loop = 0
							# break
							countRefAbc += 1
					else:
						try:
							cmds.file(filepart, ir = True)
						except:
							pass
			except:
				self.numListRef -= 1
				pass

		if countRefAbc == self.numListRef:
			self.dieu_kien_loop = 0

		# self.listRef = ls(references = True)
		# self.numListRef = len(self.listRef)
		while self.dieu_kien_loop != 0 :
			if  self.numListRef == 0:
				break
			self.importRef(abc)
			
	def mainAbc(self,ref): #done
		
		ripOff = self.takeNS(self.topNode)
		fullDir=referenceQuery(ref, filename=1)
		naa=referenceQuery(fullDir, ns=1)
		if naa != ":":
			if ripOff == naa or ripOff in naa:
				return 1
			else:
				return 0
		else:
			return 1

	def takeNS(self,nameSpace): #done 
		if not self.topNode:
			return
		nS= re.sub(r"[^:]*$","",nameSpace )
		if len(nS):
			nS= nS[0:(len(nS) - 1)]
			nS=(":" + nS)
			return nS
		else:
			noName=re.search(r"^[^\_]*", nameSpace)
			return noName.group()
			

# copy --------------------------------------

	def setFilterScript(self,name): #done

		# We first test for plug-in object sets.
		try:
			apiNodeType = nodeType(name, api=True)
		except RuntimeError:
			return False
			
		if apiNodeType == "kPluginObjectSet":
			return True
		  
		  # We do not need to test is the object is a set, since that test
		# has already been done by the outliner
		try:
			nodeTypeName = nodeType(name)
		except RuntimeError:
			return False
		 
		# We do not want any rendering sets
		if nodeTypeName == "shadingEngine":
			return False
			
		# if the object is not a set, return false
		if not (nodeTypeName == "objectSet" or
				nodeTypeName == "textureBakeSet" or
				nodeTypeName == "vertexBakeSet" or
				nodeTypeName == "character"):
			return False
		
		# We also do not want any sets with restrictions
		restrictionAttrs = ["verticesOnlySet", "edgesOnlySet", "facetsOnlySet", "editPointsOnlySet", "renderableOnlySet"]
		if any(getAttr("{0}.{1}".format(name, attr)) for attr in restrictionAttrs):
			return False
			
		# Do not show layers
		if getAttr("{0}.isLayer".format(name)):
			return False
		
		# Do not show bookmarks
		annotation = getAttr("{0}.annotation".format(name))
		if annotation == "bookmarkAnimCurves":
			return False
			
		# Whew ... we can finally show it
		return True
			

	def getOutlinerSets(self):
		return [name for name in ls(sets=True) if setFilterScript(name)]

# copy ------------------------------------------

	def deleteAllNamespace(self): #done
		listName=namespaceInfo(lon=1)
		listName.remove("UI")
		listName.remove("shared")
		num = len(listName)
		for i in range(0,num):
			child=namespaceInfo(listName[i], lon=1)
			try:
				namespace(mergeNamespaceWithParent=1, removeNamespace=listName[i])
			except:
				pass
			if child:
				for c in child:
					c = c.replace((listName[i] + ":"),"")
					listName[num]= c[0]
					num += 1

	def deleteNg(self): #done
		
		try:
			LayerUtils.deleteCustomNodes()
		except:
			pass
		flushUndo()
		try:
			unloadPlugin('ngSkinTools')
		except:
			pass
			
	def deleteDelLayer(self): #done
		listAllLayer= ls(type='displayLayer')
		for x in listAllLayer:
			if "delete" in x.lower():
				listObjinLayer = editDisplayLayerMembers(x, q=1)
				if listObjinLayer:
					for x in listObjinLayer:
						try:
							delete(x)
						except:
							pass
							
	def deleteAllLayer(self): #done
		listAllLayer= ls(type='displayLayer')
		listAllLayer.remove("defaultLayer")
		for x in listAllLayer:
			try:
				delete(x)
			except:
				pass

	def deleteDagNode(self): #done
		self.deleteDagOln()
		dntHideFaceSet = ls("*ShapeDeformedHiddenFacesSet", "*ShapeHiddenFacesSet", "*defaultHideFaceDataSet")
		delSet = ls(sets=1)
		if dntHideFaceSet: 
			delSet = list(set(delSet).difference(set(dntHideFaceSet)))
		for x in delSet:
			if self.setFilterScript(x):
				try:
					catch(delete(str(x)))
				except:
					pass
																		
	def deleteDagOln(self): #done
		listOln = ls(assemblies=1)
		for x in listOln:
			if  str(x) not in self.topNode:
				try:
					delete(x)
				except:
					pass
				
	def optimizeScn(self): #done
		mel.eval("cleanUpScene 3")

	def turnAnimmode(self): #done
		try:
			setAttr((self.rigGrpName + ".animMode"), 1)
		except:
			pass
		if not self.makeAnimModeN():
			print "Create AnimMode FAIL! \n"
			confirmDialog(message=("Create AnimMode FAIL!      \n"), button="Okay", defaultButton="Okay", title="QA Tool Python v01")
			return 1
		return 0
		
	def smoothDiv(self): #done
		displaySmoothness(self.topNode, pointsWire=4, polygonObject=1, pointsShaded=1, divisionsV=0, divisionsU=0)	
		

	def autoExp(self, expAll = False): #done
		if self.mbCheckBox.isChecked():
			typExp = "mayaBinary"
		else:
			typExp = "mayaAscii"
			
		select(self.topNode)
		queryDir= self.expDir.text()
		cutScene= re.search(r"^.*/", queryDir).group()
		if not os.path.exists(cutScene):
			os.mkdir(cutScene)
		if not expAll:
			cmds.file(queryDir, pr=1, typ=typExp, es=1, op="v=0")
		else:
			cmds.file(queryDir, pr=1, ea=1, typ = typExp, op="v=0")	

	def getParentHier(self, node, result): #done
		
		parents = listRelatives(node, ap=1) or []
		for p in parents:
			result.append(p)
			self.getParentHier(p, result)
		return result
		
	def nodeIsVisible(self,node): #done
	
		if not objExists(node):
			return False
			
		if not attributeQuery("visibility", node=node, exists=1):
			return False
			
		visible = getAttr(node + ".visibility")
		if attributeQuery("intermediateObject", node=node, exists=1):
			visible=visible
			visible and not getAttr(node + ".intermediateObject")
			
		if attributeQuery("overrideEnabled", node=node, exists=1) and getAttr(node + ".overrideEnabled"):
			visible=visible
			visible and getAttr(node + ".overrideVisibility")
			
		if visible:
			allParent = []
			self.getParentHier(node, allParent)
			if allParent:
				visible=visible
				visible and self.nodeIsVisible(allParent[0])
		return visible
		
	def rigGrp(self): #done
		lsAllRig = ls("rig_grp", "*:rig_grp", "Rig_grp", "*:Rig_grp", typ="transform")
		if not lsAllRig:
			lsRigGrp = None
			return
		
		lsRigGrp = lsAllRig[-1]
		if "Rig" not in lsRigGrp:
			lsRigGrp= rename(lsRigGrp, "Rig_grp")
		else:
			pass		
		self.rigGrpName = lsRigGrp	
		self.listAttrObj = listAttr(lsRigGrp, ud = True) or []

	def makeAnimModeN(self): #done
		self.rigGrp()
		if "animMode" in self.listAttrObj :
			self.deleteAnim()
		else:
			pass
		
		if not self.rigGrpName:
			confirmDialog(message="Doesn't have rig_grp node yet. Please create one!", 
				button="Yes", defaultButton="Yes", 
				title="QA Tool Python v01")
			return 0
			
		else:
			select(self.rigGrpName)
			mel.eval("catchQuiet (`addAttr -ln \"animMode\" -keyable true  -at long  -min 0 -max 1 -dv 1 "+ self.rigGrpName + "`)")
			mel.eval("catchQuiet (`shadingNode -n \"rig_animMode_rev\" -asUtility reverse`)")
			mel.eval("catchQuiet (`connectAttr " + self.rigGrpName +".animMode \"rig_animMode_rev.inputX\"`)")
			
			cleanedJnts = ls("zeroJntComeBack", type="joint")
			cleanedJnts += ["rig_C_torso_chest_jnt"][:1]
			
			#deal with jnt
			jnts=ls(type="joint")
			jnts = list(set(jnts).difference(set(cleanedJnts)))
			for x in jnts:
				if "ctrl" in x:
					mel.eval("catchQuiet (`setAttr " + x + ".drawStyle  2`)")
				
				test=listRelatives(x, ad=1)
				if test:
					for i in test:
						if "ctrl" in i:
							mel.eval("catchQuiet (`setAttr  "+ x + ".drawStyle 2`)")
				if getAttr( x + ".drawStyle") != 2:
					mel.eval("catchQuiet(`connectAttr " + self.rigGrpName + ".animMode " + x + ".template`)")

			#deal with locator
			locs = ls(type="locator")
			for loc in locs:
				mel.eval("catchQuiet (`connectAttr \"rig_animMode_rev.outputX\" " + loc + ".v`)")
			
			#deal with mesh	
			
			self.dealM()
			
			# deal with nurb surface
			nurbGeo = ls("*:*_geoShape", "*_geoShape", type="nurbsSurface")
			for obj in nurbGeo:
				obj = obj.replace("Shape","")
				if self.nodeIsVisible(obj):
					mel.eval("catchQuiet (`setAttr " + obj + ".overrideDisplayType 2`)")
					mel.eval("catchQuiet (`connectAttr "+ self.rigGrpName +".animMode " + obj + ".overrideEnabled`)")
					
			nurb = ls(type="nurbsSurface")
			for x in nurb:
				if not "_geoShape" in x:
					subNurb=x.replace("Shape","")
					mel.eval("catchQuiet (`setAttr " + subNurb + ".v 0`)")
			# deal with follicle
			fol = ls(type="follicle")
			for x in fol:
				mel.eval("catchQuiet (` setAttr " + x + ".v 0`)")
				
			# deal with ikHandle
			ikHandle=ls(type="ikHandle")
			for x in ikHandle:
				mel.eval("catchQuiet (` setAttr "+ x + ".v 0`)")

			return 1
	
	def toggleAnimode(self): #done
		self.rigGrp()
		if "animMode" in self.listAttrObj:
			setAttr((self.rigGrpName + ".animMode"), self.Btn1.isChecked())
		else:
			raise ValueError("Chua tao Anim Mode hoac khong co rig_grp!")

	def deleteAnim(self): #done
		
		setAttr((self.rigGrpName + ".animMode"), 0)
		deleteAttr(self.rigGrpName + ".animMode")
		delete('rig_animMode_rev')
			
	def setCtrlZero(self): #done
		clearKey = ls("*_ctrl", "*:*_ctrl", "*_Ctrl", "*:*_Ctrl")

		for x in clearKey:
			shape = listRelatives(x, s=1)
			intersect = []
			if shape:
				mel.eval("catchQuiet (`cutKey " + x + "`)")
				userDef=listAttr(x, ud=1)
				if userDef and self.attr(x): intersect = list(set(self.attr(x)).intersection(set(userDef)))
				if intersect:	
					for i in range(0,len(intersect)):
						mel.eval("catchQuiet (`cutKey " + x + "." + intersect[i] + " `)")
						getDef = addAttr((x + "." + intersect[i]), q=1, dv=1)
						mel.eval("catchQuiet (`setAttr " + x + "." + intersect[i] + " " + str(getDef) + "`)")
				
				mel.eval("catchQuiet (`setAttr " + x + ".scaleX  1 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".scaleY  1 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".scaleZ  1 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".visibility  1 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".translateX  0 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".translateY  0 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".translateZ  0 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".rotateX  0 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".rotateY  0 `)")
				mel.eval("catchQuiet (`setAttr " + x + ".rotateZ  0 `)")
				
				if objExists("rig_*_upArm_A_pos_loc") or objExists("*:rig_*_upArm_A_pos_loc"):
					upArmCtrl = ls("rig_*_arm_upArm_fk_ctrl", "*:rig_*_arm_upArm_fk_ctrl")
					upArmLoc = ls("rig_*_upArm_A_pos_loc", "*:rig_*_upArm_A_pos_loc")
					for i in range(0,len(upArmLoc)):
						select(upArmCtrl[i], upArmLoc[i])
						cmds.MatchRotation()
		try:
			mel.eval("source \"V:/libraries/Scripts/LumiPicker/_script/IkFkSwitch.mel\"")
		except:
			pass
		
		mel.eval("catchQuiet(`kinematicSwitch \"\" \"L\" \"arm\"`)")
		mel.eval("catchQuiet(`kinematicSwitch \"\" \"R\" \"arm\"`)")
		armSwitchCtrl = ls("rig_*_arm_switch_ctrl", "*:rig_*_arm_switch_ctrl")
		
		if armSwitchCtrl:
			for x in armSwitchCtrl:
				mel.eval("catchQuiet (`setAttr " + x + ".ikEnable 0`)")
		
		select(cl = True)
					
	def checkHideJnt(self): #done
		listVi=ls(type="joint", v=1)
		cleanedJnts=ls("*_ctrlEnv", type="joint")
		listVi=[x for x in listVi if x not in cleanedJnts]
		for i in listVi:
			if getAttr(i + ".template"):
				testRe= listRelatives(i, s=1)
				if not testRe:
					mel.eval("catchQuiet (`setAttr " + i + ".drawStyle 2`)")

	def toggleView(self):	#done	
		activePanel = cmds.getPanel(wf=1)
		if "scriptEditor" in activePanel:
			return
		if 	self.Btn2.isChecked():
			cmds.modelEditor(activePanel, cameras=False, j=False, e=1, nurbsCurves=False, lc=False)
		else:
			cmds.modelEditor(activePanel, allObjects=1, e=1) 
	
	def openS(self): #done
		if self.openSButton.isChecked() and os.path.exists(self.expDir.text()):
			cmds.file((self.expDir.text()), open=1, f=1)
		
	def dealM(self): #done
		mesh=ls(type="mesh")
		for obj in mesh:
			getPare = listRelatives(obj, p=1)[0]
			hhs= getAttr(obj + ".visibility")
			if ls(getPare + ".visibility"):
				hh = getAttr(getPare + ".visibility")
				if hh and hh == hhs:
					mel.eval ("catchQuiet (`connectAttr " + self.rigGrpName +".animMode " + obj +".overrideEnabled`)")
					mel.eval ("catchQuiet (`setAttr "+ obj +".overrideDisplayType 2`)")
					
	def removeUnknowPlugin(self): #done
		lsPlugin = unknownPlugin(q=1, l=1) or []
		for x in lsPlugin:
			unknownPlugin(x, r=1)

	def killAllWindow(self ): #done
		lsP = getPanel(vis=1)
		for each in lsP:
			getTypP = getPanel(to=each)
			win = (getTypP + " -q -ctl " + each)
			execute= mel.eval(win)
			try:
				tokens = execute.split("|")[0]
				print "day la token", tokens
				if "MainPane" not in tokens and "Outliner" not in tokens and "scriptEditorPanel" not in tokens:
					deleteUI(tokens)
			except:
				pass
				
	def ctrlShapeAttrCheck(self):  #done
		clearKey = ls("*_ctrl", "*:*_ctrl","*_Ctrl") or []
		for x in clearKey:
			shape = listRelatives(x, s=1)
			for i in shape:
				if len(ls(i)) == 1:
					if self.attr(i):
						for n in range(0,len(self.attr(i))):
							mel.eval("catchQuiet(`setAttr -lock true "+ i + "." + self.attr(i)[n] + "`)")
				else:
					list= ls(i)
					for m in range(0,len(ls(i))):
						if self.attr(list[m]):
							for n in range(0,len(self.attr(list[m]))):
								mel.eval("catchQuiet(`setAttr -lock true "+ i + "." + self.attr(list[m])[n] + "`)")

	def attr(self,input): #done
		attrInCb = listAttr(input, cb=True) or []
		attrKeyable = listAttr(input, k=True) or []
		attrLock = listAttr(input, l = True) or []
		attr = attrInCb + attrKeyable
		attr = list(set(attr).difference(set(attrLock)))		
		if not len(attr):
			attr = None
		return attr
		
	def lockAbc(self,num): #ko dung chuc nang nay
		lsRef=ls(rf=1)
		if lsRef:
			for x in lsRef:
				if self.mainAbc(x):
					print "innnnn"
					mel.eval("catchQuiet (`file -unloadReference " + x + "`)")
					mel.eval("catchQuiet (`setAttr "+ x +".locked " + str(num) + "`)")
					mel.eval("catchQuiet (`file -loadReference " + x + "`)")
					print "done"
				
	def toggleLimit(self): #ko dung chuc nang nay
		if self.topNode:
			if button('lmGeo', q=1, l=1) == "Lock Abc":
				self.lockAbc(1)
				button('lmGeo', e=1, l="Unlock Abc")
			else:
				self.lockAbc(0)
				button('lmGeo', e=1, l="Lock Abc")
	
	def checkDeformer(self): #done
			allList =ls(dag=1)
			#check tat ca cac deformer trong scene, xem co deform rac nao khong
			errorList = []
			for t in range(0,len(allList)):
				his=listHistory(allList [t], pruneDagObjects=True, interestLevel=1)
				if his:
					for each in his:
						types=nodeType(each, inherited=1)
						if types[0] == "geometryFilter" and not getAttr(each + ".envelope") and  not self.checkConnection(each) and not self.checkBsConnection(each):
							errorList.append(str(each))
			
			erShortList= list(set(errorList))
			if len(erShortList):
				printError="\n".join(erShortList)
				popup = confirmDialog(message=("Found: %s errors \n\n" + "This nodes has .envelope = 0 and has no in/out connection : \n \n" + printError) %len(erShortList), button=["Stop QA process", "Ignore_Con", "Set 1_Con", "Delete_Con"], defaultButton="Ignore_Con", title="QA Tool Python v01")
				if popup == "Set 1_Con":
					for l in erShortList:
						setAttr((l + ".envelope"), 1)
					return 0
				if popup == "Stop QA process":
					return 0
				if popup == "Delete_Con":
					for l in erShortList:
						delete(l)
					return 1					
				else:
					return 1					
			return 1
			
	def checkConnection(self, attr): #done
		array = self.attr(attr)
		connect = 0
		for each in array:
			try:
				checkD = connectionInfo((attr + "." + each), isDestination=1)
				checkS = connectionInfo((attr + "." + each), isSource=1)
			except:
				continue
			if checkD or checkS:
				connect =  1
		if connect:
			return 1
		return 0

	def checkBsConnection(self, each): #done
		listBs = aliasAttr(each, q=1)
		if listBs:
			for r in listBs:
				if "weight" in r:
					checkD = connectionInfo((each + "." + r), isDestination=1)
					checkS = connectionInfo((each + "." + r), isSource=1)
					if checkD or checkS:
						return 1
						
		return 0


	def cleanCb(self): 
		clearKey = ls("*_ctrl", "*:*_ctrl", "*_Ctrl", "*:*_Ctrl")
		for x in clearKey:
			self.ihi(x)
		listDep= ls(dep=True)
		objIih=["polySmoothFace", "reference", "reverse", "remapValue", "blendShape", "skinCluster", "shapeEditorManager", "multDoubleLinear", "nonLinear", "createColorSet", "ffd", "tweak", "polyTweakUV", "nurbsTessellate", "ngSkinLayerData", "cluster", "wrap", "lambert", "deleteComponent", "deltaMush", "plusMinusAverage", "wire", "multiplyDivide", "clamp", "condition", "nodeGraphEditorInfo", "blendColors", "dagPose", "setRange", "parentConstraint", "pointConstraint", "scaleConstraint", "orientConstraint", "aimConstraint", "blendTwoAttr"]
		for x in listDep:
			type= objectType(x)
			if type in objIih:
				mel.eval("catchQuiet (`connectAttr rig_animMode_rev.outputX " + x + ".ihi`)")
				
		mel.eval("catchQuiet (`outlinerEditor -e -showDagOnly true outlinerPanel1`)")

	
	def ihi(self,ctrl): #du kie
		listH = listHistory(ctrl)
		for y in listH:
			mel.eval("catchQuiet(`connectAttr rig_animMode_rev.outputX "+ y + ".ihi`)")
		
	def loadPluginQA(self): 
		loadPlugin=["weightDriver", "poseReader", "cvwrap"]
		eList = []
		for x in loadPlugin:
			check= mel.eval("catchQuiet (`loadPlugin "+ x +"`)")
			if check != 0:
				eList.append(x)
			if eList:
				printError = "\n".join(eList)
				confirmDialog(title="QA Tool Python v01", cancelButton="No", defaultButton="Yes", button=["Yes", "No"], message=("List of unload plug-in:\n" + printError), dismissString="No")
		
	def optiUnitNode(self): 
		transNode= ls(typ="transform")
		for each in transNode:
			self.checkSourceNOpti(each)

	
	def checkSourceNOpti(self, input):	
		rX = []
		rY = []
		rZ = []
		R = []
		if connectionInfo((input + ".r"), isSource=1):
			RR = connectionInfo((input + ".r"), destinationFromSource=1)
			sizeR=len(RR)
			for x in range(0,sizeR):
				if self.checkUnitNode(RR[x]) != 0:
					R += [RR[x]][:1]
			if len(R) > 1:
				self.connectUnit (input,"rotate",R);
			
		if connectionInfo((input + ".rx"), isSource=1):
			RrX=connectionInfo((input + ".rx"), destinationFromSource=1)
			RrX=[x for x in RrX if x not in R]
			sizeRx=len(RrX)
			for x in range(0,sizeRx):
				if self.checkUnitNode(RrX[x]) != 0:
					rX += [RrX[x]][:1]

				
			if len(rX) >1:
				self.connectUnit (input,"rx",rX)
				
			
		if connectionInfo((input + ".ry"), isSource=1):
			RrY=connectionInfo((input + ".ry"), destinationFromSource=1)
			RrY=[x for x in RrY if x not in R]
			sizeRy=len(RrY)
			for x in range(0,sizeRy):
				if self.checkUnitNode(RrY[x]) != 0:
					rY += [RrY[x]][:1]

			if len(rY) >1:
				self.connectUnit (input,"ry",rY)
			
		if connectionInfo((input + ".rz"), isSource=1):
			RrZ=connectionInfo((input + ".rz"), destinationFromSource=1)
			RrZ=[x for x in RrZ if x not in R]
			sizeRz=len(RrZ)
			for x in range(0,sizeRz):
				if self.checkUnitNode(RrZ[x]) != 0:
					rZ += [RrZ[x]][:1]

			if len(rZ) >1:
				self.connectUnit (input,"rz",rZ)
				
	def checkUnitNode(self, input): 
		
		cutName=re.search(r"[^\\.]*", input)
		if objectType(cutName.group()) == "unitConversion":
			return 1
			
		return 0

	def connectUnit(self,input, attr, output): 
		inputName = input + "." + attr
		outputOfUnit = []
		if len(output)>1:
			for x in output:
				cutName=re.search(r"[^\\.]*", x)
				out=connectionInfo((cutName.group() + ".output"), destinationFromSource=1)
				if not len(out):
					mel.eval(" catchQuiet(`delete " + cutName.group()+"`)")
								
				else:
					outputOfUnit += out[:len(out)]
					for e in out:
						mel.eval("catchQuiet(`disconnectAttr "+ cutName.group() + ".output " + e + "`)")

			winner=re.search(r"[^\\.]*", output[0])
			# da loc va disconnect xong output. Gio se xoa cac node unit thua va noi sang output moi
			winner =rename(winner.group(), (input + "_" + winner.group() + "_optiNode"))
			for z in range(1,len(output)):
				cutName=re.search(r"[^\\.]*", output[z])
				delete(cutName.group())
				
			for i in outputOfUnit:
				mel.eval("catchQuiet(`connectAttr -f "+ winner + ".output "+i +"`)")
				


	def convertMatrixNlock(self): 
		nFeatureNode = ls("*:*rig_C_torso_up_crv", "rig_C_torso_up_crv")
		if len(nFeatureNode) == 1:
			sMtx="source \"V:/libraries/Scripts/ConstraintToMatrix.mel\""
			#
			eval(sMtx)
			sel=ls()
			pass_ = []
			camera=ls(type='camera')
			for c in camera:
				p=listRelatives(c, p=1)
				pass_.append(c)
				pass_.append(p[0])
				
			ikh=ls(type='ikHandle')
			ikj = []
			for ik in ikh:
				jl=ikHandle(ik, q=1, jl=1)
				ikj += jl[:len(jl)]
				
			shape=ls(type='shape')
			sets=ls(type='objectSet')
			pass_ += camera[:len(camera)]
			pass_ += shape[:len(shape)]
			pass_ += sets[:len(sets)]
			for o in sel:
				if not o in pass_ and not "ctrl" in o:
					a1=listAttr(o, ud=1, k=1)
					a2=listAttr(o, ud=1, cb=1)
					a3=listAttr(o, k=1, v=1)
					attr = []
					attr += a1[:len(a1)]
					attr += a2[:len(a2)]
					attr += a3[:len(a3)]
					if nodeType(o) == "joint":
						attr.append("radius")
					for a in attr:
						if not (o in ikj and "rotate" in a):
							mel.eval("catch(`setAttr -l "+ o + "." + a +"`)")	
							
							

	def findAbc(self):
		for x in range(self.numListRef):
			try:
				dirName = referenceQuery(self.listRef[x], f=1)
				if "abc" in str(dirName).split("/")[-1]:
					return dirName
				else:
					return None
			except:
				continue
		return None
		
	def checkAbcGeo(self):
		abc = self.findAbc()
		errors = []
		if abc:
			listC = referenceQuery(abc, n = 1, dp = 1)
			finList = [PyNode(x) for x in listC if objectType(x) == "transform"]
			for x in finList:
				tran = x.getTranslation()
				rot = x.getRotation()
				scale = x.getScale()
				end = tran + rot + scale
				if end[0] != 1.0 or end[1] != 1.0 or end[2] != 1.0:
					errors.append(str(x))
			if len(errors):
				found =  ("Found: " + str(len(errors)) + " errors./ \n")
				print found, errors
				popup = confirmDialog(title = "QA Tool Python v01", message = ( found + "Hey mannnnnn! Model is not clean!"), button = ["Okay","View error list","Ignore"], defaultButton = "Okay" ) 
				if popup == "Okay":
					return 0
				elif popup == "View error list":
					confirmDialog(title = "QA Tool Python v01", message = ("Error list: \n \n " + str(errors)), button = "Okay", defaultButton = "Okay")				
					return 0
				else:
					return 1

			return 1
