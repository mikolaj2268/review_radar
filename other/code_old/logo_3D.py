from PIL import Image, ImageOps
import streamlit as st
import base64

# Path to the logo
logo_path = "assets/images/logo.png"

# Utility function for glowing HTML
def glowing_logo_html(image_url):
    return f"""
    <style>
      @keyframes glow {{
        0% {{ box-shadow: 0 0 10px #ff66cc, 0 0 20px #ff66cc; }}
        50% {{ box-shadow: 0 0 20px #ff99cc, 0 0 30px #ff99cc; }}
        100% {{ box-shadow: 0 0 10px #ff66cc, 0 0 20px #ff66cc; }}
      }}
      .logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
      }}
      .logo {{
        animation: glow 2s infinite alternate;
        border-radius: 20px;
        background: #222;
        padding: 10px;
      }}
    </style>
    <div class="logo-container">
      <img class="logo" src="{image_url}" alt="Glowing Logo" width="200">
    </div>
    """

# Utility function for starry animation HTML
def starry_logo_html(image_url):
    return f"""
    <style>
      canvas {{
        background: #000;
        display: block;
        margin: 0 auto;
        border-radius: 20px;
      }}
    </style>
    <div style="position: relative; text-align: center;">
      <canvas id="canvas"></canvas>
      <img src="{image_url}" alt="Logo" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 200px;">
    </div>
    <script>
      const canvas = document.getElementById('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = 400;
      canvas.height = 400;

      function getRandomInt(min, max) {{
        return Math.floor(Math.random() * (max - min + 1)) + min;
      }}

      const stars = Array(100).fill().map(() => {{
        return {{
          x: getRandomInt(0, canvas.width),
          y: getRandomInt(0, canvas.height),
          r: Math.random() * 1.5 + 0.5,
          speed: Math.random() * 0.05 + 0.01
        }};
      }});

      function drawStars() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        stars.forEach(star => {{
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
          ctx.fillStyle = 'white';
          ctx.fill();
          star.y += star.speed;
          if (star.y > canvas.height) {{
            star.y = 0;
            star.x = getRandomInt(0, canvas.width);
          }}
        }});
        requestAnimationFrame(drawStars);
      }}

      drawStars();
    </script>
    """

# Utility function to change background color
def change_logo_background(image_path, color):
    img = Image.open(image_path).convert("RGBA")
    bg = Image.new("RGBA", img.size, color)
    img_with_bg = Image.alpha_composite(bg, img)
    return img_with_bg



# App title
st.title("Enhanced Logo Display Ideas")

# Convert the logo to base64 for embedding
with open(logo_path, "rb") as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode()

# Glowing Effect Section
st.subheader("1. Glowing Effect")
st.components.v1.html(glowing_logo_html(f"data:image/png;base64,{logo_base64}"), height=400)

# Interactive Background Section
st.subheader("2. Interactive Background")
bg_color = st.color_picker("Pick a background color", "#000000")
modified_logo = change_logo_background(logo_path, bg_color)
st.image(modified_logo, caption="Logo with Custom Background", use_column_width=True)

# Starry Animation Section
st.subheader("3. Starry Animation")
st.components.v1.html(starry_logo_html(f"data:image/png;base64,{logo_base64}"), height=400)

# Footer
st.markdown("---")
st.markdown("Feel free to experiment with these enhancements for your logo!")
