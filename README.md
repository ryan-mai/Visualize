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
- `/upload` - Upload a 3D model file (any works, i.e. .obj, .glb, etc.)

### Effect Commands (Require uploaded mesh)
- `/crinkle` - Apply crinkle effect with noise
  - **noise**: Noise level (0.0 to 1.0) - Recommended to start lower
- `/dot` - Creates a lot of dots to form the 3D model
- `/poly` - Simplify 3D model into low poly!
  - **simplification_factor**: How much to simplify
- **Output Type**: "image", "video", or "mesh"

### Helpful Commands
- `/info` - Get bot information and current mesh statistics

## Setup
### 1. Clone Github Repo
- `github clone https://github.com/ryan-mai/Visualize.git`

### 2. Create a Discord Application
- Go to [Discord Developer Portal](https://discord.com/developers/applications) > New Application > My Application > Bot > Token
- Bot > Bot Permissions: `Send Messages`, `Use Slash Commands`, `Attach Files` or https://discord.com/oauth2/authorize?client_id=<**YOUR_CLIENT_ID**>&scope=bot%20applications.commands&permissions=2147518464
- Now invite it to your cool

### 4. Install Dependencies
- Assuming you have python installed, run `pip install -r requirements.txt`

### 5. Run the Bot

- BOOM Done: ```python discord_bot.py```

