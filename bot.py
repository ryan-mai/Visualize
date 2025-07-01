import discord
from discord.ext import commands
from discord import app_commands
import open3d as o3d
import numpy as np
import os
import tempfile
import asyncio
from typing import Optional
import cv2
import imageio.v2 as imageio
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

class CrinkleBot:
    def __init__(self):
        self.mesh_path = None
        self.base_mesh = None
        print("CrinkleBot initialized - waiting for mesh upload...")

    def has_mesh(self) -> bool:
        return self.base_mesh is not None and not self.base_mesh.is_empty()

    def load_base_mesh(self):
        if not self.mesh_path or not os.path.exists(self.mesh_path):
            raise ValueError('No valid mesh path set')

        self.base_mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        if self.base_mesh.is_empty():
            raise ValueError('Invalid Mesh...')
        print(f"Loaded mesh with {len(self.base_mesh.vertices)} vertices")

    def set_mesh(self, new_mesh_path: str) -> bool:
        try:
            test_mesh = o3d.io.read_triangle_mesh(new_mesh_path)
            if test_mesh.is_empty():
                return False

            self.mesh_path = new_mesh_path
            self.load_base_mesh()
            return True
        except Exception as e:
            print(f"Error loading mesh: {e}")
            return False

    def get_current_mesh_name(self) -> str:
        if not self.mesh_path:
            return "No mesh loaded"
        return os.path.basename(self.mesh_path)

    def create_360_video(self, geometry, output_path: str, frames: int = 72, width: int = 800, height: int = 600) -> str:
        print(f"Creating 360° video with {frames} frames...")

        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False, width=width, height=height)
        vis.add_geometry(geometry)

        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.2, 0.2, 0.2])
        opt.mesh_show_wireframe = False
        opt.mesh_show_back_face = True
        opt.light_on = True
        opt.point_size = 4.0

        view_ctrl = vis.get_view_control()

        vis.poll_events()
        vis.update_renderer()

        view_ctrl.set_up([0, 1, 0])

        temp_dir = tempfile.gettempdir()
        frames_dir = os.path.join(temp_dir, f"video_frames_{np.random.randint(1000, 9999)}")
        os.makedirs(frames_dir, exist_ok=True)

        frame_paths = []

        bbox = geometry.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        extent = bbox.get_extent()
        radius = np.linalg.norm(extent) * 1.5

        for i in range(frames):

            angle = (i / frames) * 2 * np.pi  

            cam_x = center[0] + radius * np.cos(angle)
            cam_z = center[2] + radius * np.sin(angle)
            cam_y = center[1]  

            view_ctrl.set_front([center[0] - cam_x, center[1] - cam_y, center[2] - cam_z])
            view_ctrl.set_up([0, 1, 0])  
            view_ctrl.set_lookat(center)
            view_ctrl.set_zoom(0.7)

            vis.poll_events()
            vis.update_renderer()

            frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
            vis.capture_screen_image(frame_path)
            frame_paths.append(frame_path)

        vis.destroy_window()

        print("Combining frames into video...")

        fps = max(20, frames // 3)  
        with imageio.get_writer(output_path, fps=fps, codec='libx264', quality=8) as writer:
            for frame_path in frame_paths:
                if os.path.exists(frame_path):
                    image = imageio.imread(frame_path)
                    writer.append_data(image)

        for frame_path in frame_paths:
            try:
                os.remove(frame_path)
            except:
                pass

        try:
            os.rmdir(frames_dir)
        except:
            pass

        print(f"Video saved to: {output_path}")
        return output_path

    def crinkle_video(self, noise: float = 0.2) -> str:
        """Apply crinkle effect and create 360° video"""
        print(f'Creating crinkle video with noise level: {noise}')

        mesh_in = o3d.io.read_triangle_mesh(self.mesh_path)

        vertices = np.asarray(mesh_in.vertices)
        vertices += np.random.uniform(0, noise, size=vertices.shape)
        mesh_in.vertices = o3d.utility.Vector3dVector(vertices)

        mesh_out = mesh_in.filter_smooth_simple(number_of_iterations=1)
        mesh_out.compute_vertex_normals()

        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, f"crinkled_mesh_360_{np.random.randint(1000, 9999)}.mp4")
        return self.create_360_video(mesh_out, video_path)

    def dot_video(self, points: int = 1000) -> str:
        """Create point cloud and 360° video"""
        print(f'Creating dot video with {points} points')

        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        mesh.compute_vertex_normals()

        pcd = mesh.sample_points_uniformly(points)
        pcd = mesh.sample_points_poisson_disk(points, pcl=pcd)

        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, f"dot_mesh_360_{np.random.randint(1000, 9999)}.mp4")
        return self.create_360_video(pcd, video_path)

    def poly_video(self, simplify: int = 16) -> str:
        """Simplify mesh and create 360° video"""
        print(f'Creating poly video with simplification factor: {simplify}')

        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        mesh.compute_vertex_normals()

        voxel_size = max(mesh.get_max_bound() - mesh.get_min_bound()) / simplify
        mesh_smp = mesh.simplify_vertex_clustering(
            voxel_size=voxel_size,
            contraction=o3d.geometry.SimplificationContraction.Average)

        print(f'Simplified mesh has {len(mesh_smp.vertices)} vertices and {len(mesh_smp.triangles)} triangles')

        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, f"poly_mesh_360_{np.random.randint(1000, 9999)}.mp4")
        return self.create_360_video(mesh_smp, video_path)

    def crinkle_mesh(self, noise: float = 0.2) -> str:
        """Apply crinkle effect and save as image"""
        print(f'Creating Noisy mesh with noise level: {noise}')

        mesh_in = o3d.io.read_triangle_mesh(self.mesh_path)

        vertices = np.asarray(mesh_in.vertices)
        vertices += np.random.uniform(0, noise, size=vertices.shape)
        mesh_in.vertices = o3d.utility.Vector3dVector(vertices)

        print('Applying smoothing filter...')
        mesh_out = mesh_in.filter_smooth_simple(number_of_iterations=1)
        mesh_out.compute_vertex_normals()

        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False, width=800, height=600)
        vis.add_geometry(mesh_out)

        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.2, 0.2, 0.2])  
        opt.mesh_show_wireframe = False
        opt.mesh_show_back_face = True
        opt.light_on = True

        view_ctrl = vis.get_view_control()

        vis.poll_events()
        vis.update_renderer()
        view_ctrl.set_zoom(0.7)

        view_ctrl.rotate(300, 200)

        vis.poll_events()
        vis.update_renderer()

        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, f"crinkled_mesh_{np.random.randint(1000, 9999)}.png")
        vis.capture_screen_image(image_path)
        vis.destroy_window()

        return image_path

    def save_crinkled_mesh(self, noise: float = 0.2) -> str:
        """Apply crinkle effect and save mesh file"""
        print(f'Creating and saving crinkled mesh with noise level: {noise}')

        mesh_in = o3d.io.read_triangle_mesh(self.mesh_path)

        vertices = np.asarray(mesh_in.vertices)
        vertices += np.random.uniform(0, noise, size=vertices.shape)
        mesh_in.vertices = o3d.utility.Vector3dVector(vertices)

        mesh_out = mesh_in.filter_smooth_simple(number_of_iterations=1)
        mesh_out.compute_vertex_normals()

        temp_dir = tempfile.gettempdir()
        mesh_path = os.path.join(temp_dir, f"crinkled_mesh_{np.random.randint(1000, 9999)}.obj")
        o3d.io.write_triangle_mesh(mesh_path, mesh_out)

        return mesh_path

    def dot_mesh(self, points: int = 1000) -> str:
        """Convert mesh to point cloud and save as image"""
        print(f'Creating point cloud with {points} points')

        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        mesh.compute_vertex_normals()

        pcd = mesh.sample_points_uniformly(points)
        pcd = mesh.sample_points_poisson_disk(points, pcl=pcd)

        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False, width=800, height=600)
        vis.add_geometry(pcd)

        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.2, 0.2, 0.2])  
        opt.point_size = 4.0
        opt.light_on = True

        view_ctrl = vis.get_view_control()

        vis.poll_events()
        vis.update_renderer()
        view_ctrl.set_zoom(0.7)

        view_ctrl.rotate(300, 200)

        vis.poll_events()
        vis.update_renderer()

        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, f"dot_mesh_{np.random.randint(1000, 9999)}.png")
        vis.capture_screen_image(image_path)
        vis.destroy_window()

        return image_path

    def save_dot_mesh(self, points: int = 1000) -> str:
        """Convert mesh to point cloud and save as file"""
        print(f'Creating and saving point cloud with {points} points')

        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        mesh.compute_vertex_normals()

        pcd = mesh.sample_points_uniformly(points)
        pcd = mesh.sample_points_poisson_disk(points, pcl=pcd)

        temp_dir = tempfile.gettempdir()
        pcd_path = os.path.join(temp_dir, f"dot_mesh_{np.random.randint(1000, 9999)}.ply")
        o3d.io.write_point_cloud(pcd_path, pcd)

        return pcd_path

    def poly_mesh(self, simplify: int = 16) -> str:
        """Simplify mesh and save as image"""
        print(f'Simplifying mesh with factor: {simplify}')

        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        mesh.compute_vertex_normals()

        voxel_size = max(mesh.get_max_bound() - mesh.get_min_bound()) / simplify
        print(f'voxel_size = {voxel_size:e}')

        mesh_smp = mesh.simplify_vertex_clustering(
            voxel_size=voxel_size,
            contraction=o3d.geometry.SimplificationContraction.Average)

        print(f'Simplified mesh has {len(mesh_smp.vertices)} vertices and {len(mesh_smp.triangles)} triangles')

        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False, width=800, height=600)
        vis.add_geometry(mesh_smp)

        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.2, 0.2, 0.2])  
        opt.mesh_show_wireframe = False
        opt.mesh_show_back_face = True
        opt.light_on = True

        view_ctrl = vis.get_view_control()

        vis.poll_events()
        vis.update_renderer()
        view_ctrl.set_zoom(0.7)

        view_ctrl.rotate(300, 200)

        vis.poll_events()
        vis.update_renderer()

        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, f"poly_mesh_{np.random.randint(1000, 9999)}.png")
        vis.capture_screen_image(image_path)
        vis.destroy_window()

        return image_path

    def save_poly_mesh(self, simplify: int = 16) -> str:
        """Simplify mesh and save as file"""
        print(f'Simplifying and saving mesh with factor: {simplify}')

        mesh = o3d.io.read_triangle_mesh(self.mesh_path)
        mesh.compute_vertex_normals()

        voxel_size = max(mesh.get_max_bound() - mesh.get_min_bound()) / simplify
        print(f'voxel_size = {voxel_size:e}')

        mesh_smp = mesh.simplify_vertex_clustering(
            voxel_size=voxel_size,
            contraction=o3d.geometry.SimplificationContraction.Average)

        print(f'Simplified mesh has {len(mesh_smp.vertices)} vertices and {len(mesh_smp.triangles)} triangles')

        temp_dir = tempfile.gettempdir()
        mesh_path = os.path.join(temp_dir, f"poly_mesh_{np.random.randint(1000, 9999)}.obj")
        o3d.io.write_triangle_mesh(mesh_path, mesh_smp)
        print(f"Mesh saved as {mesh_path}")

        return mesh_path

