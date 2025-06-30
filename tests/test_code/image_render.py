# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# Copyright (c) 2018-2024 www.open3d.org
# SPDX-License-Identifier: MIT
# ----------------------------------------------------------------------------

import open3d as o3d
import open3d.visualization.rendering as rendering # type: ignore


def main():
    # Load your gravity-tram model
    print("Loading gravity-tram model...")
    mesh = o3d.io.read_triangle_mesh("demo.glb")
    
    if mesh.is_empty():
        print("Failed to load the model! Creating fallback geometry...")
        # Fallback to a simple box if model fails to load
        mesh = o3d.geometry.TriangleMesh.create_box(2, 2, 1)
        mesh.paint_uniform_color([0.7, 0.7, 0.9])
    else:
        print(f"Successfully loaded model with {len(mesh.vertices)} vertices and {len(mesh.triangles)} triangles")
    
    # Compute normals if they don't exist
    mesh.compute_vertex_normals()
    
    # Create visualizer and capture screen
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False, width=1024, height=1024)
    
    # Add the gravity-tram model
    vis.add_geometry(mesh)
    
    # Set up view
    opt = vis.get_render_option()
    opt.light_on = True
    opt.show_coordinate_frame = True
    
    # Update visualization
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image("images/front.png")
    
    # Change view and capture second image
    view_ctrl = vis.get_view_control()
    view_ctrl.set_front([-1, 0, 0])
    view_ctrl.set_up([0, 0, 1])
    vis.poll_events()
    vis.update_renderer()

    vis.capture_screen_image("images/top_down.png")
    
    # Change to a third angle - top-down view
    view_ctrl.set_front([0, 0, -1])
    view_ctrl.set_up([0, 1, 0])
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image("images/back.png")
    
    # Change to a fourth angle - diagonal/angled view
    view_ctrl.set_front([1, -0.5, -0.5])  # Looking from front-right and slightly above
    view_ctrl.set_up([0, 1, 0])
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image("images/bottom.png")

    view_ctrl.set_front([0.5, 0, 0.5])  # Looking from front-right and slightly above
    view_ctrl.set_up([0, 1, 0])
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image("images/side_right.png")
    

    view_ctrl.set_front([-0.5, 0, 0.5])  # Looking from front-right and slightly above
    view_ctrl.set_up([0, 1, 0])
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image("images/side_left.png")

    vis.destroy_window()


if __name__ == "__main__":
    main()