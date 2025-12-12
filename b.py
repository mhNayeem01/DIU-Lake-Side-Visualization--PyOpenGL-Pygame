"""
DIU Lake Side Visualization - Computer Graphics Project
========================================================

This project creates a 2D visualization of the DIU (Daffodil International University) 
lakeside scene using OpenGL and Pygame. It demonstrates various computer graphics 
algorithms and techniques.

Features:
- DDA Line Drawing Algorithm for text rendering
- Midpoint Circle Algorithm (Bresenham's) for circles and text
- Multiple animated objects (buses, kayaks, plane, fish, deer, clouds)
- Realistic scene elements (building, trees, gazebos, monument, flowers)
- Transparency effects using OpenGL blending

Author: PixelForge
Course: Computer Graphics
Submitted To: Md Mehefujur Rahman Mubin
Institution: Daffodil International University
"""

import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import cos, sin, pi

# ------------------ Window Configuration ------------------
# Window dimensions for the visualization
WINDOW_WIDTH = 1000  # Width of the window in pixels
WINDOW_HEIGHT = 600  # Height of the window in pixels

# ------------------ Animation State Variables ------------------
# These variables control the positions and states of all animated objects

# Bus animations - two buses moving from left to right
bus_x = -200.0  # Position of the first yellow bus
bus2_x = -600.0  # Position of the second red bus (starts behind first)

# Kayak animations - three kayaks moving from right to left
kayak1_x = 200.0  # Position of the first kayak (red)
kayak2_x = 500.0  # Position of the second kayak (orange)
kayak3_x = 800.0  # Position of the third kayak (blue)

# Plane animation - plane flying across the sky
plane_x = -200.0  # Position of the PT-6 aircraft

# Fish animation - four fish jumping out of water at different positions
fish_positions = [(100, 80), (300, 60), (600, 90), (850, 70)]  # X,Y coordinates of each fish
fish_colors = [
    (0.9, 0.4, 0.1),   # Orange fish - RGB color values
    (0.2, 0.6, 0.9),   # Blue fish
    (0.9, 0.8, 0.2),   # Yellow fish
    (0.8, 0.3, 0.5),   # Pink fish
]
fish_jump_states = [0, 0, 0, 0]  # Current jump frame (0 = underwater, 1-40 = jumping)
fish_timers = [0, 0, 0, 0]  # Timers to control when each fish jumps

# Deer animations - two deer walking back and forth on the lakeside
deer1_x = 320.0  # Position of the first deer
deer2_x = 380.0  # Position of the second deer
deer_direction = 1  # Movement direction: 1 for right, -1 for left

# Cloud animation - slowly moving clouds across the sky
cloud_offset = 0.0  # Horizontal offset for cloud movement


# ------------------ Basic Drawing Helper Functions ------------------
# These functions provide simple primitives for drawing shapes

def draw_rect(x1, y1, x2, y2, color):
    """
    Draw a filled rectangle.
    
    Parameters:
    x1, y1 - Bottom-left corner coordinates
    x2, y2 - Top-right corner coordinates
    color - RGB tuple (r, g, b) with values from 0.0 to 1.0
    """
    glColor3f(*color)  # Set the drawing color
    glBegin(GL_QUADS)  # Start drawing a quadrilateral
    glVertex2f(x1, y1)  # Bottom-left vertex
    glVertex2f(x2, y1)  # Bottom-right vertex
    glVertex2f(x2, y2)  # Top-right vertex
    glVertex2f(x1, y2)  # Top-left vertex
    glEnd()  # Finish drawing


def draw_polygon(points, color):
    """
    Draw a filled polygon with any number of vertices.
    
    Parameters:
    points - List of (x, y) tuples representing polygon vertices
    color - RGB tuple (r, g, b)
    """
    glColor3f(*color)
    glBegin(GL_POLYGON)  # Start drawing a polygon
    for x, y in points:
        glVertex2f(x, y)  # Add each vertex
    glEnd()


def draw_circle(cx, cy, radius, color, segments=32):
    """
    Draw a filled circle using triangle fan approximation.
    Supports both RGB and RGBA colors for transparency.
    
    Parameters:
    cx, cy - Center coordinates of the circle
    radius - Radius of the circle
    color - RGB tuple (r, g, b) or RGBA tuple (r, g, b, a)
    segments - Number of line segments to approximate the circle (higher = smoother)
    """
    # Check if color has alpha channel (transparency)
    if len(color) == 4:
        glColor4f(*color)  # Use RGBA with transparency
    else:
        glColor3f(*color)  # Use RGB without transparency
    
    glBegin(GL_TRIANGLE_FAN)  # Draw circle as a fan of triangles from center
    glVertex2f(cx, cy)  # Center point of the circle
    
    # Generate vertices around the circle
    for i in range(segments + 1):
        angle = 2 * pi * i / segments  # Calculate angle for this segment
        x = cx + radius * cos(angle)  # X coordinate on circle circumference
        y = cy + radius * sin(angle)  # Y coordinate on circle circumference
        glVertex2f(x, y)
    glEnd()


# ------------------ DDA Line Drawing Algorithm ------------------
def draw_line_dda(x1, y1, x2, y2, color):
    """
    DDA (Digital Differential Analyzer) Line Drawing Algorithm
    
    This is a computer graphics algorithm for drawing lines by calculating
    intermediate points using incremental calculations. It's more efficient
    than calculating y = mx + b for each point.
    
    Algorithm:
    1. Calculate dx and dy (differences in x and y)
    2. Determine number of steps based on the larger difference
    3. Calculate increments for x and y per step
    4. Starting from (x1, y1), increment by calculated amounts
    5. Round to integer coordinates and plot each point
    
    Parameters:
    x1, y1 - Starting point coordinates
    x2, y2 - Ending point coordinates
    color - RGB tuple for line color
    """
    glColor3f(*color)
    glBegin(GL_POINTS)  # Draw line as individual points
    
    # Calculate differences in x and y
    dx = x2 - x1
    dy = y2 - y1
    
    # Determine number of steps: use the larger difference to ensure no gaps
    steps = int(max(abs(dx), abs(dy)))
    
    if steps == 0:
        # If start and end are the same point, just draw that point
        glVertex2f(x1, y1)
    else:
        # Calculate how much to increment x and y in each step
        x_inc = dx / steps  # X increment per step
        y_inc = dy / steps  # Y increment per step
        
        # Starting point
        x = x1
        y = y1
        
        # Draw all points along the line
        for _ in range(steps + 1):
            glVertex2f(round(x), round(y))  # Round to nearest integer pixel
            x += x_inc
            y += y_inc
    
    glEnd()


# ------------------ Midpoint Circle Drawing Algorithm ------------------
def draw_circle_midpoint(cx, cy, radius, color, fill=True):
    """
    Midpoint Circle Algorithm (Bresenham's Circle Algorithm)
    Draws a circle using the midpoint decision parameter
    More efficient than trigonometric approach
    Supports both RGB and RGBA colors for transparency
    """
    if fill:
        # For filled circles, draw using the original method
        draw_circle(cx, cy, radius, color)
    else:
        # For outline circles using midpoint algorithm
        if len(color) == 4:
            glColor4f(*color)  # RGBA with transparency
        else:
            glColor3f(*color)  # RGB
        glBegin(GL_POINTS)
        
        x = 0
        y = radius
        d = 1 - radius  # Initial decision parameter
        
        # Plot 8-way symmetry points
        def plot_circle_points(xc, yc, x, y):
            glVertex2f(xc + x, yc + y)
            glVertex2f(xc - x, yc + y)
            glVertex2f(xc + x, yc - y)
            glVertex2f(xc - x, yc - y)
            glVertex2f(xc + y, yc + x)
            glVertex2f(xc - y, yc + x)
            glVertex2f(xc + y, yc - x)
            glVertex2f(xc - y, yc - x)
        
        while x <= y:
            plot_circle_points(cx, cy, x, y)
            
            if d < 0:
                d = d + 2 * x + 3
            else:
                d = d + 2 * (x - y) + 5
                y -= 1
            x += 1
        
        glEnd()


