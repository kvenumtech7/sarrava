#!/usr/bin/env python3
"""
Optimized Voice Assistant for Raspberry Pi 5 (4GB RAM)
Uses: Vosk (wake word detection) + Whisper (command processing)
Issues Fixed: Slow wake detection, Blank animated face
"""

import threading
import queue
import time
import sys
import signal
from audio_processor import AudioProcessor
from wake_word_detector import WakeWordDetector
from command_processor import CommandProcessor
from face_animator import FaceAnimator


class VoiceAssistant:
    def __init__(self):
        self.running = True
        self.wake_detected = False
        
        # Thread-safe queues
        self.audio_queue = queue.Queue(maxsize=10)
        self.wake_queue = queue.Queue(maxsize=5)
        self.command_queue = queue.Queue(maxsize=5)
        self.animation_queue = queue.Queue(maxsize=20)
        
        # Initialize components
        print("[INIT] Initializing Voice Assistant...")
        self.audio_processor = AudioProcessor(self.audio_queue)
        self.wake_detector = WakeWordDetector(self.audio_queue, self.wake_queue)
        self.command_processor = CommandProcessor(self.wake_queue, self.command_queue)
        self.face_animator = FaceAnimator(self.animation_queue)
        
    def signal_handler(self, sig, frame):
        """Handle graceful shutdown"""
        print("\n[SHUTDOWN] Stopping assistant...")
        self.running = False
        time.sleep(0.5)
        sys.exit(0)
    
    def start(self):
        """Start all threads"""
        print("[START] Starting threads...")
        
        # Register signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Thread 1: Audio capture (non-blocking)
        audio_thread = threading.Thread(
            target=self.audio_processor.run,
            daemon=True,
            name="AudioThread"
        )
        
        # Thread 2: Wake word detection (priority)
        wake_thread = threading.Thread(
            target=self.wake_detector.run,
            daemon=True,
            name="WakeThread"
        )
        
        # Thread 3: Command processing
        command_thread = threading.Thread(
            target=self.command_processor.run,
            daemon=True,
            name="CommandThread"
        )
        
        # Thread 4: Face animation (GUI)
        anim_thread = threading.Thread(
            target=self.face_animator.run,
            daemon=True,
            name="AnimationThread"
        )
        
        # Start all threads
        audio_thread.start()
        wake_thread.start()
        command_thread.start()
        anim_thread.start()
        
        print("[OK] All threads started")
        print("[STATUS] Listening for wake word: 'hey raspberry'...")
        
        # Queue initial animation state
        self.animation_queue.put(("idle", None))
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.start()
