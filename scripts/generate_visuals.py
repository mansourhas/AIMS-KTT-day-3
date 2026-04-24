import json
import os
import math
from PIL import Image, ImageDraw, ImageFont

# Paths
CURRICULUM_FILE = './dataset/generated/expanded_curriculum.json'
OUTPUT_DIR = './dataset/generated/visuals/'

# Map nouns to Emojis instead of colors
EMOJI_MAP = {
    "apples": "🍎",
    "mangoes": "🥭",
    "goats": "🐐",
    "beans": "🫘",
    "stones": "🪨",
    "cows": "🐄"
}

def get_large_font(size=60):
    """Attempts to load a large TrueType font for regular text/numbers."""
    font_paths = [
        "arial.ttf",                                        # Standard Windows
        "C:\\Windows\\Fonts\\arial.ttf",                    # Explicit Windows
        "/Library/Fonts/Arial.ttf",                         # Mac
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"   # Linux
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
    return ImageFont.load_default()

def get_emoji_font(size=50):
    """Attempts to load an OS-specific emoji font."""
    font_paths = [
        "seguiemj.ttf",                                  # Windows
        "C:\\Windows\\Fonts\\seguiemj.ttf",              # Explicit Windows
        "/System/Library/Fonts/Apple Color Emoji.ttc",   # Mac
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf" # Linux
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
    print("Warning: Could not find an Emoji font on your system. Emojis might not render.")
    return ImageFont.load_default()

def create_canvas(width=800, height=400):
    """Creates a clean white canvas."""
    return Image.new('RGB', (width, height), 'white')

def draw_items(draw, count, noun, box_x, box_y, box_w, box_h, emoji_font):
    """Draws emojis dynamically scaled to fit within the provided bounding box."""
    if count <= 0: return
    
    emoji_char = EMOJI_MAP.get(noun, "❓")
    
    # Calculate an optimal grid layout to fit the items in the box
    cols = math.ceil(math.sqrt(count * (box_w / box_h)))
    rows = math.ceil(count / cols)
    
    cell_w = box_w / cols
    cell_h = box_h / rows
    
    # Calculate total grid size to center it in the box
    grid_w = cols * cell_w
    grid_h = rows * cell_h
    start_x = box_x + (box_w - grid_w) / 2
    start_y = box_y + (box_h - grid_h) / 2

    for i in range(count):
        r = i // cols
        c = i % cols
        
        # Calculate top-left point for this text cell, with a slight offset to center the character
        cx = start_x + c * cell_w + (cell_w * 0.1)
        cy = start_y + r * cell_h + (cell_h * 0.1)
        
        # Draw the emoji. 
        # Note: embedded_color=True ensures modern Pillow renders the color versions
        try:
            draw.text((cx, cy), emoji_char, font=emoji_font, embedded_color=True, fill="black")
        except TypeError:
            # Fallback if using an older version of Pillow that doesn't support embedded_color
            draw.text((cx, cy), emoji_char, font=emoji_font, fill="black")

def generate_image_from_tag(visual_tag):
    """Parses the tag and draws it using emojis."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    big_font = get_large_font(size=70)
    emoji_font = get_emoji_font(size=50) # Tweak size if emojis look too big/small
    
    parts = visual_tag.split('_')
    
    try:
        # Handle Word Problems (e.g., 'apples_word_add_4_5')
        if "word" in parts:
            noun = parts[0]
            a, b = int(parts[-2]), int(parts[-1])
            draw_items(draw, a, noun, box_x=50, box_y=50, box_w=300, box_h=300, emoji_font=emoji_font)
            draw_items(draw, b, noun, box_x=450, box_y=50, box_w=300, box_h=300, emoji_font=emoji_font)
            draw.text((375, 150), "+", fill="black", font=big_font)

        # Handle Comparisons (e.g., 'compare_12_8')
        elif parts[0] == "compare":
            a, b = int(parts[1]), int(parts[2])
            draw.text((150, 150), str(a), fill="blue", font=big_font)
            draw.text((350, 160), "vs", fill="black", font=get_large_font(size=50))
            draw.text((600, 150), str(b), fill="red", font=big_font)

        # Handle Operations (e.g., 'mangoes_4_plus_5' or 'goats_8_minus_3')
        elif "plus" in parts or "minus" in parts:
            noun = parts[0]
            op_idx = parts.index("plus") if "plus" in parts else parts.index("minus")
            a, b = int(parts[op_idx - 1]), int(parts[op_idx + 1])
            op_symbol = "+" if "plus" in parts else "-"
            
            draw_items(draw, a, noun, box_x=50, box_y=50, box_w=300, box_h=300, emoji_font=emoji_font)
            draw.text((375, 150), op_symbol, fill="black", font=big_font)
            draw_items(draw, b, noun, box_x=450, box_y=50, box_w=300, box_h=300, emoji_font=emoji_font)

        # Handle Simple Counting (e.g., 'stones_14')
        else:
            noun, count = parts[0], int(parts[1])
            # Use most of the canvas as the bounding box
            draw_items(draw, count, noun, box_x=50, box_y=50, box_w=700, box_h=300, emoji_font=emoji_font)

    except Exception as e:
        print(f"Failed to parse or draw {visual_tag}: {e}")
        draw.text((50, 50), f"Error generating: {visual_tag}", fill="red")

    return img

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists(CURRICULUM_FILE):
        print(f"Error: Could not find {CURRICULUM_FILE}. Make sure the data generator has been run.")
        return

    with open(CURRICULUM_FILE, 'r', encoding='utf-8') as f:
        curriculum = json.load(f)
        
    # Safely extract unique tags and warn about missing ones
    unique_tags = set()
    for item in curriculum:
        if 'visual' in item and item['visual']:
            unique_tags.add(item['visual'])
        else:
            print(f"Warning: Item {item.get('id', 'Unknown')} is missing a 'visual' tag. Skipping.")
    
    print(f"Generating {len(unique_tags)} unique visual assets...")
    
    for tag in unique_tags:
        img = generate_image_from_tag(tag)
        save_path = os.path.join(OUTPUT_DIR, f"{tag}.png")
        img.save(save_path)
        
    print(f"Done! Check the '{OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    main()