def draw_text(text, x, y, scale=1.0):
    """Simple block letter text using rectangles."""
    # Letter patterns (5x7 grid, 1=filled, 0=empty)
    letters = {
        'D': [
            [1,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,0],
        ],
        'I': [
            [1,1,1,1,1],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [1,1,1,1,1],
        ],
        'U': [
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0],
        ],
    }
    
    offset_x = 0
    for char in text:
        if char in letters:
            pattern = letters[char]
            for row in range(7):
                for col in range(5):
                    if pattern[row][col]:
                        px = x + offset_x + col * 2 * scale
                        py = y + (6 - row) * 2 * scale
                        draw_rect(px, py, px + 1.5 * scale, py + 1.5 * scale, (1, 1, 1))
            offset_x += 12 * scale
        elif char == ' ':
            offset_x += 8 * scale


def draw_text_dda(text, x, y, scale=1.0, color=(0, 0, 0), char_spacing=1.0):
    """
    Draw text using DDA Line Drawing Algorithm
    More sophisticated text rendering with line segments
    Coordinates: y goes UP (0 at bottom, 7 at top of letter)
    char_spacing: multiplier for spacing between characters
    """
    # Complete alphabet patterns using line segments
    # Each letter defined as list of line segments: [(x1,y1,x2,y2), ...]
    # y-axis: 0=bottom, 7=top of letter (normal orientation)
    letter_lines = {
        'D': [(0,7,0,0), (0,7,3,7), (3,7,4,6), (4,6,4,1), (4,1,3,0), (3,0,0,0)],
        'A': [(0,0,2,7), (2,7,4,0), (1,3,3,3)],
        'F': [(0,0,0,7), (0,7,4,7), (0,4,3,4)],
        'O': [(1,7,3,7), (0,6,0,1), (4,6,4,1), (1,0,3,0), (0,6,1,7), (3,7,4,6), (0,1,1,0), (3,0,4,1)],
        'I': [(0,7,4,7), (2,7,2,0), (0,0,4,0)],
        'L': [(0,7,0,0), (0,0,4,0)],
        'N': [(0,0,0,7), (0,7,4,0), (4,0,4,7)],
        'T': [(0,7,4,7), (2,7,2,0)],
        'E': [(0,7,0,0), (0,7,4,7), (0,4,3,4), (0,0,4,0)],
        'R': [(0,0,0,7), (0,7,3,7), (3,7,4,6), (4,6,4,4), (4,4,3,3), (3,3,0,3), (2,3,4,0)],
        'S': [(4,6,3,7), (3,7,1,7), (1,7,0,6), (0,6,0,4), (0,4,1,3), (1,3,3,3), (3,3,4,2), (4,2,4,1), (4,1,3,0), (3,0,1,0), (1,0,0,1)],
        'U': [(0,7,0,1), (0,1,1,0), (1,0,3,0), (3,0,4,1), (4,1,4,7)],
        'V': [(0,7,2,0), (2,0,4,7)],
        'Y': [(0,7,2,4), (4,7,2,4), (2,4,2,0)],
    }
    
    offset_x = 0
    
    for char in text.upper():
        if char in letter_lines:
            lines = letter_lines[char]
            for (x1, y1, x2, y2) in lines:
                # Scale and position the line with broader width
                px1 = x + offset_x + x1 * scale * 1.5
                py1 = y + y1 * scale * 1.2
                px2 = x + offset_x + x2 * scale * 1.5
                py2 = y + y2 * scale * 1.2
                
                # Draw line using DDA algorithm with extra thickness for bold
                for dx in range(3):
                    for dy in range(3):
                        draw_line_dda(px1+dx, py1+dy, px2+dx, py2+dy, color)
            
            offset_x += 6 * scale * 1.5 * char_spacing
        elif char == ' ':
            offset_x += 5 * scale * 1.5 * char_spacing


# ------------------ Scene parts ------------------
def draw_sky():
    # Sky is just the clear color - no sun needed
    pass


def draw_sun():
    """
    Realistic Sun using Midpoint Circle Algorithm
    Positioned at top right side of the scene
    """
    sun_x = 95
    sun_y = 520
    
    # Sun glow effect - outer layers using Midpoint Circle Algorithm
    draw_circle_midpoint(sun_x, sun_y, 50, (1.0, 0.95, 0.7, 0.15), fill=True)
    draw_circle_midpoint(sun_x, sun_y, 45, (1.0, 0.93, 0.65, 0.2), fill=True)
    draw_circle_midpoint(sun_x, sun_y, 40, (1.0, 0.9, 0.6, 0.3), fill=True)
    
    # Main sun body using Midpoint Circle Algorithm
    draw_circle_midpoint(sun_x, sun_y, 35, (1.0, 0.95, 0.4), fill=True)
    draw_circle_midpoint(sun_x, sun_y, 32, (1.0, 0.98, 0.5), fill=True)
    draw_circle_midpoint(sun_x, sun_y, 28, (1.0, 1.0, 0.6), fill=True)
    
    # Sun core highlight
    draw_circle_midpoint(sun_x - 8, sun_y + 8, 12, (1.0, 1.0, 0.85), fill=True)


