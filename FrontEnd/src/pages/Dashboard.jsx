import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Video, AlertTriangle, Users, Loader2 } from 'lucide-react';
import AnalystPanel from '../components/AnalystPanel';

const Dashboard = () => {
  const [mode, setMode] = useState('upload'); // 'upload' or 'camera'
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  // Webcam refs
  const videoRef = React.useRef(null);
  const canvasRef = React.useRef(null);
  const [isMonitoring, setIsMonitoring] = useState(false);

  // Stop monitoring on unmount
  React.useEffect(() => {
    return () => stopMonitoring();
  }, []);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResults(null);
      setError(null);
      setIsAnalyzing(true);

      const formData = new FormData();
      formData.append('video', file);
      // Retrieve User ID from local storage (set during login/register)
      const userId = localStorage.getItem('user_id');
      if (userId) {
          formData.append('user_id', userId);
      }

      try {
        const response = await fetch('http://localhost:7001/analyze_video', {
          method: 'POST',
          headers: {
              'X-User-ID': userId || ''
          },
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Analysis failed');
        }

        setResults(data);
      } catch (err) {
        console.error("Analysis error:", err);
        setError(err.message);
      } finally {
        setIsAnalyzing(false);
      }
    }
  };
  
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Camera error:", err);
      setError("Could not access camera. Please allow permissions.");
    }
  };

  const stopCamera = () => {
      if (videoRef.current && videoRef.current.srcObject) {
          const tracks = videoRef.current.srcObject.getTracks();
          tracks.forEach(track => track.stop());
          videoRef.current.srcObject = null;
      }
  };

  const toggleMode = (newMode) => {
    setMode(newMode);
    setResults(null);
    setError(null);
    stopMonitoring();
    if (newMode === 'camera') {
      startCamera();
    } else {
      stopCamera();
    }
  };

  const [intervalId, setIntervalId] = useState(null);

  const startMonitoring = () => {
    setIsMonitoring(true);
    const id = setInterval(captureAndAnalyze, 2000); // Analyze every 2 seconds
    setIntervalId(id);
  };

  const stopMonitoring = () => {
    setIsMonitoring(false);
    if (intervalId) {
        clearInterval(intervalId);
        setIntervalId(null);
    }
  };

  const captureAndAnalyze = async () => {
      if (videoRef.current && canvasRef.current) {
          const video = videoRef.current;
          const canvas = canvasRef.current;
          
          if (video.readyState === video.HAVE_ENOUGH_DATA) {
              canvas.width = video.videoWidth;
              canvas.height = video.videoHeight;
              canvas.getContext('2d').drawImage(video, 0, 0);
              
              canvas.toBlob(async (blob) => {
                  if (!blob) return;
                  
                  const formData = new FormData();
                  formData.append('image', blob, 'frame.jpg');

                  try {
                      const response = await fetch('http://localhost:7001/analyze_frame', {
                          method: 'POST',
                          body: formData
                      });
                      
                      if (response.ok) {
                          const data = await response.json();
                          setResults(data);
                          // If threat detected, maybe pause or alert? 
                          // For now we just update the UI live.
                      }
                  } catch (err) {
                      console.error("Frame analysis error:", err);
                  }
              }, 'image/jpeg');
          }
      }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    
      {/* Mode Toggle */}
      <div className="flex justify-center mb-8">
        <div className="bg-slate-800 p-1 rounded-lg inline-flex">
            <button 
                onClick={() => toggleMode('upload')}
                className={`px-4 py-2 rounded-md transition-colors ${mode === 'upload' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
                Upload Video
            </button>
            <button 
                onClick={() => toggleMode('camera')}
                className={`px-4 py-2 rounded-md transition-colors ${mode === 'camera' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
                Live Camera
            </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="space-y-6">
          <div className="glass-panel p-8 min-h-[500px] flex flex-col">
            <h2 className="text-2xl font-bold text-white mb-6">
                {mode === 'upload' ? 'Upload Video Footage' : 'Live Camera Feed'}
            </h2>
            
            {mode === 'upload' ? (
                <>
                    <div className="relative border-2 border-dashed border-slate-700 rounded-xl p-12 text-center hover:border-blue-500/50 transition-colors group flex-1 flex flex-col justify-center">
                    <input
                        type="file"
                        accept="video/*"
                        onChange={handleFileChange}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <div className="flex flex-col items-center space-y-4">
                        <div className="p-4 bg-slate-800 rounded-full group-hover:bg-slate-700 transition-colors">
                        <Upload className="w-8 h-8 text-blue-400" />
                        </div>
                        <div>
                        <p className="text-lg font-medium text-white">Drop video here or click to upload</p>
                        <p className="text-slate-400 text-sm mt-1">Supports MP4, AVI, MOV</p>
                        </div>
                    </div>
                    </div>
                    {previewUrl && (
                        <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass-panel p-4 mt-4"
                        >
                        <video controls src={previewUrl} className="w-full rounded-lg" />
                        </motion.div>
                    )}
                </>
            ) : (
                <div className="flex-1 flex flex-col">
                    <div className="relative bg-slate-900 rounded-xl overflow-hidden aspect-video mb-4 border border-slate-700">
                        <video 
                            ref={videoRef} 
                            autoPlay 
                            playsInline 
                            muted 
                            className="w-full h-full object-cover" 
                        />
                        {/* Hidden canvas for capturing frames */}
                        <canvas ref={canvasRef} className="hidden" />
                        
                        {isMonitoring && (
                            <div className="absolute top-4 right-4 flex items-center gap-2 bg-red-500/80 px-3 py-1 rounded-full animate-pulse">
                                <div className="w-2 h-2 bg-white rounded-full"></div>
                                <span className="text-xs font-bold text-white">LIVE REC</span>
                            </div>
                        )}
                    </div>
                    
                    <button
                        onClick={isMonitoring ? stopMonitoring : startMonitoring}
                        className={`w-full py-3 rounded-lg font-bold transition-all ${isMonitoring ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-blue-600 hover:bg-blue-500 text-white'}`}
                    >
                        {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
                    </button>
                </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          <div className="glass-panel p-8 h-full min-h-[500px]">
            <h2 className="text-2xl font-bold text-white mb-6">Analysis Results</h2>
            
            {!results && !isAnalyzing ? (
              <div className="h-64 flex items-center justify-center text-slate-500 border border-slate-800 rounded-xl bg-slate-900/30">
                <p>
                    {mode === 'upload' ? 'Upload a video to see analysis' : 'Start monitoring to see real-time results'}
                </p>
              </div>
            ) : isAnalyzing ? (
              <div className="h-64 flex flex-col items-center justify-center text-blue-400 border border-slate-800 rounded-xl bg-slate-900/30">
                <Loader2 className="w-12 h-12 animate-spin mb-4" />
                <p>Processing...</p>
              </div>
            ) : error ? (
               <div className="h-64 flex flex-col items-center justify-center text-red-400 border border-red-900/30 rounded-xl bg-red-900/10">
                <AlertTriangle className="w-12 h-12 mb-4" />
                <p className="font-semibold">Analysis Failed</p>
                <p className="text-sm mt-2">{error}</p>
              </div>
            ) : (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {/* Disaster Type */}
                <div className={`p-6 border rounded-xl ${results?.classification === 'Normal' ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                  <div className="flex items-center gap-4 mb-2">
                    <AlertTriangle className={`w-6 h-6 ${results?.classification === 'Normal' ? 'text-green-400' : 'text-red-400'}`} />
                    <h3 className={`text-lg font-semibold ${results?.classification === 'Normal' ? 'text-green-400' : 'text-red-400'}`}>
                        {results?.classification === 'Normal' ? 'Status Normal' : 'Disaster Detected'}
                    </h3>
                  </div>
                  <p className="text-2xl font-bold text-white">{results?.classification || "Unknown"}</p>
                  <p className="text-slate-400 mt-1">Based on frame analysis</p>
                </div>

                {/* People Count */}
                <div className="p-6 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                  <div className="flex items-center gap-4 mb-2">
                    <Users className="w-6 h-6 text-blue-400" />
                    <h3 className="text-lg font-semibold text-blue-400">People Detected</h3>
                  </div>
                  <p className="text-2xl font-bold text-white">{results?.people_count || 0} Individuals</p>
                </div>
                
                {/* Smart Analyst Report */}
                {results?.analyst_report && (
                  <AnalystPanel report={results.analyst_report} />
                )}
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