crinkle_bot = CrinkleBot()

import random
from datetime import timedelta

@bot.tree.command(name="giveaway", description="Start a giveaway in this channel!")
@app_commands.describe(
    prize="What is the prize for the giveaway?",
    duration="How long should the giveaway last (in minutes)?",
    winners="Number of winners to pick"
)
async def giveaway_command(
    interaction: discord.Interaction,
    prize: str,
    duration: int,
    winners: int = 1
):
    if duration <= 0:
        await interaction.response.send_message("❌ Duration must be a positive number.", ephemeral=True)
        return
    if winners < 1:
        await interaction.response.send_message("❌ There must be at least one winner.", ephemeral=True)
        return

    await interaction.response.defer()

    embed = discord.Embed(
        title="🎉 Giveaway Started!",
        description=f"**Prize:** {prize}\n**Hosted by:** {interaction.user.mention}\nReact with 🎉 to enter!\n\n⏳ Ends in {duration} minute(s)\n🏆 Winner(s): {winners}",
        color=0x00ff99
    )
    embed.set_footer(text="Giveaway ends soon...")

    message = await interaction.followup.send(embed=embed)
    await message.add_reaction("🎉")

    await asyncio.sleep(duration * 60)

    updated_message = await message.channel.fetch_message(message.id)
    users = [user async for user in updated_message.reactions[0].users() if not user.bot]

    if not users:
        await message.channel.send("❌ No valid entries, giveaway cancelled.")
        return

    winner_count = min(winners, len(users))
    selected = random.sample(users, k=winner_count)

    winners_text = ', '.join(user.mention for user in selected)
    result_embed = discord.Embed(
        title="🎊 Giveaway Ended!",
        description=f"**Prize:** {prize}\n🏆 Winner(s): {winners_text}",
        color=0xFFD700
    )
    await message.channel.send(embed=result_embed)

