import React, { useRef, useState, useEffect } from 'react'
import env from './assets/env.png'
import mic from './assets/mic.png'
import cam from './assets/cam.png'
import subir from './assets/subir.png'

export default function App() {
  const [prompt, setPrompt] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [capturedBlob, setCapturedBlob] = useState(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [listening, setListening] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const recognitionRef = useRef(null)

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
    if (capturedBlob) form.append('image', new File([capturedBlob], 'selfie.jpg', { type: 'image/jpeg' }))

    console.log('Enviar payload:', { prompt, file: selectedFile || capturedBlob })
    alert('Simulación: prompt y archivo preparados. Revisa la consola para ver el FormData.')
  }

  return (
    <div className="min-h-screen relative bg-gradient-to-b from-gray-900 via-black to-gray-800 text-white flex items-center justify-center px-4">
      {/* Fondo con videos superpuesto */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <video autoPlay loop muted playsInline className="w-full h-full object-cover opacity-30">
          <source src=".\assets\VideosFondo\pez.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
      </div>

      <div className="w-full h-full min-h-screen mx-auto p-4 lg:p-8 flex flex-col">

        <header className="text-center mb-6">
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight drop-shadow-xl">IA IMAGEN A VIDEO - DEMO</h1>
        </header>

          <main className="w-full bg-white/5 backdrop-blur-md rounded-2xl p-4 lg:p-6 shadow-2xl border border-white/6">
          <p className="text-center text-gray-300 mb-5">Sube una imagen o toma una selfie para comenzar</p>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {/* Columna izquierda: prompt + mic */}
            <div className="col-span-2">
              <label className="block text-sm text-gray-400 mb-3">Describe tu prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ejemplo: 'Coloca unos lentes de sol, cámara lenta al atardecer, correr'"
                className="w-full rounded-lg p-4 text-black resize-none min-h-[160px]"
              />
              <div className="mt-3 flex items-center gap-3">



                {/* Botones*/}
                <label className="relative inline-flex items-center justify-center cursor-pointer">
                  <input type="file" accept="image/*" onChange={handleFileChange} className="sr-only" />
                  <span className="w-12 h-12 inline-flex items-center justify-center rounded-full bg-white/6 hover:bg-white/10" title='Subir archivo'>
                    <img src={subir} alt="Subir archivo" className="w-8 h-8" />
                  </span>
                </label>

                <button onClick={openCamera} className="w-15 h-15 inline-flex items-center justify-center rounded-full bg-white/6 hover:bg-white/10" title="Abrir cámara">
                  <img src={cam} alt="Abrir cámara" className="w-8 h-8" />
                </button>

                <button onClick={toggleListening} className={`w-15 h-15 inline-flex items-center justify-center rounded-full ${listening ? 'bg-red-600' : 'bg-white/6'} hover:opacity-90`} title={listening ? 'Detener microfono' : 'Usar micrófono'}>
                  <img src={mic} alt="Micrófono" className="w-8 h-8" />
                </button>

                <button onClick={handleSubmit} className="ml-auto w-15 h-15 inline-flex items-center justify-center rounded-full bg-blue-600 hover:bg-blue-700" title="Enviar prompt">
                  <img src={env} alt="Enviar" className="w-8 h-8" />
                </button>
              </div>

              {/* Transcripción */}
              {interimTranscript && (
                <p className="mt-2 text-sm text-red-300">{interimTranscript}</p>
              )}
            </div>

            {/* Columna derecha: preview*/}
            <aside className="space-y-4">
              <div className="bg-white/6 rounded-lg p-3 text-center">
                <p className="text-sm text-gray-300 mb-1">Previsualización</p>
                {selectedFile && (
                  <img src={URL.createObjectURL(selectedFile)} alt="preview" className="mx-auto rounded-md max-h-40 object-contain" />
                )}
                {capturedBlob && (
                  <img src={URL.createObjectURL(capturedBlob)} alt="selfie" className="mx-auto rounded-md max-h-40 object-contain" />
                )}
                {!selectedFile && !capturedBlob && (
                  <div className="text-gray-500 text-sm">No hay imagen</div>
                )}
              </div>

              <div className="bg-white/6 rounded-lg p-3 text-center">
                <p className="text-sm text-gray-300">Controles</p>
                <div className="mt-2 flex gap-2 justify-center">
                  <button onClick={() => { setPrompt(''); setSelectedFile(null); setCapturedBlob(null); }} className="px-3 py-1 rounded-md bg-white/8">Limpiar</button>
                </div>
              </div>

              <div className="text-xs text-gray-400">Tip: Usa el micrófono para dictar el prompt. El botón se pondrá rojo cuando esté escuchando.</div>
            </aside>
          </div>
        </main>

        {/* Modal de cámara simple */}
        {cameraActive && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-4 text-black max-w-2xl w-full">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-bold">Tomar foto</h2>
                <div className="flex gap-2">
                  <button onClick={() => { setCameraActive(false); if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; } }} className="px-3 py-1 rounded-md bg-gray-200">Cerrar</button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <video ref={videoRef} autoPlay playsInline className="w-full rounded-md bg-black h-64 object-cover" />
                <div className="flex flex-col gap-3">
                  <p className="text-sm text-gray-700">Cuando estes listo presionar capturar</p>
                  <div className="mt-auto flex gap-2">
                    <button onClick={capturePhoto} className="flex-1 px-4 py-2 rounded-md bg-blue-600 text-white">Capturar</button>
                    <button onClick={() => { setCameraActive(false); if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; } }} className="px-4 py-2 rounded-md bg-gray-200">Cancelar</button>
                  </div>
                </div>
              </div>

              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}