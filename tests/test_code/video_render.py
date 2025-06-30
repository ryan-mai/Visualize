"""

Required packages:
- trimesh  # For loading GLB files only
- matplotlib  # For headless rendering
- imageio  # For GIF creation
"""

import trimesh
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import imageio
import os
import tempfile
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore')

def load_model(file_path):
    """Load 3D model using trimesh"""
    try:
        mesh = trimesh.load(file_path)
        
        # Handle scenes (GLB files)
        if hasattr(mesh, 'geometry'):
            print(f"Found scene with {len(mesh.geometry)} geometries")
            geometries = list(mesh.geometry.values())
            if geometries:
                if len(geometries) == 1:
                    mesh = geometries[0]
                    print("Using single geometry")
                else:
                    # Combine all geometries into one mesh
                    print(f"Combining {len(geometries)} geometries into single mesh...")
                    combined_vertices = []
                    combined_faces = []
                    vertex_offset = 0
                    
                    for i, geom in enumerate(geometries):
                        if hasattr(geom, 'vertices') and hasattr(geom, 'faces'):
                            print(f"  Geometry {i+1}: {len(geom.vertices)} vertices, {len(geom.faces)} faces")
                            combined_vertices.extend(geom.vertices)
                            # Adjust face indices to account for vertex offset
                            adjusted_faces = geom.faces + vertex_offset
                            combined_faces.extend(adjusted_faces)
                            vertex_offset += len(geom.vertices)
                    
                    if combined_vertices and combined_faces:
                        # Create new combined mesh
                        import numpy as np
                        mesh = trimesh.Trimesh(
                            vertices=np.array(combined_vertices),
                            faces=np.array(combined_faces)
                        )
                        print(f"Combined mesh created: {len(mesh.vertices)} total vertices, {len(mesh.faces)} total faces")
                    else:
                        print("ERROR: No valid geometries found to combine!")
                        return None
            else:
                print("ERROR: No geometries found in scene!")
                return None
        
        print(f"Final loaded model: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        return mesh
        
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None

def render_image_from_angle(mesh, elevation, azimuth, output_path, 
                          figsize=(8, 6), dpi=100):
    """Render mesh from specific angle using matplotlib (completely headless)"""
    
    # Ensure headless operation
    plt.ioff()  # Turn off interactive mode
    
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    
    # Get mesh data
    vertices = mesh.vertices
    faces = mesh.faces
    
    # Create the 3D polygon collection
    poly3d = []
    for face in faces:
        try:
            triangle = vertices[face]
            poly3d.append(triangle)
        except IndexError:
            continue
    
    if poly3d:
        # Create collection with nice colors
        collection = Poly3DCollection(poly3d, 
                                     alpha=0.8, 
                                     facecolor='lightsteelblue',
                                     edgecolor='navy',
                                     linewidth=0.1)
        ax.add_collection3d(collection)
    
    # Set the aspect ratio and limits to preserve model proportions
    # Calculate individual axis ranges
    x_min, x_max = vertices[:, 0].min(), vertices[:, 0].max()
    y_min, y_max = vertices[:, 1].min(), vertices[:, 1].max()
    z_min, z_max = vertices[:, 2].min(), vertices[:, 2].max()
    
    # Calculate centers
    mid_x = (x_min + x_max) * 0.5
    mid_y = (y_min + y_max) * 0.5
    mid_z = (z_min + z_max) * 0.5
    
    # Find the maximum dimension to create a square bounding box
    max_dim = max(x_max - x_min, y_max - y_min, z_max - z_min)
    half_range = max_dim * 0.6  # Add some padding
    
    # Set equal ranges for all axes to avoid stretching
    ax.set_xlim(mid_x - half_range, mid_x + half_range)
    ax.set_ylim(mid_y - half_range, mid_y + half_range)
    ax.set_zlim(mid_z - half_range, mid_z + half_range)
    
    # Ensure equal aspect ratio
    ax.set_box_aspect([1,1,1])
    
    # Set the viewing angle
    ax.view_init(elev=elevation, azim=azimuth)
    
    # Remove all grid and axis elements for clean appearance
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    
    # Hide axis panes completely
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('none')
    ax.yaxis.pane.set_edgecolor('none')
    ax.zaxis.pane.set_edgecolor('none')
    ax.xaxis.pane.set_alpha(0)
    ax.yaxis.pane.set_alpha(0)
    ax.zaxis.pane.set_alpha(0)
    
    # Make axes completely invisible
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.zaxis.set_visible(False)
    
    # Remove any remaining tick marks and lines
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.set_axis_off()
    
    # Hide axis lines
    ax.xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1, 
                facecolor='white', edgecolor='none', dpi=dpi)
    plt.close(fig)  # Important: close figure to free memory
    
    return True

