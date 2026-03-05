"""QA Tool Core Module

Author: Thai Ha Trieu (Hannah Trieu)
Studio: Vintata Animation Studio
Role: Rigger

Provides core functionality for character and prop rig validation and cleanup
before exporting to the animation department.
"""

from maya import cmds as mc
import maya.mel as mel
import re
import pymel.core as pm
import shutil
import os
import os.path


class InputInfo(object):
    """Base class for managing rig input information.
    
    Retrieves scene references and selected character nodes from Maya UI.
    """
    
    def __init__(self):
        """Initialize input information from Maya scene."""
        if mc.textScrollList('charTopnode', q=True, selectUniqueTagItem=1):
            # List all references in the scene
            self.listRef = mc.ls(references=1)
            # Count references in the scene
            self.numListRef = len(self.listRef)
            # Top node is the group to export at the end of QA process
            self.topNode = mc.textScrollList('charTopnode', q=True, selectUniqueTagItem=1)
            print("Got the info")
        else:
            print("Nothing selected yet!")
	
class QAtool(InputInfo):
    """Main QA Tool class for rig validation and cleanup.
    
    Handles importing references, managing file exports, and executing
    various rig cleanup operations.
    """
    
    def __init__(self, *args):
        """Initialize QA Tool with parent class."""
        super(QAtool, self).__init__()

    def importAll(self):
        """Import all references in the scene."""
        nested = self.nestedAbc()
        for x in range(0, self.numListRef):
            refName = self.listRef[x]
            try:
                mc.referenceQuery(refName, f=1)
            except RuntimeError:
                dirName = mc.referenceQuery(refName, f=1)
                filepart = re.search(r"[^/\\]*$", dirName)
                try:
                    condition = mc.file(filepart, ir=1)
                    if condition:
                        self.listRef[self.numListRef] = self.listRef[x]
                        self.numListRef += 1
                except RuntimeError:
                    pass
        if nested:
            for x in nested:
                try:
                    mc.file(x, ir=1)
                except RuntimeError:
                    pass
    def doOWrite(self):
        """Handle file overwrite operations for export.
        
        Creates backup or removes existing file based on radio button selection.
        """
        name = mc.textField('expDir', q=1, fi=1)
        typExp = ""
        if mc.radioButton('chkMB', q=1, sl=1):
            typExp = ".mb"
        else:
            typExp = ".ma"
        ripOff = name[0:(len(name) - 3)]
        if mc.radioButton('rNE', q=1, sl=1):
            os.rename(name, (ripOff + ".backup" + typExp))
        if mc.radioButton('oW', q=1, sl=1):
            os.remove(name)
	    def importFacialRef(self):
        """Import facial rig references excluding ABC files."""
        if self.check_text_selection():
            for x in range(0, self.numListRef):
                refName = self.listRef[x]
                try:
                    con = mc.referenceQuery(refName, f=1)
                    if con:
                        dirName = mc.referenceQuery(refName, f=1)
                        filepart = re.search(r"[^/\\]*$", dirName)
                        filepart = filepart.group()
                        if "abc" not in filepart:
                            try:
                                con = mc.file(filepart, ir=True)
                                if con:
                                    self.listRef[self.numListRef] = self.listRef[x]
                                    self.numListRef += 1
                            except RuntimeError:
                                pass
                except RuntimeError:
                    pass
            nested = self.nestedAbc()
            if nested:
                for x in nested:
                    try:
                        mc.file(x, ir=True)
                    except RuntimeError:
                        pass
						

	    def mainAbc(self, ref):
        """Process main ABC reference.
        
        Args:
            ref: Reference node name
            
        Returns:
            int: 1 if namespace matches, 0 otherwise
        """
        sel_list = mc.textScrollList('charTopnode', q=1, selectUniqueTagItem=1)
        namespace_prefix = self.extract_namespace(sel_list[0])
        fullDir = mc.referenceQuery(ref, filename=1)
        namespace = mc.referenceQuery(fullDir, ns=1)
        if namespace != ":":
            if namespace_prefix == namespace or namespace_prefix in namespace:
                return 1
            else:
                return 0
        else:
            return 1

    @staticmethod
    def chop_string(string):
        """Remove last character from string.
        
        Args:
            string: Input string
            
        Returns:
            str: String without last character, or empty if length <= 1
        """
        if len(string) <= 1:
            return ""
        return string[0:len(string) - 1]
    
    def extract_namespace(self, namespace):
        """Extract namespace prefix from node name.
        
        Args:
            namespace: Node name or namespace
            
        Returns:
            str: Namespace prefix or node prefix
        """
        namespace_match = re.sub(r"[^:]*$", "", namespace)
        if len(namespace_match):
            namespace_match = self.chop_string(namespace_match)
            namespace_match = (":" + namespace_match)
            return namespace_match
        else:
            node_match = re.search(r"^[^_]*", namespace)
            return node_match.group()
    
    def nestedAbc(self):
        """Find nested ABC files in the scene.
        
        Returns:
            list: List of nested ABC file paths
        """
        topNodeRef = mc.file(q=1, r=1)
        allUseFile = mc.file(q=1, list=1)
        results = []
        for x in allUseFile:
            if "abc" in x and x not in topNodeRef:
                results.append(x)
        return results
    
    @staticmethod
    def check_text_selection():
        """Check if text is selected in UI element.
        
        Returns:
            bool: True if selection exists, False otherwise
        """
        try:
            return bool(mc.textScrollList('charTopnode', q=True, selectUniqueTagItem=1))
        except RuntimeError:
            return False

