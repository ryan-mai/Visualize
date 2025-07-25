import discord
from discord.ext import commands
from discord import app_commands
import open3d as o3d
import numpy as np
import os
import tempfile
import asyncio
from typing import Optional
import imageio.v2 as imageio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

class CrinkleBot:
    def __init__(self):
        self.mesh_path = None
        self.base_mesh = None

    def has_mesh(self) -> bool:
        return self.base_mesh is not None and not self.base_mesh.is_empty()

    def set_mesh(self, new_mesh_path: str) -> bool:
        try:
            test_mesh = o3d.io.read_triangle_mesh(new_mesh_path)
            if test_mesh.is_empty():
                return False
            self.mesh_path = new_mesh_path
            self.base_mesh = test_mesh
            return True
        except:
            return False

    def _render_geometry(self, geometry, filename_prefix: str) -> str:
        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False, width=800, height=600)
        vis.add_geometry(geometry)

        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.2, 0.2, 0.2])
        opt.light_on = True
        if hasattr(geometry, 'triangles'):
            opt.mesh_show_wireframe = False
        else:
            opt.point_size = 4.0

        view_ctrl = vis.get_view_control()
        vis.poll_events()
        vis.update_renderer()
        view_ctrl.set_zoom(0.7)
        view_ctrl.rotate(300, 200)
        vis.poll_events()
        vis.update_renderer()

        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, f"{filename_prefix}_{np.random.randint(1000, 9999)}.png")
        vis.capture_screen_image(image_path)
        vis.destroy_window()
        return image_path

    def _create_video(self, geometry, filename_prefix: str, frames: int = 72) -> str:
        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False, width=800, height=600)
        vis.add_geometry(geometry)

        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.2, 0.2, 0.2])
        opt.light_on = True
        if hasattr(geometry, 'triangles'):
            opt.mesh_show_wireframe = False
        else:
            opt.point_size = 4.0

        view_ctrl = vis.get_view_control()
        vis.poll_events()
        vis.update_renderer()

        bbox = geometry.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        radius = np.linalg.norm(bbox.get_extent()) * 1.5

        temp_dir = tempfile.gettempdir()
        frames_dir = os.path.join(temp_dir, f"frames_{np.random.randint(1000, 9999)}")
        os.makedirs(frames_dir, exist_ok=True)

        frame_paths = []
        for i in range(frames):
            angle = (i / frames) * 2 * np.pi
            cam_x = center[0] + radius * np.cos(angle)
            cam_z = center[2] + radius * np.sin(angle)

            view_ctrl.set_front([center[0] - cam_x, center[1] - center[1], center[2] - cam_z])
            view_ctrl.set_up([0, 1, 0])
            view_ctrl.set_lookat(center)
            view_ctrl.set_zoom(0.7)
            vis.poll_events()
            vis.update_renderer()

            frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
            vis.capture_screen_image(frame_path)
            frame_paths.append(frame_path)

        vis.destroy_window()

        video_path = os.path.join(temp_dir, f"{filename_prefix}_360_{np.random.randint(1000, 9999)}.mp4")
        with imageio.get_writer(video_path, fps=20, codec='libx264', quality=8) as writer:
            for frame_path in frame_paths:
                if os.path.exists(frame_path):
                    writer.append_data(imageio.imread(frame_path))
                    os.remove(frame_path)

        try:
            os.rmdir(frames_dir)
        except:
            pass
        return video_path

    def process_crinkle(self, noise: float = 0.2, output_type: str = "image") -> str:
        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        vertices = np.asarray(mesh.vertices)
        vertices += np.random.uniform(0, noise, size=vertices.shape)
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh = mesh.filter_smooth_simple(number_of_iterations=1)
        mesh.compute_vertex_normals()

        if output_type == "image":
            return self._render_geometry(mesh, "crinkled_mesh")
        elif output_type == "video":
            return self._create_video(mesh, "crinkled_mesh")
        else:  
            temp_dir = tempfile.gettempdir()
            mesh_path = os.path.join(temp_dir, f"crinkled_mesh_{np.random.randint(1000, 9999)}.obj")
            o3d.io.write_triangle_mesh(mesh_path, mesh)
            return mesh_path

    def process_dot(self, points: int = 1000, output_type: str = "image") -> str:
        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        mesh.compute_vertex_normals()
        pcd = mesh.sample_points_uniformly(points)

        if output_type == "image":
            return self._render_geometry(pcd, "dot_mesh")
        elif output_type == "video":
            return self._create_video(pcd, "dot_mesh")
        else:  
            temp_dir = tempfile.gettempdir()
            pcd_path = os.path.join(temp_dir, f"dot_mesh_{np.random.randint(1000, 9999)}.ply")
            o3d.io.write_point_cloud(pcd_path, pcd)
            return pcd_path

    def process_poly(self, simplify: int = 16, output_type: str = "image") -> str:
        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        mesh.compute_vertex_normals()
        voxel_size = max(mesh.get_max_bound() - mesh.get_min_bound()) / simplify
        mesh = mesh.simplify_vertex_clustering(voxel_size=voxel_size)

        if output_type == "image":
            return self._render_geometry(mesh, "poly_mesh")
        elif output_type == "video":
            return self._create_video(mesh, "poly_mesh")
        else:  
            temp_dir = tempfile.gettempdir()
            mesh_path = os.path.join(temp_dir, f"poly_mesh_{np.random.randint(1000, 9999)}.obj")
            o3d.io.write_triangle_mesh(mesh_path, mesh)
            return mesh_path