@bot.event
async def on_member_join(member):
    role_name = "aura farmers"

    # Find the role by name
    role = discord.utils.get(member.guild.roles, name=role_name)

    if role:
        try:
            await member.add_roles(role)
            print(f"✅ Assigned '{role.name}' to {member.name}")
        except Exception as e:
            print(f"❌ Failed to assign role: {e}")
    else:
        print(f"⚠️ Role '{role_name}' not found in {member.guild.name}")

@bot.event
async def on_ready():
    print(f'{bot.user} has landed and is ready to crinkle meshes!')
    print(f'Bot is in {len(bot.guilds)} server(s)')

    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
        for cmd in synced:
            print(f'  - /{cmd.name}: {cmd.description}')

    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event 
async def on_guild_join(guild):
    print(f'Joined guild: {guild.name} (id: {guild.id})')

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f'Slash command error in /{interaction.data.get("name", "unknown")}: {error}')
    if not interaction.response.is_done():
        await interaction.response.send_message("❌ An error occurred while processing the command.", ephemeral=True)
    else:
        await interaction.followup.send("❌ An error occurred while processing the command.", ephemeral=True)

@bot.tree.command(name="crinkle", description="Apply a crinkle effect to the 3D mesh")
@app_commands.describe(
    noise="Amount of noise to apply (0.0 to 1.0, default: 0.2)",
    output_type="Choose output type: image, mesh file, or video"
)
async def crinkle_command(
    interaction: discord.Interaction, 
    noise: Optional[float] = 0.2,
    output_type: Optional[str] = "image"
):

    if not crinkle_bot.has_mesh():
        await interaction.response.send_message("❌ No mesh loaded! Please upload a mesh first using `/upload`", ephemeral=True)
        return

    if noise < 0.0 or noise > 1.0:
        await interaction.response.send_message("❌ Noise level must be between 0.0 and 1.0", ephemeral=True)
        return

    if output_type.lower() not in ["image", "mesh", "video"]:
        await interaction.response.send_message("❌ Output type must be either 'image', 'mesh', or 'video'", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        if output_type.lower() == "image":

            image_path = await asyncio.to_thread(crinkle_bot.crinkle_mesh, noise)

            embed = discord.Embed(
                title="🎨 Crinkled Mesh Preview",
                description=f"Applied noise level: **{noise}**",
                color=0x00ff00
            )

            file = discord.File(image_path, filename="crinkled_mesh.png")
            embed.set_image(url="attachment://crinkled_mesh.png")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(image_path)
            except:
                pass

        elif output_type.lower() == "video":

            video_path = await asyncio.to_thread(crinkle_bot.crinkle_video, noise)

            embed = discord.Embed(
                title="🎬 Crinkled Mesh 360° Video",
                description=f"Applied noise level: **{noise}**\nWatch the 360° rotating view!",
                color=0x9932cc
            )

            file = discord.File(video_path, filename="crinkled_mesh_360.mp4")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(video_path)
            except:
                pass

        else:  

            mesh_path = await asyncio.to_thread(crinkle_bot.save_crinkled_mesh, noise)

            embed = discord.Embed(
                title="📁 Crinkled Mesh File",
                description=f"Applied noise level: **{noise}**\nDownload the .obj file to view in your 3D software!",
                color=0x0099ff
            )

            file = discord.File(mesh_path, filename="crinkled_mesh.obj")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(mesh_path)
            except:
                pass

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to process mesh: {str(e)}",
            color=0xff0000
        )
        await interaction.followup.send(embed=error_embed)
        print(f"Error in crinkle command: {e}")

