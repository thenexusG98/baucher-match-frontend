import { invoke } from '@tauri-apps/api/core';

/**
 * Servicio para gestionar el backend FastAPI
 */
export class BackendService {
  private readonly baseUrl = 'http://127.0.0.1:8000';
  private readonly healthEndpoint = `${this.baseUrl}/api/v1/health`;
  
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
  async waitForReady(maxAttempts: number = 30, delayMs: number = 1000): Promise<boolean> {
    console.log('⏳ Esperando que el backend esté listo...');
    
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const response = await fetch(this.healthEndpoint, {
          method: 'GET',
          signal: AbortSignal.timeout(2000), // 2 segundos de timeout
        });
        
        if (response.ok) {
          console.log('✅ Backend está listo y respondiendo');
          return true;
        }
      } catch (error) {
        // Si es el último intento, mostrar el error
        if (i === maxAttempts - 1) {
          console.error('❌ Backend no respondió después de', maxAttempts, 'intentos');
          console.error('Error:', error);
        } else {
          console.log(`⏳ Intento ${i + 1}/${maxAttempts}... esperando...`);
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
        console.log('🚀 Iniciando backend...');
        await this.start();
      } else {
        console.log('✅ Backend ya está corriendo');
      }
      
      // Esperar a que esté listo
      const isReady = await this.waitForReady();
      
      if (!isReady) {
        throw new Error('El backend no pudo iniciarse correctamente');
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
