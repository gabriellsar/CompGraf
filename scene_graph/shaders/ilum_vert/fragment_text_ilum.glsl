#version 410

out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord; // Coordenadas de textura

// Propriedades da luz
uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;
uniform vec4 lpos;

// Propriedades do material
uniform vec4 mamb;
uniform vec4 mdif;
uniform vec4 mspe;
uniform float mshi;

// Posição da Câmera
uniform vec3 viewPos;

// Textura
uniform sampler2D decal;

void main()
{
    vec3 ambient = lamb.rgb * mamb.rgb;

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lpos.xyz - FragPos);

    vec3 texColor = texture(decal, TexCoord).rgb;
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = ldif.rgb * (diff * mdif.rgb * texColor);

    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), mshi);
    vec3 specular = lspe.rgb * (spec * mspe.rgb);

    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, 1.0);
}