def draw_text_midpoint_circle(text, x, y, scale=1.0, color=(0, 0, 0)):
    """
    Draw text using Midpoint Circle Algorithm
    Creates letters from circles and dots for bold appearance
    """
    # Letter patterns using circle positions: [(x, y, radius), ...]
    letter_circles = {
        'D': [
            (0,0,1), (0,1,1), (0,2,1), (0,3,1), (0,4,1), (0,5,1), (0,6,1), (0,7,1),
            (1,7,1), (2,7,1), (3,6,1), (3,5,1), (3,4,1), (3,3,1), (3,2,1), (3,1,1), (2,0,1), (1,0,1)
        ],
        'I': [
            (0,7,1), (1,7,1), (2,7,1), (3,7,1), (4,7,1),
            (2,6,1), (2,5,1), (2,4,1), (2,3,1), (2,2,1), (2,1,1),
            (0,0,1), (1,0,1), (2,0,1), (3,0,1), (4,0,1)
        ],
        'U': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1),
            (1,0,1), (2,0,1), (3,0,1),
            (4,1,1), (4,2,1), (4,3,1), (4,4,1), (4,5,1), (4,6,1), (4,7,1)
        ],
        'L': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,0,1), (2,0,1), (3,0,1), (4,0,1)
        ],
        'A': [
            (2,7,1), (1,6,1), (3,6,1), (0,5,1), (4,5,1), (0,4,1), (4,4,1),
            (0,3,1), (1,3,1), (2,3,1), (3,3,1), (4,3,1),
            (0,2,1), (4,2,1), (0,1,1), (4,1,1), (0,0,1), (4,0,1)
        ],
        'K': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (3,7,1), (2,6,1), (1,5,1), (1,4,1), (2,3,1), (3,2,1), (4,1,1), (4,0,1)
        ],
        'E': [
            (0,7,1), (1,7,1), (2,7,1), (3,7,1), (4,7,1),
            (0,6,1), (0,5,1), (0,4,1), (1,4,1), (2,4,1), (3,4,1),
            (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,0,1), (2,0,1), (3,0,1), (4,0,1)
        ],
        'S': [
            (1,7,1), (2,7,1), (3,7,1), (4,7,1), (0,6,1), (0,5,1), (0,4,1),
            (1,4,1), (2,4,1), (3,4,1), (4,3,1), (4,2,1), (4,1,1),
            (0,0,1), (1,0,1), (2,0,1), (3,0,1)
        ],
        'V': [
            (0,7,1), (0,6,1), (0,5,1), (1,4,1), (1,3,1), (1,2,1), (2,1,1), (2,0,1),
            (3,2,1), (3,3,1), (3,4,1), (4,5,1), (4,6,1), (4,7,1)
        ],
        'Z': [
            (0,7,1), (1,7,1), (2,7,1), (3,7,1), (4,7,1),
            (4,6,1), (3,5,1), (2,4,1), (1,3,1), (0,2,1), (0,1,1),
            (0,0,1), (1,0,1), (2,0,1), (3,0,1), (4,0,1)
        ],
        'T': [
            (0,7,1), (1,7,1), (2,7,1), (3,7,1), (4,7,1),
            (2,6,1), (2,5,1), (2,4,1), (2,3,1), (2,2,1), (2,1,1), (2,0,1)
        ],
        'O': [
            (1,7,1), (2,7,1), (3,7,1),
            (0,6,1), (4,6,1), (0,5,1), (4,5,1), (0,4,1), (4,4,1),
            (0,3,1), (4,3,1), (0,2,1), (4,2,1), (0,1,1), (4,1,1),
            (1,0,1), (2,0,1), (3,0,1)
        ],
        'N': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,6,1), (2,5,1), (2,4,1), (3,3,1), (3,2,1),
            (4,7,1), (4,6,1), (4,5,1), (4,4,1), (4,3,1), (4,2,1), (4,1,1), (4,0,1)
        ],
        'M': [
            (0,0,1), (0,1,1), (0,2,1), (0,3,1), (0,4,1), (0,5,1), (0,6,1), (0,7,1),
            (1,6,1), (2,5,1), (3,6,1),
            (4,0,1), (4,1,1), (4,2,1), (4,3,1), (4,4,1), (4,5,1), (4,6,1), (4,7,1)
        ],
        'H': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,4,1), (2,4,1), (3,4,1),
            (4,7,1), (4,6,1), (4,5,1), (4,4,1), (4,3,1), (4,2,1), (4,1,1), (4,0,1)
        ],
        'R': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,7,1), (2,7,1), (3,6,1), (3,5,1), (3,4,1), (2,4,1), (1,4,1),
            (2,3,1), (3,2,1), (4,1,1), (4,0,1)
        ],
        'F': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,7,1), (2,7,1), (3,7,1), (4,7,1),
            (1,4,1), (2,4,1), (3,4,1)
        ],
        'G': [
            (1,7,1), (2,7,1), (3,7,1), (4,7,1),
            (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1),
            (1,0,1), (2,0,1), (3,0,1), (4,1,1), (4,2,1), (4,3,1), (3,3,1), (2,3,1)
        ],
        'P': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,7,1), (2,7,1), (3,7,1), (4,6,1), (4,5,1), (4,4,1), (3,4,1), (2,4,1), (1,4,1)
        ],
        'X': [
            (0,7,1), (0,6,1), (1,5,1), (2,4,1), (1,3,1), (0,2,1), (0,1,1), (0,0,1),
            (4,7,1), (4,6,1), (3,5,1), (3,3,1), (4,2,1), (4,1,1), (4,0,1)
        ],
        'Y': [
            (0,7,1), (0,6,1), (1,5,1), (2,4,1), (2,3,1), (2,2,1), (2,1,1), (2,0,1),
            (4,7,1), (4,6,1), (3,5,1)
        ],
        'B': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,7,1), (2,7,1), (3,6,1), (3,5,1), (2,4,1), (1,4,1),
            (2,4,1), (3,4,1), (3,3,1), (3,2,1), (3,1,1), (2,0,1), (1,0,1)
        ],
        'W': [
            (0,7,1), (0,6,1), (0,5,1), (0,4,1), (0,3,1), (0,2,1), (0,1,1), (0,0,1),
            (1,1,1), (2,2,1), (3,1,1),
            (4,7,1), (4,6,1), (4,5,1), (4,4,1), (4,3,1), (4,2,1), (4,1,1), (4,0,1)
        ],
    }
    
    offset_x = 0
    
    for char in text.upper():
        if char in letter_circles:
            circles = letter_circles[char]
            for (cx, cy, r) in circles:
                # Draw multiple circles for bold effect
                px = x + offset_x + cx * scale * 2
                py = y + cy * scale * 2
                # Draw main circle using midpoint algorithm
                draw_circle_midpoint(px, py, r * scale * 1.8, color, fill=True)
                # Add extra circles for bold/thick appearance
                draw_circle_midpoint(px + 0.5, py, r * scale * 1.8, color, fill=True)
                draw_circle_midpoint(px, py + 0.5, r * scale * 1.8, color, fill=True)
                draw_circle_midpoint(px + 0.5, py + 0.5, r * scale * 1.8, color, fill=True)
            
            offset_x += 7 * scale * 2  # Increased character gap
        elif char == ' ':
            offset_x += 5 * scale * 2


def draw_header_text():
    """
    Draw header text using Midpoint Circle Algorithm
    "DIU Lake Side Visualization
     PixelForge
     Submitted To
     Md Mehefujur Rahman Mubin"
    Positioned at top middle-left part in bold blue color
    """
    # Blue text with slight shadow for visibility
    text_color = (0.2, 0.4, 0.9)  # Blue color
    shadow_color = (0.0, 0.0, 0.0)
    
    # Line 1: "DIU LAKE SIDE VISUALIZATION"
    line1 = "DIU LAKE SIDE VISUALIZATION"
    line1_width = len(line1) * 14 * 0.8  # Adjusted for increased char gap
    line1_x = (WINDOW_WIDTH - line1_width) / 2 - 120  # More left
    # Shadow
    draw_text_midpoint_circle(line1, line1_x - 1, 575 - 1, 0.8, shadow_color)
    # Main text
    draw_text_midpoint_circle(line1, line1_x, 575, 0.8, text_color)
    
    # Line 2: "PIXELFORGE"
    line2 = "PIXELFORGE"
    line2_width = len(line2) * 14 * 0.7
    line2_x = (WINDOW_WIDTH - line2_width) / 2 - 120
    # Shadow
    draw_text_midpoint_circle(line2, line2_x - 1, 557 - 1, 0.7, shadow_color)
    # Main text
    draw_text_midpoint_circle(line2, line2_x, 557, 0.7, text_color)
    
    # Line 3: "SUBMITTED TO"
    line3 = "SUBMITTED TO"
    line3_width = len(line3) * 14 * 0.6
    line3_x = (WINDOW_WIDTH - line3_width) / 2 - 120
    # Shadow
    draw_text_midpoint_circle(line3, line3_x - 1, 542 - 1, 0.6, shadow_color)
    # Main text
    draw_text_midpoint_circle(line3, line3_x, 542, 0.6, text_color)
    
    # Line 4: "MD MEHEFUJUR RAHMAN MUBIN"
    line4 = "MD MEHEFUJUR RAHMAN MUBIN"
    line4_width = len(line4) * 14 * 0.65
    line4_x = (WINDOW_WIDTH - line4_width) / 2 - 120
    # Shadow
    draw_text_midpoint_circle(line4, line4_x - 1, 527 - 1, 0.65, shadow_color)
    # Main text
    draw_text_midpoint_circle(line4, line4_x, 527, 0.65, text_color)


