bl_info = {
    "name": "Voxelator",
    "author": "15shekels aka derpy.radio aka TITANDERP aka Ivan",
    "version": (1, 2, 1),
    "blender": (2, 93, 4),
    "location": "View3D > Object",
    "description": "Converts any mesh into a voxelized mesh made up by cubes",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}


import bpy
from bpy.props import (
    IntProperty,
    BoolProperty
)
from bpy.types import (
    AddonPreferences,
    Operator,
    Panel,
    PropertyGroup
)

class OBJECT_OT_voxelize(Operator):
    bl_label = "Voxelate"
    bl_idname = "object.voxelize"
    bl_description = "Converts any mesh into a voxelized mesh made up by cubes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'REGISTER', 'UNDO'}
    
    voxelizeResolution: bpy.props.IntProperty(
        name = "Voxel Resolution",
        default = 16,
        min = 1,
        max = 250,
        description = "Maximum amount of cubes used per axis of mesh. *warning*: amounts higher than 32 can result in long load times during voxelization.",
    )
    
    fill_volume: bpy.props.BoolProperty(
        name="Fill Volume",
        description="Fill the inside of the voxelized mesh with cubes as well.",
        default = False
    )
    separate_cubes: bpy.props.BoolProperty(
        name="Separate Cubes",
        description="Keep cubes as separate meshes inside the same object.",
        default = False
    )
    
    @classmethod
    def poll(cls, context):
        return context.object.select_get() and context.object.type == 'MESH' or context.object.type == 'CURVE'
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):

        #set selected object as source
        source_name = bpy.context.object.name
        source = bpy.data.objects[source_name]

        #create copy of object to perform 
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})
        bpy.context.object.name = source_name + "_voxelized"
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        #hide the original object
        source.hide_set(True)

        #rename the duplicated mesh
        target_name = bpy.context.object.name
        target = bpy.data.objects[target_name]

        #create cube to be used for voxels
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "voxel_cube"

        #decide cube size based on resolution and size of original mesh
        cube_size = max(target.dimensions) / (self.voxelizeResolution*2)

        #apply cube particles to duplicated mesh to create voxels
        target.modifiers.new(name='voxel system',type='PARTICLE_SYSTEM')
        target_ps_settings = target.particle_systems[0].settings
        target_ps_settings.count = 1
        target_ps_settings.frame_end = 1
        target_ps_settings.lifetime = 1
        if self.fill_volume == True:
            target_ps_settings.emit_from = 'VOLUME'
        if self.fill_volume == False:
            target_ps_settings.emit_from = 'FACE'
        target_ps_settings.distribution = 'GRID'
        target_ps_settings.grid_resolution = self.voxelizeResolution
        target_ps_settings.render_type = 'OBJECT'
        target_ps_settings.instance_object = bpy.data.objects["voxel_cube"]
        target_ps_settings.use_scale_instance = False
        target_ps_settings.show_unborn = True
        target_ps_settings.use_dead = True
        target_ps_settings.particle_size = cube_size

        bpy.context.scene.objects["voxel_cube"].select_set(False)
        bpy.context.scene.objects[target_name].select_set(True)

        #create cubes from the particles
        bpy.ops.object.duplicates_make_real()

        #remove the duplicated mesh, leaving behind the voxelized mesh
        bpy.data.objects.remove(bpy.data.objects[target_name], do_unlink=True)
        #delete the original cube particle
        bpy.data.objects.remove(bpy.data.objects["voxel_cube"], do_unlink=True)

        #make one of the cubes selected active
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

        #join the cubes into a single mesh
        bpy.ops.object.join()

        bpy.context.object.name = source_name + "_voxel_mesh"
        
        #join cubes together by vertice
        bpy.ops.object.editmode_toggle()
        if self.separate_cubes == False:
            bpy.ops.mesh.remove_doubles()
        bpy.ops.object.editmode_toggle()
        
        #transfer the uv map from the source object to the new cube mesh
        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        bpy.context.object.modifiers["DataTransfer"].use_loop_data = True
        bpy.context.object.modifiers["DataTransfer"].data_types_loops = {'UV'}
        bpy.context.object.modifiers["DataTransfer"].loop_mapping = 'POLYINTERP_NEAREST'
        bpy.context.object.modifiers["DataTransfer"].object = source
        bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
        bpy.ops.object.modifier_apply(modifier="DataTransfer")

        #make sure each cube is exactly scaled to 1m
        resize_value = 1 / (max(bpy.context.object.dimensions) / self.voxelizeResolution)
        bpy.ops.transform.resize(value=(resize_value, resize_value, resize_value))

        #copy material from source object to cube mesh
        bpy.context.object.active_material = source.active_material

        #shrink uvs so each face is filled with one color
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.context.area.ui_type = 'UV'
        bpy.context.scene.tool_settings.use_uv_select_sync = False
        bpy.context.space_data.uv_editor.sticky_select_mode = 'DISABLED'
        bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
        bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy.ops.mesh.select_all(action='DESELECT')

        count = 0
        while count < 100:
            bpy.ops.mesh.select_random(ratio=count*.01 + .01, seed=count)
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.transform.resize(value=(0.00001, 0.00001, 0.00001))
            bpy.ops.mesh.hide(unselected=False)

            count+=1

        #revert ui areas
        bpy.context.area.ui_type = 'VIEW_3D'
        bpy.ops.mesh.reveal()
        bpy.context.area.ui_type = 'VIEW_3D'

        bpy.ops.object.editmode_toggle()

        #make sure new model is centered
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.context.object.location[2] = 0

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_voxelize.bl_idname)
    
def register():
    bpy.utils.register_class(OBJECT_OT_voxelize)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_voxelize)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    
if __name__ == "__main__":
    register()
    
