# Tekent de woning in echte kleuren (baksteen, pannendak, witte kozijnen) als isometrische SVG.
# Dezelfde geometrie als de oude groene render (viewBox 0 0 320 300), zodat buren en markers blijven passen.
import math

V = 50 / 110   # helling van de voorgevel (langs de straat)
Z = -0.5       # helling van de zijgevel (de diepte in)
AV = math.degrees(math.atan(V))
AZ = math.degrees(math.atan(Z))


def defs(p, kleur='eigen'):
    if kleur == 'eigen':
        steen, steen_zij, voeg, pan, pan_lijn, pan_achter = '#A85B41', '#7C412F', '#D9C6B4', '#45423F', '#2E2C2A', '#33302E'
        glas1, glas2 = '#8FA6AF', '#3E5660'
    else:  # buur: echte kleuren, maar teruggetrokken
        steen, steen_zij, voeg, pan, pan_lijn, pan_achter = '#C7AE9F', '#AE9585', '#E6DBCF', '#9C9792', '#87827D', '#8F8A85'
        glas1, glas2 = '#D3DADB', '#B2BEC1'
    return f'''<defs>
<pattern id="{p}bv" width="14" height="10" patternUnits="userSpaceOnUse" patternTransform="skewY({AV:.2f})"><rect width="14" height="10" fill="{steen}"/><path d="M0 4.6h14M0 9.6h14M3 0v4.6M10 5v4.6" stroke="{voeg}" stroke-width="0.7" opacity=".7"/></pattern>
<pattern id="{p}bz" width="14" height="10" patternUnits="userSpaceOnUse" patternTransform="skewY({AZ:.2f})"><rect width="14" height="10" fill="{steen_zij}"/><path d="M0 4.6h14M0 9.6h14M3 0v4.6M10 5v4.6" stroke="{voeg}" stroke-width="0.7" opacity=".45"/></pattern>
<pattern id="{p}pan" width="9" height="7" patternUnits="userSpaceOnUse" patternTransform="skewY({AZ:.2f})"><rect width="9" height="7" fill="{pan}"/><path d="M0 6.4h9M4.5 0v6.4" stroke="{pan_lijn}" stroke-width="1"/></pattern>
<linearGradient id="{p}licht" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF5E6" stop-opacity=".22"/><stop offset="1" stop-color="#000" stop-opacity=".12"/></linearGradient>
<linearGradient id="{p}schaduwzij" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".05"/><stop offset="1" stop-color="#000" stop-opacity=".22"/></linearGradient>
<linearGradient id="{p}dakglans" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset="1" stop-color="#000" stop-opacity=".18"/></linearGradient>
<linearGradient id="{p}glas" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{glas1}"/><stop offset="1" stop-color="{glas2}"/></linearGradient>
<linearGradient id="{p}warm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6E3B4"/><stop offset="1" stop-color="#CBA45C"/></linearGradient>
<filter id="{p}zacht" x="-30%" y="-100%" width="160%" height="300%"><feGaussianBlur stdDeviation="11"/></filter>
</defs>'''


def raam_voor(x, y, w, h, p, kozijn='#F4F1EA', glas='glas'):
    def pt(dx, dy):
        return f'{x + dx:.1f},{y + dy + dx * V:.1f}'
    frame = f'<polygon points="{pt(0,0)} {pt(w,0)} {pt(w,h)} {pt(0,h)}" fill="{kozijn}"/>'
    i = 2.4
    vul = f'<polygon points="{pt(i,i)} {pt(w-i,i)} {pt(w-i,h-i)} {pt(i,h-i)}" fill="url(#{p}{glas})"/>'
    m = w / 2
    roede = f'<path d="M{x+m:.1f} {y+i+m*V:.1f}V{y+h-i+m*V:.1f}M{x+i:.1f} {y+h*0.42+i*V:.1f}L{x+w-i:.1f} {y+h*0.42+(w-i)*V:.1f}" stroke="{kozijn}" stroke-width="1.6"/>'
    glans = f'<polygon points="{pt(i+1,i+1)} {pt(i+6,i+1)} {pt(i+2,h*0.4)} {pt(i+1,h*0.4)}" fill="#fff" opacity=".28"/>'
    dorpel = f'<path d="M{x-1.5:.1f} {y+h+0.6-1.5*V:.1f}L{x+w+1.5:.1f} {y+h+0.6+(w+1.5)*V:.1f}" stroke="{kozijn}" stroke-width="2.4" stroke-linecap="round"/>'
    return frame + vul + roede + glans + dorpel