@bot.tree.command(name="dot", description="Convert the 3D mesh to a point cloud")
@app_commands.describe(
    points="Number of points to sample (100 to 10000, default: 1000)",
    output_type="Choose output type: image, point cloud file, or video"
)
async def dot_command(
    interaction: discord.Interaction, 
    points: Optional[int] = 1000,
    output_type: Optional[str] = "image"
):

    if not crinkle_bot.has_mesh():
        await interaction.response.send_message("❌ No mesh loaded! Please upload a mesh first using `/upload`", ephemeral=True)
        return

    if points < 100 or points > 10000:
        await interaction.response.send_message("❌ Points must be between 100 and 10000", ephemeral=True)
        return

    if output_type.lower() not in ["image", "pointcloud", "video"]:
        await interaction.response.send_message("❌ Output type must be either 'image', 'pointcloud', or 'video'", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        if output_type.lower() == "image":

            image_path = await asyncio.to_thread(crinkle_bot.dot_mesh, points)

            embed = discord.Embed(
                title="🔵 Point Cloud Preview",
                description=f"Sampled **{points}** points from mesh",
                color=0x0066ff
            )

            file = discord.File(image_path, filename="point_cloud.png")
            embed.set_image(url="attachment://point_cloud.png")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(image_path)
            except:
                pass

        elif output_type.lower() == "video":

            video_path = await asyncio.to_thread(crinkle_bot.dot_video, points)

            embed = discord.Embed(
                title="🎬 Point Cloud 360° Video",
                description=f"Sampled **{points}** points from mesh\nWatch the 360° rotating view!",
                color=0x9932cc
            )

            file = discord.File(video_path, filename="point_cloud_360.mp4")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(video_path)
            except:
                pass

        else:  

            pcd_path = await asyncio.to_thread(crinkle_bot.save_dot_mesh, points)

            embed = discord.Embed(
                title="📁 Point Cloud File",
                description=f"Sampled **{points}** points from mesh\nDownload the .ply file to view in your 3D software!",
                color=0x0099ff
            )

            file = discord.File(pcd_path, filename="point_cloud.ply")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(pcd_path)
            except:
                pass

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to process mesh: {str(e)}",
            color=0xff0000
        )
        await interaction.followup.send(embed=error_embed)
        print(f"Error in dot command: {e}")

