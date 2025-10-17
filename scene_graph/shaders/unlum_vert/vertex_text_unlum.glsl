#version 410

layout (location = 0) in vec3 aPos;
layout (location = 3) in vec2 aTexCoord;

out vec2 TexCoord;

uniform mat4 Mvp;

void main()
{
    TexCoord = aTexCoord;
    gl_Position = Mvp * vec4(aPos, 1.0);
}