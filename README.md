# 3D Model Discord Bot

A Discord bot that allows users to upload 3D models and apply various effects using Open3D, including 360° video rendering.

### To Find Out How to Use the Bot Skip Past My Dev Log

# DEV LOG 1. 🚀
---
I Used open3D library with documentation + AI to develop three functions. I initially built this bot to provide myself a way to develop low poly renders as I have recently begun 3D modeling and printing for my past hackathons and as a personal hobby at my local library.

Since I am interested in hardware, 3D printing is obviously crucial to polish my product. For example, for an AI camera I developed I built a case to hold the design. However, I think it was too complex and may also have greatly increased print times due to inefficient design.

As a result, I thought that a discord bot to convert my 3D models and others would be useful. The project is not fully polished, however, majority of the things I wanted to implement work. In addition, you can notice there are two other functions dot and crinkle which are more humorous features I discovered on the open3d docs, so I was like why not!

Furthermore, this was my second time building a discord bot, so it was challenging to implement an already difficult task of rendering images, models, and videos of the finished product. While I did use AI for assistance, you can notice in the tests folder, I wrote the core features of the code. The reason for the length of code is due to discord's nit picky lines of code, requiring numerous lines of code for the same feature that can be written in under 10 lines of code.

In the future, if I continue to work on it, I will build a working website to go alongside gifs and other interactive features.

One key feature is textures. Currently, I am unsure why, but there is rendering issues when I try to texturized the model. I may be required to use Blender's API if I plan to have texturized models. In addition, I am eyeing an interactive 3D model either on Discord itself using a bunch of images from various angles and then the user can use buttons to play with the perspective. Alternatively, I can link them a web browser and create a playground for them to use.

UPDATE: It seems I CANNOT use open3D in order to keep the discord bot up on render...For now, if you want to use the app, you will have to follow the instructions below and run `python bot.py`
---

## Features

### Upload & Render Commands
- `/upload` - Upload a 3D model file (.obj, .ply, .glb, .gltf, .stl, .off, .xyz, .pcd)
- `/render3d` - Simple 3D model rendering from multiple angles (8 static views)

### Effect Commands (Require uploaded mesh)
- `/crinkle` - Apply crinkle effect with noise
  - **noise**: Noise level (0.0 to 1.0) - I recommend you start with a lower number
  - **output_type**: "image", "video", or "mesh"
- `/dot` - Create dotted mesh effect
  - **output_type**: "image", "video", or "mesh"  
- `/poly` - Simplify mesh into low-poly version
  - **simplification_factor**: How much to simplify (higher = more simplified)
  - **output_type**: "image", "video", or "mesh"

### Info Commands
- `/info` - Get bot information and current mesh statistics
- `/help3d` - Get help with all available commands

## Key Features

✅ **Dynamic Mesh Loading**: No default mesh required - upload any 3D model to start
✅ **360° Video Rendering**: Smooth orbital camera rotation for video effects  
✅ **Multiple File Formats**: Support for .obj, .ply, .glb, .gltf, .stl, .off, .xyz, .pcd
✅ **Multiple Output Types**: Images, 360° videos, or downloadable mesh files
✅ **Automatic Cleanup**: Temporary files are cleaned up automatically
✅ **File Size Validation**: 25MB upload limit with format checking

## Setup

### 1. Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token

### 2. Configure the Bot

1. Edit the `.env` file and replace `your_bot_token_here` with your actual bot token:
   ```
   DISCORD_BOT_TOKEN=your_actual_token_here
   ```

### 3. Install Dependencies

Make sure you have Python 3.8+ installed, then run:
```bash
pip install -r requirements.txt
```

### 4. Invite Bot to Server

1. In Discord Developer Portal, go to OAuth2 > URL Generator
2. Select scopes: `bot` and `applications.commands`
3. Select bot permissions: `Send Messages`, `Use Slash Commands`, `Attach Files`
4. Copy the generated URL and open it to invite the bot to your server

### 5. Run the Bot

```bash
python discord_bot.py
```

## Usage

Once the bot is running and invited to your server:

1. **Upload a 3D model first**:
   - Use `/upload` to upload your 3D model file
   - Supported formats: .obj, .ply, .glb, .gltf, .stl, .off, .xyz, .pcd
   - Maximum file size: 25MB

2. **Apply effects to your uploaded model**:
   - `/crinkle noise:0.3 output_type:video` - Crinkle effect with 360° video
   - `/dot output_type:image` - Dotted mesh effect as image
   - `/poly simplification_factor:10 output_type:mesh` - Low-poly version as downloadable file

3. **Use info commands**:
   - `/info` - See current mesh information and bot statistics
   - `/help3d` - Get help with all commands

## Notes

- **Upload Required**: Bot requires a mesh upload before effects can be applied
- **Temporary Files**: All generated files are cleaned up automatically  
- **Mesh Validation**: Bot validates mesh integrity before processing
- **Error Handling**: Clear error messages for invalid files or missing uploads
