import os
import copy
import openmc
import numpy as np

def summarize_simple_tok_statepoint(sp_path):
    sp = openmc.StatePoint(sp_path)
    transport_time = sp.runtime['transport']
    tally = sp.get_tally(id=44)
    means = tally.get_values(value='mean').ravel()
    means_safe = np.where(means == 0, 1.0, means)
    sigmas = tally.get_values(value='std_dev').ravel()
    sigmas_safe = np.where(sigmas == 0, 1.0, sigmas)
    
    avg_rel_sigma = np.mean(sigmas_safe / means_safe)
    max_rel_sigma = np.max(sigmas_safe / means_safe)
    figure_of_merit = 1 / (avg_rel_sigma**2 * transport_time)

    results = {}
    results['transport_time'] = transport_time
    results['avg_rel_sigma'] = avg_rel_sigma
    results['max_rel_sigma'] = max_rel_sigma
    results['figure_of_merit'] = figure_of_merit

    return results

def run_simple_tok():

    #---------------------------
    # run_random_ray calculation
    #---------------------------

    orig_dir = os.getcwd()
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(SCRIPT_DIR)

    geometry = openmc.Geometry.from_xml("geometry.xml")
    materials = openmc.Materials.from_xml("materials.xml")
    settings = openmc.Settings.from_xml("settings.xml")
    tallies = openmc.Tallies.from_xml("tallies.xml")
    model = openmc.Model(geometry = geometry, materials = materials, settings = settings, tallies = tallies)
    model.settings.photon_transport   = False
    model.settings.electron_transport = False
    model.settings.positron_transport = False

    reflective_face_1 = model.geometry.get_all_surfaces()[10000]
    reflective_face_2 = model.geometry.get_all_surfaces()[11000]

    vac_zmax = openmc.ZPlane(z0=  1000, boundary_type='vacuum')
    vac_zmin = openmc.ZPlane(z0= -1000, boundary_type='vacuum')
    vac_ymax = openmc.YPlane(y0=  625, boundary_type='vacuum')
    vac_ymin = openmc.YPlane(y0= -625, boundary_type='vacuum')
    vac_xmax = openmc.XPlane(x0= 1864.0, boundary_type='vacuum')
    vac_xmin = openmc.XPlane(x0= -100.0, boundary_type='vacuum')
                    
    outer_region = (
        -vac_zmax & +vac_zmin &
        -vac_ymax & +vac_ymin &
        -vac_xmax & +vac_xmin &
        +reflective_face_1 & -reflective_face_2
    )

    outer_cell = openmc.Cell(region=outer_region, 
                              fill=model.geometry.root_universe)
    outer_universe  = openmc.Universe(cells=[outer_cell])
    model.geometry.root_universe = outer_universe
    model.geometry.determine_paths()

    random_ray_model = copy.deepcopy(model)
    random_ray_model.tallies = []
    random_ray_model.convert_to_multigroup(
        method = "stochastic_slab",
        nparticles = 10000
    )
    random_ray_model.convert_to_random_ray()  

    lower_left  = (vac_xmin.x0, vac_ymin.y0, vac_zmin.z0)
    upper_right = (vac_xmax.x0, vac_ymax.y0, vac_zmax.z0)
    box_space   = openmc.stats.Box(lower_left, upper_right)

    constraints={}
    constraints['domains'] = [outer_cell]
    random_ray_model.settings.random_ray['ray_source'] = openmc.IndependentSource(space=box_space, 
                                                                                  constraints=constraints)
    
    bbox = random_ray_model.geometry.bounding_box
    mesh = openmc.RegularMesh()
    mesh.lower_left, mesh.upper_right = bbox.lower_left, bbox.upper_right
    mesh.dimension = (100, 100, 100)

    random_ray_model.settings.random_ray["source_region_meshes"] = [(mesh, [outer_cell])]
    random_ray_model.settings.random_ray["distance_inactive"] = 1500.0
    random_ray_model.settings.random_ray["distance_active"] = 3000.0
    random_ray_model.settings.random_ray["sample_method"] = "prng"
    random_ray_model.settings.particles = 30000
    random_ray_model.settings.batches   = 100
    random_ray_model.settings.inactive  = 50

    wwg = openmc.WeightWindowGenerator(
        mesh, method='fw_cadis', max_realizations = random_ray_model.settings.batches)
    random_ray_model.settings.weight_window_generators = [wwg]
    
    # plot = openmc.Plot()
    # plot.origin = bbox.center
    # plot.width = bbox.width
    # plot.pixels = (400, 400, 400)
    # plot.type = 'voxel'
    # random_ray_model.plots = [plot]

    random_ray_model.run(path="random_ray.xml")

    #-------------------
    # run_mc calculation
    #-------------------

    model.settings.weight_window_checkpoints = {"collision": True, "surface"  : True}
    model.settings.survival_biasing = False
    model.settings.weight_windows = openmc.hdf5_to_wws("weight_windows.h5")

    model.settings.particles = 10000
    model.settings.batches   = 25

    model.settings.weight_windows_on = True
    statepoint_name = model.run(path="mc.xml")
    results_with_WW = summarize_simple_tok_statepoint(statepoint_name)

    model.settings.particles = 10000
    model.settings.batches   = 50

    model.settings.weight_windows_on = False
    statepoint_name = model.run(path="mc.xml")
    results_no_WW = summarize_simple_tok_statepoint(statepoint_name)

    os.chdir(orig_dir)

    return results_with_WW, results_no_WW

if __name__ == "__main__":
    run_simple_tok()