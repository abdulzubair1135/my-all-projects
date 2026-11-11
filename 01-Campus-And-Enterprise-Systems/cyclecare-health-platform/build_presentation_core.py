# -*- coding: utf-8 -*-
"""
CycleCare — Master Project Presentation Generator
Generates:
  1. CycleCare_Project_Presentation.pptx (23 Widescreen 16:9 Slides)
  2. CycleCare_Presentation_PDF.pdf (via Windows PowerPoint COM)
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

# Directory Paths
WORKSPACE_DIR = os.getcwd()
ASSET_DIR = os.path.join(WORKSPACE_DIR, "CycleCare_Presentation_Assets")
PPTX_OUT = os.path.join(WORKSPACE_DIR, "CycleCare_Project_Presentation.pptx")
PDF_OUT = os.path.join(WORKSPACE_DIR, "CycleCare_Presentation_PDF.pdf")

# Neumorphic Wellness Dashboard Theme Palette
COLOR_BG = RGBColor(16, 23, 41)          # Deep Navy #101729
COLOR_CARD = RGBColor(32, 43, 62)        # Navy Card #202B3E
COLOR_CARD_ALT = RGBColor(25, 34, 50)    # Darker Navy Card #192232
COLOR_CARD_HL = RGBColor(37, 51, 74)     # Highlight Navy Card #25334A
COLOR_BORDER = RGBColor(44, 55, 74)      # Subtle Border #2C374A
COLOR_BORDER_HL = RGBColor(65, 80, 105)  # Subtle Accent Border
COLOR_PINK = RGBColor(212, 20, 99)       # Primary Pink #D41463
COLOR_ROSE = RGBColor(244, 63, 94)       # Bright Rose #F43F5E
COLOR_CYAN = RGBColor(18, 184, 199)      # Accent Cyan #12B8C7
COLOR_GREEN = RGBColor(22, 160, 133)     # Success Green #16A085
COLOR_PURPLE = RGBColor(139, 92, 246)    # Accent Violet #8B5CF6
COLOR_AMBER = RGBColor(245, 158, 11)     # Warning Amber #F59E0B
COLOR_CRIMSON = RGBColor(225, 29, 72)    # Menstrual Crimson #E11D48
COLOR_WHITE = RGBColor(247, 248, 252)    # Crisp White #F7F8FC
COLOR_SLATE = RGBColor(183, 193, 210)    # Muted Slate #B7C1D2
COLOR_DIM = RGBColor(126, 139, 159)      # Dim Slate #7E8B9F

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"

# Initialize Presentation
prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide, color=COLOR_BG):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def create_card(slide, left, top, width, height, bg_color=COLOR_CARD, border_color=COLOR_BORDER, border_width=1.0):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
    else:
        shape.line.fill.background()
    return shape

def create_pill(slide, left, top, width, height, text, bg_color, text_color=COLOR_WHITE, font_size=9, bold=True):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = FONT_HEADING
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = text_color
    p.alignment = PP_ALIGN.CENTER
    return shape

def add_header(slide, stage_name, title_text, subtitle_text, slide_num, total_slides=23, badge_color=COLOR_PINK):
    # Top Stage Pill
    create_pill(slide, Inches(0.8), Inches(0.4), Inches(3.6), Inches(0.32), stage_name.upper(), badge_color, font_size=8.5)
    
    # Slide Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(10.5), Inches(0.55))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE
    
    # Subtitle
    tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.30), Inches(10.5), Inches(0.35))
    tf_sub = tb_sub.text_frame
    tf_sub.word_wrap = True
    tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = subtitle_text
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_SLATE
    
    # Subtle Top Accent Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.68), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_BORDER
    line.line.fill.background()
    
    # Footer Slide Number
    tb_num = slide.shapes.add_textbox(Inches(9.5), Inches(7.05), Inches(3.0), Inches(0.3))
    tf_num = tb_num.text_frame
    tf_num.word_wrap = False
    tf_num.margin_left = tf_num.margin_top = tf_num.margin_right = tf_num.margin_bottom = 0
    p_num = tf_num.paragraphs[0]
    p_num.text = f"Slide {slide_num} of {total_slides}  |  CycleCare Capstone"
    p_num.font.name = FONT_BODY
    p_num.font.size = Pt(9.5)
    p_num.font.color.rgb = COLOR_DIM
    p_num.alignment = PP_ALIGN.RIGHT

def add_image_fit(slide, img_name, left, top, max_w, max_h, border_color=COLOR_BORDER):
    img_path = os.path.join(ASSET_DIR, img_name)
    if not os.path.exists(img_path):
        print(f"Warning: Image {img_name} not found at {img_path}")
        return None
    try:
        with Image.open(img_path) as im:
            orig_w, orig_h = im.size
        scale = min(max_w / orig_w, max_h / orig_h)
        scaled_w = orig_w * scale
        scaled_h = orig_h * scale
        pos_x = left + (max_w - scaled_w) / 2
        pos_y = top + (max_h - scaled_h) / 2
        
        # Border container
        if border_color:
            bg_pad = Inches(0.04)
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(pos_x) - bg_pad, Inches(pos_y) - bg_pad,
                Inches(scaled_w) + bg_pad*2, Inches(scaled_h) + bg_pad*2
            )
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD
            card.line.color.rgb = border_color
            card.line.width = Pt(1.0)
            
        pic = slide.shapes.add_picture(img_path, Inches(pos_x), Inches(pos_y), width=Inches(scaled_w), height=Inches(scaled_h))
        return pic
    except Exception as e:
        print(f"Error loading image {img_name}: {e}")
        return None

print("Presentation Builder initialized successfully.")
