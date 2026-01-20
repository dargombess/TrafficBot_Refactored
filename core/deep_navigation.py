"""
Deep Navigation Engine
Simulate realistic user navigation with depth levels
Smart link selection, adaptive behavior, and session simulation
"""

import time
import random
from urllib.parse import urlparse
from typing import List, Optional, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from utils.logger import logger


class DeepNavigationEngine:
    """
    Engine untuk navigasi dalam website dengan depth levels
    Simulate realistic user journey dengan multiple page visits
    """
    
    def __init__(self, driver, config):
        """
        Initialize Deep Navigation Engine
        
        Args:
            driver: Selenium WebDriver instance
            config: Bot configuration object
        """
        self.driver = driver
        self.config = config
        
        # Navigation state
        self.current_depth = 0
        self.max_depth = random.randint(
            getattr(config, 'MIN_DEPTH', 2),
            getattr(config, 'MAX_DEPTH', 5)
        )
        
        # URL tracking
        self.visited_urls: Set[str] = set()
        self.base_domain = None
        self.current_url = None
        
        # Behavior config
        self.depth_behaviors = getattr(config, 'DEPTH_BEHAVIORS', {
            0: {'scroll_min': 30, 'scroll_max': 60, 'read_min': 20, 'read_max': 30, 'click_prob': 80},
            1: {'scroll_min': 20, 'scroll_max': 40, 'read_min': 15, 'read_max': 25, 'click_prob': 70},
            2: {'scroll_min': 15, 'scroll_max': 30, 'read_min': 10, 'read_max': 20, 'click_prob': 50},
            3: {'scroll_min': 10, 'scroll_max': 20, 'read_min': 8, 'read_max': 15, 'click_prob': 30},
            4: {'scroll_min': 5, 'scroll_max': 15, 'read_min': 5, 'read_max': 10, 'click_prob': 10},
        })
        
        # Link selection settings
        self.link_priority_nav = getattr(config, 'LINK_PRIORITY_NAV_MENU', True)
        self.link_priority_related = getattr(config, 'LINK_PRIORITY_RELATED', True)
        self.link_priority_content = getattr(config, 'LINK_PRIORITY_CONTENT', True)
        self.link_priority_footer = getattr(config, 'LINK_PRIORITY_FOOTER', False)
        
        # Link filtering
        self.link_internal_only = getattr(config, 'LINK_INTERNAL_ONLY', True)
        self.link_avoid_visited = getattr(config, 'LINK_AVOID_VISITED', True)
        self.link_exclude_social = getattr(config, 'LINK_EXCLUDE_SOCIAL', True)
        self.link_exclude_external = getattr(config, 'LINK_EXCLUDE_EXTERNAL', True)
        
        logger.debug(f"Deep Navigation Engine initialized - Max depth: {self.max_depth}")
    
    def initialize(self, url: str):
        """
        Initialize navigation dengan landing page URL
        
        Args:
            url: Landing page URL
        """
        self.current_url = url
        self.visited_urls.add(url)
        self.base_domain = self._extract_domain(url)
        self.current_depth = 0
        
        logger.info(f"Deep Navigation initialized - Base domain: {self.base_domain}, Max depth: {self.max_depth}")
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: Full URL
        
        Returns:
            Domain string (e.g., 'example.com')
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    def should_navigate_deeper(self) -> bool:
        """
        Determine apakah harus navigate ke page berikutnya
        
        Returns:
            True jika harus navigate deeper
        """
        # Check max depth
        if self.current_depth >= self.max_depth:
            logger.debug(f"Max depth {self.max_depth} reached, stopping navigation")
            return False
        
        # Get click probability untuk current depth
        behavior = self.get_behavior_for_depth(self.current_depth)
        click_prob = behavior.get('click_prob', 50)
        
        # Random decision based on probability
        should_click = random.random() * 100 < click_prob
        
        if should_click:
            logger.debug(f"Depth {self.current_depth}: Will navigate deeper (prob: {click_prob}%)")
        else:
            logger.debug(f"Depth {self.current_depth}: Will not navigate (prob: {click_prob}%)")
        
        return should_click
    
    def get_behavior_for_depth(self, depth: int) -> dict:
        """
        Get behavior settings untuk depth level tertentu
        
        Args:
            depth: Current depth level
        
        Returns:
            Dict dengan scroll_min, scroll_max, read_min, read_max, click_prob
        """
        # Return behavior untuk depth level, atau default ke level 4
        return self.depth_behaviors.get(depth, self.depth_behaviors.get(4, {
            'scroll_min': 5, 'scroll_max': 15, 
            'read_min': 5, 'read_max': 10, 
            'click_prob': 10
        }))
    
    def find_best_link(self) -> Optional[WebElement]:
        """
        Find best link untuk diklik berdasarkan priority & filtering
        
        Returns:
            WebElement link, atau None jika tidak ada
        """
        try:
            all_links = []
            
            # Priority 1: Navigation menu links
            if self.link_priority_nav:
                try:
                    nav_links = self.driver.find_elements(By.CSS_SELECTOR, 
                        "nav a, .menu a, .navigation a, header a, .navbar a, .nav-menu a")
                    all_links.extend(nav_links)
                    logger.debug(f"Found {len(nav_links)} navigation links")
                except:
                    pass
            
            # Priority 2: Related posts/articles
            if self.link_priority_related:
                try:
                    related_links = self.driver.find_elements(By.CSS_SELECTOR,
                        ".related a, .similar a, .more-posts a, .related-articles a, .you-may-like a")
                    all_links.extend(related_links)
                    logger.debug(f"Found {len(related_links)} related links")
                except:
                    pass
            
            # Priority 3: Content links
            if self.link_priority_content:
                try:
                    content_links = self.driver.find_elements(By.CSS_SELECTOR,
                        "article a, .content a, .post a, .entry-content a, main a")
                    all_links.extend(content_links)
                    logger.debug(f"Found {len(content_links)} content links")
                except:
                    pass
            
            # Priority 4: Footer links (optional)
            if self.link_priority_footer:
                try:
                    footer_links = self.driver.find_elements(By.CSS_SELECTOR,
                        "footer a, .footer a")
                    all_links.extend(footer_links)
                    logger.debug(f"Found {len(footer_links)} footer links")
                except:
                    pass
            
            # Filter links
            valid_links = self._filter_links(all_links)
            
            if valid_links:
                # Pick random link from valid ones
                selected_link = random.choice(valid_links)
                href = selected_link.get_attribute('href')
                logger.info(f"Selected link: {href[:100]}...")
                return selected_link
            else:
                logger.warning("No valid links found for navigation")
                return None
                
        except Exception as e:
            logger.error(f"Error finding links: {e}")
            return None
    
    def _filter_links(self, links: List[WebElement]) -> List[WebElement]:
        """
        Filter links berdasarkan criteria
        
        Args:
            links: List of link elements
        
        Returns:
            Filtered list of valid links
        """
        valid_links = []
        
        for link in links:
            try:
                href = link.get_attribute('href')
                
                if not href:
                    continue
                
                # Filter: Exclude javascript, mailto, tel
                if any(x in href.lower() for x in ['javascript:', 'mailto:', 'tel:', '#']):
                    continue
                
                # Filter: Internal only
                if self.link_internal_only:
                    link_domain = self._extract_domain(href)
                    if link_domain and link_domain != self.base_domain:
                        continue
                
                # Filter: Avoid visited
                if self.link_avoid_visited:
                    if href in self.visited_urls:
                        continue
                
                # Filter: Exclude social media
                if self.link_exclude_social:
                    social_patterns = ['facebook.com', 'twitter.com', 'instagram.com', 
                                     'linkedin.com', 'youtube.com', 'tiktok.com',
                                     'whatsapp.com', 'telegram.org']
                    if any(pattern in href.lower() for pattern in social_patterns):
                        continue
                
                # Filter: Exclude file downloads
                file_extensions = ['.pdf', '.zip', '.rar', '.doc', '.docx', '.xls', 
                                 '.xlsx', '.ppt', '.pptx', '.jpg', '.png', '.gif']
                if any(href.lower().endswith(ext) for ext in file_extensions):
                    continue
                
                # Check if link is visible and enabled
                if link.is_displayed() and link.is_enabled():
                    valid_links.append(link)
                    
            except Exception as e:
                logger.debug(f"Error filtering link: {e}")
                continue
        
        logger.debug(f"Filtered {len(valid_links)} valid links from {len(links)} total")
        return valid_links
    
    def navigate_to_link(self, link: WebElement) -> bool:
        """
        Navigate ke link dengan human-like behavior
        
        Args:
            link: Link element to click
        
        Returns:
            True jika sukses navigate
        """
        try:
            href = link.get_attribute('href')
            
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Mouse hover simulation
            self.driver.execute_script("""
                var element = arguments[0];
                var event = new MouseEvent('mouseover', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true
                });
                element.dispatchEvent(event);
            """, link)
            
            time.sleep(random.uniform(0.3, 0.8))
            
            # Click link
            try:
                link.click()
                logger.info(f"✅ Clicked link with Selenium click")
            except:
                # Fallback: JavaScript click
                self.driver.execute_script("arguments[0].click();", link)
                logger.info(f"✅ Clicked link with JavaScript")
            
            # Wait for page load
            time.sleep(random.uniform(2, 4))
            
            # Update state
            new_url = self.driver.current_url
            self.visited_urls.add(new_url)
            self.current_url = new_url
            self.current_depth += 1
            
            logger.info(f"📍 Navigated to depth {self.current_depth}: {new_url[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error navigating to link: {e}")
            return False
    
    def get_session_summary(self) -> dict:
        """
        Get summary of navigation session
        
        Returns:
            Dict dengan session statistics
        """
        return {
            'pages_visited': len(self.visited_urls),
            'max_depth_reached': self.current_depth,
            'max_depth_configured': self.max_depth,
            'base_domain': self.base_domain,
            'visited_urls': list(self.visited_urls)
        }