# copy --------------------------------------

	def setFilterScript(self,name):

		# We first test for plug-in object sets.
		try:
			apiNodeType = mc.nodeType(name, api=True)
		except RuntimeError:
			return False
			
		if apiNodeType == "kPluginObjectSet":
			return True
		  
		  # We do not need to test is the object is a set, since that test
		# has already been done by the outliner
		try:
			nodeType = mc.nodeType(name)
		except RuntimeError:
			return False
		 
		# We do not want any rendering sets
		if nodeType == "shadingEngine":
			return False
			
		# if the object is not a set, return false
		if not (nodeType == "objectSet" or
				nodeType == "textureBakeSet" or
				nodeType == "vertexBakeSet" or
				nodeType == "character"):
			return False
		
		# We also do not want any sets with restrictions
		restrictionAttrs = ["verticesOnlySet", "edgesOnlySet", "facetsOnlySet", "editPointsOnlySet", "renderableOnlySet"]
		if any(mc.getAttr("{0}.{1}".format(name, attr)) for attr in restrictionAttrs):
			return False
			
		# Do not show layers
		if mc.getAttr("{0}.isLayer".format(name)):
			return False
		
		# Do not show bookmarks
		annotation = mc.getAttr("{0}.annotation".format(name))
		if annotation == "bookmarkAnimCurves":
			return False
			
		# Whew ... we can finally show it
		return True
			

	def getOutlinerSets(self):
		return [name for name in mc.ls(sets=True) if setFilterScript(name)]

