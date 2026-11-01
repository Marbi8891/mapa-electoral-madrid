"""Genera data/mesas-electorales.json a partir del inventario del docx + resultados de geocodificación (Nominatim/OSM).
El distrito se calcula por punto-en-polígono contra data/distritos.geojson (no se estima a mano)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
G = "https://maps.app.goo.gl/"
V, A, P = "verificada", "aproximada", "pendiente"
N = "OpenStreetMap Nominatim"
# id, zona del documento, nombre/texto original, dirección original, enlace Google del docx, lat, lon, estado, nota
R = [
(1,"MONCLOA","Intercambiador Moncloa",None,None,40.435343,-3.719161,V,"Intercambiador de Moncloa (islas 2 y 3), c/ Princesa 89."),
(2,"LATINA","Centro comercial San Ignacio",None,"zcz2wJDVfienKNSB8",40.378863,-3.779911,V,"CC San Ignacio de Loyola, c/ Oliva de Plasencia 1 (punto del local dentro del CC)."),
(3,"LATINA","I E GARCIA MORATO","Calle del General Millán Astray, 28044 Madrid","tyirk2XfcAwKiaGb6",40.373854,-3.766985,A,"OSM sitúa el IES García Morato en c/ Soledad Cazorla 34, no en la dirección del documento. Revisar."),
(4,"LATINA","Calle de Blas Cabrera, 125","Calle de Blas Cabrera, 125, 28044 Madrid","ypSfXwWE8ocfQ7Yx7",40.377661,-3.768277,V,"Coincide el número de portal."),
(5,"LATINA","Calle Poema Sinfónico, 2","Calle Poema Sinfonico, 2, 28054 Madrid","QmtVkw1gYCZjo9Rv6",40.372441,-3.773994,A,"OSM solo localiza la calle (no el nº 2); punto sobre la calle."),
(6,"LATINA","Avenida de las Águilas, 2A","Avenida de las Águilas, 2A, 28044 Madrid","i1AMpJBTsQMrd3Nd9",40.384597,-3.765075,V,"Portal nº 2 localizado; el sufijo «A» no se distingue en OSM."),
(7,"LATINA","Glorieta San Vicente junto a centro comercial Príncipe Pío",None,None,40.42051,-3.720398,A,"Punto sobre la glorieta (OSM la sitúa en Moncloa-Aravaca)."),
(8,"CARABANCHEL","Intercambiador Plaza Elíptica",None,"R1PFoLNKa1PkdsG97",40.384444,-3.718376,V,"Intercambiador de Plaza Elíptica."),
(9,"CARABANCHEL","Plaza de Oporto",None,"jgbbPLgeYRkAMjx86",40.388084,-3.731782,A,"Centro de la plaza; punto exacto de la mesa no indicado."),
(10,"CARABANCHEL","CC Isla Azul",None,"8HsBXYT7mk1hV63o9",40.363998,-3.737129,V,"CC Islazul, c/ Calderilla 1."),
(11,"VILLAVERDE","Calle Santa Petronila esquina José Martínez Seco",None,"UGryV3a1Luf9q1XN8",40.348891,-3.692163,A,"OSM no resuelve la esquina; punto sobre c/ Santa Petronila."),
(12,"VILLAVERDE","Calle Pícara Molinera esquina Lucero del Alba",None,"cfFC2jxuSF5UC6oj8",40.355711,-3.702368,A,"OSM no resuelve la esquina; punto sobre c/ Pícara Molinera."),
(13,"VILLAVERDE","Avenida Andalucía paralela Gigantes y Cabezudos",None,"wakLhQ3t7wiBn5rW8",None,None,P,"Sin coincidencia en OSM. Usar el enlace de Google del documento."),
(14,"USERA","Av. del Manzanares, 210","Av del Manzanares, 210, Usera, 28026 Madrid","oUAQXtRkdW2hfENX6",40.390821,-3.701449,V,"Coincide el número de portal (CC Plaza Río 2)."),
(15,"USERA","Glorieta de Cádiz",None,"iF9ABG1W5cSwRsVS6",40.387958,-3.69955,A,"Centro de la glorieta."),
(16,"LEGAZPI","(sin nombre en el documento)",None,"dySjDjsrxGPt7P4i8",None,None,P,"El documento solo trae un enlace corto de Google Maps, no resoluble desde aquí."),
(17,"LEGAZPI","Plaza de la Beata María Ana de Jesús, 13","Plaza de la beata maría ana de jesus, 13","WLRRvVSUNGmeyjVv8",40.394553,-3.695495,V,"Coincide el número de portal."),
(18,"MÉNDEZ ÁLVARO","Estación de autobuses Méndez Álvaro",None,None,40.394298,-3.677671,V,"Estación Sur de Autobuses, c/ Méndez Álvaro 83."),
(19,"VALLECAS","Puente de Vallecas (junto Asamblea de Madrid) CC Madrid Sur",None,None,40.381186,-3.663091,V,"CC Madrid Sur, a pocos metros de la Asamblea de Madrid."),
(20,"VALLECAS","Plaza de Conde de Casal junto a paradas de autobús",None,None,40.406317,-3.670838,A,"Punto en la plaza; paradas exactas no indicadas."),
(21,"VALLECAS","Villa de Vallecas, estación Renfe Santa Eugenia",None,None,None,None,P,"OSM no devuelve la estación con esta búsqueda."),
(22,"VALLECAS","Av. de las Glorietas, 39","Av. de las Glorietas, 39","",40.372807,-3.657262,V,"Coincide el número de portal."),
(23,"ENSANCHE DE VALLECAS","CC La Gavia","Calle Avenida de las Suertes",None,40.36816,-3.597554,V,"CC La Gavia, c/ Adolfo Bioy Casares 2."),
(24,"MORATALAZ","Vinateros con Avenida de Moratalaz",None,None,None,None,P,"OSM no resuelve el cruce."),
(25,"MORATALAZ","Moratalaz (intercambiador de Pavones)",None,None,40.400426,-3.635003,A,"Punto de la vía «Intercambiador de Pavones»."),
(26,"CIUDAD LINEAL / SAN BLAS","Calle Virgen de África",None,None,40.437206,-3.65313,A,"Calle larga; punto en un tramo."),
(27,"CIUDAD LINEAL / SAN BLAS","Ciudad Lineal (CC Alcalá Norte e intercambiador)",None,None,40.436897,-3.638077,V,"CC Alcalá Norte, c/ Alcalá 414."),
(28,"CIUDAD LINEAL / SAN BLAS","San Blas (CC Las Rosas e intercambiador)",None,None,40.418176,-3.621583,V,"CC Las Rosas."),
(29,"ARTURO SORIA","Arturo Soria (centro comercial y hospital)",None,None,40.449983,-3.650756,V,"CC Arturo Soria Plaza; el hospital no se localizó."),
(30,"BARRIO HORTALEZA","Calle Ayacucho",None,None,40.469616,-3.635979,A,"Calle larga; punto en un tramo."),
(31,"BARRIO HORTALEZA","Avenida San Luis",None,None,40.472047,-3.661237,A,"Avenida larga; punto en el tramo de Hortaleza."),
(32,"BARRIO HORTALEZA","Hortaleza junto Palacio de Hielo",None,None,40.463141,-3.636102,V,"Complejo mk2 Palacio de Hielo, c/ Silvano."),
(33,"BARRIO HORTALEZA","Hortaleza junto comisaría policía municipal, comisaría Canillas y centro comercial",None,None,None,None,P,"Descripción demasiado ambigua (texto incompleto en el documento)."),
(34,"MONTECARMELO","Avenida Monasterio de El Escorial",None,None,40.504126,-3.703086,A,"Avenida larga; punto junto a Alcampo (Av. Monasterio de El Escorial 35)."),
(35,"MIRASIERRA","Calle Costa del Sol",None,None,None,None,P,"OSM solo halla una c/ Costa del Sol en Hortaleza (Pinar del Rey), no en Mirasierra."),
(36,"PLAZA CASTILLA","Frente a juzgados",None,None,40.464903,-3.690206,V,"Juzgados de Plaza de Castilla."),
(37,"PLAZA CASTILLA","Plaza Duque de Pastrana",None,"AHyQJX69FQf7qSQg9",40.468298,-3.677763,A,"Centro de la plaza."),
(38,"NUEVOS MINISTERIOS","En salida intercambiador",None,None,40.446604,-3.692189,A,"Estación Nuevos Ministerios; salida concreta no indicada."),
(39,"SALAMANCA","Goya 47","Calle de Goya, 47",None,40.425272,-3.682353,V,"Se asume calle de Goya (Madrid); coincide el número."),
(40,"SALAMANCA","Plaza Manuel Becerra",None,None,40.427805,-3.668511,A,"Centro de la plaza."),
]
NORM = {1:"Estación de autobuses Moncloa, Madrid",2:"Centro Comercial San Ignacio, Madrid",3:"IES García Morato, Madrid",4:"Calle de Blas Cabrera 125, Madrid",5:"Calle Poema Sinfónico 2, Madrid",6:"Avenida de las Águilas 2, Madrid",7:"Glorieta de San Vicente, Madrid",8:"Intercambiador de Plaza Elíptica, Madrid",9:"Plaza de Oporto, Madrid",10:"Centro Comercial Islazul, Madrid",11:"Calle de Santa Petronila, Madrid",12:"Calle Pícara Molinera, Madrid",13:"Avenida de Andalucía, Gigantes y Cabezudos, Madrid",14:"Avenida del Manzanares 210, Madrid",15:"Glorieta de Cádiz, Madrid",17:"Plaza de la Beata María Ana de Jesús 13, Madrid",18:"Estación de autobuses Méndez Álvaro, Madrid",19:"Centro Comercial Madrid Sur, Madrid",20:"Plaza de Conde de Casal, Madrid",21:"Estación de Santa Eugenia, Madrid",22:"Avenida de las Glorietas 39, Madrid",23:"Centro Comercial La Gavia, Madrid",24:"Calle de Vinateros con Avenida de Moratalaz, Madrid",25:"Intercambiador de Pavones, Madrid",26:"Calle Virgen de África, Madrid",27:"Centro Comercial Alcalá Norte, Madrid",28:"Centro Comercial Las Rosas, Madrid",29:"Centro Comercial Arturo Soria Plaza, Madrid",30:"Calle Ayacucho, Hortaleza, Madrid",31:"Avenida de San Luis, Madrid",32:"Palacio de Hielo, Calle Silvano, Madrid",33:"Comisaría Policía Municipal Hortaleza, Madrid",34:"Avenida Monasterio de El Escorial, Madrid",35:"Calle Costa del Sol, Madrid",36:"Juzgados de Plaza de Castilla, Madrid",37:"Plaza del Duque de Pastrana, Madrid",38:"Nuevos Ministerios, Madrid",39:"Calle de Goya 47, Madrid",40:"Plaza de Manuel Becerra, Madrid"}
IMG = {
1: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7e/Intercambiador_de_Moncloa%2C_2024_%2801%29.jpg/960px-Intercambiador_de_Moncloa%2C_2024_%2801%29.jpg","https://commons.wikimedia.org/wiki/File:Intercambiador_de_Moncloa,_2024_(01).jpg","Draceane","CC BY-SA 4.0","Interior del intercambiador de Moncloa"),
7: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/9/99/Centro_Comercial_Principe_Pio_Entrada.jpg/960px-Centro_Comercial_Principe_Pio_Entrada.jpg","https://commons.wikimedia.org/wiki/File:Centro_Comercial_Principe_Pio_Entrada.jpg","FDV","CC BY 3.0","Centro Comercial Príncipe Pío, junto a la glorieta"),
8: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ea/Madrid_-_Carabanchel%2C_Abrantes%2C_Intercambiador_de_Plaza_El%C3%ADptica_1.jpg/960px-Madrid_-_Carabanchel%2C_Abrantes%2C_Intercambiador_de_Plaza_El%C3%ADptica_1.jpg","https://commons.wikimedia.org/wiki/File:Madrid_-_Carabanchel,_Abrantes,_Intercambiador_de_Plaza_El%C3%ADptica_1.jpg","Zarateman","CC0","Intercambiador de Plaza Elíptica"),
9: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1d/Madrid_-_Carabanchel%2C_Puerta_Bonita%2C_Plaza_de_Oporto.jpg/960px-Madrid_-_Carabanchel%2C_Puerta_Bonita%2C_Plaza_de_Oporto.jpg","https://commons.wikimedia.org/wiki/File:Madrid_-_Carabanchel,_Puerta_Bonita,_Plaza_de_Oporto.jpg","Zarateman","CC0","Plaza de Oporto"),
10: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/3/37/C.C._Islazul_%28Madrid%29_01.jpg/960px-C.C._Islazul_%28Madrid%29_01.jpg","https://commons.wikimedia.org/wiki/File:C.C._Islazul_(Madrid)_01.jpg","Luis García (Zaqarbal)","CC BY-SA 3.0","Centro comercial Islazul"),
15: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e0/Madrid_-_Glorieta_de_C%C3%A1diz_1.jpg/960px-Madrid_-_Glorieta_de_C%C3%A1diz_1.jpg","https://commons.wikimedia.org/wiki/File:Madrid_-_Glorieta_de_C%C3%A1diz_1.jpg","Zarateman","CC0","Glorieta de Cádiz"),
18: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f7/Madrid_-_Estaci%C3%B3n_Sur_de_Autobuses_%28M%C3%A9ndez_%C3%81lvaro%29_1.JPG/960px-Madrid_-_Estaci%C3%B3n_Sur_de_Autobuses_%28M%C3%A9ndez_%C3%81lvaro%29_1.JPG","https://commons.wikimedia.org/wiki/File:Madrid_-_Estaci%C3%B3n_Sur_de_Autobuses_(M%C3%A9ndez_%C3%81lvaro)_1.JPG","Zarateman","CC0","Estación Sur de Autobuses"),
19: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f6/Madrid_-_Puente_de_Vallecas_-_Centro_Comercial_Madrid_Sur_3.JPG/960px-Madrid_-_Puente_de_Vallecas_-_Centro_Comercial_Madrid_Sur_3.JPG","https://commons.wikimedia.org/wiki/File:Madrid_-_Puente_de_Vallecas_-_Centro_Comercial_Madrid_Sur_3.JPG","Zarateman","CC0","Centro Comercial Madrid Sur"),
27: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6b/Madrid_-_Centro_Comercial_Alcal%C3%A1_Norte.JPG/960px-Madrid_-_Centro_Comercial_Alcal%C3%A1_Norte.JPG","https://commons.wikimedia.org/wiki/File:Madrid_-_Centro_Comercial_Alcal%C3%A1_Norte.JPG","Zarateman","CC0","Centro Comercial Alcalá Norte"),
32: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/0/08/Palacio_de_Hielo_%28Madrid_-_2022%29.jpg/960px-Palacio_de_Hielo_%28Madrid_-_2022%29.jpg","https://commons.wikimedia.org/wiki/File:Palacio_de_Hielo_(Madrid_-_2022).jpg","KingValid04","CC BY-SA 4.0","Palacio de Hielo"),
36: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/b/bb/Madrid_-_Juzgados_de_la_Plaza_de_Castilla_1.jpg/960px-Madrid_-_Juzgados_de_la_Plaza_de_Castilla_1.jpg","https://commons.wikimedia.org/wiki/File:Madrid_-_Juzgados_de_la_Plaza_de_Castilla_1.jpg","Zarateman","CC0","Juzgados de Plaza de Castilla"),
38: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/2/25/Estaci%C3%B3n_de_Nuevos_Ministerios_%28Madrid%29_01.jpg/960px-Estaci%C3%B3n_de_Nuevos_Ministerios_%28Madrid%29_01.jpg","https://commons.wikimedia.org/wiki/File:Estaci%C3%B3n_de_Nuevos_Ministerios_(Madrid)_01.jpg","Luis García from Madrid (Spain)","CC BY-SA 2.0","Interior de la estación de Nuevos Ministerios"),
40: ("https://thumb.wikimedia.org/wikipedia/commons/thumb/2/23/Plaza_de_Manuel_Becerra_%28Madrid%29_01.jpg/960px-Plaza_de_Manuel_Becerra_%28Madrid%29_01.jpg","https://commons.wikimedia.org/wiki/File:Plaza_de_Manuel_Becerra_(Madrid)_01.jpg","Luis García (Zaqarbal)","CC BY-SA 3.0 es","Plaza de Manuel Becerra"),
}
gj = json.load(open(root/"data/distritos.geojson"))
def inring(x,y,ring):
    c=False; j=len(ring)-1
    for i in range(len(ring)):
        xi,yi=ring[i]; xj,yj=ring[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: c=not c
        j=i
    return c
def district(lat,lon):
    for f in gj["features"]:
        g=f["geometry"]; polys=[g["coordinates"]] if g["type"]=="Polygon" else g["coordinates"]
        for p in polys:
            if inring(lon,lat,p[0]) and not any(inring(lon,lat,h) for h in p[1:]): return f["properties"]["nombre"]
    return None
import re, math
out=[]
for id_,zona,nom,dire,link,lat,lon,est,nota in R:
    d = district(lat,lon) if lat is not None else None
    cp = (re.search(r"\b28\d{3}\b", dire or "") or [None])[0]
    out.append({"id":id_,"nombre":nom,"direccion_original":dire,"direccion_normalizada":NORM.get(id_),"codigo_postal":cp,
      "zona_documento":zona,"distrito":d,"latitud":lat,"longitud":lon,"estado_geocodificacion":est,
      "fuente_geocodificacion":N if lat is not None else None,"identificador_mesa":None,
      "enlace_google_documento":(G+link) if link else None,"observaciones":nota})
    im=IMG.get(id_)
    out[-1].update({"imagen_url":im[0] if im else None,"imagen_fuente":im[1] if im else None,"imagen_autor":im[2] if im else None,"imagen_licencia":im[3] if im else None,"imagen_leyenda":im[4] if im else None,"imagen_verificada":bool(im),
      "street_view_url":f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lon}" if lat is not None else None,
      "estado_imagen":"verificada" if im else ("street_view" if lat is not None else "sin_imagen")})
# agrupar por coordenadas idénticas (mismo edificio) y detectar cercanos
pts=[o for o in out if o["latitud"] is not None]
for o in pts: o["mesas_en_direccion"]=sum(1 for p in pts if (p["latitud"],p["longitud"])==(o["latitud"],o["longitud"]))
near=[(a["id"],b["id"],round(math.hypot((a["latitud"]-b["latitud"])*111320,(a["longitud"]-b["longitud"])*85000))) for i,a in enumerate(pts) for b in pts[i+1:]]
near=[n for n in near if n[2]<150]
fuera=[o["id"] for o in pts if not (40.31<o["latitud"]<40.65 and -3.89<o["longitud"]<-3.51)]
json.dump({"generado":"2026-11-01","fuente_docx":"MESAS ELECTORALES.docx","total":len(out),"ubicaciones":out},open(root/"data/mesas-electorales.json","w"),ensure_ascii=False,indent=1)
from collections import Counter
print(len(out),Counter(o["estado_geocodificacion"] for o in out))
print("imágenes:",Counter(o["estado_imagen"] for o in out)); print("sin distrito (con coords):",[o["id"] for o in pts if not o["distrito"]],"| fuera de Madrid:",fuera,"| a <150 m:",near)