def raam_zij(x, y, w, h, p, kozijn='#ECE7DE'):
    def pt(dx, dy):
        return f'{x + dx:.1f},{y + dy + dx * Z:.1f}'
    frame = f'<polygon points="{pt(0,0)} {pt(w,0)} {pt(w,h)} {pt(0,h)}" fill="{kozijn}"/>'
    i = 2.2
    glas = f'<polygon points="{pt(i,i)} {pt(w-i,i)} {pt(w-i,h-i)} {pt(i,h-i)}" fill="url(#{p}glas)" opacity=".9"/>'
    m = w / 2
    roede = f'<path d="M{x+m:.1f} {y+i+m*Z:.1f}V{y+h-i+m*Z:.1f}" stroke="{kozijn}" stroke-width="1.4"/>'
    return frame + glas + roede


def huis(p, kleur='eigen', deur='#2F5D45', schaduw=True):
    kozijn = '#F4F1EA' if kleur == 'eigen' else '#F1ECE4'
    pan_achter = '#33302E' if kleur == 'eigen' else '#8F8A85'
    s = []
    if schaduw:
        s.append(f'<ellipse cx="165" cy="290" rx="150" ry="24" fill="#3A2E22" opacity=".22" filter="url(#{p}zacht)"/>')
    # achterste dakvlak
    s.append(f'<polygon points="60,150 115,105 205,60 150,105" fill="{pan_achter}"/>')
    # voorgevel (puntgevel) met baksteen en licht
    s.append('<polygon points="60,250 60,150 115,105 170,200 170,300" fill="url(#%sbv)"/>' % p)
    s.append('<polygon points="60,250 60,150 115,105 170,200 170,300" fill="url(#%slicht)"/>' % p)
    # plint
    s.append('<polygon points="60,250 170,300 170,294 60,244" fill="#5A4034" opacity=".55"/>')
    # zijgevel
    s.append('<polygon points="170,200 260,155 260,255 170,300" fill="url(#%sbz)"/>' % p)
    s.append('<polygon points="170,200 260,155 260,255 170,300" fill="url(#%sschaduwzij)"/>' % p)
    s.append('<polygon points="170,300 260,255 260,249 170,294" fill="#4A352B" opacity=".55"/>')
    # dakvlak met pannen
    s.append('<polygon points="115,105 170,200 260,155 205,60" fill="url(#%span)"/>' % p)
    s.append('<polygon points="115,105 170,200 260,155 205,60" fill="url(#%sdakglans)"/>' % p)
    # goot en windveer
    s.append(f'<path d="M170 200L260 155" stroke="#2A2826" stroke-width="2.6" stroke-linecap="round"/>')
    s.append(f'<path d="M60 150L115 105L170 200" stroke="{kozijn}" stroke-width="2.2" stroke-linejoin="round" fill="none"/>')
    # schoorsteen
    s.append('<polygon points="205,96 215,100.5 215,76 205,71.5" fill="#8E4A35"/><polygon points="215,100.5 223,96.5 223,72 215,76" fill="#6A3526"/><polygon points="203,70.5 215,76 225,71 213,65.5" fill="#3B3836"/>')
    # ramen voorgevel
    s.append(raam_voor(75, 182, 28, 34, p, kozijn))
    s.append(raam_voor(127, 206, 28, 34, p, kozijn))
    s.append(raam_voor(103, 141, 22, 22, p, kozijn))
    # zijgevel: raam en voordeur
    s.append(raam_zij(186, 202, 30, 30, p, kozijn))
    s.append(f'<polygon points="229,200.5 251,189.5 251,257.5 229,268.5" fill="{kozijn}"/><polygon points="231.5,201.8 248.5,193.3 248.5,256.8 231.5,265.3" fill="{deur}"/><circle cx="245" cy="230" r="1.3" fill="#CBA45C"/>')
    return ''.join(s)


