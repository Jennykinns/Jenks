#
#    Renaming Tool by Clement Chaudat - 2014 v1.1.0
#
#    CONSTANTS IN TEXTFIELDS
#    Multiple constants with right-click on textField:
#        - OldName: good for prefix/suffix
#        - ObjectType
#        - ParentName
#
#    INCREMENT: "###" or "%3d"
#    Right-click on textField then "Set Start/Step" for
#    start number and step value for indent.
#
#    RENAME USING REGEXP:
#    example :   "end$" will replace "end" at the end of the name
#                "^start" will replace "start" at the beginning of the name
#

import re
import functools
import maya.cmds as cmds
from maya import OpenMaya

uiFile = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Dialog</class>
 <widget class="QDialog" name="winRenamer">
  <property name="geometry">
   <rect>
    <x>120</x>
    <y>120</y>
    <width>320</width>
    <height>100</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Rename / Replace</string>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="spacing">
    <number>4</number>
   </property>
   <property name="margin">
    <number>4</number>
   </property>
   <item>
    <widget class="QLineEdit" name="cc_edit_rename"/>
   </item>
   <item>
    <layout class="QHBoxLayout" name="horizontalLayout">
     <item>
      <widget class="QCheckBox" name="cc_check_replace">
       <property name="text">
        <string>Replace By:</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLineEdit" name="cc_edit_replace">
       <property name="enabled">
        <bool>false</bool>
       </property>
      </widget>
     </item>
    </layout>
   </item>
   <item>
    <layout class="QHBoxLayout" name="horizontalLayout_2">
     <item>
      <widget class="QRadioButton" name="cc_check_all">
       <property name="enabled">
        <bool>false</bool>
       </property>
       <property name="text">
        <string>All</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QRadioButton" name="cc_check_selected">
       <property name="text">
        <string>Selected</string>
       </property>
       <property name="checked">
        <bool>true</bool>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QRadioButton" name="cc_check_hierarchy">
       <property name="text">
        <string>Hierarchy</string>
       </property>
      </widget>
     </item>
    </layout>
   </item>
   <item>
    <widget class="QPushButton" name="cc_push_rename">
     <property name="text">
      <string>Rename / Replace</string>
     </property>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections>
  <connection>
   <sender>cc_check_replace</sender>
   <signal>toggled(bool)</signal>
   <receiver>cc_edit_replace</receiver>
   <slot>setEnabled(bool)</slot>
   <hints>
    <hint type="sourcelabel">
     <x>43</x>
     <y>32</y>
    </hint>
    <hint type="destinationlabel">
     <x>118</x>
     <y>31</y>
    </hint>
   </hints>
  </connection>
  <connection>
   <sender>cc_check_replace</sender>
   <signal>toggled(bool)</signal>
   <receiver>cc_check_all</receiver>
   <slot>setEnabled(bool)</slot>
   <hints>
    <hint type="sourcelabel">
     <x>34</x>
     <y>39</y>
    </hint>
    <hint type="destinationlabel">
     <x>34</x>
     <y>59</y>
    </hint>
   </hints>
  </connection>
 </connections>
</ui>

