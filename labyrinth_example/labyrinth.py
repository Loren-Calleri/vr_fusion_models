import os
import numpy as np
import openmc
import copy
import subprocess
# from matplotlib import pyplot as plt
# from matplotlib.colors import LogNorm
# import pyvista as pv
# import matplotlib.pyplot as plt
# from IPython.display import Image, display

def run_labyrinth():

    orig_dir = os.getcwd()
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(SCRIPT_DIR)

    mat_air = openmc.Material(name="air")
    mat_air.add_element("N", 0.784431)
    mat_air.add_element("O", 0.210748)
    mat_air.add_element("Ar", 0.0046)
    mat_air.set_density("g/cc", 0.001205)

    mat_concrete = openmc.Material(name='concrete')
    mat_concrete.add_element("H",0.168759)
    mat_concrete.add_element("C",0.001416)
    mat_concrete.add_element("O",0.562524)
    mat_concrete.add_element("Na",0.011838)
    mat_concrete.add_element("Mg",0.0014)
    mat_concrete.add_element("Al",0.021354)
    mat_concrete.add_element("Si",0.204115)
    mat_concrete.add_element("K",0.005656)
    mat_concrete.add_element("Ca",0.018674)
    mat_concrete.add_element("Fe",0.00426)
    mat_concrete.set_density("g/cm3", 2.3)

    materials_continuous_xs = openmc.Materials([mat_air, mat_concrete])

    width_a = 100
    width_b = 100
    width_c = 500
    width_d = 100
    width_e = 100
    width_f = 100
    width_g = 100

    depth_a = 100
    depth_b = 100
    depth_c = 700
    depth_d = 600
    depth_e = 100
    depth_f = 100

    height_j = 100
    height_k = 500
    height_l = 100

    xplane_0 = openmc.XPlane(x0=0, boundary_type="vacuum")
    xplane_1 = openmc.XPlane(x0=xplane_0.x0 + width_a)
    xplane_2 = openmc.XPlane(x0=xplane_1.x0 + width_b)
    xplane_3 = openmc.XPlane(x0=xplane_2.x0 + width_c)
    xplane_4 = openmc.XPlane(x0=xplane_3.x0 + width_d)
    xplane_5 = openmc.XPlane(x0=xplane_4.x0 + width_e)
    xplane_6 = openmc.XPlane(x0=xplane_5.x0 + width_f)
    xplane_7 = openmc.XPlane(x0=xplane_6.x0 + width_g, boundary_type="vacuum")

    yplane_0 = openmc.YPlane(y0=0, boundary_type="vacuum")
    yplane_1 = openmc.YPlane(y0=yplane_0.y0 + depth_a)
    yplane_2 = openmc.YPlane(y0=yplane_1.y0 + depth_b)
    yplane_3 = openmc.YPlane(y0=yplane_2.y0 + depth_c)
    yplane_4 = openmc.YPlane(y0=yplane_3.y0 + depth_d)
    yplane_5 = openmc.YPlane(y0=yplane_4.y0 + depth_e)
    yplane_6 = openmc.YPlane(y0=yplane_5.y0 + depth_f, boundary_type="vacuum")

    zplane_1 = openmc.ZPlane(z0=0, boundary_type="vacuum")
    zplane_2 = openmc.ZPlane(z0=zplane_1.z0 + height_j)
    zplane_3 = openmc.ZPlane(z0=zplane_2.z0 + height_k)
    zplane_4 = openmc.ZPlane(z0=zplane_3.z0 + height_l, boundary_type="vacuum")

    outside_left_region = +xplane_0 & -xplane_1 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_4
    wall_left_region = +xplane_1 & -xplane_2 & +yplane_2 & -yplane_4 & +zplane_2 & -zplane_3
    wall_right_region = +xplane_5 & -xplane_6 & +yplane_2 & -yplane_5 & +zplane_2 & -zplane_3
    wall_top_region = +xplane_1 & -xplane_4 & +yplane_4 & -yplane_5 & +zplane_2 & -zplane_3
    outside_top_region = +xplane_0 & -xplane_7 & +yplane_5 & -yplane_6 & +zplane_1 & -zplane_4
    wall_bottom_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_2 & +zplane_2 & -zplane_3
    outside_bottom_region = +xplane_0 & -xplane_7 & +yplane_0 & -yplane_1 & +zplane_1 & -zplane_4
    wall_middle_region = +xplane_3 & -xplane_4 & +yplane_3 & -yplane_4 & +zplane_2 & -zplane_3
    outside_right_region = +xplane_6 & -xplane_7 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_4

    room_region = +xplane_2 & -xplane_3 & +yplane_2 & -yplane_4 & +zplane_2 & -zplane_3
    gap_region = +xplane_3 & -xplane_4 & +yplane_2 & -yplane_3 & +zplane_2 & -zplane_3
    corridor_region = +xplane_4 & -xplane_5 & +yplane_2 & -yplane_5 & +zplane_2 & -zplane_3

    roof_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_2
    floor_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_5 & +zplane_3 & -zplane_4

    outside_left_cell = openmc.Cell(region=outside_left_region, fill=mat_air)
    outside_right_cell = openmc.Cell(region=outside_right_region, fill=mat_air)
    outside_top_cell = openmc.Cell(region=outside_top_region, fill=mat_air)
    outside_bottom_cell = openmc.Cell(region=outside_bottom_region, fill=mat_air)
    wall_left_cell = openmc.Cell(region=wall_left_region, fill=mat_concrete)
    wall_right_cell = openmc.Cell(region=wall_right_region, fill=mat_concrete)
    wall_top_cell = openmc.Cell(region=wall_top_region, fill=mat_concrete)
    wall_bottom_cell = openmc.Cell(region=wall_bottom_region, fill=mat_concrete)
    wall_middle_cell = openmc.Cell(region=wall_middle_region, fill=mat_concrete)
    room_cell = openmc.Cell(region=room_region, fill=mat_air)
    gap_cell = openmc.Cell(region=gap_region, fill=mat_air)
    corridor_cell = openmc.Cell(region=corridor_region, fill=mat_air)

    roof_cell = openmc.Cell(region=roof_region, fill=mat_concrete)
    floor_cell = openmc.Cell(region=floor_region, fill=mat_concrete)

    geometry = openmc.Geometry(
        [
            outside_bottom_cell,
            outside_top_cell,
            outside_left_cell,
            outside_right_cell,
            wall_left_cell,
            wall_right_cell,
            wall_top_cell,
            wall_bottom_cell,
            wall_middle_cell,
            room_cell,
            gap_cell,
            corridor_cell,
            roof_cell,
            floor_cell,
        ]
    )

    # plot = geometry.plot(basis='xy',  color_by='material')
    # plot.figure.savefig('geometry_top_down_view.png', bbox_inches="tight")

    source_x = width_a + width_b + width_c * 0.5
    source_y = depth_a + depth_b + depth_c * 0.75
    source_z = height_j + height_k * 0.5
    space = openmc.stats.Point((source_x, source_y, source_z))

    source = openmc.IndependentSource(
        space=space,
        angle=openmc.stats.Isotropic(),
        energy=openmc.stats.Discrete([2.5e6], [1.0]),
        particle="neutron"
    )

    settings = openmc.Settings()
    settings.run_mode = "fixed source"
    settings.source = source
    settings.particles = 80
    settings.batches = 100
    settings.inactive = 50

    # plot = openmc.Plot()
    # plot.origin = geometry.root_universe.bounding_box.center
    # plot.width = geometry.root_universe.bounding_box.width
    # plot.pixels = [1000, 1000, 1]
    # plot.type = 'voxel'
    # plot.id = 100

    # plots = openmc.Plots([plot]) <-- to put this back in add 'plots=plots' to the line below 

    ce_model = openmc.Model(geometry, materials_continuous_xs, settings)

    rr_model = copy.deepcopy(ce_model)
    rr_model.convert_to_multigroup(method="material_wise", overwrite_mgxs_library=False)

    rr_model.convert_to_random_ray()

    mesh = openmc.RegularMesh().from_domain(geometry)
    mesh.dimension = (100, 100, 1)
    mesh.id = 1

    mesh_filter = openmc.MeshFilter(mesh, filter_id=1)
    flux_tally = openmc.Tally(name="flux tally")
    flux_tally.filters = [mesh_filter]
    flux_tally.scores = ["flux"]
    flux_tally.id = 42 
    tallies = openmc.Tallies([flux_tally])

    rr_model.settings.random_ray['source_region_meshes'] = [(mesh, [rr_model.geometry.root_universe])]

    # random_ray_wwg_statepoint = rr_model.run()

    # def plot_random_ray_vtk(fname, title):

    #     plt_mesh = pv.read(fname)
    #     p = pv.Plotter(off_screen=True)
    #     actor = p.add_mesh(plt_mesh, scalars="flux_group_0", cmap="bwr")
    #     mapper = actor.GetMapper()
    #     lut = mapper.GetLookupTable()
    #     lut.SetScaleToLog10()
    #     mapper.Update()
    #     p.view_xy()
    #     p.render()
    #     p.add_title(title)

    #     p.screenshot("output.png")
    #     p.close()
    #     display(Image("output.png"))

    # plot_random_ray_vtk("plot_100.vtk", "Random Ray Forward Flux (Thermal)")

    rr_model.settings.weight_window_generators = openmc.WeightWindowGenerator(
        method='fw_cadis',
        mesh=mesh,
        max_realizations=settings.batches
    )

    rr_model.run()
    
    # plot_random_ray_vtk("plot_100.vtk", "Random Ray Adjoint Flux (Thermal)")

    subprocess.run(["ls", "-lh", "weight_windows.h5"])

    weight_windows = openmc.hdf5_to_wws('weight_windows.h5')

    # plt.imshow(
    #         weight_windows[0].lower_ww_bounds.squeeze().T,
    #         origin='lower', norm=LogNorm(), aspect=17.0 / 11.0
    # )
    # plt.title('lower_ww_bounds')
    # plt.colorbar()

    subprocess.run(["cp", "weight_windows.h5", "ww_fw_cadis.h5"])

    settings = openmc.Settings()
    settings.weight_window_checkpoints = {'collision': True, 'surface': True}
    settings.survival_biasing = False
    settings.weight_windows = weight_windows
    settings.particles = 65000
    settings.batches = 30
    settings.source = source
    settings.run_mode = "fixed source"

    tallies = openmc.Tallies([flux_tally])

    settings.weight_windows_on = False
    simulation_using_ww_off = openmc.Model(geometry, materials_continuous_xs, settings, tallies)
    sp_default = simulation_using_ww_off.run()
    os.replace(sp_default, "labyrinth_statepoint_no_WW.h5")
    statepoint_off = "labyrinth_statepoint_no_WW.h5"
    results_no_WW = summarize_labyrinth_statepoint(statepoint_off)

    # def plot_mesh_tally(statepoint_filename, image_filename):

    #     with openmc.StatePoint(statepoint_filename) as sp:
    #         flux_tally = sp.get_tally(name="flux tally")

    #     mesh_extent = flux_tally.find_filter(openmc.MeshFilter).mesh.bounding_box.extent['xy']

    #     fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)

    #     flux_mean = flux_tally.get_reshaped_data(value="mean", expand_dims=True).squeeze()
    #     im1 = axes[0].imshow(
    #         flux_mean[:, :].T,
    #         origin="lower",
    #         extent=mesh_extent,
    #         norm=LogNorm(),
    #         cmap="coolwarm"
    #     )
    #     axes[0].set_title("Flux")
    #     cbar1 = fig.colorbar(im1, ax=axes[0])
    #     cbar1.set_label("Flux")

    #     flux_rel_err = flux_tally.get_reshaped_data(value="rel_err", expand_dims=True).squeeze()

    #     invalid_mask = np.isnan(flux_rel_err) | (flux_rel_err == 0.0)
    #     flux_rel_err = np.where(invalid_mask, 1.0, flux_rel_err)
        
    #     im2 = axes[1].imshow(
    #         flux_rel_err[:, :].T,
    #         origin="lower",
    #         extent=mesh_extent,
    #         norm=LogNorm(vmin=1e-3, vmax=1e0), 
    #         cmap="coolwarm"
    #     )
    #     axes[1].set_title("Flux Rel Err")
    #     cbar2 = fig.colorbar(im2, ax=axes[1])
    #     cbar2.set_label("Flux Rel Err")

    #     avg_rel_err = np.mean(flux_rel_err)
    #     max_rel_err = np.max(flux_rel_err)
    #     rms_rel_err = np.sqrt(np.mean(np.square(flux_rel_err)))
    #     print(f"Average Relative Error: {avg_rel_err * 100.0:.6f}%")
    #     print(f"Maximum Relative Error: {max_rel_err * 100.0:.6f}%")
    #     print(f"RMS Relative Error: {rms_rel_err * 100.0:.6f}%")

    #     plt.savefig(image_filename)

    # plot_mesh_tally(statepoint_off, "no_fw_cadis.png")

    settings.weight_windows_on = True
    settings.particles = 30000
    settings.batches = 15
    weight_windows = openmc.hdf5_to_wws('ww_fw_cadis.h5')
    settings.weight_windows = weight_windows
    simulation_using_ww_on = openmc.Model(geometry, materials_continuous_xs, settings, tallies)
    sp_default = simulation_using_ww_on.run()
    os.replace(sp_default, "labyrinth_statepoint_with_WW.h5")
    statepoint_on = "labyrinth_statepoint_with_WW.h5"
    results_with_WW = summarize_labyrinth_statepoint(statepoint_on)

    # plot_mesh_tally(statepoint_on, "fw_cadis.png")
    
    os.chdir(orig_dir)

    return results_with_WW, results_no_WW

def summarize_labyrinth_statepoint(sp_path):
    sp = openmc.StatePoint(sp_path)
    transport_time = sp.runtime['transport']
    tally = sp.get_tally(name="flux tally")
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

if __name__ == "__main__":
    run_labyrinth()