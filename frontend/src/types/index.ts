export interface DatasetMetadata {
  dataset_id: string
  filename: string
  rows_count: number
  columns_count: number
  schema_info: Record<string, string>
}

export interface ChatResponse {
  answer: string
  sql: string
  columns: string[]
  rows: any[][]
}

export interface ChatRequest {
  dataset_id: string
  question: string
}