def draw_clouds():
    """
    Draw small transparent clouds with slow movement animation
    Very subtle and light
    """
    global cloud_offset
    
    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    cloud_color = (1.0, 1.0, 1.0, 0.4)  # Very transparent white
    
    # Cloud 1 - top left area
    c1_x = 150 + cloud_offset
    if c1_x > WINDOW_WIDTH + 100:
        c1_x -= WINDOW_WIDTH + 200
    draw_circle(c1_x, 520, 18, cloud_color)
    draw_circle(c1_x + 20, 525, 20, cloud_color)
    draw_circle(c1_x + 40, 520, 16, cloud_color)
    draw_circle(c1_x + 20, 515, 15, cloud_color)
    
    # Cloud 2 - top middle
    c2_x = 420 + cloud_offset * 0.8
    if c2_x > WINDOW_WIDTH + 100:
        c2_x -= WINDOW_WIDTH + 200
    draw_circle(c2_x, 540, 15, cloud_color)
    draw_circle(c2_x + 18, 543, 18, cloud_color)
    draw_circle(c2_x + 35, 540, 14, cloud_color)
    
    # Cloud 3 - small cloud near sun
    c3_x = 750 + cloud_offset * 1.2
    if c3_x > WINDOW_WIDTH + 100:
        c3_x -= WINDOW_WIDTH + 200
    draw_circle(c3_x, 550, 12, cloud_color)
    draw_circle(c3_x + 15, 552, 14, cloud_color)
    draw_circle(c3_x + 28, 550, 11, cloud_color)
    
    # Cloud 4 - lower cloud
    c4_x = 320 + cloud_offset * 0.6
    if c4_x > WINDOW_WIDTH + 100:
        c4_x -= WINDOW_WIDTH + 200
    draw_circle(c4_x, 480, 16, cloud_color)
    draw_circle(c4_x + 20, 483, 19, cloud_color)
    draw_circle(c4_x + 38, 480, 15, cloud_color)
    
    glDisable(GL_BLEND)


def draw_lake():
    # Main water area with gradient effect
    draw_rect(0, 0, WINDOW_WIDTH, 170, (0.35, 0.65, 0.85))

    # Darker strip near shore to suggest depth
    draw_rect(0, 0, WINDOW_WIDTH, 40, (0.25, 0.55, 0.75))


def draw_grass_banks():
    # Left green bank
    draw_polygon(
        [
            (0, 170),
            (520, 170),
            (520, 260),
            (0, 260),
        ],
        (0.45, 0.8, 0.3),
    )

    # Right green bank
    draw_polygon(
        [
            (520, 170),
            (WINDOW_WIDTH, 170),
            (WINDOW_WIDTH, 260),
            (520, 260),
        ],
        (0.42, 0.78, 0.32),
    )


def draw_flower(x, y, petal_color, center_color):
    """Draw a simple flower with petals and center"""
    # Petals (5 petals in circle)
    for i in range(5):
        angle = i * (2 * pi / 5)
        petal_x = x + 6 * cos(angle)
        petal_y = y + 6 * sin(angle)
        draw_circle(petal_x, petal_y, 3, petal_color)
    
    # Center
    draw_circle(x, y, 2.5, center_color)


def draw_flower_gardens():
    """Draw flower gardens on the green grass areas"""
    # Left bank flower garden
    flowers_left = [
        # Red flowers
        (50, 210, (0.9, 0.2, 0.2), (0.95, 0.8, 0.1)),
        (70, 215, (0.9, 0.2, 0.2), (0.95, 0.8, 0.1)),
        (60, 225, (0.9, 0.2, 0.2), (0.95, 0.8, 0.1)),
        (45, 235, (0.9, 0.2, 0.2), (0.95, 0.8, 0.1)),
        (75, 230, (0.9, 0.2, 0.2), (0.95, 0.8, 0.1)),
        
        # Pink flowers
        (300, 180, (0.95, 0.5, 0.7), (0.95, 0.95, 0.4)),
        (320, 185, (0.95, 0.5, 0.7), (0.95, 0.95, 0.4)),
        (310, 195, (0.95, 0.5, 0.7), (0.95, 0.95, 0.4)),
        (295, 200, (0.95, 0.5, 0.7), (0.95, 0.95, 0.4)),
        (325, 200, (0.95, 0.5, 0.7), (0.95, 0.95, 0.4)),
        
        # Yellow flowers
        (400, 190, (0.95, 0.85, 0.2), (0.9, 0.5, 0.1)),
        (420, 195, (0.95, 0.85, 0.2), (0.9, 0.5, 0.1)),
        (410, 205, (0.95, 0.85, 0.2), (0.9, 0.5, 0.1)),
        (395, 215, (0.95, 0.85, 0.2), (0.9, 0.5, 0.1)),
        (425, 210, (0.95, 0.85, 0.2), (0.9, 0.5, 0.1)),
        
        # Purple flowers
        (180, 220, (0.7, 0.3, 0.85), (0.95, 0.9, 0.3)),
        (195, 225, (0.7, 0.3, 0.85), (0.95, 0.9, 0.3)),
        (190, 235, (0.7, 0.3, 0.85), (0.95, 0.9, 0.3)),
        (175, 240, (0.7, 0.3, 0.85), (0.95, 0.9, 0.3)),
        (200, 245, (0.7, 0.3, 0.85), (0.95, 0.9, 0.3)),
    ]
    
    # Right bank flower garden
    flowers_right = [
        # Orange flowers
        (680, 190, (0.95, 0.6, 0.15), (0.9, 0.85, 0.3)),
        (700, 195, (0.95, 0.6, 0.15), (0.9, 0.85, 0.3)),
        (690, 205, (0.95, 0.6, 0.15), (0.9, 0.85, 0.3)),
        (675, 215, (0.95, 0.6, 0.15), (0.9, 0.85, 0.3)),
        (705, 210, (0.95, 0.6, 0.15), (0.9, 0.85, 0.3)),
        
        # Blue flowers
        (820, 200, (0.3, 0.6, 0.95), (0.95, 0.95, 0.5)),
        (840, 205, (0.3, 0.6, 0.95), (0.95, 0.95, 0.5)),
        (830, 215, (0.3, 0.6, 0.95), (0.95, 0.95, 0.5)),
        (815, 225, (0.3, 0.6, 0.95), (0.95, 0.95, 0.5)),
        (845, 220, (0.3, 0.6, 0.95), (0.95, 0.95, 0.5)),
        
        # White flowers
        (760, 220, (0.95, 0.95, 0.95), (0.95, 0.85, 0.2)),
        (780, 225, (0.95, 0.95, 0.95), (0.95, 0.85, 0.2)),
        (770, 235, (0.95, 0.95, 0.95), (0.95, 0.85, 0.2)),
        (755, 240, (0.95, 0.95, 0.95), (0.95, 0.85, 0.2)),
        (785, 240, (0.95, 0.95, 0.95), (0.95, 0.85, 0.2)),
    ]
    
    # Draw all flowers
    for (x, y, petal_color, center_color) in flowers_left:
        draw_flower(x, y, petal_color, center_color)
    
    for (x, y, petal_color, center_color) in flowers_right:
        draw_flower(x, y, petal_color, center_color)


def draw_paths_and_stairs():
    # Main walkway on top of left bank
    draw_rect(0, 260, 520, 280, (0.85, 0.85, 0.85))

    # Right side walkway/road where bus will move
    draw_rect(350, 260, WINDOW_WIDTH, 290, (0.8, 0.8, 0.8))

    # Left stairs going to the lake
    step_width_start = 90
    step_width_end = 260
    step_height = 20
    base_y = 170
    num_steps = 6

    for i in range(num_steps):
        y1 = base_y + i * step_height
        y2 = y1 + step_height - 2
        x1 = step_width_start - i * 5
        x2 = step_width_end + i * 5
        draw_rect(x1, y1, x2, y2, (0.9, 0.9, 0.9))