@bot.tree.command(name="poly", description="Simplify the 3D mesh by reducing polygon count")
@app_commands.describe(
    simplify="Simplification factor (4 to 100, default: 16, higher = more simplified)",
    output_type="Choose output type: image, mesh file, or video"
)
async def poly_command(
    interaction: discord.Interaction, 
    simplify: Optional[int] = 16,
    output_type: Optional[str] = "image"
):

    if not crinkle_bot.has_mesh():
        await interaction.response.send_message("❌ No mesh loaded! Please upload a mesh first using `/upload`", ephemeral=True)
        return

    if simplify < 4 or simplify > 100:
        await interaction.response.send_message("❌ Simplify factor must be between 4 and 100", ephemeral=True)
        return

    if output_type.lower() not in ["image", "mesh", "video"]:
        await interaction.response.send_message("❌ Output type must be either 'image', 'mesh', or 'video'", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        if output_type.lower() == "image":

            image_path = await asyncio.to_thread(crinkle_bot.poly_mesh, simplify)

            embed = discord.Embed(
                title="🔺 Simplified Mesh Preview",
                description=f"Simplification factor: **{simplify}**",
                color=0xff6600
            )

            file = discord.File(image_path, filename="simplified_mesh.png")
            embed.set_image(url="attachment://simplified_mesh.png")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(image_path)
            except:
                pass

        elif output_type.lower() == "video":

            video_path = await asyncio.to_thread(crinkle_bot.poly_video, simplify)

            embed = discord.Embed(
                title="🎬 Simplified Mesh 360° Video",
                description=f"Simplification factor: **{simplify}**\nWatch the 360° rotating view!",
                color=0x9932cc
            )

            file = discord.File(video_path, filename="simplified_mesh_360.mp4")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(video_path)
            except:
                pass

        else:  

            mesh_path = await asyncio.to_thread(crinkle_bot.save_poly_mesh, simplify)

            embed = discord.Embed(
                title="📁 Simplified Mesh File",
                description=f"Simplification factor: **{simplify}**\nDownload the .obj file to view in your 3D software!",
                color=0x0099ff
            )

            file = discord.File(mesh_path, filename="simplified_mesh.obj")

            await interaction.followup.send(embed=embed, file=file)

            try:
                os.remove(mesh_path)
            except:
                pass

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to process mesh: {str(e)}",
            color=0xff0000
        )
        await interaction.followup.send(embed=error_embed)
        print(f"Error in poly command: {e}")

