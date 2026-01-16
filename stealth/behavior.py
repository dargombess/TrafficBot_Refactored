"""
Human Behavior Simulation
Simulasi perilaku manusia (scroll, mouse movement, delays)
"""

import random
import time
import numpy as np
from scipy import interpolate
from selenium.webdriver.common.action_chains import ActionChains

class HumanBehavior:
    """Simulator untuk human-like behavior"""
    
    def __init__(self, driver):
        """
        Initialize behavior simulator
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.action = ActionChains(driver)
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        Random delay seperti manusia
        
        Args:
            min_seconds: Minimal delay
            max_seconds: Maksimal delay
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def human_scroll(self, scroll_count: int = 5):
        """
        Scroll seperti manusia (tidak langsung, bertahap)
        
        Args:
            scroll_count: Jumlah scroll actions
        """
        try:
            for _ in range(scroll_count):
                # Random scroll amount
                scroll_amount = random.randint(200, 500)
                
                # Execute scroll
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                
                # Random delay antar scroll
                self.random_delay(0.5, 2.0)
            
            # Scroll back up sedikit (like manusia reading)
            if random.random() > 0.7:  # 30% chance
                scroll_back = random.randint(100, 300)
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_back});")
                self.random_delay(0.5, 1.5)
        
        except Exception as e:
            print(f"Error during human scroll: {e}")
    
    def smooth_mouse_move(self, element):
        """
        Move mouse dengan kurva smooth ke element
        
        Args:
            element: Selenium WebElement target
        """
        try:
            # Get window size
            window_size = self.driver.get_window_size()
            w = window_size['width']
            h = window_size['height']
            
            # Get element position
            rect = element.rect
            target_x = rect['x'] + rect['width'] / 2
            target_y = rect['y'] + rect['height'] / 2
            
            # Start position (random)
            start_x = random.randint(0, w // 3)
            start_y = random.randint(0, h // 3)
            
            # Generate smooth curve points
            points = self._generate_curve_points(
                start_x, start_y, target_x, target_y
            )
            
            # Move along curve
            for x, y in points:
                self.action.move_by_offset(
                    int(x - start_x), int(y - start_y)
                ).perform()
                start_x, start_y = x, y
                time.sleep(0.01)  # Smooth movement
            
        except Exception as e:
            print(f"Error during smooth mouse move: {e}")
    
    def _generate_curve_points(self, x1, y1, x2, y2, num_points=20):
        """
        Generate bezier curve points untuk smooth movement
        
        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            num_points: Jumlah points di curve
        
        Returns:
            List of (x, y) tuples
        """
        # Control points untuk bezier curve
        ctrl_x1 = random.randint(min(x1, x2), max(x1, x2))
        ctrl_y1 = random.randint(min(y1, y2), max(y1, y2))
        ctrl_x2 = random.randint(min(x1, x2), max(x1, x2))
        ctrl_y2 = random.randint(min(y1, y2), max(y1, y2))
        
        # Generate curve
        t = np.linspace(0, 1, num_points)
        
        # Cubic bezier formula
        x = ((1-t)**3 * x1 + 
             3*(1-t)**2*t * ctrl_x1 + 
             3*(1-t)*t**2 * ctrl_x2 + 
             t**3 * x2)
        
        y = ((1-t)**3 * y1 + 
             3*(1-t)**2*t * ctrl_y1 + 
             3*(1-t)*t**2 * ctrl_y2 + 
             t**3 * y2)
        
        return list(zip(x, y))
    
    def human_click(self, element):
        """
        Click dengan delay dan movement seperti manusia
        
        Args:
            element: Selenium WebElement to click
        """
        try:
            # Move mouse smooth ke element
            self.smooth_mouse_move(element)
            
            # Small delay before click (hesitation)
            self.random_delay(0.1, 0.3)
            
            # Click
            element.click()
            
            # Small delay after click
            self.random_delay(0.2, 0.5)
        
        except Exception as e:
            print(f"Error during human click: {e}")
            # Fallback to direct click
            try:
                element.click()
            except:
                pass
    
    def reading_pause(self):
        """Pause seperti orang sedang baca (random duration)"""
        reading_time = random.uniform(3.0, 10.0)
        time.sleep(reading_time)
    
    def generate_behavior_profile(self) -> dict:
        """
        Generate random behavior profile untuk session
        
        Returns:
            Dict dengan behavior parameters
        """
        return {
            'scroll_speed': random.uniform(0.5, 2.0),
            'reading_speed': random.uniform(2.0, 8.0),
            'attention_span': random.randint(30, 120),  # seconds
            'click_probability': random.uniform(0.05, 0.15),
            'scroll_probability': random.uniform(0.7, 0.95),
        }