def draw_building():
    # Main block (AB4 style)
    draw_rect(520, 280, 930, 520, (0.85, 0.92, 1.0))

    # Roof
    roof_points = [(520, 520), (930, 520), (900, 550), (550, 550)]
    draw_polygon(roof_points, (0.7, 0.7, 0.75))
    
    # University name on building using DDA Line Drawing Algorithm
    # Draw "DAFFODIL INTERNATIONAL UNIVERSITY" in bold on single line
    # Centered in middle-upper part of building with increased character spacing
    draw_text_dda('DAFFODIL INTERNATIONAL UNIVERSITY', 555, 500, 0.95, (0.1, 0.2, 0.5), char_spacing=1.15)

    # Windows (3 rows × 5 columns)
    window_color = (0.7, 0.85, 0.95)
    for row in range(3):
        y1 = 300 + row * 70
        y2 = y1 + 35
        for col in range(5):
            x1 = 540 + col * 70
            x2 = x1 + 40
            draw_rect(x1, y1, x2, y2, window_color)

    # Ground floor wall strip
    draw_rect(520, 260, 930, 280, (0.8, 0.88, 0.95))

    # Main door
    draw_rect(640, 260, 680, 310, (0.65, 0.7, 0.8))


def draw_gazebo():
    # Floor base with texture detail
    draw_rect(210, 260, 330, 275, (0.8, 0.75, 0.7))
    draw_rect(215, 265, 325, 270, (0.75, 0.7, 0.65))

    # Pillars with 3D effect
    pillar_color = (0.55, 0.27, 0.07)
    pillar_highlight = (0.65, 0.35, 0.12)
    
    # Left pillars
    draw_rect(220, 275, 230, 325, pillar_color)
    draw_rect(220, 275, 226, 325, pillar_highlight)
    draw_rect(265, 275, 275, 325, pillar_color)
    draw_rect(265, 275, 271, 325, pillar_highlight)
    
    # Right pillars
    draw_rect(310, 275, 320, 325, pillar_color)
    draw_rect(310, 275, 316, 325, pillar_highlight)

    # Roof with shading
    roof_points = [(200, 325), (340, 325), (270, 375)]
    draw_polygon(roof_points, (0.75, 0.22, 0.15))
    # Roof highlight
    roof_highlight = [(200, 325), (270, 375), (250, 375)]
    draw_polygon(roof_highlight, (0.85, 0.28, 0.2))


def draw_second_gazebo():
    # Smaller gazebo near the right bank
    # Floor base
    draw_rect(390, 260, 480, 273, (0.8, 0.75, 0.7))

    # Pillars
    pillar_color = (0.55, 0.27, 0.07)
    pillar_highlight = (0.65, 0.35, 0.12)
    
    draw_rect(400, 273, 408, 315, pillar_color)
    draw_rect(400, 273, 405, 315, pillar_highlight)
    draw_rect(432, 273, 440, 315, pillar_color)
    draw_rect(432, 273, 437, 315, pillar_highlight)
    draw_rect(464, 273, 472, 315, pillar_color)
    draw_rect(464, 273, 469, 315, pillar_highlight)

    # Roof
    roof_points = [(385, 315), (485, 315), (435, 355)]
    draw_polygon(roof_points, (0.75, 0.22, 0.15))
    roof_highlight = [(385, 315), (435, 355), (420, 355)]
    draw_polygon(roof_highlight, (0.85, 0.28, 0.2))


def draw_tree(x, y):
    # x,y = bottom of trunk - more realistic tree
    # Trunk with texture
    draw_rect(x - 6, y, x + 6, y + 40, (0.35, 0.22, 0.08))
    draw_rect(x - 6, y, x - 3, y + 40, (0.45, 0.28, 0.12))
    
    # Foliage with multiple layers for depth
    draw_circle(x - 12, y + 52, 16, (0.08, 0.45, 0.08))
    draw_circle(x + 12, y + 52, 16, (0.08, 0.45, 0.08))
    draw_circle(x, y + 48, 20, (0.1, 0.5, 0.1))
    draw_circle(x - 8, y + 62, 15, (0.12, 0.55, 0.12))
    draw_circle(x + 8, y + 62, 15, (0.12, 0.55, 0.12))
    draw_circle(x, y + 68, 18, (0.15, 0.6, 0.15))


def draw_tree_midpoint(x, y):
    """
    Tree created using Midpoint Circle Algorithm
    Uses the Bresenham's circle approach for efficient circle drawing
    """
    # Trunk with texture
    draw_rect(x - 6, y, x + 6, y + 40, (0.35, 0.22, 0.08))
    draw_rect(x - 6, y, x - 3, y + 40, (0.45, 0.28, 0.12))
    
    # Foliage using Midpoint Circle Algorithm - filled circles for tree crown
    # Multiple layers for realistic appearance
    draw_circle_midpoint(x - 12, y + 52, 16, (0.08, 0.45, 0.08), fill=True)
    draw_circle_midpoint(x + 12, y + 52, 16, (0.08, 0.45, 0.08), fill=True)
    draw_circle_midpoint(x, y + 48, 20, (0.1, 0.5, 0.1), fill=True)
    draw_circle_midpoint(x - 8, y + 62, 15, (0.12, 0.55, 0.12), fill=True)
    draw_circle_midpoint(x + 8, y + 62, 15, (0.12, 0.55, 0.12), fill=True)
    draw_circle_midpoint(x, y + 68, 18, (0.15, 0.6, 0.15), fill=True)


def draw_trees():
    # Regular trees on left side
    for tx in [80, 120, 160]:
        draw_tree(tx, 260)

    # Regular trees on right side
    for tx in [520, 560, 600]:
        draw_tree(tx - 40, 260)
    
    # Tree using Midpoint Circle Algorithm - placed in middle area
    draw_tree_midpoint(350, 260)


def draw_poles():
    # Electric poles on right side
    pole_color = (0.45, 0.45, 0.45)
    x_positions = [650, 720, 790, 860, 930]
    for x in x_positions:
        draw_rect(x - 3, 260, x + 3, 420, pole_color)
        # Cross bar
        draw_rect(x - 40, 400, x + 40, 405, pole_color)


