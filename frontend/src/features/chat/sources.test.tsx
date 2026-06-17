import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Sources } from './sources'
import type { Source } from '@/lib/api'

const ctx: Source[] = [
  { chunkId: 1, content: 'High score chunk', score: 0.923, filename: 'beta.pdf' },
  { chunkId: 2, content: 'Null score chunk', score: null, filename: 'beta.pdf' },
  { chunkId: 3, content: 'Alpha chunk', score: 0.751, filename: 'alpha.txt' },
]

describe('Sources', () => {
  it('renders nothing when context is empty array', () => {
    const { container } = render(<Sources context={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when context is undefined', () => {
    const { container } = render(<Sources />)
    expect(container.firstChild).toBeNull()
  })

  it('shows total chunk count in header', () => {
    render(<Sources context={ctx} />)
    expect(screen.getByRole('button', { name: 'Sources (3)' })).toBeInTheDocument()
  })

  it('is collapsed by default — chunks not visible', () => {
    render(<Sources context={ctx} />)
    expect(screen.queryByText('High score chunk')).not.toBeInTheDocument()
    expect(screen.queryByText('Alpha chunk')).not.toBeInTheDocument()
  })

  it('expands when header is clicked', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    await user.click(screen.getByRole('button', { name: 'Sources (3)' }))
    expect(screen.getByText('High score chunk')).toBeInTheDocument()
    expect(screen.getByText('Null score chunk')).toBeInTheDocument()
    expect(screen.getByText('Alpha chunk')).toBeInTheDocument()
  })

  it('collapses again when header is clicked twice', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    const btn = screen.getByRole('button', { name: 'Sources (3)' })
    await user.click(btn)
    await user.click(btn)
    expect(screen.queryByText('High score chunk')).not.toBeInTheDocument()
  })

  it('two sources with the same filename render as separate rows with distinct scores', async () => {
    const user = userEvent.setup()
    const repeated: Source[] = [
      { chunkId: 1, content: 'First passage', score: 0.9, filename: 'doc.pdf' },
      { chunkId: 2, content: 'Second passage', score: 0.6, filename: 'doc.pdf' },
    ]
    render(<Sources context={repeated} />)
    await user.click(screen.getByRole('button', { name: 'Sources (2)' }))

    expect(screen.getByText('First passage')).toBeInTheDocument()
    expect(screen.getByText('Second passage')).toBeInTheDocument()
    expect(screen.getByText('doc.pdf — 0.900')).toBeInTheDocument()
    expect(screen.getByText('doc.pdf — 0.600')).toBeInTheDocument()
  })

  it('expanding a row reveals chunk content and score in summary', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    await user.click(screen.getByRole('button', { name: 'Sources (3)' }))
    expect(screen.getByText('High score chunk')).toBeInTheDocument()
    expect(screen.getByText('beta.pdf — 0.923')).toBeInTheDocument()
  })

  it('shows "—" for null score in summary', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    await user.click(screen.getByRole('button', { name: 'Sources (3)' }))
    expect(screen.getByText('beta.pdf — —')).toBeInTheDocument()
  })
})
