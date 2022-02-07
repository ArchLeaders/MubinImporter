#pragma warning disable CS8602

// Satisfy VSCode
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;

using CafeLibrary;
using Toolbox.Core;
using Toolbox.Core.Collada;
using Toolbox.Core.IO;

if (args.Length < 4)
{
    Console.WriteLine("Invalid args. Expected <\"path\\to\\file.sbfres\"> <\"path\\to\\file.Tex1.sbfres\"> <\"folder_name\"> <\"path\\to\\export\\dir\">");
    return;
}

try
{
    await ExtractDae(args[0], args[1], args[2], args[3]);
}
catch (Exception ex)
{
    Console.WriteLine($"{ex.Message}\n{ex.StackTrace}");

    if (Directory.Exists($"{args[3]}\\{args[2]}"))
        Directory.Delete($"{args[3]}\\{args[2]}", true);
}

static async Task ExtractDae(string sbfres, string tex1, string folder, string output)
{
    List<Task> export = new();

    Directory.CreateDirectory($"{output}\\{folder}");

    // Export textures
    if (File.Exists(tex1))
    {
        export.Add(Task.Run(() =>
        {
            var texfile = STFileLoader.OpenFileFormat(tex1);
            var texscene = ((IModelSceneFormat)texfile).ToGeneric();
            foreach (var tex in texscene.Textures)
            {
                tex.Export($"{output}\\{folder}\\{tex.Name}.png",
                    new TextureExportSettings()
                    {
                        ExportArrays = false,
                        ExportMipmaps = false,
                    });
            }
        }));
    }
    else
    {
        Console.WriteLine("The Tex1 file was not found!");
    }

    // Export models
    export.Add(Task.Run(() =>
    {
        var bfres = (BFRES)STFileLoader.OpenFileFormat(sbfres);
        var scene = ((IModelSceneFormat)bfres).ToGeneric();

        foreach (var model in scene.Models)
        {
            DAE.Export($"{output}\\{folder}\\{model.Name}.dae", new DAE.ExportSettings()
            {
                ExportTextures = true,
            }, model, model.GetMappedTextures(), model.Skeleton);
        }
    }));

    await Task.WhenAll(export);
}