# copy ------------------------------------------

    def deleteAllNamespace(self):
		listName=mc.namespaceInfo(lon=1)
		num = len(listName)
		for i in range(0,num):
			if "UI" not in listName[i] and  "shared" not in listName[i]:
				child=mc.namespaceInfo(listName[i], lon=1)
				try:
					mc.namespace(mergeNamespaceWithParent=1, removeNamespace=listName[i])
				except:
					pass
				if child:
					for c in child:
						c = c.replace((listName[i] + ":"),"")
						listName[num]= c[0]
						num += 1

	def deleteNg(self): #done
		from ngSkinTools.layerUtils import LayerUtils
		try:
			LayerUtils.deleteCustomNodes()
		except:
			pass
		mc.flushUndo()
		try:
			mc.unloadPlugin('ngSkinTools')
		except:
			pass
	def deleteDelLayer(self,*args): #done
		listAllLayer= mc.ls(type='displayLayer')
		for x in listAllLayer:
			if "delete" in x:
				listObjinLayer = mc.editDisplayLayerMembers('delete', q=1)
				if listObjinLayer:
					for x in listObjinLayer:
						try:
							mc.delete(x)
						except:
							pass
	def deleteAllLayer(self, *args): #done
		listAllLayer= mc.ls(type='displayLayer')
		listAllLayer.remove("defaultLayer")
		for x in listAllLayer:
			try:
				mc.delete(x)
			except:
				pass

	def deleteDagNode(self): #done
		#delete DAG node
		if checktextSl():
			try:
				self.deleteDagOln()
			except:
				pass
		#delete Set
		dntHideFaceSet = mc.ls("*ShapeDeformedHiddenFacesSet", "*ShapeHiddenFacesSet", "*defaultHideFaceDataSet")
		delSet = mc.ls(sets=1)
		if dntHideFaceSet: 
			delSet = list(set(delSet).difference(set(dntHideFaceSet)))
		for x in delSet:
			if self.setFilterScript(x):
				try:
					mel.eval("catchQuiet(`delete " + x + "`)")
				except:
					pass
										
	def deleteDagOln(self): #done
		listOln = mc.ls(assemblies=1)
		for x in listOln:
			if  x not in self.topNode[0]:
				mel.eval("catchQuiet(`delete " + x + "`)")
	def optimizeScn(self): #done
		mel.eval("catch(`cleanUpScene 3`)")

	def turnAnimmode(self): #done
		try:
			mc.setAttr((self.rigGrp() + ".animMode"), 1)
		except:
			pass
		if not self.makeAnimModeN():
			print "Create AnimMode FAIL! \n"
			mc.confirmDialog(message=("Create AnimMode FAIL!      \n"), button="Okay", defaultButton="Okay", title="QA Tool v.16")
			return 1
		return 0
		
	def smoothDiv(self): #done
		mc.select(self.topNode)
		mc.displaySmoothness(pointsWire=4, polygonObject=1, pointsShaded=1, divisionsV=0, divisionsU=0)
		mc.select(cl = True)
		
	def export(self): #done
		if not self.topNode:
			mc.confirmDialog ( message = "Please select character node!", button = "Yes", defaultButton = "Yes", title = "QA Tool v.16")
		else:
			self.autoExp()
			
	def autoExp(self): #done
		
		typExp = ""
		if mc.radioButton('chkMB', q=1, sl=1):
			typExp = "mayaBinary"
		else:
			typExp = "mayaAscii"
			
		mc.select(self.topNode)
		queryDir= mc.textField('expDir', q=1, fi=1)
		cutScene= re.search(r"^.*/", queryDir)
		cutScene = cutScene.group()
		if os.path.exists(cutScene):
			mc.file(queryDir, pr=1, typ=typExp, es=1, op="v=0")
		else:
			os.mkdir(cutScene)
			mc.file(queryDir, pr=1, typ=typExp, es=1, op="v=0")

	def expAll(self): #done
		typExp = ""
		if mc.radioButton('chkMB', q=1, sl=1):
			typExp="mayaBinary"
		else:
			typExp="mayaAscii"
			
		queryDir= mc.textField('expDir', q=1, fi=1)
		cutScene= re.search(r"^.*/", queryDir)
		cutScene = cutScene.group()
		if os.path.exists(cutScene):
			mc.file(queryDir, pr=1, ea=1, typ = typExp, op="v=0")

		else:
			os.mkdir(cutScene)
			mc.file(queryDir, pr=1, ea=1, typ = typExp, op="v=0")	
	

	def getParentHier(self, node, result): #done
		
		parents = mc.listRelatives(node, ap=1)

		if parents:
			for p in parents:
				result.append(p)
				self.getParentHier(p, result)
		return result
		
	def nodeIsVisible(self,node): #done
	
		if not mc.objExists(node):
			return False
			
		if not mc.attributeQuery("visibility", node=node, exists=1):
			return False
			
		visible = mc.getAttr(node + ".visibility")
		if mc.attributeQuery("intermediateObject", node=node, exists=1):
			visible=visible
			visible and not mc.getAttr(node + ".intermediateObject")
			
		if mc.attributeQuery("overrideEnabled", node=node, exists=1) and mc.getAttr(node + ".overrideEnabled"):
			visible=visible
			visible and mc.getAttr(node + ".overrideVisibility")
			
		if visible:
			allParent = []
			self.getParentHier(node, allParent)
			if allParent:
				visible=visible
				visible and self.nodeIsVisible(allParent[0])
		return visible
		
	def rigGrp(self): #done
		
		lsRigGrp = mc.ls("rig_grp", "*:rig_grp", "Rig_grp", "*:Rig_grp", typ="transform")
		s=len(lsRigGrp)
		s = s - 1
		if "Rig" not in lsRigGrp[s]:
			newName= mc.rename(lsRigGrp[s], "Rig_grp")
			return newName
		else:
			return lsRigGrp[s]

	def makeAnimModeN(self): #done
		listAttr = mc.listAttr(self.rigGrp(), ud = True)
		if listAttr and "animMode" in listAttr :
			self.deleteAnim()
		else:
			pass
		
		
		if not mc.ls(self.rigGrp()):
			mc.confirmDialog(message="Doesn't have rig_grp node yet. Please create one!", 
				button="Yes", defaultButton="Yes", 
				title="QA Tool v.16")
			return 0
			
		else:
			mc.select(self.rigGrp())
			mel.eval("catchQuiet (`addAttr -ln \"animMode\" -keyable true  -at long  -min 0 -max 1 -dv 1 "+ self.rigGrp() + "`)")
			mel.eval("catchQuiet (`shadingNode -n \"rig_animMode_rev\" -asUtility reverse`)")
			mel.eval("catchQuiet (`connectAttr " + self.rigGrp() +".animMode \"rig_animMode_rev.inputX\"`)")
			
			cleanedJnts = mc.ls("zeroJntComeBack", type="joint")
			cleanedJnts += ["rig_C_torso_chest_jnt"][:1]
			
			#deal with jnt
			jnts=mc.ls(type="joint")
			jnts = list(set(jnts).difference(set(cleanedJnts)))
			for x in jnts:
				if "ctrl" in x:
					mel.eval("catchQuiet (`setAttr " + x + ".drawStyle  2`)")
				
				test=mc.listRelatives(x, ad=1)
				if test:
					for i in test:
						if "ctrl" in i:
							mel.eval("catchQuiet (`setAttr  "+ x + ".drawStyle 2`)")
				if mc.getAttr( x + ".drawStyle") != 2:
					mel.eval("catchQuiet(`connectAttr " + self.rigGrp() + ".animMode " + x + ".template`)")

			#deal with locator
			locs = mc.ls(type="locator")
			for loc in locs:
				mel.eval("catchQuiet (`connectAttr \"rig_animMode_rev.outputX\" " + loc + ".v`)")
			
			#deal with mesh	
			
			self.dealM()
			
			# deal with nurb surface
			nurbGeo = mc.ls("*:*_geoShape", "*_geoShape", type="nurbsSurface")
			for obj in nurbGeo:
				obj = obj.replace("Shape","")
				if self.nodeIsVisible(obj):
					mel.eval("catchQuiet (`setAttr " + obj + ".overrideDisplayType 2`)")
					mel.eval("catchQuiet (`connectAttr "+ self.rigGrp() +".animMode " + obj + ".overrideEnabled`)")
					
			nurb = mc.ls(type="nurbsSurface")
			for x in nurb:
				if not "_geoShape" in x:
					subNurb=x.replace("Shape","")
					mel.eval("catchQuiet (`setAttr " + subNurb + ".v 0`)")
			# deal with follicle
			fol = mc.ls(type="follicle")
			for x in fol:
				mel.eval("catchQuiet (` setAttr " + x + ".v 0`)")
				
			# deal with ikHandle
			ikHandle=mc.ls(type="ikHandle")
			for x in ikHandle:
				mel.eval("catchQuiet (` setAttr "+ x + ".v 0`)")

			return 1
	
	def toggleAnimode(self, *args): #done
		listAttr = mc.listAttr(self.rigGrp(), ud = True)
		tg = 0
		if listAttr and "animMode" in listAttr :
			get=int(mc.getAttr(self.rigGrp() + ".animMode"))
			if get == 0:
				tg=1
				mc.button('togAni', e=1, l="Turn off\nAnim Mode")
				
			if get == 1:
				tg=0
				mc.button('togAni', e=1, l="Turn on\nAnim Mode")
				
			mc.setAttr((self.rigGrp() + ".animMode"), tg)

	def turnOffAnimode(self):#done
		listAttr = mc.listAttr(self.rigGrp(), ud = True)
		if listAttr and "animMode" in listAttr :
			mc.setAttr((self.rigGrp()+ ".animMode"), 0)
		else:
			pass
			
	def setCtrlZero(self, *args): #done
		clearKey = mc.ls("*_ctrl", "*:*_ctrl")
		clearKeyCase = mc.ls("*_Ctrl", "*:*_Ctrl")
		clearKey += clearKeyCase[:len(clearKeyCase)]
		
		for x in clearKey:
			shape = mc.listRelatives(x, s=1)
			intersect = []
			if shape:
				mel.eval("catchQuiet (`cutKey " + x + "`)")
				userDef=mc.listAttr(x, ud=1)
				if userDef and self.attr(x): intersect = list(set(self.attr(x)).intersection(set(userDef)))
				if intersect:	
					for i in range(0,len(intersect)):
						mel.eval("catchQuiet (`cutKey " + x + "." + intersect[i] + " `)")
						getDef = mc.addAttr((x + "." + intersect[i]), q=1, dv=1)
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
				
				if mc.objExists("rig_*_upArm_A_pos_loc") or mc.objExists("*:rig_*_upArm_A_pos_loc"):
					upArmCtrl = mc.ls("rig_*_arm_upArm_fk_ctrl", "*:rig_*_arm_upArm_fk_ctrl")
					upArmLoc = mc.ls("rig_*_upArm_A_pos_loc", "*:rig_*_upArm_A_pos_loc")
					for i in range(0,len(upArmLoc)):
						mc.select(upArmCtrl[i], upArmLoc[i])
						mc.MatchRotation()
		try:
			mel.eval("source \"V:/libraries/Scripts/LumiPicker/_script/IkFkSwitch.mel\"")
		except:
			pass
		
		mel.eval("catchQuiet(`kinematicSwitch \"\" \"L\" \"arm\"`)")
		mel.eval("catchQuiet(`kinematicSwitch \"\" \"R\" \"arm\"`)")
		armSwitchCtrl = mc.ls("rig_*_arm_switch_ctrl", "*:rig_*_arm_switch_ctrl")
		
		if armSwitchCtrl:
			for x in armSwitchCtrl:
				mel.eval("catchQuiet (`setAttr " + x + ".ikEnable 0`)")
		
		mc.select(cl = True)
					
	def checkHideJnt(self): #done
		listVi=mc.ls(type="joint", v=1)
		cleanedJnts=mc.ls("*_ctrlEnv", type="joint")
		listVi=[x for x in listVi if x not in cleanedJnts]
		for i in listVi:
			if mc.getAttr(i + ".template"):
				testRe= mc.listRelatives(i, s=1)
				if not testRe:
					mel.eval("catchQuiet (`setAttr " + i + ".drawStyle 2`)")
					
					

	def deleteAnim(self, *args): #done
		listAttr = mc.listAttr(self.rigGrp(), ud = True)
		if listAttr and "animMode" in listAttr :
			self.turnOffAnimode()
			mc.deleteAttr(self.rigGrp() + ".animMode")
			mc.delete('rig_animMode_rev')
		else:
			mc.confirmDialog(message=("AnimMode doesn't exist! \n  "), button="Okay", defaultButton="Okay", title="QA Tool v.16")

	def viewOff(self):	#done	
		activePanel = mc.getPanel(wf=1)
		mc.modelEditor(activePanel, cameras=False, j=False, e=1, nurbsCurves=False, lc=False)

	def viewOn(self): #done
		activePanel = mc.getPanel(wf=1)
		mc.modelEditor(activePanel, allObjects=1, e=1)
		
	def changeName(self): #done - chuc nang nay tam thoi dung hoat dong
		allNodes = mc.ls(ap=1)
		for node in allNodes:
			buffer = node.split("|")
			mel.eval("catchQuiet(`rename "+node + " rig_"+ buffer[len(buffer) - 1]  + " `)")
		mel.eval("searchReplaceNames(\"_lf_\", \"_L_\", \"all\")")
		mel.eval("searchReplaceNames(\"_rt_\", \"_R_\", \"all\")")
		mel.eval("searchReplaceNames(\"_ct_\", \"_C_\", \"all\")")
		mel.eval("searchReplaceNames(\"rig_rig_\", \"rig_\", \"all\")")
	def openS(self): #done
		mc.file((mc.textField('expDir', q=1, fi=1)), open=1, f=1)
	def dealM(self): #done
		mesh=mc.ls(type="mesh")
		for obj in mesh:
			getPare = mc.listRelatives(obj, p=1)
			hhs= mc.getAttr(obj + ".visibility")
			if mc.ls(getPare[0] + ".visibility"):
				hh = mc.getAttr(getPare[0] + ".visibility")
				if hh and hh == hhs:
					mel.eval ("catchQuiet (`connectAttr " + self.rigGrp() +".animMode " + obj +".overrideEnabled`)")
					mel.eval ("catchQuiet (`setAttr "+ obj +".overrideDisplayType 2`)")
					
	def removeUnknowPlugin(self): #done
		lsPlugin = mc.unknownPlugin(q=1, l=1)
		if lsPlugin:
			for x in lsPlugin:
				mc.unknownPlugin(x, r=1)

	def killAllWindow(self , *args): #done
		lsP = mc.getPanel(vis=1)
		for each in lsP:
			getTypP = mc.getPanel(to=each)
			win = (getTypP + " -q -ctl " + each)
			execute= mel.eval(win)
			tokens = execute.split("|")
			if tokens and "MainPane" not in tokens[0] and "Outliner" not in tokens[0] and "scriptEditorPanel" not in tokens[0]:
				mc.deleteUI(tokens[0])
				
	def ctrlShapeAttrCheck(self): #done
		clearKey = mc.ls("*_ctrl", "*:*_ctrl","*_Ctrl")
		if clearKey:
			for x in clearKey:
				shape = mc.listRelatives(x, s=1)
				for i in shape:
					if self.count(i) == 1:
						if self.attr(i):
							for n in range(0,len(self.attr(i))):
								mel.eval("catchQuiet(`setAttr -lock true "+ i + "." + self.attr(i)[n] + "`)")
					else:
						list= mc.ls(i)
						for m in range(0,self.count(i)):
							if self.attr(list[m]):
								for n in range(0,len(self.attr(list[m]))):
									mel.eval("catchQuiet(`setAttr -lock true "+ i + "." + self.attr(list[m])[n] + "`)")
	def count(self,input): #done
		list = mc.ls(input)
		return len(list)

	def attr(self, input): #done
		attr = []
		attrInCb = mc.listAttr(input, cb=True)
		attrKeyable = mc.listAttr(input, k=True)
		if attrInCb and attrKeyable:
			attr = attrInCb + attrKeyable
		elif not attrInCb and attrKeyable:
			attr = attrKeyable
		elif attrInCb and not attrKeyable:
			attr = attrInCb
		else:
			attr = None
		return attr

	
		
	def lockAbc(self,num): #done
		lsRef=mc.ls(rf=1)
		print "LOL"
		if lsRef:
			for x in lsRef:
				print self.mainAbc(x)
				if self.mainAbc(x):
					print "innnnn"
					mel.eval("catchQuiet (`file -unloadReference " + x + "`)")
					mel.eval("catchQuiet (`setAttr "+ x +".locked " + str(num) + "`)")
					mel.eval("catchQuiet (`file -loadReference " + x + "`)")
					print "done"
				
	def toggleLimit(self, *args): #done
		if checktextSl():
			if mc.button('lmGeo', q=1, l=1) == "Lock Abc":
				self.lockAbc(1)
				mc.button('lmGeo', e=1, l="Unlock Abc")
				
			else:
				self.lockAbc(0)
				mc.button('lmGeo', e=1, l="Lock Abc")
	


	def checkDeformer(self): #done
			ls=mc.ls(dag=1)
			#check tat ca cac deformer trong scene, xem co deform rac nao khong
			errorList = []
			for t in range(0,len(ls)):
				his=mc.listHistory(ls[t], pruneDagObjects=True, interestLevel=1)
				if his:
					for each in his:
						types=mc.nodeType(each, inherited=1)
						if types[0] == "geometryFilter" and not mc.getAttr(each + ".envelope") and not self.checkConnection(each) and not self.checkBsConnection(each):
							errorList = errorList + each

			erShortList= list(dict.fromkeys(errorList))
			error=len(erShortList)
			if error:
				printError="\n".join(erShortList)
				popup = mc.confirmDialog(message=("Found: %s errors \n\n" + "This nodes has .envelope = 0 and has no in/out connection : \n \n" + printError) %error, button=["Cancel. Stop the process", "Ignore. Continue", "Set to 1", "Delete. Continue"], defaultButton="Ignore. Continue", title="QA Tool v.16")
				if popup == "Set to 1":
					for l in erShortList:
						mc.setAttr((l + ".envelope"), 1)
					return 0
				if popup == "Cancel. Stop the process":
					return 0
				if popup == "Delete. Continue":
					for l in erShortList:
						mc.delete(l)
					return 1					
				else:
					return 1					
			return 1
			
	def checkConnection(self, attr): #done
		array = self.showAttr(attr)
		arrayCv = array.split("\n")
		error=0
		for each in arrayCv:
			checkD = mc.connectionInfo((attr + "." + each), isDestination=1)
			if checkD:
				error = error + 1
		if error:
			return 1
		return 0

	def checkBsConnection(self, each): #done
		listBs = mc.aliasAttr(each, q=1)
		if listBs:
			for r in listBs:
				if "weight" in r:
					checkD = mc.connectionInfo((each + "." + r), isDestination=1)
					if checkD:
						return 1
						
		return 0

	def showAttr(self, x): #done
		attrLock=mc.listAttr(x, l=1)
		if self.attr(x):
			attrInCb= [y for y in self.attr(x) if y not in attrLock]
		else:
			attrInCb = None
		# nhung attr o channel box dang hien thi va khong bi lock
		userDef=mc.listAttr(x, ud=True)
		if attrInCb and userDef:
			intersect = list(set(attrInCb).intersection(set(userDef)))
			return intersect
		elif attrInCb and not userDef:
			return attrInCb
		elif not attrInCb and userDef:
			return userDef
		else:
			return None

	def cleanCb(self): #done
		clearKey = mc.ls("*_ctrl", "*:*_ctrl", "*_Ctrl", "*:*_Ctrl")
		for x in clearKey:
			self.ihi(x)
		listDep= mc.ls(dep=True)
		objIih=["polySmoothFace", "reference", "reverse", "remapValue", "blendShape", "skinCluster", "shapeEditorManager", "multDoubleLinear", "nonLinear", "createColorSet", "ffd", "tweak", "polyTweakUV", "nurbsTessellate", "ngSkinLayerData", "cluster", "wrap", "lambert", "deleteComponent", "deltaMush", "plusMinusAverage", "wire", "multiplyDivide", "clamp", "condition", "nodeGraphEditorInfo", "blendColors", "dagPose", "setRange", "parentConstraint", "pointConstraint", "scaleConstraint", "orientConstraint", "aimConstraint", "blendTwoAttr"]
		for x in listDep:
			type= mc.objectType(x)
			if type in objIih:
				mel.eval("catchQuiet (`connectAttr rig_animMode_rev.outputX " + x + ".ihi`)")
				
		mel.eval("catchQuiet (`outlinerEditor -e -showDagOnly true outlinerPanel1`)")

	def ihi(self,ctrl): #done
		listH = mc.listHistory(ctrl)
		for y in listH:
			mel.eval("catchQuiet(`connectAttr rig_animMode_rev.outputX "+ y + ".ihi`)")
		
	def loadPluginQA(self): #done
		loadPlugin=["weightDriver", "poseReader", "cvwrap"]
		eList = []
		for x in loadPlugin:
			check= mel.eval("catchQuiet (`loadPlugin "+ x +"`)")
			if check != 0:
				eList.append(x)
			if eList:
				printError = "\n".join(eList)
				mc.confirmDialog(title="QA Tool v.16", cancelButton="No", defaultButton="Yes", button=["Yes", "No"], message=("List of unload plug-in:\n" + printError), dismissString="No")
		
	def optiUnitNode(self): #done
		transNode= mc.ls(typ="transform")
		for each in transNode:
			self.checkSourceNOpti(each)

	
	def checkSourceNOpti(self, input):	#done
		rX = []
		rY = []
		rZ = []
		R = []
		if mc.connectionInfo((input + ".r"), isSource=1):
			RR = mc.connectionInfo((input + ".r"), destinationFromSource=1)
			sizeR=len(RR)
			for x in range(0,sizeR):
				if self.checkUnitNode(RR[x]) != 0:
					R += [RR[x]][:1]
			if len(R) > 1:
				self.connectUnit (input,"rotate",R);
			
		if mc.connectionInfo((input + ".rx"), isSource=1):
			RrX=mc.connectionInfo((input + ".rx"), destinationFromSource=1)
			RrX=[x for x in RrX if x not in R]
			sizeRx=len(RrX)
			for x in range(0,sizeRx):
				if self.checkUnitNode(RrX[x]) != 0:
					rX += [RrX[x]][:1]

				
			if len(rX) >1:
				self.connectUnit (input,"rx",rX)
				
			
		if mc.connectionInfo((input + ".ry"), isSource=1):
			RrY=mc.connectionInfo((input + ".ry"), destinationFromSource=1)
			RrY=[x for x in RrY if x not in R]
			sizeRy=len(RrY)
			for x in range(0,sizeRy):
				if self.checkUnitNode(RrY[x]) != 0:
					rY += [RrY[x]][:1]

			if len(rY) >1:
				self.connectUnit (input,"ry",rY)
			
		if mc.connectionInfo((input + ".rz"), isSource=1):
			RrZ=mc.connectionInfo((input + ".rz"), destinationFromSource=1)
			RrZ=[x for x in RrZ if x not in R]
			sizeRz=len(RrZ)
			for x in range(0,sizeRz):
				if self.checkUnitNode(RrZ[x]) != 0:
					rZ += [RrZ[x]][:1]

			if len(rZ) >1:
				self.connectUnit (input,"rz",rZ)
				
	def checkUnitNode(self, input): #done
		
		cutName=re.search(r"[^\\.]*", input)
		if mc.objectType(cutName.group()) == "unitConversion":
			return 1
			
		return 0

	def connectUnit(self,input, attr, output): #done
		inputName = input + "." + attr
		outputOfUnit = []
		if len(output)>1:
			for x in output:
				cutName=re.search(r"[^\\.]*", x)
				out=mc.connectionInfo((cutName.group() + ".output"), destinationFromSource=1)
				if not len(out):
					mel.eval(" catchQuiet(`delete " + cutName.group()+"`)")
								
				else:
					outputOfUnit += out[:len(out)]
					for e in out:
						mel.eval("catchQuiet(`disconnectAttr "+ cutName.group() + ".output " + e + "`)")

			winner=re.search(r"[^\\.]*", output[0])
			# da loc va disconnect xong output. Gio se xoa cac node unit thua va noi sang output moi
			winner =mc.rename(winner.group(), (input + "_" + winner.group() + "_optiNode"))
			for z in range(1,len(output)):
				cutName=re.search(r"[^\\.]*", output[z])
				mc.delete(cutName.group())
				
			for i in outputOfUnit:
				mel.eval("catchQuiet(`connectAttr -f "+ winner + ".output "+i +"`)")
				


