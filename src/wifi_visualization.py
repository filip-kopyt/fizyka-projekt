import arcade
from array import array
from typing import NoReturn, Generator

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

def todo() -> NoReturn:
    raise NotImplementedError()

def generate_init_buffer(
    screen_size: tuple[int, int]
) -> array[float]:
    width, height = screen_size
    
    def _data_generator() -> Generator[float, None, None]:
        for _ in range(width * height):
            yield 0.0
            yield 0.0
            yield 0.0
    
    return array('f', _data_generator())

class WifiVisualizerWindow(arcade.Window):
    def __init__(self):
        super().__init__(
            WINDOW_WIDTH, WINDOW_HEIGHT,
            "Wi-Fi range visualization",
            gl_version=(4, 3),
            resizable=False
        )
        
        self.center_window()
        
        initial_data = generate_init_buffer(self.get_size())
        # SSBO - Shader Storage Buffer Object
        self.ssbo_previous = self.ctx.buffer(data=initial_data)
        self.ssbo_current = self.ctx.buffer(data=initial_data)
        
        
        
        
        