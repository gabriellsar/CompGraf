import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PIL import Image, ImageOps

import glm
from scene_graph.python.camera3d import *
from scene_graph.python.light import *
from scene_graph.python.shader import *
from scene_graph.python.material import *
from scene_graph.python.state import State
from scene_graph.python.texture import Texture
from scene_graph.python.texcube import TexCube
from scene_graph.python.skybox import SkyBox
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

camera_mode = 'sun_focus' # 'sun_focus', 'earth_to_moon'

class SolarSystemEngine3D(Engine):
    def __init__(self, sun_trf, earth_orbit_trf, earth_local_trf, moon_orbit_trf, moon_local_trf, mercury_orbit_trf, mercury_local_trf,
                 camera_ref, earth_node, moon_node_ref):
        self.camera = camera_ref
        self.earth_position_node = earth_node
        self.moon_local_node = moon_node_ref

        self.sun_trf = sun_trf
        self.earth_local_trf = earth_local_trf
        self.earth_position_node = earth_node
        self.earth_orbit_trf = earth_orbit_trf
        self.moon_local_trf = moon_local_trf
        self.moon_orbit_trf = moon_orbit_trf
        self.mercury_local_trf = mercury_local_trf
        self.mercury_orbit_trf = mercury_orbit_trf


    def Update(self, dt):
        earth_orbit_speed = 360 / 10.0
        mercury_orbit_speed = 360 / 6.0
        moon_orbit_speed = 360 / 3.0

        earth_rotation_speed = 360 / 2.0
        sun_rotation_speed = 360 / 8.0
        mercury_rotation_speed = 360 / 4.0
        moon_rotation_speed = 360 / 27.0

        self.earth_orbit_trf.Rotate(earth_orbit_speed * dt, 0, 1, 0)
        self.mercury_orbit_trf.Rotate(mercury_orbit_speed * dt, 0, 1, 0)
        self.moon_orbit_trf.Rotate(moon_orbit_speed * dt, 0, 1, 0)

        self.sun_trf.Rotate(sun_rotation_speed * dt, 0, 1, 0)
        self.earth_local_trf.Rotate(earth_rotation_speed * dt, 0, 1, 0)
        self.mercury_local_trf.Rotate(mercury_rotation_speed * dt, 0, 1, 0)
        self.moon_local_trf.Rotate(moon_rotation_speed * dt, 0, 1, 0)

        if camera_mode == 'earth_to_moon':
            earth_matrix = self.earth_position_node.GetModelMatrix()
            earth_pos = glm.vec3(earth_matrix[3])

            moon_matrix = self.moon_local_node.GetModelMatrix()
            moon_pos = glm.vec3(moon_matrix[3])

            self.camera.SetEye(earth_pos.x, earth_pos.y, earth_pos.z)
            self.camera.SetCenter(moon_pos.x, moon_pos.y, moon_pos.z)