def svg(inhoud, vb, w=300, h=270, label='Jouw woning', stijl='position: absolute; left: 50%; top: 0; transform: translateX(-50%)', klasse=''):
    k = f' class="{klasse}"' if klasse else ''
    return f'<svg{k} width="{w}" height="{h}" viewBox="{vb}" fill="none" role="img" aria-label="{label}" style="{stijl}">{inhoud}</svg>'


def g(dx, dy, body):
    return f'<g transform="translate({dx},{dy})">{body}</g>'


def grond(cx, cy, rx, ry):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#D9D0BD" opacity=".55"/>'


def variant(soort, p='w'):
    d_eigen = defs(p, 'eigen')
    d_buur = defs(p + 'b', 'buur')
    eigen = huis(p, 'eigen', schaduw=False)
    buur = huis(p + 'b', 'buur', deur='#7A756C', schaduw=False)
    sch = lambda cx, cy, rx: f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="24" fill="#3A2E22" opacity=".2" filter="url(#{p}zacht)"/>'
    if soort == 'vrijstaand':
        return svg(d_eigen + grond(165, 278, 158, 34) + sch(165, 288, 150) + eigen, '0 0 320 310')
    if soort == 'tussenwoning':
        return svg(d_eigen + d_buur + grond(165, 292, 230, 46) + sch(165, 300, 230) + g(-110, -50, buur) + eigen + g(110, 50, buur), '-70 -30 460 400')
    if soort == 'hoekwoning':
        return svg(d_eigen + d_buur + grond(60, 262, 230, 46) + sch(40, 252, 230) + g(-220, -100, buur) + g(-110, -50, buur) + eigen, '-180 -80 470 400')
    if soort == 'twee-onder-een-kap':
        return svg(d_eigen + d_buur + grond(110, 278, 185, 40) + sch(110, 280, 180) + g(-110, -50, buur) + eigen, '-70 -30 350 345')
    if soort == 'appartement':
        return svg(d_eigen + grond(165, 286, 160, 34) + sch(165, 290, 150) + appartement(p), '0 20 330 300')
    raise ValueError(soort)


def appartement(p):
    y = lambda x, f, off=0: 90 + 32.5 * f + off + (x - 40) * V
    s = ['<polygon points="40,90 200,163 290,118 130,45" fill="#4A4744"/>',
         f'<polygon points="40,90 200,163 200,293 40,220" fill="url(#{p}bv)"/>', f'<polygon points="40,90 200,163 200,293 40,220" fill="url(#{p}licht)"/>',
         f'<polygon points="200,163 290,118 290,248 200,293" fill="url(#{p}bz)"/>', f'<polygon points="200,163 290,118 290,248 200,293" fill="url(#{p}schaduwzij)"/>',
         '<path d="M40 90L200 163L290 118" stroke="#E9E3D8" stroke-width="2"/>']
    eigen = 1
    for f in range(4):
        s.append(f'<path d="M40 {90+32.5*(f+1):.1f}L200 {163+32.5*(f+1):.1f}" stroke="#8E4E38" stroke-width="1.2" opacity=".6"/>')
        for i in range(3):
            x0 = 56 + i * 50
            s.append(raam_voor(x0, y(x0, f, 7), 26, 18, p, glas='warm' if f == eigen else 'glas'))
        for i in range(2):
            x0 = 214 + i * 38
            s.append(raam_zij(x0, 163 + 32.5 * f + 7 - (x0 - 200) * 0.5, 20, 18, p))
    # eigen verdieping: gouden lijn eronder en erboven
    s.append(f'<path d="M40 {y(40,eigen):.1f}L200 {y(200,eigen):.1f}M40 {y(40,eigen)+32.5:.1f}L200 {y(200,eigen)+32.5:.1f}" stroke="#CBA45C" stroke-width="1.6"/>')
    return ''.join(s)


if __name__ == '__main__':
    import sys
    out = '<html><body style="margin:0;background:#ECE5D7;display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:10px">'
    for v in ['vrijstaand', 'tussenwoning', 'hoekwoning', 'twee-onder-een-kap', 'appartement']:
        out += f'<div style="position:relative;height:290px;background:#ECE5D7;border:1px solid #ccc">{variant(v, "x"+v[:3])}<span style="position:absolute;left:6px;bottom:4px;font:12px system-ui">{v}</span></div>'
    open(sys.argv[1], 'w').write(out + '</body></html>')
