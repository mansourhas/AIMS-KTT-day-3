import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Create output directory
OUTPUT_DIR = './reports/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def draw_trend_bars(c, x, y, history):
    """Draws a tiny 3-bar chart to show progress over time visually."""
    max_height = 30
    bar_width = 8
    spacing = 4
    
    # Draw a faint baseline
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(1)
    c.line(x, y, x + (bar_width + spacing) * 3, y)

    for i, val in enumerate(history):
        h = max(3, val * max_height) # Minimum height of 3px so 0% is still visible
        bx = x + (bar_width + spacing) * i
        
        # Color the historical bars grey, and the current (last) bar blue to highlight 'now'
        if i == len(history) - 1:
            c.setFillColor(colors.HexColor("#2196F3")) # Blue
        else:
            c.setFillColor(colors.lightgrey)
            
        c.rect(bx, y, bar_width, h, fill=1, stroke=0)

def draw_visual_progress_bar(c, x, y, width, height, skill_data, icon_text):
    """Draws a visual 'battery' bar and a trend graph."""
    current_mastery = skill_data["current"]
    history = skill_data["history"]

    # 1. Draw the Subject Text/Icon (Safely using standard characters)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.dimgrey)
    c.drawString(x, y + 8, icon_text)
    
    # Add extra padding so the text doesn't touch the bar
    bar_x = x + 60 
    
    # 2. Draw the background outline (empty battery)
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(2)
    c.rect(bar_x, y, width, height, fill=0)
    
    # 3. Determine Color based on Current Mastery
    if current_mastery >= 0.8:
        fill_color = colors.HexColor("#4CAF50") # Strong Green (Mastered)
    elif current_mastery >= 0.4:
        fill_color = colors.HexColor("#FFC107") # Yellow/Gold (Growing)
    else:
        fill_color = colors.HexColor("#FF9800") # Orange (Just started)

    # 4. Draw the fill block
    fill_width = width * current_mastery
    c.setFillColor(fill_color)
    c.rect(bar_x, y, fill_width, height, fill=1, stroke=0)
    
    # 5. Add a Star if Mastered! (Using ZapfDingbats 'H' which is a star)
    if current_mastery >= 0.8:
        c.setFont("ZapfDingbats", 16)
        c.setFillColor(colors.goldenrod)
        c.drawString(bar_x + width + 10, y + 8, "H") # 'H' is a solid star in ZapfDingbats

    # 6. Draw the Trend Bars on the far right
    trend_x = bar_x + width + 40
    draw_trend_bars(c, trend_x, y, history)

def draw_smiley(c, x, y):
    """Draws a vector smiley face so we don't rely on emojis."""
    c.setFillColor(colors.gold)
    c.setStrokeColor(colors.orange)
    c.circle(x, y, 20, fill=1, stroke=1) # Face
    
    c.setFillColor(colors.black)
    c.circle(x - 7, y + 5, 2.5, fill=1) # Left eye
    c.circle(x + 7, y + 5, 2.5, fill=1) # Right eye
    
    # Smile arc
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.arc(x - 10, y - 10, x + 10, y + 5, startAng=190, extent=160)

def draw_bean(c, x, y):
    """Draws a simple bean shape for the footer instructions."""
    c.setFillColor(colors.saddlebrown)
    c.ellipse(x, y, x+12, y+18, fill=1, stroke=0)

def generate_visual_pdf(student_name, bkt_mastery_data):
    """Generates the robust, non-literate PDF report card."""
    file_path = os.path.join(OUTPUT_DIR, f"{student_name}_visual_report.pdf")
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.black)
    c.drawString(50, 730, f"Student: {student_name}")
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.gray)
    c.drawString(50, 705, "Visual Progress Report")

    # Overall Mood (Vector Graphic)
    avg_mastery = sum(d["current"] for d in bkt_mastery_data.values()) / len(bkt_mastery_data)
    if avg_mastery > 0.5:
        draw_smiley(c, 500, 730)

    # Column Headers for visual clarity
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.lightgrey)
    c.drawString(110, 650, "Current Skill Level")
    c.drawString(450, 650, "Recent Progress")

    # Skill Mapping
    skill_icons = {
        "counting": "1, 2, 3",  
        "addition": "[ + ]",      
        "subtraction": "[ - ]",     
        "number_sense": "[ < > ]",  
        "word_problem": "[ ? ]"    
    }

    # Draw the progress bars & trends
    y_position = 600
    for skill, data in bkt_mastery_data.items():
        icon = skill_icons.get(skill, "•")
        draw_visual_progress_bar(c, 50, y_position, width=280, height=25, skill_data=data, icon_text=icon)
        y_position -= 70 # Move down for the next row

    # Footer - Safe Vector Call to Actions
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 150, "At home please:")
    
    c.setFont("Helvetica", 14)
    # Instruction 1: Count beans
    draw_bean(c, 50, 110)
    c.drawString(65, 115, "+")
    draw_bean(c, 80, 110)
    c.drawString(105, 115, "(Count items together)")
    
    # Instruction 2: Praise (Using ZapfDingbats Checkmark and Star)
    c.setFont("ZapfDingbats", 16)
    c.setFillColor(colors.HexColor("#4CAF50"))
    c.drawString(50, 75, "4") # Checkmark
    c.setFillColor(colors.goldenrod)
    c.drawString(70, 75, "H") # Star
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawString(95, 75, "(Praise their hard work)")

    c.save()
    print(f"✅ Visual PDF generated: {file_path}")

# ==========================================
# QUICK TEST WITH TREND DATA
# ==========================================
if __name__ == "__main__":
    # Simulated data: Includes 'current' mastery, and 'history' (last 3 sessions)
    mock_student_mastery = {
        "counting": {"current": 0.95, "history": [0.60, 0.80, 0.95]},      # Going up!
        "addition": {"current": 0.60, "history": [0.60, 0.55, 0.60]},      # Flat/Struggling slightly
        "subtraction": {"current": 0.25, "history": [0.05, 0.15, 0.25]},   # Slowly learning
        "number_sense": {"current": 0.85, "history": [0.30, 0.60, 0.85]},  # Fast learner
        "word_problem": {"current": 0.10, "history": [0.10, 0.10, 0.10]}   # Stuck
    }
    
    generate_visual_pdf("Uwase", mock_student_mastery)