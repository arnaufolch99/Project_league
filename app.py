from flask import Flask, render_template, request

app = Flask(__name__)

# Memoria temporal para mantener guardados los datos de la liga activa
DATOS_LIGA = {
    "equipos": [],
    "calendario": [],
    "resultados": {}
}

def generar_calendario(equipos):
    lista = equipos.copy()
    if len(lista) % 2 != 0:
        lista.append("Descansa")
    
    n = len(lista)
    jornadas = []
    
    for jornada in range(n - 1):
        partidos = []
        for i in range(n // 2):
            local = lista[i]
            visitante = lista[n - 1 - i]
            if local != "Descansa" and visitante != "Descansa":
                partidos.append({"local": local, "visitante": visitante, "goles_local": None, "goles_visitante": None})
        jornadas.append(partidos)
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]
        
    return jornadas

def calcular_clasificacion():
    stats = {
        eq: {"equipo": eq, "pj": 0, "pg": 0, "pe": 0, "pp": 0, "gf": 0, "gc": 0, "dg": 0, "pts": 0}
        for eq in DATOS_LIGA["equipos"]
    }
    
    for (local, visitante), (gl, gv) in DATOS_LIGA["resultados"].items():
        if gl is not None and gv is not None:
            stats[local]["pj"] += 1
            stats[visitante]["pj"] += 1
            
            stats[local]["gf"] += gl
            stats[local]["gc"] += gv
            stats[visitante]["gf"] += gv
            stats[visitante]["gc"] += gl
            
            stats[local]["dg"] = stats[local]["gf"] - stats[local]["gc"]
            stats[visitante]["dg"] = stats[visitante]["gf"] - stats[visitante]["gc"]
            
            if gl > gv:
                stats[local]["pg"] += 1
                stats[local]["pts"] += 3
                stats[visitante]["pp"] += 1
            elif gv > gl:
                stats[visitante]["pg"] += 1
                stats[visitante]["pts"] += 3
                stats[local]["pp"] += 1
            else:
                stats[local]["pe"] += 1
                stats[local]["pts"] += 1
                stats[visitante]["pe"] += 1
                stats[visitante]["pts"] += 1

    clasificacion_ordenada = sorted(
        stats.values(),
        key=lambda x: (x["pts"], x["dg"], x["gf"]),
        reverse=True
    )
    return clasificacion_ordenada

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/crear-liga', methods=['POST'])
def crear_liga():
    texto_equipos = request.form.get('equipos')
    DATOS_LIGA["equipos"] = [e.strip() for e in texto_equipos.split(',') if e.strip()]
    DATOS_LIGA["calendario"] = generar_calendario(DATOS_LIGA["equipos"])
    DATOS_LIGA["resultados"] = {}
    
    clasificacion = calcular_clasificacion()
    return render_template('liga.html', calendario=DATOS_LIGA["calendario"], clasificacion=clasificacion)

@app.route('/actualizar-resultados', methods=['POST'])
def actualizar_resultados():
    for jornada in DATOS_LIGA["calendario"]:
        for partido in jornada:
            local = partido["local"]
            visitante = partido["visitante"]
            
            gl_str = request.form.get(f"goles_{local}_{visitante}")
            gv_str = request.form.get(f"goles_{visitante}_{local}")
            
            if gl_str != "" and gv_str != "" and gl_str is not None and gv_str is not None:
                gl = int(gl_str)
                gv = int(gv_str)
                DATOS_LIGA["resultados"][(local, visitante)] = (gl, gv)
                partido["goles_local"] = gl
                partido["goles_visitante"] = gv

    clasificacion = calcular_clasificacion()
    return render_template('liga.html', calendario=DATOS_LIGA["calendario"], clasificacion=clasificacion)

if __name__ == '__main__':
    app.run(debug=True)