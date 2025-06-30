# 3D Model Discord Bot

A Discord bot that allows users to upload 3D models and apply various effects using Open3D, including 360° video rendering.

## Features

### Upload & Render Commands
- `/upload` - Upload a 3D model file (.obj, .ply, .glb, .gltf, .stl, .off, .xyz, .pcd)
- `/render3d` - Simple 3D model rendering from multiple angles (8 static views)

### Effect Commands (Require uploaded mesh)
- `/crinkle` - Apply crinkle effect with noise
  - **noise**: Noise level (0.0 to 1.0) 
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

## Output Types

- **image**: Generates a PNG preview of the effect
- **video**: Generates a 360° rotating MP4 video (2-3 seconds)
- **mesh**: Generates a downloadable .obj file

## 360° Video Features

- **Smooth Orbital Rotation**: Camera orbits around the model center
- **Automatic Centering**: Model is automatically centered and scaled
- **High Quality**: 800x600 resolution at 24fps for smooth playback
- **Multiple Effects**: All effects (crinkle, dot, poly) support video output

## Notes

- **Upload Required**: Bot requires a mesh upload before effects can be applied
- **Temporary Files**: All generated files are cleaned up automatically  
- **Mesh Validation**: Bot validates mesh integrity before processing
- **Error Handling**: Clear error messages for invalid files or missing uploads