def main():
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)

    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    win = glfw.create_window(mode.size.width, mode.size.height, "Mini Sistema Solar 3D", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.set_key_callback(win,keyboard)

    glfw.make_context_current(win)
    print("OpenGL version: ",glGetString(GL_VERSION))

    initialize(win)

    t0 = glfw.get_time()
    while not glfw.window_should_close(win):
        t = glfw.get_time()
        dt = t - t0
        t0 = t

        scene.Update(dt)

        display(win)
        glfw.swap_buffers(win)
        glfw.poll_events()

viewer_pos = glm.vec3(0, 10, 25)

def initialize (win):
    global camera, scene, shd_ger, shd_recp
    global sun_node, earth_position_node, moon_local_node

    glClearColor(0.1,0.1,0.1,1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    camera = Camera3D(viewer_pos[0],viewer_pos[1],viewer_pos[2])

    light = Light(0.0,0.0,0.0,1.0,"world")

    # Shader SkyBox
    shd_skybox = Shader()
    shd_skybox.AttachVertexShader("scene_graph/shaders/skybox_vertex.glsl")
    shd_skybox.AttachFragmentShader("scene_graph/shaders/skybox_fragment.glsl")
    shd_skybox.Link()

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
    skybox_tex = TexCube("skybox", "scene_graph/images/space-skybox.png")
    skybox_geom = SkyBox()

    sun_tex = Texture("decal", "scene_graph/images/sun.jpg")

    earth_tex = Texture("decal", "scene_graph/images/earth.jpg")
    earth_normal_map = Texture("normalMap", "scene_graph/images/earth-normal.png")
    earth_specular_map = Texture("specularMap", "scene_graph/images/earth-specular.jpg")

    moon_tex = Texture("decal", "scene_graph/images/moon.jpg")
    moon_normal_map = Texture("normalMap", "scene_graph/images/moon-normal.png")

    mercury_tex = Texture("decal", "scene_graph/images/mercury.jpg")
    crater_normal_map = Texture("normalMap", "scene_graph/images/crater-normal.jpg")


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
    sun_node = Node(shader=shd_ger, trf=sun_trf, apps=[sun_tex], shps=[sphere])

    mercury_inner_node = Node(shader=shd_recp, apps=[mercury_tex,crater_normal_map,white], shps=[sphere])
    mercury_position_node = Node(trf=mercury_local_trf, nodes=[mercury_inner_node])

    moon_local_node = Node(shader=shd_recp, trf=moon_local_trf, apps=[moon_tex,moon_normal_map,white], shps=[sphere])
    moon_position_node = Node(trf=moon_position_trf, nodes=[moon_local_node])
    moon_orbit_node = Node(trf=moon_orbit_trf, nodes=[moon_position_node])

    earth_local_node = Node(
        shader=shd_recp,
        trf=earth_local_trf,
        apps=[earth_tex,earth_normal_map,earth_specular_map,white],
        shps=[sphere]
    )
    earth_position_node = Node(trf=earth_position_trf, nodes=[earth_local_node, moon_orbit_node])
    earth_orbit_node = Node(trf=earth_orbit_trf, nodes=[earth_position_node])

    skybox_node = Node(shader=shd_skybox, apps=[skybox_tex], shps=[skybox_geom])

    root = Node(nodes=[
        sun_node,
        Node(trf=mercury_orbit_trf, nodes=[mercury_position_node]),
        earth_orbit_node
    ])
    scene = Scene(root)
    scene.skybox = skybox_node

    engine = SolarSystemEngine3D(
        sun_trf, earth_orbit_trf, earth_local_trf,
        moon_orbit_trf, moon_local_trf,
        mercury_orbit_trf, mercury_local_trf,
        camera, earth_position_node, moon_local_node
    )
    scene.AddEngine(engine)

def display (win):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDepthMask(GL_FALSE)
    glDepthFunc(GL_LEQUAL)

    skybox_st = State(camera)
    skybox_shader = scene.skybox.shader
    skybox_st.PushShader(skybox_shader)

    skybox_shader.SetUniform("view", camera.GetViewMatrix())
    skybox_shader.SetUniform("projection", camera.GetProjMatrix())

    scene.skybox.apps[0].Load(skybox_st)
    scene.skybox.shps[0].Draw(skybox_st)
    scene.skybox.apps[0].Unload(skybox_st)

    skybox_st.PopShader()
    glDepthFunc(GL_LESS)
    glDepthMask(GL_TRUE)

    shd_recp.UseProgram()
    shd_recp.SetUniform("viewPos", camera.GetEye())

    scene.Render(camera)

def keyboard (win, key, scancode, action, mods):
    global camera_mode, camera, viewer_pos
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)

    elif key == glfw.KEY_C and action == glfw.PRESS:
        print("Câmera focada no Sol.")
        camera_mode = 'sun_focus'
        camera.SetCenter(0.0, 0.0, 0.0)
        camera.SetEye(viewer_pos.x, viewer_pos.y, viewer_pos.z)

    elif key == glfw.KEY_L:
        print("Modo Câmera: Na Terra, olhando para a Lua.")
        camera_mode = 'earth_to_moon'

if __name__ == "__main__":
    main()
