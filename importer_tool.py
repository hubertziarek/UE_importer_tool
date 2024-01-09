import unreal
from pathlib import Path

DESTINATION_PATH = "/Game/TestingImport"
BASE_MATERIAL_PATH = "/Game/TavernAssets"
SAVE_FREQ = 5 #save after each N models

#directory path is the source path on the disk
def batch_import(directory_path):
    num_models_to_save = 0
    SOURCE_DIR = Path(directory_path)
    for file_path in SOURCE_DIR.iterdir():
        dir_name = file_path.stem

        if file_path.is_dir() and dir_name[0] == 'T' and dir_name[1] == 'P':
            #finding paths for all assets related to the importing model
            mesh_path = get_mesh_path(file_path)
            color_tex_path = get_texture_path(file_path, 'BaseColor')
            normal_tex_path = get_texture_path(file_path, 'Normal')
            ORM_tex_path = get_texture_path(file_path, 'OcclusionRoughnessMetallic')
            
            #checking if all assets exist
            if (mesh_path is not None and
                color_tex_path is not None and
                normal_tex_path is not None and
                ORM_tex_path is not None):

                #importing assets
                import_asset(mesh_path, dir_name) #directory name (dir_name) is the same like model name
                import_asset(color_tex_path, dir_name)
                import_asset(normal_tex_path, dir_name)
                import_asset(ORM_tex_path, dir_name)

                #setting up material instance and assigning it to the mesh
                material_instance = create_material_instance(dir_name)
                set_up_instance(material_instance, dir_name)
                set_up_mesh_material(material_instance, dir_name)
                
                #saving
                num_models_to_save += 1
                if num_models_to_save >= SAVE_FREQ:
                    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(False, True)
                    num_models_to_save = 0

    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(False, True)
                
def get_mesh_path(directory_path):
    for file_path in directory_path.iterdir():
        #we're searching for the fbx file whose name is the same as the name of the currently checking directory
        if file_path.suffix == '.fbx' and directory_path.parts[-1] == file_path.stem:
            return file_path

#texture texture: BaseColor, Normal, OcclusionRoughnessMetallic
def get_texture_path(directory_path, texture_type):
    model_code = directory_path.parts[-1].split('_')[0]
    
    for file_path in directory_path.iterdir():
        #moving to the directory with Unreal versions of the textures
        if file_path.stem == 'textures_UE':
            for tex_path in file_path.iterdir():
                #we're searching for the png file whose name contains the model code and the correct texture type
                if (tex_path.suffix == '.png' and
                    tex_path.stem.split('_')[0] == model_code and
                    tex_path.stem.split('_')[1] == texture_type):
                    return tex_path
                
def import_asset(asset_path, model_name):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    task = unreal.AssetImportTask()
    task.automated = True
    task.destination_path = DESTINATION_PATH + '/' + model_name
    task.filename = str(asset_path)
    task.replace_existing = True
    task.save = False

    asset_tools.import_asset_tasks([task])

def create_material_instance(model_name):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    package_name, asset_name = asset_tools.create_unique_asset_name(DESTINATION_PATH, '')
    if not unreal.EditorAssetLibrary.does_asset_exist(package_name):
        path = DESTINATION_PATH + '/' + model_name
        name = "MI_" + model_name
        instance = asset_tools.create_asset(name, path, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        return instance
    
def set_up_instance(material_instance, model_name):
    #setting up master material as a parent for the instance
    asset = unreal.EditorAssetLibrary.find_asset_data(BASE_MATERIAL_PATH + "/M_AssetsMasterMaterial")
    master_material = asset.get_asset()
    if isinstance(master_material, unreal.Material):
        unreal.MaterialEditingLibrary.set_material_instance_parent(material_instance, master_material)

    #setting up textures as parameters of the material instance
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path(DESTINATION_PATH + '/' + model_name)
    for asset in assets:
        texture = asset.get_asset()
        if isinstance(texture, unreal.Texture):
            texture.set_editor_property("virtual_texture_streaming", False)
            
            if texture.get_full_name().split('_')[-1] == 'BaseColor':
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, "ColorMap", texture)

            if texture.get_full_name().split('_')[-1] == 'Normal':
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, "NormalMap", texture)

            if texture.get_full_name().split('_')[-1] == 'OcclusionRoughnessMetallic':
                texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, "OcclusionRoughnessMetallic", texture)
    
def set_up_mesh_material(material_instance, model_name):
    asset = unreal.EditorAssetLibrary.find_asset_data(DESTINATION_PATH + '/' + model_name + '/' + model_name)
    mesh = asset.get_asset()
    if isinstance(mesh, unreal.StaticMesh):
        mesh.set_material(0, material_instance)
            

