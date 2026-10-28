# Prototipo de análisis de cortocircuito por unidad

Aplicación educativa en Streamlit para redes eléctricas con buses, generadores, líneas y una falla trifásica.

## Ejecutar desde Anaconda Prompt

1. Descarga y descomprime `prototipo_cortocircuito_pu.zip`.
2. En Anaconda Prompt, cambia a la carpeta descomprimida. Por ejemplo:

```bat
cd C:\Users\TU_USUARIO\Downloads\prototipo_cortocircuito_pu
```

3. Crea un entorno de Conda e instala las dependencias:

```bat
conda create -n cortocircuito python=3.11 -y
conda activate cortocircuito
python -m pip install -r requirements.txt
```

4. Inicia la página:

```bat
python -m streamlit run app.py
```

Streamlit abrirá la aplicación en el navegador. Si no se abre automáticamente, copia la dirección local que aparece en Anaconda Prompt (normalmente `http://localhost:8501`).

## Vista del circuito`r`n`r`nEl diagrama unifilar se genera automáticamente con los buses, generadores y líneas capturados; el bus seleccionado para la falla se resalta en otro color.`r`n`r`n## Datos que puedes capturar

- Base de potencia del sistema en MVA.
- Buses y voltajes base en kV.
- Generadores con bus, MVA, kV y R/X subtransitoria en pu.
- Líneas entre buses, con R y X en pu u ohmios.
- Bus de falla e impedancia de falla en pu.

## Supuestos del prototipo

- Falla trifásica balanceada.
- Voltajes prefalla aproximados a 1∠0° pu; no calcula flujo de carga.
- Generadores como fuentes de 1 pu detrás de su impedancia subtransitoria.
- Sin cargas ni transformadores.
- No incluye todavía fallas monofásicas o bifásicas ni redes de secuencia.

Es una herramienta de aprendizaje. Compara los resultados con el procedimiento y las convenciones de tu curso.

