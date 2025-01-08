from presto import Presto
import time
import random
import math

# Initialize Presto and PicoGraphics
presto = Presto(full_res=True)
display = presto.display  # Get the PicoGraphics display instance

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 480

# Reduced canvas height
CANVAS_WIDTH, CANVAS_HEIGHT = 20, 70  # Lava column dimensions
SCALE = 6  # Scale up to fit screen

# Center the canvas on the screen
COLUMN_X = (SCREEN_WIDTH - CANVAS_WIDTH * SCALE) // 2  # Center horizontally
COLUMN_Y = (SCREEN_HEIGHT - CANVAS_HEIGHT * SCALE) // 2  # Center vertically

# Chrome dimensions (same width as lava column, height = 10px each)
CHROME_HEIGHT = 10 * SCALE

# Colors
background = display.create_pen(0, 0, 0)  # Black background
blob_color_base = display.create_pen(255, 105, 180)  # Pink color for blobs

# Chrome gradient colors (more sections for a smoother gradient)
chrome_colors = [
    display.create_pen(50, 50, 50),   # Dark gray
    display.create_pen(75, 75, 75),  # Slightly lighter gray
    display.create_pen(100, 100, 100),  # Medium gray
    display.create_pen(125, 125, 125),  # Lighter gray
    display.create_pen(150, 150, 150),  # Light gray
    display.create_pen(175, 175, 175),  # Very light gray
    display.create_pen(200, 200, 200),  # White
    display.create_pen(175, 175, 175),  # Very light gray
    display.create_pen(150, 150, 150),  # Light gray
    display.create_pen(125, 125, 125),  # Lighter gray
    display.create_pen(100, 100, 100),  # Medium gray
    display.create_pen(75, 75, 75),    # Slightly lighter gray
    display.create_pen(50, 50, 50),   # Dark gray
]

# Total "lava" area to conserve (5% of the column area)
COLUMN_AREA = CANVAS_WIDTH * CANVAS_HEIGHT * SCALE**2
TOTAL_AREA = COLUMN_AREA * 0.05  # Blobs occupy 5% of the column area
MAX_RADIUS = 15  # Maximum blob radius
MIN_RADIUS = 5   # Minimum blob radius

# Gravity and buoyancy constants
GRAVITY = 0.02       # Pulls blobs downward
BUOYANCY = 0.05      # Pushes blobs upward when heated
HEAT_ZONE = CANVAS_HEIGHT * 0.15  # Bottom 15% of the column (heat zone)
COOLING_RATE = 0.01  # Cooling rate as blobs rise
HEATING_RATE = 0.02  # Heating rate in the heat zone

# Blob class
class Blob:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.dx = random.uniform(-0.5, 0.5)  # Horizontal drift
        self.dy = random.uniform(-0.1, 0.1)  # Vertical drift
        self.temperature = 0.0  # Temperature determines rising or falling

    def update(self):
        # Apply gravity
        self.dy += GRAVITY

        # Check if in the heat zone
        if self.y > CANVAS_HEIGHT - HEAT_ZONE:
            self.temperature += HEATING_RATE  # Heat up
            self.dy -= 0.05  # Gentle upward push in heat zone
        else:
            self.temperature -= COOLING_RATE  # Cool down

        # Clamp temperature between 0 (cold) and 1 (hot)
        self.temperature = max(0.0, min(1.0, self.temperature))

        # Apply buoyancy based on temperature
        self.dy -= BUOYANCY * self.temperature * 2  # Increased buoyancy effect

        # Move the blob
        self.x += self.dx
        self.y += self.dy

        # Bounce off horizontal edges
        if self.x - self.r < 0 or self.x + self.r > CANVAS_WIDTH:
            self.dx = -self.dx

        # Reset blobs that move off the bottom or top
        if self.y - self.r > CANVAS_HEIGHT:  # Fell too far
            self.y = CANVAS_HEIGHT - self.r
            self.dy = 0
        elif self.y + self.r < 0:  # Rose too far
            self.y = self.r
            self.dy = 0

    def area(self):
        return math.pi * self.r**2

    def split(self):
        # Split large blobs into two smaller ones
        if self.r > MAX_RADIUS * 0.8:
            child_area = self.area() / 2
            child_radius = math.sqrt(child_area / math.pi)
            self.r = child_radius
            return Blob(
                self.x + random.uniform(-child_radius, child_radius),
                self.y + random.uniform(-child_radius, child_radius),
                child_radius
            )
        return None

# Initialize blobs
blobs = []
remaining_area = TOTAL_AREA
while remaining_area > 0:
    radius = random.uniform(MIN_RADIUS, MIN_RADIUS + 2)  # Smaller blobs
    blob_area = math.pi * radius**2
    if blob_area > remaining_area:
        radius = math.sqrt(remaining_area / math.pi)
        blob_area = math.pi * radius**2
    blobs.append(Blob(random.uniform(radius, CANVAS_WIDTH - radius),
                      random.uniform(radius, CANVAS_HEIGHT - radius),
                      radius))
    remaining_area -= blob_area

# Metaball field function
def metaball_field(x, y, blobs):
    value = 0
    for blob in blobs:
        dx = x - blob.x
        dy = y - blob.y
        distance_squared = dx * dx + dy * dy
        if distance_squared > 0:
            value += blob.r / (distance_squared + 1)  # Reduce blob influence
    return value

# Draw chrome gradients
def draw_chrome():
    chrome_slice_width = CANVAS_WIDTH * SCALE // len(chrome_colors)  # Narrower slices
    chrome_x = (SCREEN_WIDTH - CANVAS_WIDTH * SCALE) // 2  # Center horizontally on the screen

    # Draw top chrome gradient (horizontal gradient)
    for i, color in enumerate(chrome_colors):
        display.set_pen(color)
        display.rectangle(
            chrome_x + (i * chrome_slice_width),  # Shift rectangle horizontally
            COLUMN_Y - CHROME_HEIGHT,  # Fixed vertical position above the column
            chrome_slice_width,  # Width of the slice
            CHROME_HEIGHT  # Full height of the chrome
        )

    # Draw bottom chrome gradient (horizontal gradient)
    for i, color in enumerate(chrome_colors):
        display.set_pen(color)
        display.rectangle(
            chrome_x + (i * chrome_slice_width),  # Shift rectangle horizontally
            COLUMN_Y + CANVAS_HEIGHT * SCALE,  # Fixed vertical position below the column
            chrome_slice_width,  # Width of the slice
            CHROME_HEIGHT  # Full height of the chrome
        )

# Main loop
print("Starting lava lamp...")
while True:
    # Clear the screen
    display.set_pen(background)
    display.clear()

    # Draw chrome caps
    draw_chrome()

    # Render metaballs
    for y in range(CANVAS_HEIGHT):
        for x in range(CANVAS_WIDTH):
            field_value = metaball_field(x, y, blobs)
            if field_value > 2.5:  # Higher threshold to reduce blob rendering
                intensity = min(int(field_value * 50), 255)
                display.set_pen(display.create_pen(intensity, 105, 180))  # Pink blob gradient
                screen_x = COLUMN_X + x * SCALE
                screen_y = COLUMN_Y + y * SCALE
                display.rectangle(screen_x, screen_y, SCALE, SCALE)

    # Update blobs
    for blob in blobs:
        blob.update()

    # Dynamically split blobs
    new_blobs = []
    for blob in blobs:
        child = blob.split()
        if child:
            new_blobs.append(child)
    blobs.extend(new_blobs)

    # Update the display
    presto.update()
    time.sleep(0.01)  # Control frame rate

