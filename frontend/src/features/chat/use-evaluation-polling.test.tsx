import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useEvaluationPolling } from './use-evaluation-polling'
import type { QueryResponseDTO, Scores } from '@/lib/api'

const SESSION_ID = 'session-1'

function makeQuery(id: string, overrides: Partial<QueryResponseDTO> = {}): QueryResponseDTO {
  return {
    id,
    sessionId: SESSION_ID,
    question: 'q',
    answer: 'a',
    topic: [],
    context: [],
    createdAt: '2024-01-15T10:00:00Z',
    expiresAt: null,
    feedback: 0,
    isEvaluated: false,
    scores: null,
    ...overrides,
  }
}

const scoresFull: Scores = { relevancy: 0.9, faithfulness: 0.8, utilization: 0.7 }

describe('useEvaluationPolling', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  it('does not call client when pending set is empty', () => {
    const getQueries = vi.fn(() => Promise.resolve([] as QueryResponseDTO[]))
    renderHook(() =>
      useEvaluationPolling({
        sessionId: SESSION_ID,
        pendingQueryIds: [],
        getQueries,
        onResolved: vi.fn(),
        onFailed: vi.fn(),
      })
    )
    act(() => { vi.advanceTimersByTime(20_000) })
    expect(getQueries).not.toHaveBeenCalled()
  })

  it('polls getQueries every 5s while pending set non-empty', async () => {
    const getQueries = vi.fn(() => Promise.resolve([makeQuery('q1')]))
    renderHook(() =>
      useEvaluationPolling({
        sessionId: SESSION_ID,
        pendingQueryIds: ['q1'],
        getQueries,
        onResolved: vi.fn(),
        onFailed: vi.fn(),
      })
    )
    await act(async () => { await vi.advanceTimersByTimeAsync(5_000) })
    expect(getQueries).toHaveBeenCalledTimes(1)
    await act(async () => { await vi.advanceTimersByTimeAsync(5_000) })
    expect(getQueries).toHaveBeenCalledTimes(2)
    expect(getQueries).toHaveBeenLastCalledWith(SESSION_ID)
  })

  it('calls onResolved when query returns isEvaluated:true with scores', async () => {
    const getQueries = vi.fn(() =>
      Promise.resolve([makeQuery('q1', { isEvaluated: true, scores: scoresFull })])
    )
    const onResolved = vi.fn()
    const onFailed = vi.fn()
    renderHook(() =>
      useEvaluationPolling({
        sessionId: SESSION_ID,
        pendingQueryIds: ['q1'],
        getQueries,
        onResolved,
        onFailed,
      })
    )
    await act(async () => { await vi.advanceTimersByTimeAsync(5_000) })
    expect(onResolved).toHaveBeenCalledWith('q1', scoresFull)
    expect(onFailed).not.toHaveBeenCalled()
  })

  it('calls onFailed when query returns isEvaluated:true with scores:null', async () => {
    const getQueries = vi.fn(() =>
      Promise.resolve([makeQuery('q1', { isEvaluated: true, scores: null })])
    )
    const onResolved = vi.fn()
    const onFailed = vi.fn()
    renderHook(() =>
      useEvaluationPolling({
        sessionId: SESSION_ID,
        pendingQueryIds: ['q1'],
        getQueries,
        onResolved,
        onFailed,
      })
    )
    await act(async () => { await vi.advanceTimersByTimeAsync(5_000) })
    expect(onFailed).toHaveBeenCalledWith('q1')
    expect(onResolved).not.toHaveBeenCalled()
  })

  it('calls onFailed when 2 minutes elapse without resolution', async () => {
    const getQueries = vi.fn(() => Promise.resolve([makeQuery('q1')]))
    const onFailed = vi.fn()
    renderHook(() =>
      useEvaluationPolling({
        sessionId: SESSION_ID,
        pendingQueryIds: ['q1'],
        getQueries,
        onResolved: vi.fn(),
        onFailed,
      })
    )
    await act(async () => { await vi.advanceTimersByTimeAsync(115_000) })
    expect(onFailed).not.toHaveBeenCalled()
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000) })
    expect(onFailed).toHaveBeenCalledWith('q1')
  })

  it('stops polling after unmount', async () => {
    const getQueries = vi.fn(() => Promise.resolve([makeQuery('q1')]))
    const { unmount } = renderHook(() =>
      useEvaluationPolling({
        sessionId: SESSION_ID,
        pendingQueryIds: ['q1'],
        getQueries,
        onResolved: vi.fn(),
        onFailed: vi.fn(),
      })
    )
    await act(async () => { await vi.advanceTimersByTimeAsync(5_000) })
    expect(getQueries).toHaveBeenCalledTimes(1)
    unmount()
    await act(async () => { await vi.advanceTimersByTimeAsync(20_000) })
    expect(getQueries).toHaveBeenCalledTimes(1)
  })
})
