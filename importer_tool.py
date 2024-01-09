import unreal
from pathlib import Path

DESTINATION_PATH = "/Game/TestingImport"
BASE_MATERIAL_PATH = "/Game/TavernAssets"

def testowanie(directory_path):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path("/Game/TavernAssets", True, False)
    for asset_data in assets:
        asset = asset_data.get_asset()
        if isinstance(asset, unreal.Material) and asset.get_full_name().rsplit('.', 2)[1] == "M_AssetsMasterMaterial":
            new_parent = asset

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    package_name, asset_name = asset_tools.create_unique_asset_name("/Game/TavernAssets", '')
    unreal.log(package_name)
    unreal.log(asset_name)
    #if not unreal.EditorAssetLibrary.does_asset_exist(package_name):
    #    instance = asset_tools.create_asset("MI_test", "/Game/TavernAssets", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())

    #unreal.MaterialEditingLibrary.set_material_instance_parent(instance, new_parent)


    #instance = unreal.MaterialInstance()
    #instance.set_editor_property("parent", )


def batch_import(directory_path):
    unreal.log(directory_path)

    i = 0
    SOURCE_DIR = Path(directory_path)
    for file_path in SOURCE_DIR.iterdir():
        dir_name = file_path.stem

        if file_path.is_dir() and dir_name[0] == 'T' and dir_name[1] == 'P':
            #checking if all resources exist
            mesh_path = get_mesh_path(file_path)
            color_tex_path = get_texture_path(file_path, 'BaseColor')
            normal_tex_path = get_texture_path(file_path, 'Normal')
            ORM_tex_path = get_texture_path(file_path, 'OcclusionRoughnessMetallic')
            
            if (mesh_path is not None and
                color_tex_path is not None and
                normal_tex_path is not None and
                ORM_tex_path is not None):

                #importing assets
                import_asset(mesh_path, dir_name) #directory name is the same like model name
                import_asset(color_tex_path, dir_name)
                import_asset(normal_tex_path, dir_name)
                import_asset(ORM_tex_path, dir_name)

                #setting up material instance
                #set_texture_properties(dir_name)
                material_instance = create_material_instance(dir_name)
                set_up_instance(material_instance)
                i = i + 1
                if i > 2:
                    return
            

def get_mesh_path(directory_path):
    for file_path in directory_path.iterdir():
        if file_path.suffix == '.fbx' and directory_path.parts[-1] == file_path.stem:
            return file_path

def get_texture_path(directory_path, type):
    asset_code = directory_path.parts[-1].split('_')[0]
    
    for file_path in directory_path.iterdir():
        if file_path.stem == 'textures_UE':
            for tex_path in file_path.iterdir():
                if (tex_path.suffix == '.png' and
                    tex_path.stem.split('_')[0] == asset_code and
                    tex_path.stem.split('_')[1] == type):
                    return tex_path
                
def import_asset(asset_path, model_name):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    task = unreal.AssetImportTask()
    task.automated = True
    task.destination_path = DESTINATION_PATH + '/' + model_name
    task.filename = str(asset_path)
    task.replace_existing = True
    task.save = True

    asset_tools.import_asset_tasks([task])

def set_texture_properties(model_name):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path(DESTINATION_PATH + '/' + model_name)
    for asset in assets:
        texture = asset.get_asset()
        if isinstance(texture, unreal.Texture):
            if texture.get_full_name().split('_')[-1] == 'OcclusionRoughnessMetallic':
                texture.compression_settings = unreal.TextureCompressionSettings.TC_MASKS
                unreal.log("setting compression")
            texture.set_editor_property("virtual_texture_streaming", False)
            unreal.log("setting streaming")

def create_material_instance(model_name):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path(BASE_MATERIAL_PATH, True, False)
    for asset_data in assets:
        asset = asset_data.get_asset()
        if isinstance(asset, unreal.Material) and asset.get_full_name().rsplit('.', 2)[1] == "M_AssetsMasterMaterial":
            new_parent = asset

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    package_name, asset_name = asset_tools.create_unique_asset_name(DESTINATION_PATH, '')
    if not unreal.EditorAssetLibrary.does_asset_exist(package_name):
        path = DESTINATION_PATH + '/' + model_name
        name = "MI_" + model_name
        instance = asset_tools.create_asset(name, path, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())

    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, new_parent)

    return instance

def set_up_instance (instance):
    unreal.log("setting")
            