def draw_pt6_monument():
    """
    Realistic PT-6 Aircraft Monument
    Positioned at top right side
    Features detailed plane on elevated pedestal with arc structure
    """
    # Base position - moved more right and down
    base_x = 920
    base_y = 245
    
    # Ground platform - wide base
    draw_rect(base_x - 55, base_y, base_x + 55, base_y + 8, (0.75, 0.75, 0.75))
    draw_rect(base_x - 50, base_y + 8, base_x + 50, base_y + 12, (0.8, 0.8, 0.8))
    
    # Main pedestal column
    draw_rect(base_x - 25, base_y + 12, base_x + 25, base_y + 80, (0.88, 0.88, 0.88))
    # Column shading
    draw_rect(base_x - 25, base_y + 12, base_x - 15, base_y + 80, (0.95, 0.95, 0.95))
    
    # Decorative arch support structure
    # Left support
    draw_rect(base_x - 45, base_y + 12, base_x - 38, base_y + 75, (0.85, 0.85, 0.85))
    # Right support  
    draw_rect(base_x + 38, base_y + 12, base_x + 45, base_y + 75, (0.85, 0.85, 0.85))
    
    # Top connecting arch using circles
    draw_circle(base_x - 41, base_y + 75, 8, (0.85, 0.85, 0.85))
    draw_circle(base_x + 41, base_y + 75, 8, (0.85, 0.85, 0.85))
    draw_circle(base_x, base_y + 85, 25, (0.85, 0.85, 0.85))
    
    # Platform top for plane
    draw_rect(base_x - 30, base_y + 80, base_x + 30, base_y + 85, (0.82, 0.82, 0.82))
    draw_circle(base_x, base_y + 85, 28, (0.88, 0.88, 0.88))
    
    # PT-6 Aircraft - positioned on monument
    plane_x = base_x - 40
    plane_y = base_y + 95
    
    # Aircraft colors - Yellow and Red scheme
    yellow = (0.98, 0.88, 0.15)
    yellow_light = (1.0, 0.95, 0.35)
    red = (0.82, 0.18, 0.25)
    red_dark = (0.68, 0.12, 0.18)
    
    # Fuselage (main body) - Yellow
    # Lower section
    draw_rect(plane_x, plane_y - 8, plane_x + 80, plane_y, yellow)
    # Upper section with highlight
    draw_rect(plane_x, plane_y, plane_x + 80, plane_y + 8, yellow_light)
    # Middle section
    draw_rect(plane_x + 5, plane_y - 6, plane_x + 75, plane_y + 6, yellow)
    
    # Nose cone - Red
    nose = [
        (plane_x + 80, plane_y - 8),
        (plane_x + 92, plane_y),
        (plane_x + 80, plane_y + 8),
    ]
    draw_polygon(nose, red)
    
    # Engine cowling detail
    draw_rect(plane_x + 70, plane_y - 8, plane_x + 80, plane_y + 8, (0.85, 0.75, 0.1))
    
    # Cockpit canopy
    draw_rect(plane_x + 55, plane_y + 2, plane_x + 68, plane_y + 7, (0.25, 0.4, 0.55))
    draw_rect(plane_x + 48, plane_y + 2, plane_x + 54, plane_y + 7, (0.25, 0.4, 0.55))
    
    # Main wing - Red/Pink (large)
    wing_main = [
        (plane_x + 28, plane_y + 8),
        (plane_x + 35, plane_y + 42),
        (plane_x + 50, plane_y + 42),
        (plane_x + 45, plane_y + 8),
    ]
    draw_polygon(wing_main, red)
    
    # Wing detail stripe
    wing_stripe = [
        (plane_x + 28, plane_y + 8),
        (plane_x + 35, plane_y + 42),
        (plane_x + 38, plane_y + 42),
        (plane_x + 31, plane_y + 8),
    ]
    draw_polygon(wing_stripe, (0.92, 0.28, 0.35))
    
    # Wing tip detail
    draw_polygon([
        (plane_x + 35, plane_y + 42),
        (plane_x + 50, plane_y + 42),
        (plane_x + 48, plane_y + 45),
        (plane_x + 37, plane_y + 45),
    ], red_dark)
    
    # Tail section - Red
    # Tail cone
    draw_rect(plane_x, plane_y - 8, plane_x + 18, plane_y + 8, red)
    draw_rect(plane_x + 2, plane_y - 6, plane_x + 16, plane_y + 6, (0.9, 0.22, 0.28))
    
    # Vertical stabilizer (tail fin)
    v_stab = [
        (plane_x + 8, plane_y + 8),
        (plane_x + 10, plane_y + 28),
        (plane_x + 16, plane_y + 26),
        (plane_x + 15, plane_y + 8),
    ]
    draw_polygon(v_stab, red)
    
    # Vertical stabilizer stripe
    draw_polygon([
        (plane_x + 8, plane_y + 8),
        (plane_x + 10, plane_y + 28),
        (plane_x + 12, plane_y + 27),
        (plane_x + 10, plane_y + 8),
    ], (0.92, 0.28, 0.35))
    
    # Horizontal stabilizer
    h_stab_left = [
        (plane_x + 5, plane_y - 8),
        (plane_x + 8, plane_y - 22),
        (plane_x + 16, plane_y - 20),
        (plane_x + 15, plane_y - 8),
    ]
    draw_polygon(h_stab_left, red)
    
    # Rudder detail
    draw_rect(plane_x + 2, plane_y - 8, plane_x + 5, plane_y + 8, red_dark)
    
    # Propeller hub
    draw_circle(plane_x + 92, plane_y, 5, (0.15, 0.15, 0.15))
    draw_circle(plane_x + 92, plane_y, 3, (0.25, 0.25, 0.25))
    
    # Propeller blades (3-blade design)
    # Blade 1 (vertical)
    draw_rect(plane_x + 91, plane_y - 15, plane_x + 93, plane_y + 15, (0.12, 0.12, 0.12))
    # Blade 2 (diagonal)
    blade2 = [
        (plane_x + 80, plane_y - 8),
        (plane_x + 82, plane_y - 10),
        (plane_x + 102, plane_y + 10),
        (plane_x + 100, plane_y + 12),
    ]
    draw_polygon(blade2, (0.12, 0.12, 0.12))
    
    # Landing gear (wheels)
    # Front gear
    draw_rect(plane_x + 60, plane_y - 8, plane_x + 62, plane_y - 16, (0.2, 0.2, 0.2))
    draw_circle(plane_x + 61, plane_y - 16, 3, (0.08, 0.08, 0.08))
    draw_circle(plane_x + 61, plane_y - 16, 2, (0.25, 0.25, 0.25))
    
    # Main gear
    draw_rect(plane_x + 32, plane_y - 8, plane_x + 34, plane_y - 16, (0.2, 0.2, 0.2))
    draw_circle(plane_x + 33, plane_y - 16, 3, (0.08, 0.08, 0.08))
    draw_circle(plane_x + 33, plane_y - 16, 2, (0.25, 0.25, 0.25))
    
    # Decorative details
    # Fuselage stripe
    draw_rect(plane_x + 20, plane_y + 6, plane_x + 65, plane_y + 7, red)


# ------------------ Animated objects ------------------
def draw_bus():
    x = bus_x
    y = 290
    # body base
    draw_rect(x, y, x + 100, y + 28, (0.95, 0.75, 0.0))
    # body upper with gradient
    draw_rect(x + 5, y + 28, x + 95, y + 55, (1.0, 0.85, 0.2))
    draw_rect(x + 8, y + 28, x + 92, y + 52, (1.0, 0.9, 0.35))

    # windows with frames
    w_y1 = y + 32
    w_y2 = y + 48
    for i in range(4):
        w_x1 = x + 12 + i * 21
        w_x2 = w_x1 + 18
        draw_rect(w_x1, w_y1, w_x2, w_y2, (0.65, 0.8, 0.9))
        # Window frame
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINE_LOOP)
        glVertex2f(w_x1, w_y1)
        glVertex2f(w_x2, w_y1)
        glVertex2f(w_x2, w_y2)
        glVertex2f(w_x1, w_y2)
        glEnd()

    # Front windshield
    draw_rect(x + 88, y + 32, x + 98, y + 48, (0.65, 0.8, 0.9))
    
    # Headlights
    draw_circle(x + 95, y + 18, 3, (1.0, 1.0, 0.8))
    draw_circle(x + 95, y + 10, 3, (1.0, 1.0, 0.8))

    # wheels with rims
    draw_circle(x + 20, y, 10, (0.1, 0.1, 0.1))
    draw_circle(x + 20, y, 6, (0.3, 0.3, 0.3))
    draw_circle(x + 80, y, 10, (0.1, 0.1, 0.1))
    draw_circle(x + 80, y, 6, (0.3, 0.3, 0.3))
    
    # Door
    draw_rect(x + 8, y + 5, x + 20, y + 30, (0.4, 0.4, 0.4))
    
    # DIU text on bus body (bold)
    # Draw text twice with offset for bold effect
    draw_text('DIU', x + 35, y + 12, 1.2)
    draw_text('DIU', x + 36, y + 12, 1.2)


