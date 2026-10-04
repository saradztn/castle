// ocean.fx — بحر متحرك: موجات + لمعة شمس + تفتيح عند الحواف (Castle & Palace)

texture gTexture;
sampler Sampler0 = sampler_state
{
    Texture = (gTexture);
    MinFilter = Linear;
    MagFilter = Linear;
    MipFilter = Linear;
    AddressU = Wrap;
    AddressV = Wrap;
};

float gTime = 0.0;
float gWaveScale = 0.35;
float gChopAmount = 0.55;
float3 gDeepColor   = float3(0.055, 0.180, 0.235);
float3 gShallowColor= float3(0.180, 0.470, 0.520);
float3 gSunColor    = float3(1.00, 0.78, 0.48);
float3 gSunDir      = float3(-0.62, 0.55, 0.56);

float hash(float2 p)
{
    return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453);
}

float noise(float2 p)
{
    float2 i = floor(p);
    float2 f = frac(p);
    float a = hash(i);
    float b = hash(i + float2(1, 0));
    float c = hash(i + float2(0, 1));
    float d = hash(i + float2(1, 1));
    float2 u = f * f * (3.0 - 2.0 * f);
    return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
}

float4 main(float2 texCoord : TEXCOORD0) : COLOR0
{
    // موجات متراكبة
    float2 uv1 = texCoord * 4.0 + float2(gTime * 0.014, gTime * 0.009);
    float2 uv2 = texCoord * 9.0 - float2(gTime * 0.026, gTime * 0.017);

    float n1 = noise(uv1);
    float n2 = noise(uv2);
    float wave = (n1 * 0.65 + n2 * 0.35);

    // مشتق لتوليد Normal تقريبي
    float e = 0.0035;
    float nx = noise(uv1 + float2(e, 0.0)) - noise(uv1 - float2(e, 0.0));
    float ny = noise(uv1 + float2(0.0, e)) - noise(uv1 - float2(0.0, e));
    float3 N = normalize(float3(-nx * gChopAmount * 12.0, -ny * gChopAmount * 12.0, 1.0));

    // لون الماء حسب العمق التقريبي (من الألبيو)
    float4 base = tex2D(Sampler0, texCoord);
    float depth = saturate(base.r * 2.0 + base.g);
    float3 waterColor = lerp(gDeepColor, gShallowColor, (1.0 - depth) * 0.75 + wave * 0.25);

    // لمعة الشمس
    float3 V = float3(0.0, 0.0, 1.0);
    float3 H = normalize(gSunDir + V);
    float spec = pow(max(0.0, dot(N, H)), 90.0) * 0.9;

    // رغوة على القمم
    float crest = smoothstep(0.72, 0.95, wave * (1.0 + gChopAmount));

    float3 col = waterColor + gSunColor * spec + float3(crest * 0.55, crest * 0.62, crest * 0.66);

    return float4(col, base.a);
}

technique tec0
{
    pass P0
    {
        PixelShader = compile ps_3_0 main();
    }
}
