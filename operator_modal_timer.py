import bpy
import bmesh
import mathutils
import itertools

bl_info = {
    "name": "Edger",
    "author": "Reslav Hollos",
    "version": (0, 1, 1),
    "blender": (2, 72, 0),
    "description": "Lock vertices on \"edge\" they lay, make unselectable edge loops for subdivision",
    "warning": "",
#    "wiki_url": "",
    "category": "Object"
}
    
def GetGroupVerts():
    groupVerts.clear()
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
                break

def AddVertexGroup(name, addSelected = True):
    bpy.context.scene.objects.active.vertex_groups.new(name)
    return

def DeselectGroups():
    for g in groupVerts:
        for v in groupVerts[g]:
            print(v)
            v.select = False
            
def AdjacentVerts(v):    
    adjacent = []
    for e in v.link_edges:
        adjacent.append(e.other_vert(v))
    return adjacent

def AdjCollinearVertsWith(v):
    adjacent = AdjacentVerts(v)
    subsets = SubsetsOf(adjacent, 2)
    for sub in subsets:
        if AreVertsCollinear(v, sub[0], sub[1]):
            return [sub[0], sub[1]]
    return []
    
def SubsetsOf(S, m):
    return set(itertools.combinations(S, m))
        
def GetAdjInfos():
    adjInfos.clear()
    for g in groupVerts:
        for v in groupVerts[g]:
            adjColl = AdjCollinearVertsWith(v)
            aifv = AdjInfoForVertex(v, adjColl[0], adjColl[1])
            adjInfos.append(aifv)

class EdgerFunc1(bpy.types.Operator):
    """EdgerFunc1"""
    bl_idname = "wm.edger_func1_idname"
    bl_label = "EdgerFunc1_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
        #AddVertexGroup("_edger_")
        #DeselectGroups()
        
        for i in adjInfos:
            i.LockTargetOnEdge()
                
        me.update()
        return {'FINISHED'}

#TODO calculate over slope so it is scale independant
def AreVertsCollinear(a, b, c, allowedError = 0.05):
    area = mathutils.geometry.area_tri(a.co, b.co, c.co)
    # print(area)
    if abs(area) <= allowedError:
        return True
    return False

class AdjInfoForVertex(object):
    def __init__(self, target, end1, end2):
        self.target = target;
        self.end1 = end1;
        self.end2 = end2;
        self.UpdateRatio();

    def UpdateRatio(self):
        end1ToTarget = (self.end1.co -self.target.co).length
        end1ToEnd2 = (self.end1.co -self.end2.co).length
        self.ratio = end1ToTarget/end1ToEnd2; #0 is end1, 1 is end2
    
    def LockTargetOnEdge(self):
        # c = a + r(b -a)
        self.target.co = self.end1.co + self.ratio*(self.end2.co - self.end1.co)

class Edger(bpy.types.Operator):
    """Lock vertices on edge"""
    bl_idname = "wm.edger"
    bl_label = "Edger"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    _timer = None

    groupVerts = {}     #dict[group] = [list, of, vertices]
    adjInfos = []
 
    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            if context.object.mode == "EDIT":
                obj = context.object
                me = obj.data
                bm = bmesh.from_edit_mesh(me)
                
                for i in adjInfos:
                    i.LockTargetOnEdge()
                    
            # change theme color, silly!
            color = context.user_preferences.themes[0].view_3d.space.gradients.high_gradient
            color.s = 1.0
            color.h += 0.01

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
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
        row.label(text="Select Edge Loop:")
        split = layout.split()
        col = split.column(align=True)
        col.operator(Edger.bl_idname, text="Start Edger", icon = "GROUP_VERTEX")
        col.operator(EdgerFunc1.bl_idname, text="Unselectable", icon = "RESTRICT_SELECT_ON")
        row = layout.row()
        row.label(text="bla bla bla:")
        
#handle the keymap
#wm = bpy.context.window_manager
#km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
#kmi = km.keymap_items.new(UvSquaresByShape.bl_idname, 'E', 'PRESS', alt=True)
#addon_keymaps.append((km, kmi))

def register():
    bpy.utils.register_class(Edger)
    bpy.utils.register_class(EdgerFunc1)
    bpy.utils.register_class(EdgerPanel)

def unregister():
    bpy.utils.unregister_class(Edger)
    bpy.utils.unregister_class(EdgerFunc1)
    bpy.utils.unregister_class(EdgerPanel)


if __name__ == "__main__":
    register()

    # start edger
    bpy.ops.wm.edger()