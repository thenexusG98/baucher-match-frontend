import { invoke } from '@tauri-apps/api/core';

/**
 * Servicio para gestionar el backend FastAPI
 */
export class BackendService {
  private readonly baseUrl = 'http://127.0.0.1:8000';
  private readonly healthEndpoint = `${this.baseUrl}/health`; // Cambiado de /api/v1/health a /health
  
  /**
   * Iniciar el proceso del backend
   */
  async start(): Promise<string> {
    try {
      const result = await invoke<string>('start_backend');
      console.log('✅ Backend:', result);
      return result;
    } catch (error) {
      console.error('❌ Error al iniciar backend:', error);
      throw error;
    }
  }

  /**
   * Detener el proceso del backend
   */
  async stop(): Promise<string> {
    try {
      const result = await invoke<string>('stop_backend');
      console.log('✅ Backend:', result);
      return result;
    } catch (error) {
      console.error('❌ Error al detener backend:', error);
      throw error;
    }
  }

  /**
   * Verificar el estado del backend
   */
  async checkStatus(): Promise<boolean> {
    try {
      const isRunning = await invoke<boolean>('check_backend_status');
      return isRunning;
    } catch (error) {
      console.error('❌ Error al verificar estado del backend:', error);
      return false;
    }
  }

  /**
   * Esperar a que el backend esté listo para recibir peticiones
   * @param maxAttempts Número máximo de intentos
   * @param delayMs Delay entre intentos en milisegundos
   */
  async waitForReady(maxAttempts: number = 40, delayMs: number = 1000): Promise<boolean> {
    console.log('[DEBUG] Esperando que el backend este listo...');
    console.log('[DEBUG] Health endpoint:', this.healthEndpoint);
    
    // Dar tiempo inicial para que uvicorn inicie (especialmente en produccion)
    console.log('[DEBUG] Esperando 6 segundos para que uvicorn inicie...');
    await new Promise(resolve => setTimeout(resolve, 6000));
    
    for (let i = 0; i < maxAttempts; i++) {
      try {
        console.log(`[DEBUG] Intento ${i + 1}/${maxAttempts} - Haciendo fetch a ${this.healthEndpoint}`);
        
        const response = await fetch(this.healthEndpoint, {
          method: 'GET',
          signal: AbortSignal.timeout(3000), // 3 segundos de timeout
          mode: 'cors', // Explicito CORS
          headers: {
            'Accept': 'application/json',
          },
        });
        
        console.log(`[DEBUG] Response recibida - Status: ${response.status}, OK: ${response.ok}`);
        console.log(`[DEBUG] Response headers:`, Object.fromEntries(response.headers.entries()));
        
        if (response.ok) {
          const data = await response.json();
          console.log('[SUCCESS] Backend esta listo y respondiendo:', data);
          return true;
        } else {
          const text = await response.text();
          console.log(`[DEBUG] Response no OK - Status: ${response.status}, Body:`, text);
        }
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        console.error(`[DEBUG] Error en fetch:`, error);
        
        // Si es el ultimo intento, mostrar el error completo
        if (i === maxAttempts - 1) {
          console.error('[ERROR] Backend no respondio despues de', maxAttempts, 'intentos');
          console.error('[ERROR] Error:', errorMsg);
          console.error('[ERROR] URL intentada:', this.healthEndpoint);
        } else {
          console.log(`[DEBUG] Intento ${i + 1}/${maxAttempts}... (${errorMsg})`);
        }
        
        // Esperar antes del siguiente intento
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
    
    return false;
  }

  /**
   * Inicializar el backend completamente
   * Inicia el proceso y espera a que esté listo
   */
  async initialize(): Promise<boolean> {
    try {
      // Verificar si ya está corriendo
      const isRunning = await this.checkStatus();
      
      if (!isRunning) {
        console.log('[DEBUG] Iniciando backend...');
        await this.start();
      } else {
        console.log('[DEBUG] Backend ya esta corriendo');
      }
      
      // Esperar a que esté listo
      const isReady = await this.waitForReady();
      
      if (!isReady) {
        throw new Error(`El backend inicio (PID existe) pero no responde en ${this.healthEndpoint}. Verifica que uvicorn este corriendo en el puerto 8000.`);
      }
      
      return true;
    } catch (error) {
      console.error('❌ Error al inicializar backend:', error);
      throw error;
    }
  }

  /**
   * Obtener la URL base del backend
   */
  getBaseUrl(): string {
    return this.baseUrl;
  }

  /**
   * Verificar la salud del backend haciendo una petición al endpoint de health
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(this.healthEndpoint, {
        method: 'GET',
        signal: AbortSignal.timeout(3000),
      });
      return response.ok;
    } catch (error) {
      console.error('❌ Health check falló:', error);
      return false;
    }
  }
}

// Exportar instancia singleton
export const backendService = new BackendService();
