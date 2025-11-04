// Servicio de base de datos usando Tauri SQLite
import { invoke } from '@tauri-apps/api/core';

export interface ProcessedStatement {
  id?: number;
  filename: string;
  month: string;
  year: number;
  ingreso: number;
  totalCount: number;
  processedAt: string;
}

class DatabaseService {
  // Obtener todas las declaraciones procesadas
  async getAllStatements(): Promise<ProcessedStatement[]> {
    try {
      const statements = await invoke<ProcessedStatement[]>('get_all_statements');
      return statements;
    } catch (error) {
      console.error('Error al obtener declaraciones:', error);
      return [];
    }
  }

  // Agregar una nueva declaración
  async addStatement(statement: Omit<ProcessedStatement, 'id'>): Promise<ProcessedStatement> {
    try {
      console.log('Intentando agregar declaración a Tauri SQLite...', statement);
      const newStatement = await invoke<ProcessedStatement>('add_statement', {
        filename: statement.filename,
        month: statement.month,
        year: statement.year,
        ingreso: statement.ingreso,
        totalCount: statement.totalCount,
        processedAt: statement.processedAt,
      });
      console.log('Declaración agregada exitosamente:', newStatement);
      return newStatement;
    } catch (error) {
      console.error('Error al agregar declaración:', error);
      throw error;
    }
  }

  // Obtener declaraciones por año
  async getStatementsByYear(year: number): Promise<ProcessedStatement[]> {
    try {
      const statements = await invoke<ProcessedStatement[]>('get_statements_by_year', { year });
      return statements;
    } catch (error) {
      console.error('Error al filtrar declaraciones por año:', error);
      return [];
    }
  }

  // Obtener el total de ingresos por mes y año
  async getMonthlyTotals(): Promise<Array<{ month: string; year: number; ingreso: number; totalCount: number }>> {
    try {
      const totals = await invoke<Array<{ month: string; year: number; ingreso: number; totalCount: number }>>('get_monthly_totals');
      return totals;
    } catch (error) {
      console.error('Error al calcular totales mensuales:', error);
      return [];
    }
  }

  // Obtener años únicos disponibles
  async getAvailableYears(): Promise<number[]> {
    try {
      const years = await invoke<number[]>('get_available_years');
      return years;
    } catch (error) {
      console.error('Error al obtener años disponibles:', error);
      return [];
    }
  }

  // Eliminar una declaración por ID
  async deleteStatement(id: number): Promise<boolean> {
    try {
      const result = await invoke<boolean>('delete_statement', { id });
      return result;
    } catch (error) {
      console.error('Error al eliminar declaración:', error);
      return false;
    }
  }

  // Limpiar toda la base de datos
  async clearAll(): Promise<boolean> {
    try {
      const result = await invoke<boolean>('clear_all_statements');
      return result;
    } catch (error) {
      console.error('Error al limpiar base de datos:', error);
      return false;
    }
  }

  // Obtener la ruta de la base de datos
  async getDatabasePath(): Promise<string> {
    try {
      const path = await invoke<string>('get_database_path');
      return path;
    } catch (error) {
      console.error('Error al obtener ruta de base de datos:', error);
      return '';
    }
  }

  // Utilidad para extraer el año del nombre del archivo
  extractYearFromFilename(filename: string): number {
    const yearMatch = filename.match(/20\d{2}/); // Busca años tipo 2024, 2025, etc.
    return yearMatch ? parseInt(yearMatch[0]) : new Date().getFullYear();
  }
}

// Exportar instancia única (Singleton)
export const db = new DatabaseService();
