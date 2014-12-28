import bpy
import bmesh
import mathutils
from fractions import Fraction
import bgl
from bpy_extras.view3d_utils import location_3d_to_region_2d

bl_info = {
    "name": "Edger",
    "author": "Reslav Hollos",
    "version": (0, 2, 4),
    "blender": (2, 72, 0),
    "description": "Lock vertices on \"edge\" they lay, make unselectable edge loops for subdivision",
    "warning": "",
#    "wiki_url": "",
    "category": "Object"
}

#TODO change from groupVerts[group.index] to groupVerts[group] for consistency
#TODO moving and canceling with RMB spawns shadows
#TODO update vertex_groups on ReInit(), delete empty 
#TODO buttons: deselect groups toggle, add to new group, create object without groups, 
#TODO remove empty groups
#TODO detect and remove from groups button

def GetGroupVerts(obj, bm):
    groupVerts = {}
    if obj and bm:
        for g in obj.vertex_groups:
            if g.name.startswith("_edger_"):
                groupVerts[g.index] = []
        
        deform_layer = bm.verts.layers.deform.active
        if deform_layer is None: 
            deform_layer = bm.verts.layers.deform.new()
        
        for v in bm.verts:
            for g in groupVerts:
                if g in v[deform_layer]:
                    groupVerts[g].append(v)
    return groupVerts

def AddNewVertexGroup(name):
    #TODO make check if selected are already part of _edger_ group
    try: bpy.context.object.vertex_groups[groupName]
    except: return bpy.context.object.vertex_groups.new(name)
    return None

def DeselectGroups(groupVerts):
    for g in groupVerts:
        for v in groupVerts[g]:
            try: v.select = False
            except: ReInit()
                
def AdjacentVerts(v, exclude = []):    
    adjacent = []
    for e in v.link_edges:
        if e.other_vert(v) not in exclude:
            adjacent.append(e.other_vert(v))
    return adjacent
        
def GetAdjInfos(groupVerts):
    adjInfos = []
    for g in groupVerts:
        for v in groupVerts[g]:
            adj = AdjacentVerts(v, groupVerts[g])
            if len(adj) is 2:
                aifv = AdjInfoForVertex(v, adj[0], adj[1])
                adjInfos.append(aifv)
    return adjInfos
    
class AdjInfoForVertex(object):
    def __init__(self, target, end1, end2):
        self.target = target
        self.end1 = end1
        self.end2 = end2
        self.UpdateRatio()

    def UpdateRatio(self):
        end1ToTarget = (self.end1.co -self.target.co).length
        end1ToEnd2 = (self.end1.co -self.end2.co).length
        self.ratioToEnd1 = end1ToTarget/end1ToEnd2; #0 is end1, 1 is end2
       
    def LockTargetOnEdge(self):
        # c = a + r(b -a)
        self.target.co = self.end1.co +self.ratioToEnd1*(self.end2.co -self.end1.co)

def LockVertsOnEdge(adjInfos):
    for i in adjInfos:
        i.LockTargetOnEdge()
        
def AddSelectedToGroupIndex(bm, gi):
    deform_layer = bm.verts.layers.deform.active
    if deform_layer is None: 
        deform_layer = bm.verts.layers.deform.new()
    for v in bm.verts:
        if v.select is True:
            v[deform_layer][gi] = 1     #set weight to 1 as usual default

def GetGroupIndexByName(name):
    try: return bpy.context.object.vertex_groups[name].index
    except: return -1 

def draw_callback_px(self, context):
    context.area.tag_redraw()
    
    #sort all groups by adjacent
    verts2d = []
    for v in bm.verts:
        new2dCo = location_3d_to_region_2d(context.region, context.space_data.region_3d, v.co)
        verts2d.append([new2dCo.x,new2dCo.y])
        
    #draw unselectables
    DrawByVertices("points", verts2d, [0.5, 1.0, 0.1, 0.5])
    DrawByVertices("lines", verts2d, [0.5, 0.1, 0.1, 0.5])
    
def DrawByVertices(mode, verts2d, color):
    bgl.glColor4f(*color)
    
    bgl.glEnable(bgl.GL_BLEND)
    
    if mode is "points":
        bgl.glPointSize(5)
        bgl.glBegin(bgl.GL_POINTS)
            
    elif mode is "lines":
        bgl.glLineWidth(2)
        bgl.glBegin(bgl.GL_LINE_LOOP)
    
    for x, y in verts2d:
        bgl.glVertex2f(x, y)

    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)
    #restore defaults
    bgl.glLineWidth(1)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    return