# --------------- WIP ------------------------					



	def excecute(self, *args): #done
		lsCmd = allCmd()
		cnt=len(lsCmd)
		#while checktextSl() and self.checkAbcGeo() and self.checkDeformer():
		while True:
			for e in range(0,cnt):
				mc.progressWindow(status="Running, running, running...", isInterruptable=True, minValue=0, maxValue=cnt, title="QA Tool v.16")
				mc.progressWindow(edit=1, progress=e, status=lsCmd[e])
				mc.pause(sec=1)
				cmd = lsCmd[e]
				print "Step " + str(e) + "------------" + cmd + " ----------\n"
				
				try:
					print ("innnnnnnn self."+cmd+"()")
					eval("self."+cmd+"()")
				except:
					print ("outttttt self."+cmd+"()")
					break
				
				if mc.progressWindow(query=1, isCancelled=1):
					break
			break

		mc.progressWindow(edit=1, progress=cnt, status="MY JOB IS DONE!")
		mc.pause(sec=3)
		mc.progressWindow(endProgress=1)

	def checkfacial(self): #done
		
		sceneName = mc.file(q=1, loc=1, shn=1)
		if "facial"in sceneName or "Facial" in sceneName:
			self.autoDirFace()
			self.oWrite()
			
	def faceCmd(self): #done
		lsCmd=["doOWrite", "setCtrlZero", "importAll", "deleteNg", "deleteDelLayer", "deleteAllLayer", "ctrlShapeAttrCheck", "checkHideJnt", "optimizeScn", "deleteAllNamespace", "smoothDiv", "convertMatrixNlock", "optiUnitNode", "removeUnknowPlugin", "expAll"]
		if mc.checkBox('opSf', q=1, v=1):
			lsCmd += ["openS"]
		return lsCmd

	def excecuteFace(self, *args): #done
		
		lsCmd= self.faceCmd()
		cnt= self.faceCmd()
		#while self.checkDeformer():
		while True:
			for e in range(0,cnt):
				mc.progressWindow(status="Running, running, running...", isInterruptable=True, minValue=0, maxValue=cnt, title="QA Tool v.16")
				mc.progressWindow(edit=1, progress=e, status=lsCmd[e])
				mc.pause(sec=1)
				cmd = lsCmd[e]
				print "Step " + str(e) + "------------" + cmd + " ----------\n"
				try:
					eval("self."+cmd+"()")
				except:
					break
				if mc.progressWindow(query=1, isCancelled=1):
					break
			break

		mc.progressWindow(edit=1, progress=cnt, status="MY JOB IS DONE!")
		mc.pause(sec=3)
		mc.progressWindow(endProgress=1)
		
	def convertMatrixNlock(self): #done
		nFeatureNode = mc.ls("*:*rig_C_torso_up_crv", "rig_C_torso_up_crv")
		if len(nFeatureNode) == 1:
			sMtx="source \"V:/libraries/Scripts/ConstraintToMatrix.mel\""
			#
			eval(sMtx)
			sel=mc.ls()
			pass_ = []
			camera=mc.ls(type='camera')
			for c in camera:
				p=mc.listRelatives(c, p=1)
				pass_.append(c)
				pass_.append(p[0])
				
			ikh=mc.ls(type='ikHandle')
			ikj = []
			for ik in ikh:
				jl=mc.ikHandle(ik, q=1, jl=1)
				ikj += jl[:len(jl)]
				
			shape=mc.ls(type='shape')
			sets=mc.ls(type='objectSet')
			pass_ += camera[:len(camera)]
			pass_ += shape[:len(shape)]
			pass_ += sets[:len(sets)]
			for o in sel:
				if not o in pass_ and not "ctrl" in o:
					a1=mc.listAttr(o, ud=1, k=1)
					a2=mc.listAttr(o, ud=1, cb=1)
					a3=mc.listAttr(o, k=1, v=1)
					attr = []
					attr += a1[:len(a1)]
					attr += a2[:len(a2)]
					attr += a3[:len(a3)]
					if mc.nodeType(o) == "joint":
						attr.append("radius")
					for a in attr:
						if not (o in ikj and "rotate" in a):
							mel.eval("catch(`setAttr -l "+ o + "." + a +"`)")