@bot.tree.command(name="upload", description="Upload a new 3D mesh file to use with the bot")
@app_commands.describe(
    mesh_file="Upload a 3D mesh file (.obj, .ply, .glb, .gltf, .stl, etc.)"
)
async def upload_command(
    interaction: discord.Interaction,
    mesh_file: discord.Attachment
):
    await interaction.response.defer()

    try:

        max_size = 25 * 1024 * 1024  
        if mesh_file.size > max_size:
            await interaction.followup.send("❌ File too large! Please upload a file smaller than 25MB.", ephemeral=True)
            return

        allowed_extensions = ['.obj', '.ply', '.glb', '.gltf', '.stl', '.off', '.xyz']
        file_ext = os.path.splitext(mesh_file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            await interaction.followup.send(
                f"❌ Unsupported file format! Please upload one of: {', '.join(allowed_extensions)}", 
                ephemeral=True
            )
            return

        temp_dir = tempfile.gettempdir()
        temp_filename = f"uploaded_mesh_{interaction.user.id}_{np.random.randint(1000, 9999)}{file_ext}"
        temp_path = os.path.join(temp_dir, temp_filename)

        await mesh_file.save(temp_path)
        print(f"Downloaded mesh file: {temp_path}")

        success = crinkle_bot.set_mesh(temp_path)

        if success:
            embed = discord.Embed(
                title="✅ Mesh Uploaded Successfully!",
                description=f"**File**: {mesh_file.filename}\n**Vertices**: {len(crinkle_bot.base_mesh.vertices)}\n**Triangles**: {len(crinkle_bot.base_mesh.triangles)}",
                color=0x00ff00
            )
            embed.add_field(
                name="📝 Note", 
                value="This mesh will be used for all subsequent commands until you upload a new one.",
                inline=False
            )

            await interaction.followup.send(embed=embed)

        else:

            try:
                os.remove(temp_path)
            except:
                pass

            await interaction.followup.send("❌ Failed to load the mesh file. Please check that it's a valid 3D mesh file.", ephemeral=True)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Upload Error",
            description=f"Failed to process uploaded file: {str(e)}",
            color=0xff0000
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        print(f"Error in upload command: {e}")

@bot.tree.command(name="info", description="Get information about the bot and mesh")
async def info_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 3D Mesh Bot Info",
        description="This bot applies various effects to 3D meshes using Open3D!",
        color=0x9932cc
    )

    embed.add_field(
        name="📋 Commands",
        value="`/upload` - Upload your own 3D mesh file\n`/crinkle` - Apply crinkle/noise effect to mesh\n`/dot` - Convert mesh to point cloud\n`/poly` - Simplify mesh by reducing polygons\n`/info` - Show this information",
        inline=False
    )

    embed.add_field(
        name="📤 Upload Parameters",
        value="**mesh_file**: Upload .obj, .ply, .glb, .gltf, .stl files (max 25MB)\nUploaded mesh will be used for all operations until reset.",
        inline=False
    )

    embed.add_field(
        name="⚙️ Crinkle Parameters",
        value="**noise**: 0.0 (no effect) to 1.0 (maximum crinkle)\n**output_type**: 'image' for preview, 'mesh' for 3D file, or 'video' for 360° rotation",
        inline=False
    )

    embed.add_field(
        name="🔵 Dot Parameters", 
        value="**points**: 100 to 10000 (number of points to sample)\n**output_type**: 'image' for preview, 'pointcloud' for .ply file, or 'video' for 360° rotation",
        inline=False
    )

    embed.add_field(
        name="🔺 Poly Parameters",
        value="**simplify**: 4 to 100 (simplification factor, higher = more simplified)\n**output_type**: 'image' for preview, 'mesh' for .obj file, or 'video' for 360° rotation", 
        inline=False
    )
    embed.add_field(
        name="🐛 Bugs/Improvements",
        value="Gif fails to output entire model 😥 & Implement Textures", 
        inline=False
    )

    if crinkle_bot.has_mesh():
        mesh_info = f"**Current Mesh**: {crinkle_bot.get_current_mesh_name()}\n**Vertices**: {len(crinkle_bot.base_mesh.vertices)}\n**Triangles**: {len(crinkle_bot.base_mesh.triangles)}"
    else:
        mesh_info = "**No mesh loaded** - Please upload a mesh using `/upload`"

    embed.add_field(name="📊 Current Mesh Stats", value=mesh_info, inline=False)

    await interaction.response.send_message(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `/` for slash commands like `/info`, `/crinkle`, `/dot`, `/poly`")
    else:
        print(f"Command error: {error}")

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!", 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    keep_alive()
    import dotenv
    dotenv.load_dotenv()

    print("[MAIN] Starting Discord bot...")

    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ Please set DISCORD_BOT_TOKEN in your .env file or environment variables")
        print("You can get a token from: https://discord.com/developers/applications")
    else:
        print("[MAIN] Connecting to Discord...")
        try:
            bot.run(token)
        except Exception as e:
            print(f"❌ Bot failed to start: {e}")