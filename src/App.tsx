import { useEffect, useState } from 'react';
import Sidebar from "./component/Sidebar";
import { backendService } from './services/backend';

function App() {
  const [backendReady, setBackendReady] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const initBackend = async () => {
      try {
        setIsInitializing(true);
        console.log('[DEBUG] Inicializando backend...');
        
        const success = await backendService.initialize();
        
        if (success) {
          setBackendReady(true);
          console.log('[SUCCESS] Backend inicializado correctamente');
        } else {
          setBackendError('El backend no pudo iniciarse. Por favor verifica los logs.');
        }
      } catch (error) {
        console.error('[ERROR] Error al inicializar backend:', error);
        const errorMessage = error instanceof Error ? error.message : 'Error desconocido al inicializar el backend';
        console.error('[ERROR] Mensaje completo:', errorMessage);
        setBackendError(errorMessage);
      } finally {
        setIsInitializing(false);
      }
    };

    initBackend();

    // Cleanup: detener backend al desmontar
    return () => {
      backendService.stop().catch(console.error);
    };
  }, []);

  // Pantalla de carga mientras se inicializa el backend
  if (isInitializing) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">
            Iniciando Baucher Match
          </h2>
          <p className="text-gray-500">
            Configurando el servidor local...
          </p>
        </div>
      </div>
    );
  }

  // Pantalla de error si el backend no pudo iniciarse
  if (backendError) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="max-w-md p-8 bg-white rounded-lg shadow-lg">
          <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full">
            <svg 
              className="w-8 h-8 text-red-600" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M6 18L18 6M6 6l12 12" 
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
            Error al iniciar
          </h2>
          <p className="text-center text-gray-600 mb-6">
            {backendError}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  // Aplicación principal cuando el backend está listo
  if (backendReady) {
    return <Sidebar />;
  }

  return null;
}

export default App;