class getData():

	def openCloseSbs(self, *args): #done
		h=410
		if mc.frameLayout('cleanSBS', q=1, cl=1) == 0:
			h= h + 320		
		mc.window("checkFiles",e = True, wh = [300, h])   
		

	def addOn(self, *args): #done
		if self.checkAbcGeo() == 1:
			addOn=mc.ls(sl=1)
			for x in addOn:
				mc.textScrollList('charTopnode', e=1, ra=1)
				mc.textScrollList('charTopnode', a=x, e=1, uniqueTag=x)
				mc.textScrollList('charTopnode', selectUniqueTagItem=x, e=1)
			self.autoDir("body")

	def autoDir(self, type): #done dung thay cho ca autoDirFace, nhap input face hoac body
		typExp = ""
		final = ""
		con = 0
		if "face" in type:
			con = 1
		if "body" in type:
			con  = checktextSl()
		if mc.radioButton('chkMB', q=1, sl=1):
			typExp=".mb"
		else:
			typExp = ".ma"
		if con:	
			sceneName= mc.file(q=1, loc=1, shn=1)
			longSceneName = mc.file(q=1, loc=1)
			if "wip" in longSceneName :
				longSceneName = longSceneName.replace("wip","submit")
				
			cutScene= re.search(r"^.*/", longSceneName)
			curVer= re.search(r"[0-9]+", sceneName)
			nameChar= re.search(r"^[^\.]*", sceneName)
			if curVer:
				final = (cutScene.group() + nameChar.group() + ".v%s"   + typExp) %(int(curVer.group()) + 1) 
			else:
				final = (cutScene.group() + nameChar.group() + ".v001"  + typExp)
			if os.path.exists(cutScene.group()):
				mc.textField('expDir', fi = final, e=1)		
			else:
				os.makedirs(cutScene.group())
				mc.textField('expDir', fi= final, e=1)

	def oWrite(self, *args): #done
		name = mc.textField('expDir', q=1, fi=1)
		if os.path.exists(name):
			popUp=str(mc.confirmDialog(title="QA Tool v.16", cancelButton="Ignore", defaultButton="Overwrite", button=["Overwrite", "Save exist file as backup", "Ignore"], message="This file already exist! \n", dismissString="Ignore"))
			if popUp == "Overwrite":
				mc.radioButton('oW', e=1, sl=1)
				
			if popUp == "Save exist file as backup":
				mc.radioButton('rNE', e=1, sl=1)
				
	def userSave(self, *args):
		userPic = mc.fileDialog2(cap = "QA Tool v.16: Set directory and name of the file", fm = False)
		typExp = ""
		if mc.radioButton("chkMB",q = True, sl = True):
			typExp = ".mb"
		else:
			typExp = ".ma"
		cond = "\\" + typExp
		if typExp not in userPic[0]:
			if "*" in userPic[0]:
				userPic[0] = userPic[0].replace("*", "")
			userPic[0] = userPic[0] + typExp
			mc.textField("expDir", e =True, fi = userPic[0])
		else:
			mc.textField("expDir", e =True, fi = userPic[0])
		self.oWrite()

	def checkAbcGeo(self): #done
		if self.findAbc():
			listC = mc.referenceQuery(self.findAbc(), dp=1, n=1)
			errorList = []
			for t in listC:
				if self.checkShape(t):
					ee = self.checkModel(t)
					if ee: errorList = errorList + ee
			erShortList = list(dict.fromkeys(errorList))
			error = len(erShortList)
			print "Found: %s errors./ \n" %error
			if error :
				printError = "\n".join(erShortList)
				popup = mc.confirmDialog(message=("Found: %s errors.\n" + "Hey mannnnnn! Model is not clean!  ") %error, button=["Okay", "View error list", "Ignore"], defaultButton="Okay", title="QA Tool v.16")
				if popup == "Okay":
					return 0
				if popup == "View error list":
					mc.confirmDialog(message=("Found: %s errors.\n" + "Error list: \n \n " + printError) %error, button="Okay", defaultButton="Okay", title="QA Tool v.16")
					return 0
				else:
					return 1
		return 1
				
	def findAbc(self): #done
		returnList = []
		listRef = mc.ls(references = 1)
		for x in range(0, len(listRef)):
			refName= listRef[x]
			if mel.eval("catchQuiet (`referenceQuery -f  " +refName+"`)"):
				pass
			else:
				dirName = mc.referenceQuery(refName, f=1)
				filepart= re.search(r"[^/\\]*$", dirName)	
				if "abc" in filepart.group():
					returnList.append(dirName)

		return returnList
		
	def checkShape(self,geo): #done
		
		childAbc=mc.listRelatives(geo, c=1)
		if childAbc:
			for tt in childAbc:
				if self.count(tt) == 1:
					typ= mc.objectType(tt)
					if typ == "mesh" or typ == "nurbsSurface" or typ == "transform":
						return 1
		else:
			return 0
	def checkModel(self,input): #done
			error=0
			errorList = []
			t= mc.getAttr(input + ".t")
			r= mc.getAttr(input + ".r")
			s= mc.getAttr(input + ".s")
			for q in range(0,3):
				attr = ""
				addLock = ""
				if q == 0:
					attr="X "
					addLock="x"
				
				if q == 1:
					attr="Y "
					addLock="y"
				
				if q == 2:
					attr="Z "
					addLock="z"
				
				if t[0][q]:
					e= "ERROR: {} translate {} {} \n"
					errorList.append(e.format(input,attr, t[0][q]))
					error = error + 1
				if r[0][q]:
					e=("ERROR: {} rotate {} {} \n")
					errorList.append(e.format(input,attr, r[0][q]))
					error=error + 1
				if s[0][q] != 1 :
					print "lala"
					e=("ERROR: {} scale {} {} \n")
					errorList.append(e.format(input,attr, s[0][q]))
					error=error + 1

			return errorList	
	def count(self,input): #done
		list = mc.ls(input)
		return len(list)
		
