# ----------------------------------------------------------------------------------------------
#
# MakeCircularMeshBorder.py
# v1.1 (150531)
#
# create a circular polygon border for holes or extrusions
# based on a selected center vertex
#
# Ingo Clemens
# www.braverabbit.com
#
# Copyright brave rabbit, Ingo Clemens 2015
# All rights reserved.
#
# ----------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# ----------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------
#
#	USE AND MODIFY AT YOUR OWN RISK!!
#
# ----------------------------------------------------------------------------------------------


import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from functools import partial

class MakeCircularMeshBorder():
	
	def __init__(self):
		self.win = 'makeCircularWindow'
		self.center = ''
		self.mesh = ''
		self.border = []
		self.bbox = []
		self.radius = 0
		self.centerVector = [0, 0, 0]
		self.circle = ''
		self.circleNode = ''
		self.constMesh = ''
		self.startParam = 0
		self.offset = ''
		self.extrude = ''
		self.move = ''
		self.faces = []
	
	
	def _start(self):
		if self._getBorderVertices() == None:
			return
		
		self._getSelectionBBox()
		self._getRadius()
		self._getCenterNormal()
		self._createCircle()
		self._createConstraintMesh()
		self._orderBorderVerts()
		self._snapBorderToCurve()
		self._showSliderWin()
	
		
	def _getBorderVertices(self):
		sel = cmds.filterExpand(sm = 31)
		if sel == None or not len(sel) or len(sel) > 1:
			OpenMaya.MGlobal.displayError('Select a center vertex')
			return None;
		
		self.center = sel[0]
		self.centerPos = cmds.xform(self.center, q = True, ws = True, t = True)
		self.mesh = self.center.split('.')[0]
		
		mel.eval('PolySelectTraverse 1')
		self.border = cmds.filterExpand(sm = 31)
		self.border.remove(self.center)
		return self.border
	
	
	def _getSelectionBBox(self):
		for i, v in enumerate(self.border):
			pos = cmds.xform(v, q = True, ws = True, t = True)
			if i == 0:
				self.bbox = [pos[0], pos[1], pos[2], pos[0], pos[1], pos[2]]
			else:
				if pos[0] < self.bbox[0]:
					self.bbox[0] = pos[0]
				elif pos[0] > self.bbox[3]:
					self.bbox[3] = pos[0]
				
				if pos[1] < self.bbox[1]:
					self.bbox[1] = pos[1]
				elif pos[1] > self.bbox[4]:
					self.bbox[4] = pos[1]
				
				if pos[2] < self.bbox[2]:
					self.bbox[2] = pos[2]
				elif pos[2] > self.bbox[5]:
					self.bbox[5] = pos[2]
		return self.bbox
	
	
	def _getRadius(self):
		x = self.bbox[3] - self.bbox[0]
		y = self.bbox[4] - self.bbox[1]
		z = self.bbox[5] - self.bbox[2]
		if x > y and x > z:
			self.radius = x / 2
		elif y > z:
			self.radius = y / 2
		else:
			self.radius = z / 2
		return self.radius
	
	
	def _getCenterNormal(self):
		cmds.select(self.center, r = True)
		mel.eval('ConvertSelectionToFaces')
		self.faces = cmds.ls(sl = True, fl = True)
		for f in self.faces:
			string = cmds.polyInfo(f, fn = True)
			vectorList = string[0].replace('\n', '').split(':')[1].split(' ')
			vectorList.pop(0)
			for i in range(len(self.centerVector)):
				self.centerVector[i] = self.centerVector[i] + float(vectorList[i])
		for i in range(len(self.centerVector)):
			self.centerVector[i] = self.centerVector[i] / len(self.faces)
		cmds.select(self.center, r = True)
		
	
	def _createCircle(self):
		# create the helper locators to convert the face normal
		# to the rotation values for the circle
		loc1 = cmds.spaceLocator()[0]
		loc2 = cmds.spaceLocator()[0]
		cmds.setAttr(loc2 + '.t', self.centerVector[0], self.centerVector[1], self.centerVector[2])
		aim = cmds.aimConstraint(loc1, loc2, aim = (0, 0, -1), u = (0, 1, 0), wut = 'vector', wu = (0, 1, 0))
		cmds.delete(aim)
		
		circle = cmds.circle(r = self.radius)
		self.circle = circle[0]
		self.circleNode = circle[1]
		cmds.setAttr(self.circle + '.v', 0)
		cmds.rebuildCurve(self.circle, ch = True, kr = 0, kcp = True)
		cmds.xform(self.circle, ws = True, t = self.centerPos)
		const = cmds.orientConstraint(loc2, self.circle)
		cmds.delete(const)
		
		cmds.delete(loc1, loc2)
	
	
	def _createConstraintMesh(self):
		self.constMesh = cmds.duplicate(self.mesh, rr = True)[0]
		cmds.setAttr(self.constMesh + '.v', 0)
	
	
	def _orderBorderVerts(self):
		curveNode = cmds.createNode('nearestPointOnCurve')
		cmds.connectAttr(self.circle + '.worldSpace[0]', curveNode + '.inputCurve')
		vtxList = []
		paramList = []
		vtxDict = {}
		for i, v in enumerate(self.border):
			pos = cmds.xform(v, q = True, ws = True, t = True)
			cmds.setAttr(curveNode + '.inPosition', pos[0], pos[1], pos[2], type = 'double3')
			param = cmds.getAttr(curveNode + '.result.parameter')
			vtxDict[v] = param
			paramList.append(param)
		paramList = list(sorted(set(paramList)))
		self.startParam = paramList[0]
		for p in paramList:
			for v in vtxDict.keys():
				if vtxDict[v] == p:
					vtxList.append(v)
		self.border = vtxList[:]
		cmds.delete(curveNode)
		
		
	def _snapBorderToCurve(self, *args):
		cmds.select(cl = True)
		if len(args):
			cmds.setAttr(self.circleNode + '.radius', args[0])
		loc = cmds.spaceLocator()[0]
		cmds.geometryConstraint(self.constMesh, loc)
		step = 1.0 / len(self.border)
		for i, v in enumerate(self.border):
			param = i * step + self.startParam
			if param > 1:
				param -= 1
			pos = cmds.pointOnCurve(self.circle, pr = param, p = True)
			cmds.setAttr(loc + '.t', pos[0], pos[1], pos[2], type = 'double3')
			pos = cmds.getAttr(loc + '.t')[0]
			cmds.xform(v, ws = True, t = pos)
		cmds.delete(loc)
	
	
	def _cleanup(self):
		cmds.delete(self.constMesh, self.circle)
	
	
	def _showSliderWin(self):
		if cmds.window(self.win, ex = True):
			cmds.deleteUI(self.win)
		if cmds.windowPref(self.win, ex = True):
			cmds.windowPref(self.win, wh = (360, 94))
		
		cmds.window(self.win, t = 'Make Circular Hole', wh = (360, 94))
		cmds.columnLayout(adj = True)
		cmds.separator(style = 'none', h = 5)
		cmds.floatSliderGrp('MakeCircularRadiusSlider', 	l = 'Radius', 
															f = True, 
															v = self.radius, 
															min = self.radius / 2, 
															max = self.radius * 2, 
															cw3 = (80, 50, 100), 
															ct3 = ('left', 'both', 'both'), 
															co3 = (5, 5, 5), 
															dc = partial(self._snapBorderToCurve))
		cmds.checkBoxGrp('MakeCircularFilletCheck', l = 'Create Fillet', 
													v1 = False, 
													cw2 = (80, 50), 
													ct2 = ('left', 'both'), 
													co2 = (5, 5), 
													cc = partial(self._createFillet))
		cmds.floatSliderGrp('MakeCircularFilletSlider',	l = 'Fillet Radius', 
														f = True, 
														v = self.radius / 4.0, 
														min = 0.01, 
														max = self.radius, 
														cw3 = (80, 50, 100), 
														ct3 = ('left', 'both', 'both'), 
														co3 = (5, 5, 5), 
														dc = partial(self._editFillet))
		cmds.separator(style = 'none', h = 5)
		cmds.button(l = 'Close', c = partial(self._closeWindow))
		cmds.setParent('..')
		cmds.showWindow(self.win)
	
	
	def _closeWindow(self, *args):
		cmds.deleteUI(self.win)
		self._cleanup()
	
	
	def _createFillet(self, *args):
		enable = True
		if cmds.checkBoxGrp('MakeCircularFilletCheck', q = True, v1 = True):
			cmds.select(self.faces, r = True)
			self.offset = cmds.polyExtrudeFacet()[0]
			self.extrude = cmds.polyExtrudeFacet()[0]
			self.move = cmds.polyMoveFacet()[0]
			enable = False
			self._editFillet()
		else:
			cmds.delete(self.offset, self.extrude, self.move)
			self.offset = ''
			self.extrude = ''
			self.move = ''
		cmds.floatSliderGrp('MakeCircularRadiusSlider', e = True, en = enable) 
		cmds.select(cl = True)
	
	
	def _editFillet(self, *args):
		if not cmds.checkBoxGrp('MakeCircularFilletCheck', q = True, v1 = True):
			return
		
		value = cmds.floatSliderGrp('MakeCircularFilletSlider', q = True, v = True)
		cmds.setAttr(self.offset + '.offset', value)
		cmds.setAttr(self.move + '.t', self.centerVector[0] * value, self.centerVector[1] * value, self.centerVector[2] * value)
