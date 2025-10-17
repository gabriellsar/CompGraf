import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PIL import Image, ImageOps

import glm
from scene_graph.python.camera3d import *
from scene_graph.python.light import *
from scene_graph.python.shader import *
from scene_graph.python.material import *
from scene_graph.python.texture import Texture
from scene_graph.python.transform import *
from scene_graph.python.node import *
from scene_graph.python.scene import *
from scene_graph.python.sphere import *
from scene_graph.python.engine import *

SUN_RADIUS = 2.5
MERCURY_RADIUS = 0.4
EARTH_RADIUS = 1.0
MOON_RADIUS = 0.25

MERCURY_DISTANCE = 5.0
EARTH_DISTANCE = 10.0
MOON_DISTANCE = 1.8

camera = None
scene = None
shd_ger = None
shd_recp = None

class SolarSystemEngine3D(Engine):
    pass


def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)

    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    win = glfw.create_window(mode.size.width, mode.size.height, "Mini-Sistema Solar 3D", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.set_key_callback(win,keyboard)

    # Make the window's context current
    glfw.make_context_current(win)
    print("OpenGL version: ",glGetString(GL_VERSION))

    initialize(win)

    # Loop until the user closes the window
    while not glfw.window_should_close(win):
        # Render here, e.g. using pyOpenGL
        display(win)

        # Swap front and back buffers
        glfw.swap_buffers(win)

        # Poll for and process events
        glfw.poll_events()

viewer_pos = glm.vec3(0, 10, 25)

def initialize (win):
    global camera, scene, shd_ger, shd_recp
    glClearColor(0.1,0.1,0.1,1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    camera = Camera3D(viewer_pos[0],viewer_pos[1],viewer_pos[2])
    arcball = camera.CreateArcball()
    arcball.Attach(win)

    light = Light(0.0,0.0,0.0,1.0,"world")

    # Shader Receptor de Luz
    shd_recp = Shader(light, "world")
    shd_recp.AttachVertexShader("scene_graph/shaders/ilum_vert/vertex_text_ilum.glsl")
    shd_recp.AttachFragmentShader("scene_graph/shaders/ilum_vert/fragment_text_ilum.glsl")
    shd_recp.Link()

    # Shader Gerador de Luz
    shd_ger = Shader(light, "world")
    shd_ger.AttachVertexShader("scene_graph/shaders/unlum_vert/vertex_text_unlum.glsl")
    shd_ger.AttachFragmentShader("scene_graph/shaders/unlum_vert/fragment_text_unlum.glsl")
    shd_ger.Link()

    # Textura e Materiais
    sun_tex = Texture("decal", "scene_graph/images/sun.jpg")
    earth_tex = Texture("decal", "scene_graph/images/earth.jpg")
    moon_tex = Texture("decal", "scene_graph/images/moon.jpg")
    mercury_tex = Texture("decal", "scene_graph/images/mercury.jpg")
    space_tex = Texture("decal", "scene_graph/images/space.jpeg")

    white = Material(1.0, 1.0, 1.0)

    # Geometrias
    sphere = Sphere()

    # Transformações
    background_trf = Transform()
    background_trf.Scale(24, 24, 1)
    background_trf.Translate(-0.5, -0.5, -0.5)

    # Sol
    sun_trf = Transform()
    sun_trf.Scale(SUN_RADIUS, SUN_RADIUS, SUN_RADIUS)

    # Mercúrio
    mercury_local_trf = Transform()
    mercury_local_trf.Translate(MERCURY_DISTANCE, 0, 0)
    mercury_local_trf.Scale(MERCURY_RADIUS, MERCURY_RADIUS, MERCURY_RADIUS)
    mercury_orbit_trf = Transform()

    # Terra
    earth_local_trf = Transform()
    earth_position_trf = Transform()
    earth_position_trf.Translate(EARTH_DISTANCE, 0, 0)
    earth_local_trf.Scale(EARTH_RADIUS, EARTH_RADIUS, EARTH_RADIUS)

    earth_orbit_trf = Transform()

    # Lua
    moon_local_trf = Transform()
    moon_position_trf = Transform()
    moon_position_trf.Translate(MOON_DISTANCE, 0, 0)
    moon_local_trf.Scale(MOON_RADIUS, MOON_RADIUS, MOON_RADIUS)

    moon_orbit_trf = Transform()

    # Grafo de Cena
    #background_node = Node(shader=shd_recp, trf=background_trf, apps=[space_tex, white], shps=[sphere])
    sun_node = Node(shader=shd_ger, trf=sun_trf, apps=[sun_tex, white], shps=[sphere])

    mercury_inner_node = Node(shader=shd_recp, apps=[mercury_tex, white], shps=[sphere])
    mercury_position_node = Node(trf=mercury_local_trf, nodes=[mercury_inner_node])

    moon_local_node = Node(shader=shd_recp, trf=moon_local_trf, apps=[moon_tex, white], shps=[sphere])
    moon_position_node = Node(trf=moon_position_trf, nodes=[moon_local_node])
    moon_orbit_node = Node(trf=moon_orbit_trf, nodes=[moon_position_node])

    earth_local_node = Node(shader=shd_recp, trf=earth_local_trf, apps=[earth_tex, white], shps=[sphere])
    earth_position_node = Node(trf=earth_position_trf, nodes=[earth_local_node, moon_orbit_node])
    earth_orbit_node = Node(trf=earth_orbit_trf, nodes=[earth_position_node])

    root = Node(nodes=[
        sun_node,
        Node(trf=mercury_orbit_trf, nodes=[mercury_position_node]),
        earth_orbit_node
    ])
    scene = Scene(root)

def display (win):
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  shd_ger = scene.root.nodes[0].shader
  shd_recp = scene.root.nodes[1].nodes[0].nodes[0].shader

  shd_ger.UseProgram()
  shd_ger.SetUniform("lightColor", glm.vec3(1.0, 1.0, 0.8))

  shd_recp.UseProgram()
  shd_recp.SetUniform("viewPos", camera.GetEye())

  scene.Render(camera)

def keyboard (win, key, scancode, action, mods):
   if key == glfw.KEY_Q and action == glfw.PRESS:
      glfw.set_window_should_close(win,glfw.TRUE)

if __name__ == "__main__":
    main()
