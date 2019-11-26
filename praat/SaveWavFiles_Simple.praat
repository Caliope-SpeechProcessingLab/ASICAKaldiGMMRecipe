# Escala la intensidad a 70dB y
# guarda de los archivos wav seleccionados
# Usa la carpeta actual y el nombre actual
# Deberás dar a pathOut la ruta que quieras. Si es windows, algo como C:\MisArchivos\

pathOut$ = "/Users/ignaciomoreno-torres/Desktop/ResultadosBandas/temp/"

# Sufijo
sufijo$ = ".wav"

Scale intensity: 70

n = numberOfSelected ("Sound")

for i to n 
	sound'i' = selected ("Sound", i)
	sound'i'$ = selected$("Sound", i)
endfor

for i to n
	objeto$ = sound'i'$
    selectObject: "Sound 'objeto$'"
	 workingSound$ = selected$ ("Sound")
	cadena$=pathOut$+objeto$+sufijo$
	Save as WAV file: cadena$

endfor