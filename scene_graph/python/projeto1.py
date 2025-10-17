import glfw

from camera2d import *
from engine import *
from node import *
from quad import *
from scene import *
from shader import *
from texture import *
from transform import *

camera = None
scene = None
earth_shader = None

class SolarSystemEngine(Engine):
    def __init__(self, earth_orbit_trf, moon_orbit_trf, mercury_orbit_trf):
        self.earth_orbit_trf = earth_orbit_trf
        self.moon_orbit_trf = moon_orbit_trf
        self.mercury_orbit_trf = mercury_orbit_trf

    def Update(self, dt):
        earth_orbit_speed = 30.0
        moon_orbit_speed = 100.0
        mercury_orbit_speed = 50.0

        # Movimento de translação
        self.earth_orbit_trf.Rotate(earth_orbit_speed * dt, 0, 0, 1)
        self.moon_orbit_trf.Rotate(moon_orbit_speed * dt, 0, 0, 1)
        self.mercury_orbit_trf.Rotate(mercury_orbit_speed * dt, 0, 0, 1)

def main():
    if not glfw.init(): return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    win = glfw.create_window(800, 800, "Mini Sistema Solar", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.set_key_callback(win, keyboard)
    glfw.make_context_current(win)
    initialize()
    t0 = glfw.get_time()
    while not glfw.window_should_close(win):
        t = glfw.get_time()
        dt = t - t0
        t0 = t
        update(dt)
        display()
        glfw.swap_buffers(win)
        glfw.poll_events()
    glfw.terminate()


def initialize():
    global camera, scene,earth_shader
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    camera = Camera2D(xmin=-8, xmax=8, ymin=-8, ymax=8)

    # Shader
    shader = Shader()
    shader.AttachVertexShader("../shaders/2d/vertex.glsl")
    shader.AttachFragmentShader("../shaders/2d/fragment.glsl")
    shader.Link()

    # Shader Terra
    earth_shader = Shader()
    earth_shader.AttachVertexShader("../shaders/2d/vertex.glsl")
    earth_shader.AttachFragmentShader("../shaders/2d/fragment_terra.glsl")
    earth_shader.Link()

    # Geometrias
    quad = Quad()

    # Texturas
    sun_tex = Texture("decal", "../images/sun.jpg")
    earth_tex = Texture("decal", "../images/earth.jpg")
    moon_tex = Texture("decal", "../images/moon.jpg")
    mercury_tex = Texture("decal", "../images/mercury.jpg")
    space_tex = Texture("decal", "../images/space.jpeg")

    # Transformações
    background_trf = Transform()
    background_trf.Scale(24, 24, 1)
    background_trf.Translate(-0.5, -0.5, -0.5)

    # Sol
    sun_trf = Transform()
    sun_trf.Translate(-2.5, -2.5, 0)
    sun_trf.Scale(5.0, 5.0, 1.0)

    # Mercúrio
    mercury_local_trf = Transform()
    mercury_local_trf.Translate(3.2, -0.3, 0)
    mercury_local_trf.Scale(0.6, 0.6, 1.0)
    mercury_orbit_trf = Transform()

    # Terra
    earth_local_trf = Transform()
    earth_local_trf.Translate(-0.5, -0.5, 0)
    earth_local_trf.Scale(1.0, 1.0, 1.0)

    earth_orbit_trf = Transform()
    earth_position_trf = Transform()
    earth_position_trf.Translate(5.5, 0, 0)

    # Lua
    moon_local_trf = Transform()
    moon_local_trf.Translate(-0.5, -0.5, 0)
    moon_local_trf.Scale(0.5, 0.5, 1.0)

    moon_orbit_trf = Transform()
    moon_position_trf = Transform()
    moon_position_trf.Translate(1.5, 0, 0)

    # Grafo de Cena
    background_node = Node(trf=background_trf, apps=[space_tex], shps=[quad])
    sun_node = Node(trf=sun_trf, apps=[sun_tex], shps=[quad])

    mercury_inner_node = Node(apps=[mercury_tex], shps=[quad])
    mercury_position_node = Node(trf=mercury_local_trf, nodes=[mercury_inner_node])

    moon_local_node = Node(trf=moon_local_trf, apps=[moon_tex], shps=[quad])
    moon_position_node = Node(trf=moon_position_trf, nodes=[moon_local_node])
    moon_orbit_node = Node(trf=moon_orbit_trf, nodes=[moon_position_node])

    earth_local_node = Node(shader=earth_shader, trf=earth_local_trf, apps=[earth_tex], shps=[quad])
    earth_position_node = Node(trf=earth_position_trf, nodes=[earth_local_node, moon_orbit_node])
    earth_orbit_node = Node(trf=earth_orbit_trf, nodes=[earth_position_node])

    root = Node(shader=shader, nodes=[
        background_node,
        sun_node,
        Node(trf=mercury_orbit_trf, nodes=[mercury_position_node]),
        earth_orbit_node
    ])

    scene = Scene(root)
    engine = SolarSystemEngine(earth_orbit_trf, moon_orbit_trf, mercury_orbit_trf)
    scene.AddEngine(engine)


def update(dt):
    scene.Update(dt)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    scroll_speed = 0.5
    time_value = glfw.get_time()

    earth_shader.UseProgram()
    earth_shader.SetUniform("u_rotation_offset", time_value * scroll_speed)

    scene.Render(camera)


def keyboard(win, key, scancode, action, mods):
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, True)


if __name__ == "__main__":
    main()