def checktextSl(): #done
	topNode = mc.textScrollList('charTopnode', q = True, selectUniqueTagItem = 1)
	if not topNode:
		mc.confirmDialog(message="Please select character node!", 
			button="Yes", defaultButton="Yes", 
			title="QA Tool v.16")
		return 0
	else:
		return 1	

def combine_funcs(*funcs):
	def combined_func(*args, **kwargs):
		for f in funcs:
			f(*args, **kwargs)
	return combined_func	
	
def allCmd(): #done
	lsCmd=["doOWrite", "setCtrlZero", "importFacialRef", "deleteNg", "deleteDelLayer", "deleteAllLayer", "deleteDagNode", "turnAnimmode", "cleanCb", "ctrlShapeAttrCheck", "checkHideJnt", "optimizeScn", "deleteAllNamespace", "smoothDiv", "convertMatrixNlock", "optiUnitNode", "removeUnknowPlugin", "export"]
	if mc.checkBox('opSf', q=1, v=1):
		lsCmd += ["openS"]
	return lsCmd	

def dodo(input):
	d = QAtool()
	toEval = "d."+ input +"()"
	eval (toEval)
def prpr(data, *args):
	cmd = "QAtool.dodo(\"" + data +"\")"
	return cmd	
	
def showWindow():
	name = "checkFiles"
	if mc.window( name, ex = True):
		mc.deleteUI( name)
		mc.windowPref (name, remove= True )
	data = getData()

	mc.window(name, title = "QA Tool Python v.01", w = 300, h = 410, s = True)
	mc.columnLayout( w = 300, h = 410)
	mc.text(l = "  Select character node", h= 30 )
	mc.setParent()
	mc.rowColumnLayout(numberOfColumns = 2, h= 70, columnWidth = [(1, 200),( 2, 100)] )
	mc.textScrollList("charTopnode" , allowMultiSelection = True, h = 30 )
	QA = QAtool()	
	mc.button(l = "Select", w= 100, h = 30, c = combine_funcs (data.addOn, data.oWrite, QA.__init__) , al = "left")
	mc.text(l= "", h = 5)
	mc.text(l= "", h = 5)
	mc.textField("expDir", h = 30)
	mc.button(l = "Choose directory\nmanually", c= data.userSave )
	mc.setParent("..")
	mc.rowColumnLayout(numberOfColumns = 3, h = 15, columnWidth = [(1,60), (2,60),(3,180)])
	mc.radioCollection()
	mc.radioButton("chkMA",label = ".ma", sl = True, onCommand = combine_funcs(data.addOn, data.oWrite ) )
	mc.radioButton("chkMB",label = ".mb", onCommand = combine_funcs(data.addOn, data.oWrite ))
	mc.setParent()
	mc.checkBox("opSf",label = "Open summit file after export", v= 1)
	mc.setParent("..")
	mc.rowColumnLayout(numberOfColumns = 2, h = 20, columnWidth = [(1,120), (2,180)])
	mc.radioCollection()
	mc.radioButton("oW", l = "Overwrite  file", ed = 0)
	mc.radioButton("rNE", l = "Rename exist file to backup", ed = 0)
	mc.setParent()
	mc.setParent("..")
	mc.text(l= "", h = 10)
	mc.button(l = "Full Rig Cleanup and Export", w = 300, h = 50, c = QA.excecute )
	mc.text(l= "", h = 5)
	mc.button(l = "Facial Submit", w = 300, h = 50, c = QA.excecuteFace)

	mc.rowLayout(numberOfColumns = 4, columnWidth4 = (75,75,75,75), h= 60,columnAlign = (1,"center"))
	mc.button("togAni",l = "Toggle\nAnim Mode", w = 70, h = 50, c = QA.toggleAnimode)
	mc.button(l = "Delete \n Animmode", w = 70, h = 50, c = QA.deleteAnim)
	mc.button(l = "Clear all key \n Back to 0", w = 70, h = 50, c = QA.setCtrlZero)
	mc.setParent("..")
	mc.setParent("..")

	mc.rowLayout(numberOfColumns = 4, columnWidth4 = (75,75,75,75), h= 60,columnAlign = (1,"center"))
	mc.button(l = "close\nAll Panel", w = 70, h = 50, c = QA.killAllWindow)
	mc.button("lmGeo",l = "Lock\nAlembic", w = 70, h = 50, c = QA.toggleLimit)
	mc.setParent("..")
	mc.setParent("..")
	mc.frameLayout("cleanSBS",l = "Cleanup step by step", collapsable = True, collapse = True, ec = data.openCloseSbs, cc = data.openCloseSbs )
	mc.rowColumnLayout( numberOfColumns = 2, columnWidth = [(1,150), (2,150)], cal = [(1 ,"left" ), (2 , "left")], co = [(1, "both", 3)], cs = (10,10) , rs = (1,2) )
	lsCmd = allCmd()
	for x in range (0, len(lsCmd)):
		mc.button( l = (str(x) + "_" + lsCmd[x]) , h = 30 , c = prpr(lsCmd[x]) )
	mc.setParent()
	mc.setParent()
	mc.showWindow(name)
