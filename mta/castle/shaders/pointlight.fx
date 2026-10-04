// ============================================================================
//  pointlight.fx — نظام إضاءة نقطية قوي لموديل القلعة (MTA:SA)
//  يُطبَّق عبر engineApplyShaderToWorldTexture على خامات الموديل
//  يدعم حتى 32 مصدر ضوء حقيقي (مشاعل، فوانيس الشوارع، نوافذ مضيئة، منارة)
//  النموذج: Ambient + Lambert نصف-ناعم + انحلال مزدوج + ارتعاش لهب + نبض منارة
// ============================================================================

#define MAX_LIGHTS 32

float4x4 gWorldViewProj;      // تُوفّرها MTA تلقائيًا
float4x4 gWorld;

texture gTexture;
sampler sTexture = sampler_state
{
    Texture   = (gTexture);
    MinFilter = Linear;
    MagFilter = Linear;
    MipFilter = Linear;
};

// ---- بيانات المصابيح (تُعبَّأ من Lua كل 120ms) ----
float4 gLightPos[MAX_LIGHTS];      // xyz = الموضع بالعالم، w = المدى
float3 gLightColor[MAX_LIGHTS];    // اللون مضروبًا في الشدة
float2 gLightParams[MAX_LIGHTS];   // x = النوع (1 مشعل/فانوس، 2 منارة)
int    gLightCount;
float  gTime;                      // زمن بالثواني (للارتعاش)
float3 gAmbient;                   // الإضاءة المحيطة (نهار / ليل)

struct VS_OUT
{
    float4 pos : POSITION;
    float2 uv  : TEXCOORD0;
    float3 wp  : TEXCOORD1;
    float3 nrm : TEXCOORD2;
};

VS_OUT CastleVS(float4 pos : POSITION, float3 nrm : NORMAL, float2 uv : TEXCOORD0)
{
    VS_OUT o;
    o.pos = mul(pos, gWorldViewProj);
    o.wp  = mul(pos, gWorld).xyz;
    o.nrm = mul(nrm, (float3x3)gWorld);
    o.uv  = uv;
    return o;
}

float4 CastlePS(VS_OUT i) : COLOR
{
    float4 tex = tex2D(sTexture, i.uv);
    float3 base = tex.rgb;
    float3 n = normalize(i.nrm);

    float3 acc = base * gAmbient;

    for (int k = 0; k < MAX_LIGHTS; k++)
    {
        if (k >= gLightCount) break;

        float3 Lp   = gLightPos[k].xyz;
        float  r    = gLightPos[k].w;
        float  kind = gLightParams[k].x;
        if (r <= 0.0) continue;

        float3 d    = Lp - i.wp;
        float  d2   = dot(d, d);
        if (d2 > r * r) continue;

        float  dist = sqrt(d2);
        float3 L    = d / max(dist, 0.001);

        // انحلال مزدوج مع تصحيح المدى (ضوء قوي قريب، يتلاشى بسلاسة)
        float att = saturate(1.0 - dist / r);
        att = (att * att) / (1.0 + 0.20 * dist + 0.05 * d2);

        // Lambert ناعم (half-Lambert) لإبراز نسيج الحجر بلا قسوة
        float ndl = saturate(dot(n, L));
        float lam = ndl * 0.78 + 0.22 * saturate((ndl + 1.0) * 0.5);

        // ارتعاش اللهب / نبض المنارة
        float flick;
        if (kind > 1.5)
            flick = 0.70 + 0.30 * sin(gTime * 1.7);
        else
            flick = 0.93 + 0.07 * sin(gTime * 9.0 + Lp.x * 0.13 + Lp.z * 0.07);

        acc += base * gLightColor[k] * lam * att * flick * 3.6;
    }

    // تشبّع ناعم لمنع الاحتراق الأبيض
    acc = acc / (acc + 0.85) * 1.85;

    return float4(acc, tex.a);
}

technique CastleLight
{
    pass P0
    {
        VertexShader = compile vs_3_0 CastleVS();
        PixelShader  = compile ps_3_0 CastlePS();
    }
}
