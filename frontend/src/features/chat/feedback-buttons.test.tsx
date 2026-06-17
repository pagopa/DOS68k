import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FeedbackButtons } from './feedback-buttons'

function setup(props: Partial<React.ComponentProps<typeof FeedbackButtons>> = {}) {
  const onSubmit = props.onSubmit ?? (() => Promise.resolve())
  return render(<FeedbackButtons feedback={0} onSubmit={onSubmit} {...props} />)
}

describe('FeedbackButtons', () => {
  it('renders thumbs-up highlighted when feedback === 1', () => {
    setup({ feedback: 1 })
    const up = screen.getByRole('button', { name: /thumbs up/i })
    expect(up).toHaveAttribute('aria-pressed', 'true')
  })

  it('renders thumbs-down highlighted when feedback === -1', () => {
    setup({ feedback: -1 })
    const down = screen.getByRole('button', { name: /thumbs down/i })
    expect(down).toHaveAttribute('aria-pressed', 'true')
  })

  it('renders neither highlighted when feedback === 0', () => {
    setup({ feedback: 0 })
    expect(screen.getByRole('button', { name: /thumbs up/i })).toHaveAttribute('aria-pressed', 'false')
    expect(screen.getByRole('button', { name: /thumbs down/i })).toHaveAttribute('aria-pressed', 'false')
  })

  it('clicking thumbs-up optimistically highlights it and calls onSubmit(1)', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn(() => Promise.resolve())
    setup({ feedback: 0, onSubmit })
    const up = screen.getByRole('button', { name: /thumbs up/i })

    await user.click(up)

    expect(onSubmit).toHaveBeenCalledWith(1)
    expect(up).toHaveAttribute('aria-pressed', 'true')
  })

  it('clicking thumbs-down switches from up to down and calls onSubmit(-1)', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn(() => Promise.resolve())
    setup({ feedback: 1, onSubmit })
    const down = screen.getByRole('button', { name: /thumbs down/i })

    await user.click(down)

    expect(onSubmit).toHaveBeenCalledWith(-1)
    expect(down).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: /thumbs up/i })).toHaveAttribute('aria-pressed', 'false')
  })

  it('reverts optimistic state when onSubmit rejects', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn(() => Promise.reject(new Error('boom')))
    setup({ feedback: 0, onSubmit })
    const up = screen.getByRole('button', { name: /thumbs up/i })

    await user.click(up)

    await waitFor(() =>
      expect(up).toHaveAttribute('aria-pressed', 'false')
    )
  })
})
