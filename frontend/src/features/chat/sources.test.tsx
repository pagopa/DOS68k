import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Sources } from './sources'
import type { FileContext } from '@/lib/api'

const ctx: Record<string, FileContext[]> = {
  'beta.pdf': [
    { chunkId: 1, content: 'Beta chunk one', score: 0.923 },
    { chunkId: 2, content: 'Beta chunk two', score: null },
  ],
  'alpha.txt': [
    { chunkId: 3, content: 'Alpha chunk', score: 0.751 },
  ],
}

describe('Sources', () => {
  it('renders nothing when context is empty object', () => {
    const { container } = render(<Sources context={{}} />)
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
    expect(screen.queryByText('Alpha chunk')).not.toBeInTheDocument()
    expect(screen.queryByText('Beta chunk one')).not.toBeInTheDocument()
  })

  it('expands when header is clicked', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    await user.click(screen.getByRole('button', { name: 'Sources (3)' }))
    expect(screen.getByText('Alpha chunk')).toBeInTheDocument()
    expect(screen.getByText('Beta chunk one')).toBeInTheDocument()
    expect(screen.getByText('Beta chunk two')).toBeInTheDocument()
  })

  it('collapses again when header is clicked twice', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    const btn = screen.getByRole('button', { name: 'Sources (3)' })
    await user.click(btn)
    await user.click(btn)
    expect(screen.queryByText('Alpha chunk')).not.toBeInTheDocument()
  })

  it('sorts documents alphabetically', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    await user.click(screen.getByRole('button', { name: 'Sources (3)' }))
    const docNames = screen.getAllByText(/alpha\.txt|beta\.pdf/)
    expect(docNames[0]).toHaveTextContent('alpha.txt')
    expect(docNames[1]).toHaveTextContent('beta.pdf')
  })

  it('shows chunk content and numeric score', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    await user.click(screen.getByRole('button', { name: 'Sources (3)' }))
    expect(screen.getByText('Beta chunk one')).toBeInTheDocument()
    expect(screen.getByText('Score: 0.923')).toBeInTheDocument()
    expect(screen.getByText('Score: 0.751')).toBeInTheDocument()
  })

  it('shows "—" for null score', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    await user.click(screen.getByRole('button', { name: 'Sources (3)' }))
    expect(screen.getByText('Score: —')).toBeInTheDocument()
  })

  it('groups chunks under their document', async () => {
    const user = userEvent.setup()
    render(<Sources context={ctx} />)
    await user.click(screen.getByRole('button', { name: 'Sources (3)' }))
    // beta.pdf has 2 chunks, alpha.txt has 1
    const betaSection = screen.getByText('beta.pdf').closest('details')!
    expect(betaSection).toContainElement(screen.getByText('Beta chunk one'))
    expect(betaSection).toContainElement(screen.getByText('Beta chunk two'))
    const alphaSection = screen.getByText('alpha.txt').closest('details')!
    expect(alphaSection).toContainElement(screen.getByText('Alpha chunk'))
  })
})
