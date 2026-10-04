// window_emissive.fx — نوافذ زجاجية مضيئة ليلًا (Castle & Palace)
// يُطبَّق على خامة glass_leaded_pane_emissive، وشدة التوهّج تُضبط من Lua.

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

float gIntensity = 0.0;
float3 gColor = float3(1.0, 0.72, 0.40);

float4 main(float2 texCoord : TEXCOORD0) : COLOR0
{
    float4 c = tex2D(Sampler0, texCoord);

    // نُبرز الأجزاء الفاتحة من الزجاج (التي "تتوهّج" ليلًا)
    float lum = dot(c.rgb, float3(0.299, 0.587, 0.114));
    float glow = saturate(lum * 1.8 + 0.18);

    float3 emissive = gColor * glow * gIntensity * 1.35;

    return float4(c.rgb + emissive, c.a);
}

technique tec0
{
    pass P0
    {
        PixelShader = compile ps_2_0 main();
    }
}
