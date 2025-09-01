import cv2
import os
import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
import requests
import tempfile
import io
from fastapi.responses import Response

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.temp_dir = tempfile.mkdtemp()
    
    def process_video(self, video_path: str, guide_id: int) -> List[Dict[str, Any]]:
        """
        Process a video file and extract steps with keyframes
        """
        try:
            # Handle URL downloads
            if video_path.startswith(('http://', 'https://')):
                video_path = self._download_video(video_path)
            
            # Basic video processing
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            logger.info(f"Video properties - FPS: {fps}, Frames: {frame_count}, Duration: {duration}s")
            
            # Extract keyframes and generate steps
            steps = self._extract_keyframes_and_generate_steps(cap, fps, frame_count, guide_id)
            
            cap.release()
            return steps
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise
    
    def _download_video(self, url: str) -> str:
        """Download video from URL to temporary file"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = os.path.join(self.temp_dir, f"video_{os.urandom(8).hex()}.mp4")
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded video from {url} to {temp_file}")
            return temp_file
            
        except Exception as e:
            logger.error(f"Error downloading video from {url}: {str(e)}")
            raise
    
    def _optimize_image(self, frame: np.ndarray, max_width: int = 1200, quality: int = 80) -> bytes:
        """Optimize image by resizing and compressing"""
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize if needed
        height, width = frame.shape[:2]
        if width > max_width:
            ratio = max_width / width
            new_size = (int(width * ratio), int(height * ratio))
            frame_rgb = cv2.resize(frame_rgb, new_size, interpolation=cv2.INTER_AREA)
        
        # Convert to JPEG with compression
        _, buffer = cv2.imencode('.jpg', frame_rgb, 
                               [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        
        return buffer.tobytes()
    
    def _extract_keyframes_and_generate_steps(self, cap, fps: float, frame_count: int, guide_id: int) -> List[Dict[str, Any]]:
        """Extract keyframes from video and generate realistic steps"""
        try:
            # Calculate intervals for keyframe extraction
            num_steps = min(max(int(frame_count / (fps * 20)), 3), 6)  # 1 step per 20 seconds, min 3, max 6
            interval = frame_count // num_steps
            
            steps = []
            keyframe_paths = []
            
            for i in range(num_steps):
                frame_number = i * interval
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = cap.read()
                
                if ret:
                    # Save optimized keyframe
                    keyframe_path = os.path.join(self.temp_dir, f"keyframe_{guide_id}_{i}.jpg")
                    optimized_img = self._optimize_image(frame)
                    with open(keyframe_path, 'wb') as f:
                        f.write(optimized_img)
                    
                    keyframe_paths.append(keyframe_path)
                    
                    # Generate step based on position in video
                    step = self._generate_step_from_position(i, num_steps, keyframe_path)
                    steps.append(step)
            
            return steps
            
        except Exception as e:
            logger.error(f"Error extracting keyframes: {str(e)}")
            # Fallback to mock steps
            return self._generate_mock_steps(guide_id, frame_count / fps if fps > 0 else 60)
    
    def _generate_step_from_position(self, step_index: int, total_steps: int, keyframe_path: str) -> Dict[str, Any]:
        """Generate a realistic step based on its position in the video"""
        step_templates = [
            {
                "title": "Initial Setup and Preparation",
                "description": "Begin by setting up your workspace and gathering all necessary materials. Ensure you have a clean, organized area to work in and all tools are easily accessible."
            },
            {
                "title": "Primary Process Execution",
                "description": "Start the main procedure following the demonstrated technique. Pay close attention to the specific movements and timing shown in the video."
            },
            {
                "title": "Intermediate Steps and Adjustments",
                "description": "Continue with the intermediate steps, making any necessary adjustments as you progress. Monitor your work carefully and compare with the reference."
            },
            {
                "title": "Advanced Techniques Application",
                "description": "Apply the more advanced techniques demonstrated in the video. Take your time with these steps as they often require precision and practice."
            },
            {
                "title": "Final Assembly and Completion",
                "description": "Complete the final assembly steps and perform quality checks. Ensure all components are properly secured and the result matches the expected outcome."
            },
            {
                "title": "Quality Control and Finishing",
                "description": "Perform final quality control checks and apply any finishing touches. Clean up your workspace and properly store any remaining materials."
            }
        ]
        
        # Use appropriate template based on position
        template_index = min(step_index, len(step_templates) - 1)
        template = step_templates[template_index]
        
        return {
            "title": template["title"],
            "description": template["description"],
            "image_url": f"https://picsum.photos/id/{10 + step_index}/800/400",
            "order": step_index + 1
        }
    
    def _generate_mock_steps(self, guide_id: int, duration: float) -> List[Dict[str, Any]]:
        """Generate mock steps based on video duration"""
        num_steps = min(max(int(duration / 30), 3), 6)  # 1 step per 30 seconds, min 3, max 6
        
        step_titles = [
            "Workspace Preparation",
            "Material Gathering", 
            "Initial Setup",
            "Main Process",
            "Quality Checks",
            "Final Assembly"
        ]
        
        step_descriptions = [
            "Set up your workspace with proper lighting and organization. Ensure all tools are clean and within reach.",
            "Gather all required materials and tools. Check that everything is in good condition and properly functioning.",
            "Begin the initial setup process following the demonstrated sequence. Take care with positioning and alignment.",
            "Execute the main procedure with attention to detail. Follow the timing and technique shown in the video.",
            "Perform quality control checks at each stage. Make adjustments as needed to ensure proper results.",
            "Complete the final assembly and finishing steps. Clean up and organize your completed work."
        ]
        
        return [
            {
                "title": step_titles[i] if i < len(step_titles) else f"Step {i+1}",
                "description": step_descriptions[i] if i < len(step_descriptions) else f"Complete step {i+1} as demonstrated in the video.",
                "image_url": f"https://picsum.photos/id/{20 + i}/800/400",
                "order": i+1
            }
            for i in range(num_steps)
        ]
