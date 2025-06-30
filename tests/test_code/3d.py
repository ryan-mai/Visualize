import open3d as o3d
import numpy as np
import re

mesh_path = r"giant_panda.glb"
mesh = o3d.io.read_triangle_mesh(mesh_path)
save_path = re.match(r"(.*?)\.", mesh_path).group(1)

if mesh.is_empty():
    raise ValueError('Invalid Mesh...')

def crinkle(noise: int):
    print('Creating Noisy mesh')
    knot_mesh = o3d.data.KnotMesh()
    vertices = np.asarray(mesh.vertices)
    vertices += np.random.uniform(0, noise, size=vertices.shape)
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh_out = mesh.filter_smooth_simple(number_of_iterations=1)
    mesh_out.compute_vertex_normals()
    o3d.visualization.draw_geometries([mesh_out])

def dot(points: int):
    mesh.compute_vertex_normals()

    pcd = mesh.sample_points_uniformly(points)
    pcd = mesh.sample_points_poisson_disk(points, pcl=pcd)
    o3d.visualization.draw_geometries([pcd])

def poly(simplify: int = 16, save_path: str = f"{save_path}.obj"):
    mesh.compute_vertex_normals() 
    voxel_size = max(mesh.get_max_bound() - mesh.get_min_bound()) / simplify
    print(f'voxel_size = {voxel_size:e}')
    mesh_smp = mesh.simplify_vertex_clustering(
        voxel_size=voxel_size,
        contraction=o3d.geometry.SimplificationContraction.Average)
    print(
        f'Simplified mesh has {len(mesh_smp.vertices)} vertices and {len(mesh_smp.triangles)} triangles'
    )
    o3d.visualization.draw_geometries([mesh_smp])
    # Save as OBJ
    o3d.io.write_triangle_mesh(save_path, mesh_smp)
    print(f"Mesh saved as {save_path}")

if __name__ == "__main__":
    poly(20)