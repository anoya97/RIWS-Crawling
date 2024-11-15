# RIWS-Crawling
 
## Webs:
- https://guide.michelin.com/es/es
- https://guiarepsol.com/es/soles-repsol/ediciones-de-soles-guia-repsol/


## Pasos a seguir para ejecutar el proyecto:

1. Hacer el scraping de las páginas web

```bash
cd Dineology/Dineology
scrapy crawl RestaurantMichelinSpider
scrapy crawl RestaurantRepsolSpider
cd ..
```

2. Ejecutar elasticsearch
 
4. Insertar los datos de los json en elasticsearch (para ejecutar este fichero es necesario 
que los ficheros .json se encuentren en la misma carpeta que el fichero insert_data.py)

```bash
python3 insert_data.py
```

4. Ejecutar el servidor de la aplicación

```bash
cd dineology-search
npm start
```

5. Acceder a la aplicación en el navegador

```bash
http://localhost:3000/
```

6. Disfruta de la aplicación!!