def draw_bus2():
    x = bus2_x
    y = 290
    # Different color bus - red
    draw_rect(x, y, x + 100, y + 28, (0.85, 0.15, 0.1))
    draw_rect(x + 5, y + 28, x + 95, y + 55, (0.95, 0.25, 0.2))
    draw_rect(x + 8, y + 28, x + 92, y + 52, (1.0, 0.35, 0.3))

    # windows
    w_y1 = y + 32
    w_y2 = y + 48
    for i in range(4):
        w_x1 = x + 12 + i * 21
        w_x2 = w_x1 + 18
        draw_rect(w_x1, w_y1, w_x2, w_y2, (0.65, 0.8, 0.9))
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINE_LOOP)
        glVertex2f(w_x1, w_y1)
        glVertex2f(w_x2, w_y1)
        glVertex2f(w_x2, w_y2)
        glVertex2f(w_x1, w_y2)
        glEnd()

    draw_rect(x + 88, y + 32, x + 98, y + 48, (0.65, 0.8, 0.9))
    
    # Headlights
    draw_circle(x + 95, y + 18, 3, (1.0, 1.0, 0.8))
    draw_circle(x + 95, y + 10, 3, (1.0, 1.0, 0.8))

    # wheels
    draw_circle(x + 20, y, 10, (0.1, 0.1, 0.1))
    draw_circle(x + 20, y, 6, (0.3, 0.3, 0.3))
    draw_circle(x + 80, y, 10, (0.1, 0.1, 0.1))
    draw_circle(x + 80, y, 6, (0.3, 0.3, 0.3))
    
    draw_rect(x + 8, y + 5, x + 20, y + 30, (0.4, 0.4, 0.4))
    
    # DIU text on bus body (bold)
    draw_text('DIU', x + 35, y + 12, 1.2)
    draw_text('DIU', x + 36, y + 12, 1.2)


def draw_kayak(x, y, color, person_color):
    # Realistic kayak like the image
    # Main hull - elongated boat shape
    hull_points = [
        (x + 5, y - 8),
        (x + 55, y - 8),
        (x + 60, y - 4),
        (x + 60, y + 4),
        (x + 55, y + 8),
        (x + 5, y + 8),
        (x, y + 4),
        (x, y - 4),
    ]
    draw_polygon(hull_points, color)
    
    # Hull shading for 3D effect
    hull_shade = [
        (x + 5, y - 6),
        (x + 55, y - 6),
        (x + 55, y - 2),
        (x + 5, y - 2),
    ]
    draw_polygon(hull_shade, (color[0] * 1.2, color[1] * 1.2, color[2] * 1.2))
    
    # Cockpit opening (darker)
    draw_circle(x + 30, y, 8, (0.2, 0.2, 0.2))
    
    # Person sitting in kayak
    # Lower body in cockpit
    draw_circle(x + 30, y, 6, person_color)
    
    # Upper body/torso
    torso_points = [
        (x + 25, y),
        (x + 35, y),
        (x + 33, y + 15),
        (x + 27, y + 15),
    ]
    draw_polygon(torso_points, (0.3, 0.4, 0.6))  # Shirt color
    
    # Head
    draw_circle(x + 30, y + 20, 4, person_color)
    
    # Life jacket detail
    draw_rect(x + 26, y + 5, x + 34, y + 14, (0.9, 0.7, 0.1))
    
    # Paddle (both sides)
    # Paddle shaft
    paddle_angle = 0.3
    draw_rect(x + 10, y + 12, x + 50, y + 14, (0.5, 0.3, 0.1))
    
    # Left paddle blade
    paddle_left = [
        (x + 5, y + 10),
        (x + 15, y + 8),
        (x + 15, y + 18),
        (x + 5, y + 16),
    ]
    draw_polygon(paddle_left, (0.6, 0.4, 0.2))
    
    # Right paddle blade
    paddle_right = [
        (x + 45, y + 10),
        (x + 55, y + 8),
        (x + 55, y + 18),
        (x + 45, y + 16),
    ]
    draw_polygon(paddle_right, (0.6, 0.4, 0.2))


def draw_kayaks():
    # Three kayaks at different positions with different colors
    draw_kayak(kayak1_x, 100, (0.85, 0.2, 0.15), (0.9, 0.75, 0.65))
    draw_kayak(kayak2_x, 120, (0.95, 0.6, 0.1), (0.85, 0.7, 0.6))
    draw_kayak(kayak3_x, 90, (0.15, 0.5, 0.85), (0.9, 0.75, 0.65))


def draw_fish(x, y, jump_height=0, color=(0.9, 0.6, 0.2)):
    # Bigger fish that can jump out of water
    y_pos = y + jump_height
    
    # Fish body (bigger)
    body_points = [
        (x, y_pos),
        (x + 20, y_pos + 5),
        (x + 20, y_pos - 5),
    ]
    draw_polygon(body_points, color)
    
    # Body shading
    body_shade = [
        (x + 2, y_pos),
        (x + 18, y_pos + 3),
        (x + 18, y_pos - 3),
    ]
    draw_polygon(body_shade, (color[0]*0.8, color[1]*0.8, color[2]*0.8))
    
    # Tail fin
    tail_points = [
        (x, y_pos + 4),
        (x, y_pos - 4),
        (x - 8, y_pos),
    ]
    draw_polygon(tail_points, color)
    
    # Top fin
    draw_polygon(
        [(x + 10, y_pos), (x + 13, y_pos + 8), (x + 16, y_pos)],
        (color[0]*0.9, color[1]*0.9, color[2]*0.9)
    )
    
    # Bottom fin
    draw_polygon(
        [(x + 8, y_pos), (x + 11, y_pos - 6), (x + 14, y_pos)],
        (color[0]*0.9, color[1]*0.9, color[2]*0.9)
    )
    
    # Eye
    draw_circle(x + 16, y_pos + 2, 1.5, (0.1, 0.1, 0.1))
    draw_circle(x + 17, y_pos + 2.5, 0.7, (1, 1, 1))


def draw_jumping_fish():
    global fish_positions, fish_jump_states, fish_colors
    
    for i, (fx, fy) in enumerate(fish_positions):
        if fish_jump_states[i] > 0:
            # Fish is jumping - create arc motion (slower with 40 frames)
            progress = fish_jump_states[i] / 40.0
            # Parabolic jump (higher jump)
            jump_height = 35 * sin(progress * pi)
            draw_fish(fx, fy, jump_height, fish_colors[i])
            
            # Splash effect when jumping up or landing
            if fish_jump_states[i] in [1, 2, 3, 37, 38, 39, 40]:
                # Bigger splash circles
                draw_circle(fx + 10, fy + 2, 4, (0.5, 0.75, 0.9))
                draw_circle(fx + 4, fy, 3, (0.5, 0.75, 0.9))
                draw_circle(fx + 16, fy, 3, (0.5, 0.75, 0.9))


def draw_plane():
    # PT-6 style plane (more realistic propeller aircraft)
    x = plane_x
    y = 470
    
    # Fuselage (elongated body)
    draw_rect(x, y - 8, x + 85, y + 8, (0.85, 0.85, 0.9))
    # Fuselage highlight
    draw_rect(x, y - 8, x + 85, y - 2, (0.95, 0.95, 0.98))
    
    # Nose cone
    nose_points = [
        (x + 85, y - 8),
        (x + 85, y + 8),
        (x + 95, y),
    ]
    draw_polygon(nose_points, (0.9, 0.9, 0.95))
    
    # Cockpit windows
    draw_rect(x + 65, y + 2, x + 75, y + 7, (0.3, 0.5, 0.7))
    draw_rect(x + 55, y + 2, x + 62, y + 7, (0.3, 0.5, 0.7))
    
    # Main wing (larger, more realistic)
    wing_points = [
        (x + 25, y + 8),
        (x + 50, y + 35),
        (x + 55, y + 35),
        (x + 35, y + 8),
    ]
    draw_polygon(wing_points, (0.8, 0.8, 0.85))
    
    # Wing highlight
    wing_highlight = [
        (x + 25, y + 8),
        (x + 50, y + 35),
        (x + 48, y + 35),
        (x + 27, y + 8),
    ]
    draw_polygon(wing_highlight, (0.9, 0.9, 0.95))
    
    # Tail wing (horizontal stabilizer)
    tail_wing = [
        (x + 5, y - 8),
        (x + 5, y + 18),
        (x + 15, y + 15),
        (x + 15, y - 8),
    ]
    draw_polygon(tail_wing, (0.8, 0.8, 0.85))
    
    # Vertical stabilizer
    v_tail = [
        (x + 8, y + 8),
        (x + 8, y + 28),
        (x + 15, y + 22),
        (x + 15, y + 8),
    ]
    draw_polygon(v_tail, (0.85, 0.85, 0.9))
    
    # Propeller hub
    draw_circle(x + 95, y, 4, (0.2, 0.2, 0.2))
    
    # Propeller blades (simple)
    draw_rect(x + 93, y - 12, x + 97, y + 12, (0.15, 0.15, 0.15))
    
    # Landing gear
    draw_rect(x + 30, y - 8, x + 32, y - 18, (0.3, 0.3, 0.3))
    draw_circle(x + 31, y - 18, 3, (0.1, 0.1, 0.1))
    draw_rect(x + 60, y - 8, x + 62, y - 18, (0.3, 0.3, 0.3))
    draw_circle(x + 61, y - 18, 3, (0.1, 0.1, 0.1))


