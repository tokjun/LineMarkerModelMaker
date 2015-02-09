import os
import unittest
import numpy
from __main__ import vtk, qt, ctk, slicer

#
# LineMarkerModelMaker
#

class LineMarkerModelMaker:
  def __init__(self, parent):
    parent.title = "LineMarkerModelMaker" # TODO make this more human readable by adding spaces
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Junichi Tokuda (BWH)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent


#
# qLineMarkerModelMakerWidget
#

class LineMarkerModelMakerWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
    self.logic = LineMarkerModelMakerLogic()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "LineMarkerModelMaker Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Target point (vtkMRMLMarkupsFiducialNode)
    #
    self.SourceSelector = slicer.qMRMLNodeComboBox()
    self.SourceSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.SourceSelector.addEnabled = False
    self.SourceSelector.removeEnabled = False
    self.SourceSelector.noneEnabled = True
    self.SourceSelector.showHidden = False
    self.SourceSelector.renameEnabled = True
    self.SourceSelector.showChildNodeTypes = False
    self.SourceSelector.setMRMLScene( slicer.mrmlScene )
    self.SourceSelector.setToolTip( "Pick up the target point" )
    parametersFormLayout.addRow("Source: ", self.SourceSelector)

    #
    # Target point (vtkMRMLMarkupsFiducialNode)
    #
    self.DestinationSelector = slicer.qMRMLNodeComboBox()
    self.DestinationSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.DestinationSelector.addEnabled = True
    self.DestinationSelector.removeEnabled = False
    self.DestinationSelector.noneEnabled = True
    self.DestinationSelector.showHidden = False
    self.DestinationSelector.renameEnabled = True
    self.DestinationSelector.selectNodeUponCreation = True
    self.DestinationSelector.showChildNodeTypes = False
    self.DestinationSelector.setMRMLScene( slicer.mrmlScene )
    self.DestinationSelector.setToolTip( "Pick up the target point" )
    parametersFormLayout.addRow("Destination: ", self.DestinationSelector)

    #
    # check box to trigger transform conversion
    #
    self.EnableCheckBox = qt.QCheckBox()
    self.EnableCheckBox.checked = 0
    self.EnableCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable", self.EnableCheckBox)

    # connections
    self.EnableCheckBox.connect('toggled(bool)', self.onEnable)
    self.SourceSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.DestinationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)
    
    zframeModel = slicer.vtkMRMLModelNode();
    zframeDisp = slicer.vtkMRMLModelDisplayNode();
    
    slicer.mrmlScene.SaveStateForUndo();
    slicer.mrmlScene.AddNode(zframeDisp);
    slicer.mrmlScene.AddNode(zframeModel);  
    
    zframeDisp.SetScene(slicer.mrmlScene);
    zframeModel.SetScene(slicer.mrmlScene);
    zframeModel.SetAndObserveDisplayNodeID(zframeDisp.GetID());
    zframeModel.SetHideFromEditors(0);
    
    ## in RAS
    modelDimensions = [
      [60.0,-35.0,0.0,0.0,0.0,1.0],
      [60.0,0.0,0.0,0.0,-0.70710678118655,0.70710678118655],
      [60.0,35.0,0.0,0.0,0.0,1.0],
      [35.0,100.0,0.0,0.0,0.0,1.0],
      [0.0,100.0,0.0,0.70710678118655,0.0,0.70710678118655],
      [-35.0,100.0,0.0,0.0,0.0,1.0],
      [-60.0,35.0,0.0,0.0,0.0,1.0],
      [-60.0,0.0,0.0,0.0,0.70710678118655,0.70710678118655],
      [-60.0,-35.0,0.0,0.0,0.0,1.0],
    ]

    length = 60

    N = len(modelDimensions)
    
    default_vec = numpy.array([0.0, 0.0, 1.0])
    default_vec = default_vec/numpy.linalg.norm(default_vec)

    apd = vtk.vtkAppendPolyData()

    for k in range(0,N):
      v = modelDimensions[k]
      # RAS
      pos = [v[0], v[1], v[2]]
      vec = numpy.array([v[3], v[4], v[5]])
      vec = vec/numpy.linalg.norm(vec)
      
      cylinder = vtk.vtkCylinderSource()
      cylinder.SetRadius(1.5)
      cylinder.SetHeight(length)
      cylinder.SetCenter(0, 0, 0)
      cylinder.Update()

      tfilter1 = vtk.vtkTransformPolyDataFilter()
      trans1 = vtk.vtkTransform()
      trans1.RotateX(90.0)
      trans1.Update()
      tfilter1.SetInput(cylinder.GetOutput())
      tfilter1.SetTransform(trans1)
      tfilter1.Update()
      
      tfilter2 = vtk.vtkTransformPolyDataFilter()
      trans2 = vtk.vtkTransform()
      trans2.Translate(pos[0], pos[1], pos[2])

      print default_vec
      print vec
      norm  = numpy.cross(default_vec, vec)
      angle = numpy.arccos(numpy.inner(default_vec, vec))*180.0/numpy.pi
      print norm
      print angle

      trans2.RotateWXYZ(angle, norm[0], norm[1], norm[2])
      trans2.Update()
      tfilter2.SetInput(tfilter1.GetOutput())
      tfilter2.SetTransform(trans2)
      tfilter2.Update()

      apd.AddInput(tfilter2.GetOutput())

    apd.Update()
    zframeModel.SetAndObservePolyData(apd.GetOutput())
    color = [0.0, 0.0, 0.0]
    color[0] = 1.0
    color[1] = 0.5
    color[2] = 0.0

    zframeDisp.SetPolyData(zframeModel.GetPolyData())
    zframeDisp.SetColor(color)



  def cleanup(self):
    pass

  def onEnable(self, state):
    print ("onEnable() is called ")
    if (state == True and self.SourceSelector.currentNode() != None and self.DestinationSelector.currentNode() != None):
      self.logic.activateEvent(self.SourceSelector.currentNode(), self.DestinationSelector.currentNode())
    else:
      self.logic.deactivateEvent()
      self.EnableCheckBox.setCheckState(False)

  def onSelect(self):
    if (self.SourceSelector.currentNode() == None or self.DestinationSelector.currentNode() == None):
      self.logic.deactivateEvent()
      self.EnableCheckBox.setCheckState(False)

  def onReload(self,moduleName="LineMarkerModelMaker"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)


#
# LineMarkerModelMakerLogic
#

class LineMarkerModelMakerLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    self.SourceTransformNode = None
    self.DestinationTransformNode = None
    self.tag = 0

  def convertTransform(self, caller, event):
    if (caller.IsA('vtkMRMLLinearTransformNode') and event == 'ModifiedEvent'):
      src = self.SourceTransformNode.GetMatrixTransformToParent()
      dest = self.DestinationTransformNode.GetMatrixTransformToParent()

      matrix = vtk.vtkMatrix4x4()
      matrix.DeepCopy(dest)
      matrix.SetElement(0, 3, src.GetElement(0,3)) 
      matrix.SetElement(1, 3, src.GetElement(1,3))
      matrix.SetElement(2, 3, src.GetElement(2,3))
      dest.DeepCopy(matrix)
      
  def activateEvent(self, srcNode, destNode):
    if (srcNode and destNode):
      self.SourceTransformNode = srcNode
      self.DestinationTransformNode = destNode
      self.tag = self.SourceTransformNode.AddObserver('ModifiedEvent', self.convertTransform)

  def deactivateEvent(self):
    if (self.SourceTransformNode):
      self.SourceTransformNode.RemoveObserver(self.tag)
      self.SourceTransformNode = None
      self.DestinationTransformNode = None

