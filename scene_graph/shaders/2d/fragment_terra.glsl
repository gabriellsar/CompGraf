#version 410

in vec2 tex_coord_out;
out vec4 outcolor;

uniform sampler2D decal;
uniform float u_rotation_offset;

void main()
{
    if (distance(tex_coord_out, vec2(0.5, 0.5)) > 0.5)
        {
            discard;
        }

   vec2 scrolledCoords = vec2(tex_coord_out.x + u_rotation_offset, tex_coord_out.y);
   outcolor = texture(decal, scrolledCoords);
}