def draw_deer(x, y, facing_right=True):
    # Deer walking on lakeside
    flip = 1 if facing_right else -1
    
    # Body
    body_points = [
        (x, y + 15),
        (x + flip * 30, y + 15),
        (x + flip * 28, y + 30),
        (x + flip * 2, y + 30),
    ]
    draw_polygon(body_points, (0.6, 0.4, 0.2))
    
    # Neck
    neck_points = [
        (x + flip * 25, y + 28),
        (x + flip * 30, y + 28),
        (x + flip * 32, y + 42),
        (x + flip * 27, y + 42),
    ]
    draw_polygon(neck_points, (0.62, 0.42, 0.22))
    
    # Head
    draw_circle(x + flip * 30, y + 48, 6, (0.65, 0.45, 0.25))
    
    # Ears
    ear1 = [
        (x + flip * 28, y + 52),
        (x + flip * 26, y + 58),
        (x + flip * 30, y + 54),
    ]
    draw_polygon(ear1, (0.65, 0.45, 0.25))
    
    ear2 = [
        (x + flip * 32, y + 52),
        (x + flip * 34, y + 58),
        (x + flip * 30, y + 54),
    ]
    draw_polygon(ear2, (0.65, 0.45, 0.25))
    
    # Antlers (small)
    draw_rect(x + flip * 28 - 1, y + 54, x + flip * 28 + 1, y + 62, (0.4, 0.3, 0.2))
    draw_rect(x + flip * 32 - 1, y + 54, x + flip * 32 + 1, y + 62, (0.4, 0.3, 0.2))
    
    # Legs
    draw_rect(x + flip * 5 - 2, y, x + flip * 5 + 2, y + 15, (0.55, 0.35, 0.18))
    draw_rect(x + flip * 12 - 2, y, x + flip * 12 + 2, y + 15, (0.55, 0.35, 0.18))
    draw_rect(x + flip * 20 - 2, y, x + flip * 20 + 2, y + 15, (0.55, 0.35, 0.18))
    draw_rect(x + flip * 27 - 2, y, x + flip * 27 + 2, y + 15, (0.55, 0.35, 0.18))
    
    # Hooves
    draw_circle(x + flip * 5, y, 2, (0.2, 0.15, 0.1))
    draw_circle(x + flip * 12, y, 2, (0.2, 0.15, 0.1))
    draw_circle(x + flip * 20, y, 2, (0.2, 0.15, 0.1))
    draw_circle(x + flip * 27, y, 2, (0.2, 0.15, 0.1))
    
    # Tail
    tail_points = [
        (x, y + 25),
        (x - flip * 8, y + 22),
        (x - flip * 6, y + 28),
    ]
    draw_polygon(tail_points, (0.6, 0.4, 0.2))


def draw_deers():
    # Two deer walking near the lake
    draw_deer(deer1_x, 170, facing_right=True)
    draw_deer(deer2_x, 175, facing_right=False)


def draw_people_hint():
    # More realistic people silhouettes
    def person(px, py):
        # Legs
        draw_rect(px - 4, py, px - 1, py + 10, (0.15, 0.15, 0.15))
        draw_rect(px + 1, py, px + 4, py + 10, (0.15, 0.15, 0.15))
        # Torso
        draw_rect(px - 5, py + 10, px + 5, py + 22, (0.3, 0.3, 0.4))
        # Arms
        draw_rect(px - 8, py + 12, px - 5, py + 20, (0.3, 0.3, 0.4))
        draw_rect(px + 5, py + 12, px + 8, py + 20, (0.3, 0.3, 0.4))
        # Head
        draw_circle(px, py + 26, 5, (0.85, 0.75, 0.65))

    person(130, 200)
    person(150, 220)
    person(190, 240)
    person(245, 260)


def draw_static_scene():
    draw_sky()
    draw_sun()  # Sun using Midpoint Circle algorithm
    draw_clouds()  # Transparent clouds
    draw_header_text()  # Header text using Midpoint Circle algorithm
    draw_lake()
    draw_grass_banks()
    draw_flower_gardens()  # Flower gardens on grass
    draw_paths_and_stairs()
    draw_building()
    draw_gazebo()
    draw_second_gazebo()
    draw_trees()
    draw_poles()
    draw_pt6_monument()
    draw_people_hint()
    draw_deers()


def draw_dynamic_scene():
    draw_jumping_fish()
    draw_kayaks()
    draw_bus()
    draw_bus2()
    draw_plane()


def init_gl():
    glClearColor(0.7, 0.9, 1.0, 1.0)  # sky color
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)


def main():
    global bus_x, bus2_x, kayak1_x, kayak2_x, kayak3_x, plane_x, deer1_x, deer2_x, deer_direction
    global fish_positions, fish_jump_states, fish_timers, fish_colors, cloud_offset
    
    pygame.init()
    display = (WINDOW_WIDTH, WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("DIU Lake Side 2D - Enhanced Realistic Scene")
    
    init_gl()
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
        
        # Update animations
        # Buses moving right
        bus_x += 1.2
        if bus_x > WINDOW_WIDTH + 120:
            bus_x = -200
        
        bus2_x += 1.0
        if bus2_x > WINDOW_WIDTH + 120:
            bus2_x = -200
        
        # Kayaks moving slowly
        kayak1_x -= 0.35
        if kayak1_x < -100:
            kayak1_x = WINDOW_WIDTH + 100
            
        kayak2_x -= 0.28
        if kayak2_x < -100:
            kayak2_x = WINDOW_WIDTH + 100
            
        kayak3_x -= 0.4
        if kayak3_x < -100:
            kayak3_x = WINDOW_WIDTH + 100
        
        # Fish jumping animation
        for i in range(len(fish_positions)):
            fish_timers[i] += 1
            
            if fish_jump_states[i] > 0:
                fish_jump_states[i] += 1
                if fish_jump_states[i] > 40:  # Slower jump (40 frames)
                    fish_jump_states[i] = 0
                    fish_timers[i] = 0
            elif fish_timers[i] > 180 + (i * 50):  # Longer delays between jumps
                fish_jump_states[i] = 1
        
        # Plane moving right
        plane_x += 2.0
        if plane_x > WINDOW_WIDTH + 200:
            plane_x = -200
        
        # Deer walking back and forth in middle area
        deer1_x += 0.3 * deer_direction
        deer2_x += 0.25 * deer_direction
        
        # Keep deer in middle section (between 280 and 450)
        if deer1_x > 450 or deer1_x < 280:
            deer_direction *= -1
        
        # Clouds moving very slowly
        cloud_offset += 0.08
        if cloud_offset > WINDOW_WIDTH + 200:
            cloud_offset = 0
        
        # Draw scene
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        draw_static_scene()
        draw_dynamic_scene()
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
