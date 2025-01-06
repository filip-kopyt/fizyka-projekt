# taken from https://api.arcade.academy/en/platformer_tutorial_revamp/tutorials/compute_shader/index.html

import random
from array import array
from pathlib import Path
from typing import Generator, Tuple

import arcade
from arcade.gl import BufferDescription

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1200

GRAPH_WIDTH = 200
GRAPH_HEIGHT = 120
GRAPH_MARGIN = 5

NUM_STARS = 4000
USE_COLORED_STARS = True


def gen_initial_data(
    screen_size: Tuple[int, int],
    num_stars: int = NUM_STARS,
    use_color: bool = False
) -> array[float]:
    width, heigth = screen_size
    color_channel_min = 0.5 if use_color else 1.0
    
    def _data_generator() -> Generator[float, None, None]:
        for _ in range(num_stars):
            yield random.randrange(0, width)
            yield random.randrange(0, heigth)
            yield 0.0
            yield 6.0
            
            yield 0.0
            yield 0.0
            yield 0.0
            yield 0.0
            
            yield random.uniform(color_channel_min, 1.0)
            yield random.uniform(color_channel_min, 1.0)
            yield random.uniform(color_channel_min, 1.0)
            yield 1.0
            
    return array('f', _data_generator())


class NBodyGravityWindow(arcade.Window):
    def __init__(self):
        super().__init__(
            WINDOW_WIDTH, WINDOW_HEIGHT,
            "N-Body Gravity with Compute Shaders",
            gl_version=(4, 3),
            resizable=False
        )
        
        self.center_window()
        
        initial_data = gen_initial_data(self.get_size(), use_color=USE_COLORED_STARS)
        # SSBO == Shader Storage Buffer Object
        self.ssbo_previous = self.ctx.buffer(data=initial_data)
        self.ssbo_current = self.ctx.buffer(data=initial_data)
        
        buffer_format = "4f 4x4 4f"
        attributes = ["in_vertex", "in_color"]

        # VAO == Vertex Array Object
        self.vao_previous = self.ctx.geometry(
            [BufferDescription(self.ssbo_previous, buffer_format, attributes)],
            mode=self.ctx.POINTS
        )
        self.vao_current = self.ctx.geometry(
            [BufferDescription(self.ssbo_current, buffer_format, attributes)],
            mode=self.ctx.POINTS
        )
        
        vertex_shader_source = Path("src/shaders/nbody.vert").read_text()
        fragment_shader_source = Path("src/shaders/nbody.frag").read_text()
        geometry_shader_source = Path("src/shaders/nbody.geom").read_text()
        
        self.program = self.ctx.program(
            vertex_shader=vertex_shader_source,
            geometry_shader=geometry_shader_source,
            fragment_shader=fragment_shader_source
        )
        
        compute_shader_source = Path("src/shaders/nbody.comp").read_text()
        
        self.group_x = 256
        self.group_y = 1
        
        self.compute_shader_defines = {
            "COMPUTE_SIZE_X": self.group_x,
            "COMPUTE_SIZE_Y": self.group_y
        }
        
        for token, value in self.compute_shader_defines.items():
            compute_shader_source = compute_shader_source.replace(token, str(value))
            
        self.compute_shader = self.ctx.compute_shader(source=compute_shader_source)
        
        arcade.enable_timings()
        self.perf_graph_list: arcade.SpriteList[arcade.PerfGraph] = arcade.SpriteList()
        
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="FPS")
        graph.position = GRAPH_WIDTH / 2, self.height - GRAPH_HEIGHT / 2
        self.perf_graph_list.append(graph)
        
    def on_draw(self):
        self.clear()
        self.ctx.enable(self.ctx.BLEND)
        
        self.ssbo_previous.bind_to_storage_buffer(binding=0)
        self.ssbo_current.bind_to_storage_buffer(binding=1)
        
        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)
        self.vao_current.render(self.program)
        
        self.ssbo_previous, self.ssbo_current = self.ssbo_current, self.ssbo_previous
        self.vao_previous, self.vao_current = self.vao_current, self.vao_previous
        
        self.perf_graph_list.draw()
        

if __name__ == "__main__":
    app = NBodyGravityWindow()
    arcade.run()
