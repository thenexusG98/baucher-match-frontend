import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import Card from './ui/Card';
import CardContent from './ui/CardContent';

/**
 * Componente para visualizar la ubicación de los logs del sistema
 * Útil para debugging en producción
 */
const LogViewer = () => {
  const [logPath, setLogPath] = useState<string>('');
  const [backendLogPath, setBackendLogPath] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadLogPaths();
  }, []);

  const loadLogPaths = async () => {
    try {
      // Obtener ruta de logs de Tauri
      const tauriLogPath = await invoke<string>('get_log_path_command');
      setLogPath(tauriLogPath);

      // Calcular ruta de logs del backend
      const platform = navigator.platform.toLowerCase();
      let backendPath = '';
      
      if (platform.includes('mac')) {
        backendPath = `~/Library/Logs/BaucherMatch/backend_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.log`;
      } else if (platform.includes('win')) {
        backendPath = `%APPDATA%\\BaucherMatch\\logs\\backend_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.log`;
      } else {
        backendPath = `~/.local/share/BaucherMatch/logs/backend_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.log`;
      }
      
      setBackendLogPath(backendPath);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al obtener rutas de logs');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Ruta copiada al portapapeles');
  };

  return (
    <Card>
      <CardContent>
        <h2>📋 Ubicación de Archivos de Log</h2>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          Si la aplicación presenta errores, revisa estos archivos para obtener información detallada.
        </p>

        {error && (
          <div style={{ 
            padding: '10px', 
            background: '#fee', 
            border: '1px solid #fcc',
            borderRadius: '4px',
            marginBottom: '15px'
          }}>
            ⚠️ {error}
          </div>
        )}

        <div style={{ marginBottom: '20px' }}>
          <h3>Frontend (Tauri)</h3>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '10px',
            padding: '10px',
            background: '#f5f5f5',
            borderRadius: '4px',
            marginTop: '8px'
          }}>
            <code style={{ flex: 1, wordBreak: 'break-all' }}>
              {logPath || 'Cargando...'}
            </code>
            {logPath && (
              <button 
                onClick={() => copyToClipboard(logPath)}
                style={{
                  padding: '5px 10px',
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                📋 Copiar
              </button>
            )}
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3>Backend (FastAPI)</h3>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '10px',
            padding: '10px',
            background: '#f5f5f5',
            borderRadius: '4px',
            marginTop: '8px'
          }}>
            <code style={{ flex: 1, wordBreak: 'break-all' }}>
              {backendLogPath || 'Cargando...'}
            </code>
            {backendLogPath && (
              <button 
                onClick={() => copyToClipboard(backendLogPath)}
                style={{
                  padding: '5px 10px',
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                📋 Copiar
              </button>
            )}
          </div>
        </div>

        <div style={{ 
          padding: '15px', 
          background: '#e7f3ff',
          border: '1px solid #b3d9ff',
          borderRadius: '4px'
        }}>
          <h4 style={{ marginTop: 0 }}>💡 Cómo revisar los logs:</h4>
          <ol style={{ marginBottom: 0 }}>
            <li>Copia la ruta del archivo de log</li>
            <li>Abre el Finder (Mac) o Explorador de Archivos (Windows)</li>
            <li>Presiona Cmd+Shift+G (Mac) o pega la ruta en la barra de direcciones (Windows)</li>
            <li>Pega la ruta copiada y presiona Enter</li>
            <li>Abre el archivo con un editor de texto</li>
          </ol>
        </div>

        <div style={{ 
          marginTop: '20px',
          padding: '15px', 
          background: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px'
        }}>
          <h4 style={{ marginTop: 0 }}>⚠️ Información para soporte técnico</h4>
          <p style={{ marginBottom: '8px' }}>
            Si necesitas reportar un error, incluye:
          </p>
          <ul style={{ marginBottom: 0 }}>
            <li>El contenido de ambos archivos de log</li>
            <li>Los pasos que seguiste antes del error</li>
            <li>Capturas de pantalla del error (si aplica)</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default LogViewer;