"""

# support des lettres
# renommage de noms en double avec absolute path


class Renamer():

    replace = False
    _settings = {"startNb": 1, "stepNb": 1, "structure": [0]}
    _startNb = 1
    _stepNb = 1
    _steps  = [
                ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
                ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
              ]
    _format = [0]
    _win = None
    _winName = "winRenamer"
    _settingsName = "dialRenamerSettings"

    def __init__(self, *arg):
        #  ### ou %3d
        self._setupUI()

    def _setupUI(self):
        if cmds.window(self._winName, q=True, ex=True):
            cmds.deleteUI(self._winName)
        self._win = cmds.loadUI(s=uiFile)
        # rename / find
        cmds.showWindow(self._win)
        cmds.popupMenu(p="cc_edit_rename")
        cmds.menuItem(l="Old Name", c=functools.partial(self._insert, "<OldName>", "cc_edit_rename"))
        cmds.menuItem(divider=True)
        cmds.menuItem(l="Object Type", c=functools.partial(self._insert, "<ObjectType>", "cc_edit_rename"))
        cmds.menuItem(l="Parent Name", c=functools.partial(self._insert, "<ParentName>", "cc_edit_rename"))
        cmds.menuItem(divider=True)
        cmds.menuItem(l="Set Start/Step...", c=self.setNumOptions)
        # replace
        cmds.popupMenu(p="cc_edit_replace")
        cmds.menuItem(l="Old Name", c=functools.partial(self._insert, "<OldName>", "cc_edit_replace"))
        cmds.menuItem(divider=True)
        cmds.menuItem(l="Object Type", c=functools.partial(self._insert, "<ObjectType>", "cc_edit_replace"))
        cmds.menuItem(l="Parent Name", c=functools.partial(self._insert, "<ParentName>", "cc_edit_replace"))
        cmds.menuItem(divider=True)
        cmds.menuItem(l="Set Start/Step...", c=self.setNumOptions)
        cmds.button("cc_push_rename", e=True, c=self.rename)
        cmds.textField("cc_edit_rename", e=True, ec=self.rename)
        cmds.textField("cc_edit_replace", e=True, ec=self.rename)

    def setNumOptions(self, *args):

        prompt = cmds.promptDialog(title='Start/Step Settings', message='Start, Step', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel', text=str(self._startNb)+","+str(self._stepNb))
        if prompt == 'OK':
            results = cmds.promptDialog(query=True, text=True).split(",")
            self._settings["startNb"] = int(results[0])
            self._settings["stepNb"] = int(results[1])

    def _insert(self, *args):
        ajout = args[0]
        cmds.textField(args[1], e=True, it=ajout)

    def _nb_digits(self, chaine):
        nb_zeros = 0
        substr = ""
        match_hash = re.findall("(#+)", chaine)
        if match_hash:
            nb_zeros = len(match_hash[0])
            substr = match_hash[0]
        else:
            match_digit = re.findall("[%](\d)(?i)[d]", chaine)
            if match_digit:
                nb_zeros = int(match_digit[0])
                substr = re.search("%(\d)(?i)d", chaine).group()
        if nb_zeros > 0:
            return nb_zeros, substr
        else:
            return False

    def _children(self, node):
        liste = list()
        node = OpenMaya.MFnDagNode(node)
        liste.append(node.fullPathName())
        for i in xrange(0, node.childCount()):
            child = node.child(i)
            if child.hasFn(OpenMaya.MFn.kTransform):
                liste.extend(self._children(child))
        return liste

    def _parseCsts(self, obj, name):
        node = OpenMaya.MFnDependencyNode(obj)
        old_name = node.name()
        dag = self._isDag(obj)
        if dag:
            dagNode = OpenMaya.MFnDagNode(obj)
            obj = dagNode.fullPathName()

        if re.search('<OldName>', name):
            name = old_name.join(name.split('<OldName>'))

        if re.search('<ObjectType>', name):
            t = node.typeName()
            if t == "transform":
                shapes = cmds.listRelatives(obj, s=True, f=True)
                if len(shapes) > 0:
                    t = cmds.objectType(shapes[0])
            name = t.join(name.split('<ObjectType>'))

        if re.search('<ParentName>', name) and dag:
            if cmds.listRelatives(obj, p=True):
                name = cmds.listRelatives(obj, p=True)[0].join(name.split('<ParentName>'))
            else:
                name = "Root".join(name.split('<ParentName>'))
                cmds.warning("Some objects have no parent")

        return name

    def _getObjects(self):
        if cmds.radioButton("cc_check_all", q=True, sl=True):
            if self.rename:
                objects = cmds.ls("*"+cmds.textField("cc_edit_rename", q=True, text=True)+"*")
            else:
                objects = list()
        elif cmds.radioButton("cc_check_hierarchy", q=True, sl=True):
            sel = cmds.ls(sl=True, l=True)
            objects = list()
            for obj in sel:
                objects.extend(self._children(self._MObject(obj)))
        else:
            objects = cmds.ls(sl=True)
        return [self._MObject(obj) for obj in objects]

    def _parseDigits(self, nn, i=0):
        digits = self._nb_digits(nn)
        if digits:
            nn = str(self._settings["startNb"]+i*self._settings["stepNb"]).zfill(digits[0]).join(nn.split(digits[1]))
        return nn

    def _MObject(self, name):
        sel = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getSelectionListByName(name, sel)
        mObj = OpenMaya.MObject()
        sel.getDependNode(0, mObj)
        return mObj

    def _isDag(self, obj):
        if isinstance(obj, OpenMaya.MObject):
            return obj.hasFn(OpenMaya.MFn.kDagNode)
        else:
            return False

    def rename(self, *args):
        newName = cmds.textField("cc_edit_rename", q=True, text=True)

        if len(newName) < 1:
            cmds.warning("No name in the field.")
            return False

        objects = self._getObjects()

        fnNode = OpenMaya.MFnDependencyNode()

        newName = cmds.textField("cc_edit_rename", q=True, text=True)
        self.replace = cmds.checkBox("cc_check_replace", q=True, v=True)
        replaceName = cmds.textField("cc_edit_replace", q=True, text=True)

        for i, obj in enumerate(objects):
            fnNode.setObject(obj)
            if self.replace:
                n = fnNode.name()
                n = re.sub(r"(" + newName + ")", replaceName, n)
            else:
                n = newName
            n = self._parseDigits(n, i)
            n = self._parseCsts(obj, n)

            if obj.hasFn(OpenMaya.MFn.kDagNode):
                oldName = OpenMaya.MFnDagNode(obj).fullPathName()
            else:
                oldName = fnNode.name()

            try:
                cmds.rename(oldName, n)
            except:
                continue

Renamer()
