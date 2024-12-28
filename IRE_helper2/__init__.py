import bpy
import bmesh
from mathutils import Vector, Matrix
import numpy as np # type: ignore


# ctl + shift + p to popen actions on CS code 




# Global Properties for the checkboxs 
class IREAddonGlobalProperties(bpy.types.PropertyGroup):
    export_animations: bpy.props.BoolProperty(
        name="Export Animations",
        description="Enable animations during GLTF export",
        default=False
    ) # type: ignore
    export_scene: bpy.props.BoolProperty(
        name="Export Entire Scene",
        description="Export the entire scene instead of only selected objects when exporting",
        default=False
    ) # type: ignore


  
 # make selected meshes "mesh" colliders    


# make a mesh a collider 
class OBJECT_OT_parent_to_empty_with_properties(bpy.types.Operator):
    #main button that  triggers everything below 
    bl_idname = "object.parent_to_empty_with_properties"
    bl_label = "Make selected mesh a collider"
    bl_description= ("makes the currently selected meshes magically turn into colliders. \n "
                     "it will appear to you as a wireframe but invisible in iRE")
    bl_options = {'REGISTER', 'UNDO'}
    
     # Set custom properties for the empty object they throw up an error in IDE buts its cool 
     # may need to be updated as as iRE is updated 
    empty_prop1: bpy.props.StringProperty(name="EE Rigidbody Type", default="fixed") # type: ignore
    empty_prop2: bpy.props.StringProperty(name="Entity", default="base") # type: ignore
    # Set custom properties for the child objects
    child_prop1: bpy.props.StringProperty(name="EE Collider Shape", default="mesh") # type: ignore
    child_prop2: bpy.props.StringProperty(name="Entity", default="Mesh Collider") # type: ignore
    
    def execute(self, context):
        #main logic 
        selected_objects = context.selected_objects
        # checks for nothing selected if true it stops  could be updated to also trigger for emptyies and stuff we dont want
        if not selected_objects:
            self.report({'WARNING'}, " select collision meshes silly goose ಠ__ಠ")
            return {'CANCELLED'}
        if any(obj.type != 'MESH' for obj in selected_objects):
            self.report({'WARNING'}, "Select meshes only, silly goose! ಠ__ಠ")
            return {'CANCELLED'}
        
 
       
        # Ensure a "colliders collection exists  
        if "colliders" not in bpy.data.collections:
            colliders_collection = bpy.data.collections.new("colliders")
            context.scene.collection.children.link(colliders_collection)
        else:
            colliders_collection = bpy.data.collections["colliders"]   
        # Check if a "base" an empty obj already exists, or create it
        base_empty = None
        for obj in colliders_collection.objects:
            if obj.type == 'EMPTY' and obj.name == "base":
                
                base_empty = obj
                break    
        if not base_empty:
            # Create a new empty object at the world origin
            base_empty = bpy.data.objects.new("base", None)
            context.scene.collection.objects.link(base_empty)
            # Set custom properties for the empty object
            base_empty["xrengine.EE_rigidbody.type"] = self.empty_prop1
            base_empty["xrengine.entity"] = self.empty_prop2
            # Move the empty to the colliders collection
            colliders_collection.objects.link(base_empty)
            context.scene.collection.objects.unlink(base_empty)


                     
        # Create an empty object at world orgin per the requirment in iRE
        
        
        for obj in selected_objects:
            # loops through all selected objects 
            obj.parent = base_empty
            obj.matrix_parent_inverse = base_empty.matrix_world.inverted()
            # Set custom properties for the child objects
            obj["xrengine.EE_collider.shape"] = self.child_prop1
            obj["xrengine.entity"] = self.child_prop2
            # adds "Collider" in each objects name
            obj.name = f"{obj.name}-Collider"
            #colliders_collection.objects.link(obj)
            #context.collection.objects.unlink(obj)
            
            # makes the mesh a wire type for visual pleasure 
            obj.display_type = 'WIRE'

                
       
                
        #add the empty as an active object to make exporting easier  
        self.report({'INFO'}, "its a collider now ╭( ･ㅂ･)وWhoooo") 
        context.view_layer.objects.active = base_empty
        base_empty.select_set(True)    
       
        


        
        return {'FINISHED'}



