"""
DOOM Engine interface for the Discord bot.
Handles game state, player actions, and frame generation.
"""
import os
import json
import pygame
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from python_doom import DoomGame, Button, GameVariable
from PIL import Image

@dataclass
class GameState:
    health: int = 100
    armor: int = 0
    ammo: int = 50
    weapon: int = 2  # Default to pistol
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # x, y, angle
    level: int = 1
    score: int = 0

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class DoomEngine:
    def __init__(self, wad_path: str = None):
        """Initialize the DOOM engine with optional WAD file"""
        self.wad_path = wad_path or os.path.join('assets', 'doom1.wad')
        self.game_state = GameState()
        self.frame_buffer = None
        self.initialized = False
        self.game = DoomGame()
        self.setup_game()
        
    def setup_game(self):
        """Configure DOOM game settings"""
        self.game.set_doom_game_path(self.wad_path)
        self.game.set_screen_resolution(640, 400)
        self.game.set_screen_format(DoomGame.GRAY8)  # 8-bit grayscale
        
        # Configure available buttons
        self.game.add_available_button(Button.MOVE_FORWARD)
        self.game.add_available_button(Button.MOVE_BACKWARD)
        self.game.add_available_button(Button.TURN_LEFT)
        self.game.add_available_button(Button.TURN_RIGHT)
        self.game.add_available_button(Button.ATTACK)
        self.game.add_available_button(Button.USE)
        
        # Configure game variables we want to track
        self.game.add_available_game_variable(GameVariable.HEALTH)
        self.game.add_available_game_variable(GameVariable.ARMOR)
        self.game.add_available_game_variable(GameVariable.AMMO)
        self.game.add_available_game_variable(GameVariable.WEAPON)
        
        # Set render mode
        self.game.set_window_visible(False)
        self.game.set_mode(DoomGame.PLAYER)
        
    async def initialize(self):
        """Initialize the DOOM engine and pygame"""
        if self.initialized:
            return
            
        self.game.init()
        self.game.new_episode()
        self.initialized = True
        
    async def update(self, delta_time: float) -> None:
        """Update game state"""
        if not self.initialized:
            await self.initialize()
            
        # Update game state from DOOM engine
        self.game_state.health = self.game.get_game_variable(GameVariable.HEALTH)
        self.game_state.armor = self.game.get_game_variable(GameVariable.ARMOR)
        self.game_state.ammo = self.game.get_game_variable(GameVariable.AMMO)
        self.game_state.weapon = self.game.get_game_variable(GameVariable.WEAPON)
        
        # Get the current frame
        self.frame_buffer = self.game.get_state().screen_buffer
        
    async def handle_input(self, action: str) -> None:
        """Handle player input"""
        if not self.initialized:
            await self.initialize()
            
        actions = {
            'forward': self._move_forward,
            'backward': self._move_backward,
            'left': self._turn_left,
            'right': self._turn_right,
            'shoot': self._shoot,
            'use': self._use,
            'weapon_switch': self._switch_weapon
        }
        
        if action in actions:
            await actions[action]()
            
    async def get_frame(self) -> np.ndarray:
        """Get current frame as numpy array"""
        if not self.initialized:
            await self.initialize()
        return self.frame_buffer if self.frame_buffer is not None else np.zeros((400, 640), dtype=np.uint8)
        
    async def save_state(self) -> dict:
        """Save current game state"""
        state_data = self.game_state.to_dict()
        
        # Save to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join('assets', 'saves', f'save_{self.game_state.level}_{timestamp}.json')
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(state_data, f)
            
        return state_data
        
    async def load_state(self, state: dict) -> None:
        """Load saved game state"""
        self.game_state = GameState.from_dict(state)
        # TODO: Implement actual game state restoration in python-doom
        
    # Private movement methods
    async def _move_forward(self):
        """Move player forward"""
        action = [1, 0, 0, 0, 0, 0]  # MOVE_FORWARD
        reward = self.game.make_action(action)
        
    async def _move_backward(self):
        """Move player backward"""
        action = [0, 1, 0, 0, 0, 0]  # MOVE_BACKWARD
        reward = self.game.make_action(action)
        
    async def _turn_left(self):
        """Turn player left"""
        action = [0, 0, 1, 0, 0, 0]  # TURN_LEFT
        reward = self.game.make_action(action)
        
    async def _turn_right(self):
        """Turn player right"""
        action = [0, 0, 0, 1, 0, 0]  # TURN_RIGHT
        reward = self.game.make_action(action)
        
    async def _shoot(self):
        """Fire current weapon"""
        if self.game_state.ammo > 0:
            action = [0, 0, 0, 0, 1, 0]  # ATTACK
            reward = self.game.make_action(action)
        
    async def _use(self):
        """Use/interact with object in front of player"""
        action = [0, 0, 0, 0, 0, 1]  # USE
        reward = self.game.make_action(action)
        
    async def _switch_weapon(self):
        """Switch to next available weapon"""
        # TODO: Implement weapon switching through python-doom API
        pass
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'game') and self.game is not None:
            self.game.close()
