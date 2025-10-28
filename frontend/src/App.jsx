import React, { useRef, useState, useEffect } from 'react'
export default function App() {
  const [prompt, setPrompt] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [capturedBlob, setCapturedBlob] = useState(null)
  const [cameraActive, setCameraActive] = useState(false)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)

  // Iniciar cámara cuando se active el modo "tomar foto"
  useEffect(() => {
    if (!cameraActive) return
    const start = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        streamRef.current = stream
        if (videoRef.current) videoRef.current.srcObject = stream
      } catch (err) {
        console.error('No se pudo acceder a la cámara:', err)
        alert('Error al acceder a la cámara. Revisa permisos.')
        setCameraActive(false)
      }
    }
    start()

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop())
        streamRef.current = null
      }
    }
  }, [cameraActive])

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setCapturedBlob(null)
    }
  }

  const openCamera = () => {
    setCapturedBlob(null)
    setSelectedFile(null)
    setCameraActive(true)
  }

  const capturePhoto = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)
    canvas.toBlob((blob) => {
      if (blob) {
        setCapturedBlob(blob)
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop())
          streamRef.current = null
        }
        setCameraActive(false)
      }
    }, 'image/jpeg')
  }

  // Speech-to-text con Web Speech API
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      recognitionRef.current = null
      return
    }

    const rec = new SpeechRecognition()
    rec.continuous = true
    rec.interimResults = true
    rec.lang = 'es-MX'

    rec.onresult = (event) => {
      let interim = ''
      let final = ''
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) final += transcript
        else interim += transcript
      }
      if (final) setPrompt((p) => (p ? p + ' ' + final : final))
      setInterimTranscript(interim)
    }

    rec.onerror = (e) => {
      console.error('Speech recognition error', e)
    }

    recognitionRef.current = rec
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop() } catch (e) {}
        recognitionRef.current = null
      }
    }
  }, [])

  const toggleListening = () => {
    const rec = recognitionRef.current
    if (!rec) {
      alert('Tu navegador no soporta SpeechRecognition (Web Speech API). Usa Chrome o Edge.')
      return
    }
    if (!listening) {
      try {
        rec.start()
        setListening(true)
      } catch (e) {
        console.warn('No se pudo iniciar reconocimiento:', e)
      }
    } else {
      try {
        rec.stop()
      } catch (e) {}
      setListening(false)
      setInterimTranscript('')
    }
  }

  const handleSubmit = async () => {
    const form = new FormData()
    form.append('prompt', prompt)
    if (selectedFile) form.append('image', selectedFile)
    if (capturedBlob)
      form.append('image', new File([capturedBlob], 'selfie.jpg', { type: 'image/jpeg' }))

    // Ejemplo: mostrar en consola los datos que enviarías
    console.log('Enviando prompt y archivo:', { prompt, file: selectedFile || capturedBlob })

    // Simular envío
    alert('Simulación: prompt enviado. Revisa la consola para ver el FormData.')
  }

  return (
    <div className="min-h-screen relative bg-gray-900 text-white flex items-center justify-center">
      {/* VIDEOS DE FONDO - reemplaza src por tus archivos de video */}
      <div className="absolute inset-0 overflow-hidden -z-10">
        <video autoPlay loop muted playsInline className="w-full h-full object-cover opacity-40">
          <source src="/videos/background1.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
      </div>

      {/* Contenedor central */}
      <div className="w-full max-w-3xl mx-auto p-6 text-center">
        <h1 className="text-3xl sm:text-5xl font-extrabold drop-shadow-lg">IA IMAGEN A VIDEO - DEMO</h1>

        <p className="mt-6 text-lg">Sube una imagen o toma una una selfie para comenzar</p>

        <div className="mt-6 bg-white/8 backdrop-blur-md rounded-xl p-6 shadow-lg">
          {/* Cuadro de texto para prompt */}
          <label className="block text-left mb-2 font-medium">Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe lo que quieres que salga en el video (ej: 'estilo cinematográfico, amanecer, cámara lenta')"
            className="w-full rounded-md p-3 text-black resize-none h-28"
          />

          {/* Botones para subir / tomar foto / enviar */}
          <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex-1 flex gap-3">
              <label className="inline-flex items-center gap-2 cursor-pointer">
                <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
                <span className="px-4 py-2 rounded-md bg-white/10 hover:bg-white/20">Subir imagen</span>
              </label>

              <button onClick={openCamera} className="px-4 py-2 rounded-md bg-white/10 hover:bg-white/20">Tomar foto</button>

              <button onClick={handleSubmit} className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700">Enviar prompt</button>
            </div>
          </div>

          {/* Vista previa de imagen seleccionada o selfie */}
          <div className="mt-4">
            {selectedFile && (
              <div>
                <p className="mb-2">Imagen seleccionada:</p>
                <img src={URL.createObjectURL(selectedFile)} alt="preview" className="mx-auto rounded-md max-h-48" />
              </div>
            )}

            
             
          </div>

        </div>

        {/* Modal / zona de cámara (simple) */}
        {cameraActive && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-4 text-black max-w-xl w-full">
              <h2 className="font-bold mb-2">Tomar foto</h2>
              <video ref={videoRef} autoPlay playsInline className="w-full rounded-md bg-black" />

              <div className="mt-3 flex gap-3 justify-end">
                <button onClick={() => { setCameraActive(false); if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; } }} className="px-3 py-2 rounded-md bg-gray-200">Cancelar</button>
                <button onClick={capturePhoto} className="px-3 py-2 rounded-md bg-blue-600 text-white">Capturar</button>
              </div>

              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}