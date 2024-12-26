"""
Game session manager for handling individual player sessions
"""
import time
import asyncio
from typing import Dict, Optional
from .engine import DoomEngine
from .frame_buffer import FrameBuffer
from config.settings import (
    UPDATE_RATE,
    MESSAGE_RATE_LIMIT,
    REACTION_RATE_LIMIT,
    MAX_UPDATES_PER_MINUTE
)

class RateLimiter:
    def __init__(self):
        self.last_update = 0
        self.update_count = 0
        self.last_minute = 0
        
    def can_update(self) -> bool:
        current_time = time.time()
        
        # Reset counter every minute
        current_minute = int(current_time / 60)
        if current_minute > self.last_minute:
            self.update_count = 0
            self.last_minute = current_minute
            
        # Check rate limits
        if self.update_count >= MAX_UPDATES_PER_MINUTE:
            return False
            
        if current_time - self.last_update < MESSAGE_RATE_LIMIT:
            return False
            
        return True
        
    def record_update(self):
        self.last_update = time.time()
        self.update_count += 1

class GameSession:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.engine = DoomEngine()
        self.frame_buffer = FrameBuffer()
        self.message_id: Optional[int] = None
        self.channel_id: Optional[int] = None
        self.last_update: float = 0
        self.active = False
        self.rate_limiter = RateLimiter()
        self.last_input_time = 0
        
    async def start(self) -> None:
        """Start the game session"""
        await self.engine.initialize()
        self.active = True
        
    async def stop(self) -> None:
        """Stop the game session"""
        self.active = False
        # Clean up resources
        
    async def handle_input(self, action: str) -> None:
        """Handle player input with rate limiting"""
        if not self.active:
            return
            
        current_time = time.time()
        if current_time - self.last_input_time < REACTION_RATE_LIMIT:
            return  # Ignore input if too soon
            
        self.last_input_time = current_time
        await self.engine.handle_input(action)
        
    async def update(self, delta_time: float) -> None:
        """Update game state with rate limiting"""
        if not self.active:
            return
            
        if not self.rate_limiter.can_update():
            return  # Skip update if rate limited
            
        await self.engine.update(delta_time)
        self.rate_limiter.record_update()
        
    async def get_frame(self) -> str:
        """Get current frame as ASCII art"""
        if not self.active:
            return ""
            
        # Get the raw frame from the engine
        frame = await self.engine.get_frame()
        
        # Convert to ASCII
        ascii_frame = self.frame_buffer.frame_to_ascii(frame)
        
        # Add status bar
        game_state = await self.engine.save_state()
        return self.frame_buffer.add_status_bar(
            ascii_frame,
            game_state['health'],
            game_state['ammo'],
            game_state['armor'],
            game_state['weapon']
        )
        
    async def save_state(self) -> dict:
        """Save current game state"""
        return await self.engine.save_state()
        
    async def load_state(self, state: dict) -> None:
        """Load saved game state"""
        await self.engine.load_state(state)

class SessionManager:
    def __init__(self):
        self.sessions: Dict[int, GameSession] = {}
        self.last_cleanup = 0
        
    async def create_session(self, user_id: int) -> GameSession:
        """Create a new game session for user"""
        if user_id in self.sessions:
            await self.sessions[user_id].stop()
            
        session = GameSession(user_id)
        await session.start()
        self.sessions[user_id] = session
        return session
        
    async def get_session(self, user_id: int) -> Optional[GameSession]:
        """Get existing game session for user"""
        return self.sessions.get(user_id)
        
    async def end_session(self, user_id: int) -> None:
        """End user's game session"""
        if user_id in self.sessions:
            await self.sessions[user_id].stop()
            del self.sessions[user_id]
            
    async def update_all(self, delta_time: float) -> None:
        """Update all active sessions with rate limiting"""
        current_time = time.time()
        
        # Cleanup inactive sessions every minute
        if current_time - self.last_cleanup >= 60:
            self.last_cleanup = current_time
            inactive_users = [
                user_id for user_id, session in self.sessions.items()
                if current_time - session.last_update > 300  # 5 minutes timeout
            ]
            for user_id in inactive_users:
                await self.end_session(user_id)
        
        # Update active sessions
        for session in self.sessions.values():
            await session.update(delta_time)
            await asyncio.sleep(MESSAGE_RATE_LIMIT)  # Ensure rate limit compliance