def render_multiple_angles(mesh, output_dir="headless_renders"):
    """Render model from multiple angles (no GUI windows)"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Define angles (elevation, azimuth) - comprehensive coverage
    angles = {
        # Basic cardinal directions
        "front": (0, 0),
        "back": (0, 180),
        "left": (0, 270),
        "right": (0, 90),
        
        # Vertical views
        "top": (80, 0),
        "bottom": (-80, 0),
        
        # Diagonal corners (low elevation)
        "diagonal_1": (15, 45),      # Front-right low
        "diagonal_2": (15, 135),     # Back-right low
        "diagonal_3": (15, 225),     # Back-left low
        "diagonal_4": (15, 315),     # Front-left low
        
    }
    
    rendered_files = []
    
    for angle_name, (elevation, azimuth) in angles.items():
        output_path = os.path.join(output_dir, f"{angle_name}.png")
        
        if render_image_from_angle(mesh, elevation, azimuth, output_path):
            rendered_files.append(output_path)
            print(f"Rendered: {angle_name}.png")
        else:
            print(f"Failed to render: {angle_name}")
    
    return rendered_files

def create_headless_gif(mesh, output_dir="video", 
                       frames=30, duration=2.0, gif_name="rotation.gif"):
    
    print(f"Creating GIF with {frames} frames at {duration} seconds per frame...")
    print(f"Total GIF duration will be: {frames * duration:.1f} seconds")
    
    images = []
    temp_files = []
    
    for i in range(frames):
        azimuth = (i / frames) * 360
        elevation = 20
        
        # Create temp file for this frame
        temp_path = os.path.join(output_dir, f"temp_gif_frame_{i:03d}.png")
        
        if render_image_from_angle(mesh, elevation, azimuth, temp_path, figsize=(6, 6)):
            # Read the image and ensure consistent size
            image = imageio.imread(temp_path)
            if len(images) == 0:
                # First image sets the target size
                target_shape = image.shape
                images.append(image)
            else:
                # Resize subsequent images to match if needed
                if image.shape != target_shape:
                    from PIL import Image as PILImage
                    pil_img = PILImage.fromarray(image)
                    pil_img = pil_img.resize((target_shape[1], target_shape[0]))
                    image = np.array(pil_img)
                images.append(image)
            temp_files.append(temp_path)
            
            if (i + 1) % 6 == 0:
                print(f"  Generated {i + 1}/{frames} frames...")
        else:
            print(f"  Failed to generate frame {i}")
    
    if images:
        gif_path = os.path.join(output_dir, gif_name)
        imageio.mimsave(gif_path, images, duration=duration)
        
        # Clean up temp files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass
        
        print(f"GIF saved: {gif_path}")
        return gif_path
    else:
        print("No frames generated for GIF!")
        return None

def main():
    """Main function"""
    model_path = r"C:\Users\mayma\Discord Bot\untitled (1).glb"
    output_dir = "video_renders"
    
    print("Starting image rendering...")
    
    mesh = load_model(model_path)
    if mesh is None:
        print("Failed to load model!")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Render static images
    print("\n--- Rendering Static Images ---")
    rendered_files = render_multiple_angles(mesh, output_dir)
    print(f"Successfully rendered {len(rendered_files)} static images!")
    
    # Create GIF
    print("\n--- Creating Rotation GIF ---")
    gif_path = create_headless_gif(mesh, output_dir=output_dir, frames=60, duration=2.0)  # 2 seconds per frame = slow but compatible
    
    print(f"\n✅ Rendering complete!")
    print(f"📁 Output folder: {output_dir}")
    if gif_path:
        print(f"🎞️  GIF: {gif_path}")
    print(f"📸 {len(rendered_files)} static images")

if __name__ == "__main__":
    main()
