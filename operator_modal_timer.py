import bpy
bl_info = {
    "name": "Edger",
    "author": "Reslav Hollos",
    "version": (0, 1),
    "blender": (2, 72, 0),
    "description": "Lock vertices on \"edge\" they lay, make unselectable edge loops for subdivision",
    "warning": "",
#    "wiki_url": "",
    "category": "Object"
}

def AddVertexGroup(name, addSelected = True):
    bpy.ops.object.vertex_group_add()
    
class EdgerFunc1(bpy.types.Operator):
    """EdgerFunc1"""
    bl_idname = "wm.edger_func1_idname"
    bl_label = "EdgerFunc1_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
        AddVertexGroup("asd")
        
        return {'FINISHED'}
    
class Edger(bpy.types.Operator):
    """Lock vertices on edge"""
    bl_idname = "wm.edger"
    bl_label = "Edger"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    _timer = None

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            for g in context.object.vertex_groups:
                if g.name.startswith("_edger_"):
                    print(dir(g))
                    #g.vertex_group_assign()
            
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