crinkle_bot = CrinkleBot()

@bot.event
async def on_ready():
    print(f'{bot.user} ready!')
    await bot.tree.sync()

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="aura farmers")
    if role:
        await member.add_roles(role)

async def process_command(interaction, processor_func, *args, output_type="image"):
    if not crinkle_bot.has_mesh():
        await interaction.response.send_message("❌ No mesh loaded! Use `/upload` first", ephemeral=True)
        return

    await interaction.response.defer()
    try:
        result_path = await asyncio.to_thread(processor_func, *args, output_type)

        titles = {"image": "Image 🖼️", "video": "360° Video 📹", "mesh": "File", "pointcloud": "File"}
        colors = {"image": 0x00ff00, "video": 0x9932cc, "mesh": 0x0099ff, "pointcloud": 0x0099ff}

        embed = discord.Embed(title=f"🎨 {titles[output_type]}", color=colors[output_type])

        filename = f"result.{output_type if output_type != 'pointcloud' else 'ply'}"
        if output_type == "video":
            filename = "result.mp4"
        elif output_type == "mesh":
            filename = "result.obj"
        elif output_type == "image":
            filename = "result.png"
            embed.set_image(url=f"attachment://{filename}")

        file = discord.File(result_path, filename=filename)
        await interaction.followup.send(embed=embed, file=file)

        try:
            os.remove(result_path)
        except:
            pass
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="crinkle", description="Apply crinkle effect to mesh")
@app_commands.describe(noise="Noise level (0.0-1.0)", output_type="Output: image/mesh/video")
async def crinkle_command(interaction: discord.Interaction, noise: Optional[float] = 0.2, output_type: Optional[str] = "image"):
    if not 0.0 <= noise <= 1.0 or output_type not in ["image", "mesh", "video"]:
        await interaction.response.send_message("❌ Invalid parameters", ephemeral=True)
        return
    await process_command(interaction, crinkle_bot.process_crinkle, noise, output_type=output_type)

@bot.tree.command(name="dot", description="Convert mesh to a lot of DOTS!!!")
@app_commands.describe(points="Number of points (100-10000)", output_type="Output: image/pointcloud/video")
async def dot_command(interaction: discord.Interaction, points: Optional[int] = 1000, output_type: Optional[str] = "image"):
    if not 100 <= points <= 10000 or output_type not in ["image", "pointcloud", "video"]:
        await interaction.response.send_message("❌ Invalid parameters", ephemeral=True)
        return
    await process_command(interaction, crinkle_bot.process_dot, points, output_type=output_type)

@bot.tree.command(name="poly", description="Turn your 3D model into a low poly design (with a LOT of TRIANGLES!)")
@app_commands.describe(simplify="Simplify: 4x - 100x!", output_type="Output: image/mesh/video")
async def poly_command(interaction: discord.Interaction, simplify: Optional[int] = 16, output_type: Optional[str] = "image"):
    if not 4 <= simplify <= 100 or output_type not in ["image", "mesh", "video"]:
        await interaction.response.send_message("❌ Invalid parameters", ephemeral=True)
        return
    await process_command(interaction, crinkle_bot.process_poly, simplify, output_type=output_type)

@bot.tree.command(name="upload", description="Upload 3D mesh file")
async def upload_command(interaction: discord.Interaction, mesh_file: discord.Attachment):
    await interaction.response.defer()

    if mesh_file.size > 25 * 1024 * 1024:
        await interaction.followup.send("❌ File too large (max 25MB) 📁", ephemeral=True)
        return

    allowed_exts = ['.obj', '.ply', '.glb', '.gltf', '.stl']
    if not any(mesh_file.filename.lower().endswith(ext) for ext in allowed_exts):
        await interaction.followup.send("❌ Unsupported format", ephemeral=True)
        return

    _, ext = os.path.splitext(mesh_file.filename)
    temp_path = os.path.join(tempfile.gettempdir(), f"mesh_{interaction.user.id}{ext}")
    await mesh_file.save(temp_path)

    if crinkle_bot.set_mesh(temp_path):
        embed = discord.Embed(title="✅ Mesh Uploaded!", color=0x00ff00)
        embed.add_field(name="Vertices", value=len(crinkle_bot.base_mesh.vertices))
        embed.add_field(name="Triangles", value=len(crinkle_bot.base_mesh.triangles))
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Invalid mesh file", ephemeral=True)

@bot.tree.command(name="info", description="All info on the bot commands 🤓")
async def info_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 3D Mesh Bot", color=0x9932cc)
    embed.add_field(name="Commands", value="/upload, /crinkle, /dot, /poly", inline=False)

    if crinkle_bot.has_mesh():
        embed.add_field(name="Current Mesh", value=f"{len(crinkle_bot.base_mesh.vertices)} vertices")
    else:
        embed.add_field(name="Status", value="No mesh loaded")

    await interaction.response.send_message(embed=embed)

def main():
    import dotenv
    dotenv.load_dotenv()
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        bot.run(token)

if __name__ == "__main__":
    main()