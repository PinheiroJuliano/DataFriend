import type { DatasetMetadata, ChatResponse, ChatRequest } from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export async function uploadDataset(file: File): Promise<DatasetMetadata> {
  const form = new FormData()
  form.append('file', file)

  const res = await fetch(`${API_URL}/api/datasets/upload`, {
    method: 'POST',
    body: form,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao enviar arquivo' }))
    throw new Error(err.detail || 'Erro ao enviar arquivo')
  }

  return res.json()
}

export async function getDataset(datasetId: string): Promise<DatasetMetadata> {
  const res = await fetch(`${API_URL}/api/datasets/${datasetId}`)
  if (!res.ok) throw new Error('Dataset não encontrado')
  return res.json()
}

export async function sendQuestion(data: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao processar pergunta' }))
    throw new Error(err.detail || 'Erro ao processar pergunta')
  }

  return res.json()
}