#INIT
def ReInit():
    global obj, me, bm
    global groupVerts, adjInfos
    obj = bpy.context.object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    groupVerts = GetGroupVerts(obj, bm)
    adjInfos = GetAdjInfos(groupVerts)

#has to be global to sustain adjInfos between modal calls :'( sorry global haters )':
isEditMode = False
obj = bpy.context.object
me, bm = None, None
groupVerts = {}     #dict[g.index] = [list, of, vertices]
adjInfos = []
if obj is not None:
    if obj.mode == "EDIT":
        ReInit()
        
bpy.types.Scene.isEdgerActive = bpy.props.BoolProperty(
    name="Active", description="Toggle if Edger is active", default=False)

class LockEdgeLoop(bpy.types.Operator):
    """Lock this edge loop as if it was on flat surface"""
    bl_idname = "wm.lock_edge_loop_idname"
    bl_label = "LockEdgeLoop_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
        obj = context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        name = "_edger_"
        counter = 0
        
        while GetGroupIndexByName(name + "." + str(counter)) >= 0:
            counter += 1
        gi = AddNewVertexGroup(name + "." + str(counter)).index
        AddSelectedToGroupIndex(bm, gi)
        ReInit()
        
        return {'FINISHED'}

class UnselectableVertices(bpy.types.Operator):
    """Make selected vertices unselectable"""
    bl_idname = "wm.unselectable_vertices_idname"
    bl_label = "unselectable_vertices_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
        global obj, me, bm
        name = "_unselectable_"
        gi = GetGroupIndexByName(name)
        if gi < 0:
            gi = AddNewVertexGroup(name).index
        AddSelectedToGroupIndex(bm, gi)

        return {'FINISHED'}
    
'''
class EdgerFunc1(bpy.types.Operator):
    """EdgerFunc1"""
    bl_idname = "wm.edger_func1_idname"
    bl_label = "EdgerFunc1_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
      
        return {'FINISHED'}
'''
class Edger(bpy.types.Operator):
    """Lock vertices on edge"""
    bl_idname = "wm.edger"
    bl_label = "Edger"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    _timer = None
    
    def modal(self, context, event):
        #if event.type == 'ESC':
        #    return self.cancel(context)
        
        if event.type == 'TIMER':
            if context.object is None or \
               context.scene.isEdgerActive is False:
                return {'PASS_THROUGH'}
            
            if context.object.mode == "EDIT":
                global isEditMode
                global obj, me, bm
                global groupVerts, adjInfos
                
                if isEditMode is False:
                    isEditMode = True
                    ReInit()
                DeselectGroups(groupVerts)
                LockVertsOnEdge(adjInfos)
                
                me.update()
                
                # change theme color, silly!
                #color = context.user_preferences.themes[0].view_3d.space.gradients.high_gradient
                #color.s = 1.0
                #color.h += 0.01
            else:
                isEditMode = False

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        return {'CANCELLED'}

#addon_keymaps = []
#def menu_func_edger(self, context): self.layout.operator(Edger.bl_idname)

class EdgerPanel(bpy.types.Panel):
    """Edger Panel"""
    bl_label = "Edger"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'   #TODO
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'isEdgerActive')
        #row = layout.row()
        #row.label(text="Select Edge Loop:")
        split = layout.split()
        col = split.column(align=True)
        col.operator(UnselectableVertices.bl_idname, text="Unselectable", icon = "RESTRICT_SELECT_ON")
        col.operator(LockEdgeLoop.bl_idname, text="Lock Edge Loop", icon = "GROUP_VERTEX")
        row = layout.row()
        #row.label(text="bla bla bla:")
        
#handle the keymap
#wm = bpy.context.window_manager
#km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
#kmi = km.keymap_items.new(UvSquaresByShape.bl_idname, 'E', 'PRESS', alt=True)
#addon_keymaps.append((km, kmi))

def register():
    bpy.utils.register_class(Edger)
    #bpy.utils.register_class(EdgerFunc1)
    bpy.utils.register_class(LockEdgeLoop)
    bpy.utils.register_class(UnselectableVertices)
    bpy.utils.register_class(EdgerPanel)

def unregister():
    bpy.utils.unregister_class(Edger)
    #bpy.utils.unregister_class(EdgerFunc1)
    bpy.utils.unregister_class(LockEdgeLoop)
    bpy.utils.unregister_class(UnselectableVertices)
    bpy.utils.unregister_class(EdgerPanel)

if __name__ == "__main__":
    register()

    # start edger
    bpy.ops.wm.edger()