#  GLTF Export
class OBJECT_ire_combatable_gltf_export(bpy.types.Operator):
    bl_idname = "object.ire_combatable_gltf_export"
    bl_label = "IRE Compatible GLTF Export"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = (
        "Exports the scene or just the selected objects as a GLTF file compatible with the Ire engine.\n"
        "this is package all mats and colliders within one file.\n "
        "does not support lights, media or HDRIs")
   # @classmethod
    #def description():
     #return "Exports the selected objects or entire scene as a GLTF file compatible with the Ire engine."

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # type: ignore

    def execute(self, context):
        print("Exporting...")
        self.report({'INFO'}, "Exporting ")
        props = context.scene.ire_addon_global_props
        export_animations = props.export_animations
        export_scene = props.export_scene

        # Determine selection behavior based on export_scene
        if export_scene:
            bpy.ops.object.select_all(action='SELECT')  # Select all objects
            self.report({'INFO'}, "Exporting entire scene")
        else:
            #bpy.ops.object.select_all(action='DESELECT')  # Deselect all
            #for obj in context.selected_objects:
            #    obj.select_set(True)
            self.report({'INFO'}, "Exporting selected objects only")

        # Check if there are any selectable objects
        if not context.selectable_objects:
            self.report({'WARNING'}, "No objects to export")
            return {'CANCELLED'}

        # Create or link to colliders collection
        if "colliders" not in bpy.data.collections:
            collider_collection = bpy.data.collections.new("colliders")
            context.scene.collection.children.link(collider_collection)
        else:
            collider_collection = bpy.data.collections["colliders"]

        print(f"Export Animations: {export_animations}, Export Scene: {export_scene}")

        # Export as GLTF
        bpy.ops.export_scene.gltf(
            filepath=self.filepath,
            export_format='GLB',
            export_texture_dir="textures",
            check_existing=False,
            export_texcoords=True,
            export_normals=True,
            export_apply=True,
            export_materials='EXPORT',
            use_selection=True,  
            export_animations=export_animations,
            export_skins=False,
            export_morph=False,
            export_extras=True,
            #object_types={'EMPTY','MESH', 'OTHER'},
            #bake_anim = True,
           # bake_anim_use_nla_strips = True,
            #use_custom_props = True,
            
            
                  #add other export Varibales here https://docs.blender.org/api/current/bpy.ops.export_scene.html
        )

        self.report({'INFO'}, f"Exported to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# create Object bounding box

class OBJECT_OT_create_OBB(bpy.types.Operator):
    # button that  triggers everything below 
    bl_idname = "object.create_obb"
    bl_label = "Create a bounding box around a mesh"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description= ("click this button to make the math wizard fly down and sprinkle some dust on your \n"
                     "mesh and create a bounding box around that mesh with all the iRE fixinings to make it into a collider \n"
                     "watch out he's not great all the time! the bounding box will appear in wireframe but will not be visible in iRE")
    empty_prop1: bpy.props.StringProperty(name="EE Rigidbody Type", default="fixed") # type: ignore
    empty_prop2: bpy.props.StringProperty(name="Entity", default="base") # type: ignore
    # most of this is from an EE blender File author unknown but really into music 
    #changes include making each selected mesh get a bounding box and making variable combatible with add on 
    def execute(self, context):
        selected_objects = context.selected_objects
        print("button pressed ")
        selected_objects = context.selected_objects
        # check for nothing selected if true it stops  could be updated to also trigger for emptyies and stuff we dont want
        if not selected_objects:
            self.report({'WARNING'}, " select collision meshes silly goose ʕっ•ᴥ•ʔっ")
            return {'CANCELLED'}
        if any(obj.type != 'MESH' for obj in selected_objects):
            self.report({'WARNING'}, "Select meshes only, silly goose!ʕっ•ᴥ•ʔっ")
            return {'CANCELLED'}
    
        
        if "colliders" not in bpy.data.collections:
            colliders_collection = bpy.data.collections.new("colliders")
            context.scene.collection.children.link(colliders_collection)
        else:
            colliders_collection = bpy.data.collections["colliders"] 
        #Check if a "base" empty already exists, or create it
        base_empty = None
        for obj in colliders_collection.objects:
            if obj.type == 'EMPTY' and obj.name == "base":
                base_empty = obj
                break

        if not base_empty:
            # Create a new empty object at the world origin
            base_empty = bpy.data.objects.new("base", None)
            context.scene.collection.objects.link(base_empty)
            # Set custom properties for the empty object
            base_empty["xrengine.EE_rigidbody.type"] = self.empty_prop1
            base_empty["xrengine.entity"] = self.empty_prop2
            # Move the empty to the colliders collection
            colliders_collection.objects.link(base_empty)
            context.scene.collection.objects.unlink(base_empty)

     

        for obj in bpy.context.selected_objects:
            # Parent to the "base" empty
            #obj.parent = base_empty
            #obj.matrix_parent_inverse = base_empty.matrix_world.inverted()

            if bpy.context.object.type == 'MESH':
                #obj = bpy.context.object
                mw = obj.matrix_world  # World matrix, for global coordinates

                # Get the vertices, baby
                verts = [mw @ v.co for v in obj.data.vertices]

                # Turn that list into a numpy array so we can get mathematical
                verts_np = np.array([[v.x, v.y, v.z] for v in verts])

                # We use PCA to find the orientation of our mesh, getting into the groove
                mean = np.mean(verts_np, axis=0)
                verts_centered = verts_np - mean
                u, s, vh = np.linalg.svd(verts_centered, full_matrices=False)
                
                # vh now holds the principal components, the dance moves of our bounding box
                
                # Transform the vertices into the PCA coordinate system
                verts_transformed = np.dot(verts_centered, vh.T)
                
                # Find the min and max along each principal axis to determine the bounds
                min_box = np.min(verts_transformed, axis=0)
                max_box = np.max(verts_transformed, axis=0)
                center_box = (min_box + max_box) / 2
                
                # Bring our bounding box back into the world space, reversing the PCA transformation
                center_world = mean + np.dot(center_box, vh)
                
                # Create a new cube for the bounding box
                bpy.ops.mesh.primitive_cube_add(location=center_world)
                bounding_box = bpy.context.object
                bounding_box.name = 'PCA_OBB'
                   # makes the mesh a wire type for visual pleasure 
                bounding_box.display_type = 'WIRE'

                # Scale the box to match our min and max bounds, corrected to handle type properly
                scale = (max_box - min_box) / 2
                # Directly use the scale values for Blender without numpy operations for this part
                

                # Adjusting the orientation by directly setting the matrix
                # We construct a 4x4 matrix from the vh (principal components), ensuring it affects rotation only
                rotation_matrix = Matrix.Identity(4)  # Start with an identity matrix
                for i in range(3):  # For each principal component
                    for j in range(3):  # For each dimension
                        rotation_matrix[i][j] = vh[j][i]  # Transpose vh into the rotation matrix

                # Apply the rotation to the bounding box by combining it with the existing location
                bounding_box.matrix_world = Matrix.Translation(center_world) @ rotation_matrix

                bounding_box.scale.x = scale[0]
                bounding_box.scale.y = scale[1]
                bounding_box.scale.z = scale[2]
                
                obb_name = f"{obj.name}_Box"
                bounding_box.name = obb_name  # Name the OBB
                
                # Set custom properties SUBJECT TO CHANGE
                bounding_box["xrengine.entity"] = obb_name
                bounding_box["xrengine.EE_collider.shape"] = "box"
                bounding_box.parent = base_empty
                bounding_box.matrix_parent_inverse = base_empty.matrix_world.inverted()

                colliders_collection.objects.link(bounding_box)
                context.collection.objects.unlink(bounding_box)
                # some olde code from the Mysertery EE person who made this 
                #if obj.parent:
                    #   bounding_box.parent = obj.parent
                    # To keep the world transform, first apply the current transformation
                    # Then reset its local transform
                    #  current_location, current_rotation, current_scale = bounding_box.matrix_world.decompose()
                    
                    # Set the OBB's transform to match the world transform, but relative to the new parent
                    # bounding_box.matrix_parent_inverse = obj.parent.matrix_world.inverted()
                    #bounding_box.location = current_location
                    #bounding_box.rotation_euler = current_rotation.to_euler()
                    #bounding_box.scale = current_scale
                    
                    # Assuming 'bounding_box' is your OBB and 'obj' is your mesh
                    # Let's move the OBB to the same collection as the mesh
                    # if obj.users_collection:  # Check if the mesh is in any collection
                        #collection = obj.users_collection[0]  # Get the first collection containing the mesh
                        #collection.objects.link(bounding_box)  # Add the OBB to this collection

                        # To keep things clean, we also might want to unlink the OBB from its original collection if necessary
                        # for coll in bounding_box.users_collection:
                            #if coll != collection:
                            #    coll.objects.unlink(bounding_box)


                self.report({'INFO'}, "The OBB is grooving with your mesh, all aligned and smooth!")
            else:
                self.report({'WARNING'},("Hey now, you need to select a mesh to find its rhythm!"))
    
                
       
        return {'FINISHED'}
          






#panel window 

class VIEW3D_PT_custom_properties_panel(bpy.types.Panel):
    #panel layout
    bl_label = "IRE Helper "
    bl_idname = "VIEW3D_PT_custom_properties_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IRE helper'
    
    def draw(self, context):
        
        #panel layout butons and silly little art at the bottom 
        
        
        layout = self.layout
        props = context.scene.ire_addon_global_props
        layout.label(text="IRE Helper", icon='OUTLINER_DATA_META')
        #first button 
        layout.operator("object.create_obb", icon='EVENT_B')
        
        
        layout.operator("object.parent_to_empty_with_properties",icon= 'EVENT_C')
        
        #single row 
        row = layout.row()
        
        # add two columns 
        col1 = row.column()
        col2 = row.column()
        # Place the checkboxes in the columns
        col1.prop(props, "export_animations", text="Export Animations")
        col2.prop(props, "export_scene", text="Export Scene")
        
        
        
        # Add checkbox for animation export
       # layout.prop(props, "export_animations", text="Export Animations")
        #layout.prop(props, "export_scene", text="Export scene")
        
        layout.operator("object.ire_combatable_gltf_export", icon='EVENT_E')
        #placement for the checkbox
        


        # Add button for GLTF export
        #layout.operator("object.ire_combatable_gltf_export", text="Export GLTF")
        
        ascii_art = [   r"""(づ｡◕‿‿◕｡) づ
                  
                    
                            """  ]
             
                  
        
        

        for line in ascii_art:
            layout.label(text=line)
        
# Register and un register classes  
classes = (
    IREAddonGlobalProperties,
    OBJECT_OT_create_OBB,
    OBJECT_OT_parent_to_empty_with_properties,
    OBJECT_ire_combatable_gltf_export,
    VIEW3D_PT_custom_properties_panel,
)

def register():
    
    #bpy.utils.register_class(OBJECT_OT_create_OBB)
    
    #bpy.utils.register_class(OBJECT_OT_parent_to_empty_with_properties)

    #bpy.utils.register_class(OBJECT_ire_combatable_gltf_export)
    #bpy.utils.register_class(VIEW3D_PT_custom_properties_panel)
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # after some troubleshooting this lil punk needs to be here too to help set up the     
    bpy.types.Scene.ire_addon_global_props = bpy.props.PointerProperty(type=IREAddonGlobalProperties)

    
   

def unregister():
   # bpy.utils.unregister_class(OBJECT_OT_create_OBB)
    #bpy.utils.unregister_class(OBJECT_OT_parent_to_empty_with_properties)
    #bpy.utils.unregister_class(OBJECT_ire_combatable_gltf_export)
    #bpy.utils.unregister_class(VIEW3D_PT_custom_properties_panel)  
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()