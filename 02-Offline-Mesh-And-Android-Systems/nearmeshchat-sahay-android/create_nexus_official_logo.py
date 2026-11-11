import math
from PIL import Image, ImageDraw, ImageFont

def generate_nexus_logo():
    size = (512, 512)
    img = Image.new("RGBA", size, (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    # Draw Outer Metallic Circle Ring
    cx, cy = 256, 220
    r_outer = 160
    
    # Outer Glow Ring
    for i in range(12, 0, -1):
        alpha = int(40 - i * 3)
        draw.ellipse([cx - r_outer - i*2, cy - r_outer - i*2, cx + r_outer + i*2, cy + r_outer + i*2], 
                     outline=(34, 197, 94, max(0, alpha)), width=3)

    # Metallic Silver Border Ring
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], 
                 outline=(226, 232, 240, 255), width=6)

    # Hexagon Nodes (6 points)
    hex_nodes = []
    r_hex = 110
    for angle_deg in range(0, 360, 60):
        rad = math.radians(angle_deg - 90)
        nx = cx + r_hex * math.cos(rad)
        ny = cy + r_hex * math.sin(rad)
        hex_nodes.append((nx, ny))

    # Draw Outer Hexagon Lines (Green)
    for i in range(6):
        n1 = hex_nodes[i]
        n2 = hex_nodes[(i + 1) % 6]
        draw.line([n1, n2], fill=(34, 197, 94, 255), width=4)

    # Draw Central Node to Satellite Rays (Cyber Cyan / Emerald)
    for node in hex_nodes:
        draw.line([(cx, cy), node], fill=(6, 182, 212, 255), width=3)

    # Draw Central Node
    r_center = 20
    draw.ellipse([cx - r_center, cy - r_center, cx + r_center, cy + r_center], 
                 fill=(34, 197, 94, 255), outline=(255, 255, 255, 255), width=3)

    # Draw Satellite Nodes
    r_sat = 14
    for node in hex_nodes:
        nx, ny = node
        draw.ellipse([nx - r_sat, ny - r_sat, nx + r_sat, ny + r_sat], 
                     fill=(34, 197, 94, 255), outline=(226, 232, 240, 255), width=3)

    # Save Official Nexus Logo
    output_path = r"c:\Users\abdul\AndroidStudioProjects\NearMeshChat\nexus_official_logo.png"
    img.save(output_path)
    print(f"Generated official Nexus logo at {output_path}")

if __name__ == "__main__":
    generate_nexus_logo()
