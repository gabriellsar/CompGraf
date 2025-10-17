#version 410

out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec3 Tangent;
in vec2 TexCoord;

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
uniform sampler2D normalMap;
uniform sampler2D specularMap;

void main()
{
    vec3 normalFromMap = texture(normalMap, TexCoord).rgb;
    normalFromMap = normalize(normalFromMap * 2.0 - 1.0);

    vec3 T = normalize(Tangent);
    vec3 N = normalize(Normal);

    T = normalize(T - dot(T, N) * N);
    vec3 B = cross(N, T);
    mat3 TBN = mat3(T, B, N);

    vec3 finalNormal = normalize(TBN * normalFromMap);

    vec3 texColor = texture(decal, TexCoord).rgb;
    vec3 ambient = lamb.rgb * mdif.rgb * texColor;

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lpos.xyz - FragPos);

    float diff = max(dot(finalNormal, lightDir), 0.0);
    vec3 diffuse = ldif.rgb * (diff * mdif.rgb * texColor);

    vec3 specular = vec3(0.0, 0.0, 0.0);
    if(diff > 0.0)
    {
        float specularIntensity = texture(specularMap, TexCoord).r;

        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, finalNormal);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), mshi);

        specular = lspe.rgb * (spec * mspe.rgb) * specularIntensity;
    }

    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, 1.0);
}