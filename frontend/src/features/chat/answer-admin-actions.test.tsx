import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthContextProvider } from '@/lib/auth/context'
import { AnswerAdminActions } from './answer-admin-actions'

function renderAs(role: 'admin' | 'user' | null, props: Partial<React.ComponentProps<typeof AnswerAdminActions>> = {}) {
  if (role) {
    localStorage.setItem('dos68k:role', role)
    localStorage.setItem('dos68k:token', `local-token-${role}`)
  } else {
    localStorage.clear()
  }
  const onEvaluate = props.onEvaluate ?? vi.fn()
  return {
    onEvaluate,
    ...render(
      <AuthContextProvider>
        <AnswerAdminActions isEvaluated={false} onEvaluate={onEvaluate} {...props} />
      </AuthContextProvider>
    ),
  }
}

describe('AnswerAdminActions', () => {
  beforeEach(() => localStorage.clear())

  it('renders nothing for non-admin users', () => {
    const { container } = renderAs('user')
    expect(container.firstChild).toBeNull()
  })

  it('renders an overflow trigger for admin users', () => {
    renderAs('admin')
    expect(screen.getByRole('button', { name: /more actions/i })).toBeInTheDocument()
  })

  it('opens menu with "Evaluate this answer" item when admin clicks trigger', async () => {
    const user = userEvent.setup()
    renderAs('admin')
    await user.click(screen.getByRole('button', { name: /more actions/i }))
    expect(await screen.findByRole('menuitem', { name: /evaluate this answer/i })).toBeInTheDocument()
  })

  it('fires onEvaluate when the menu item is clicked', async () => {
    const user = userEvent.setup()
    const { onEvaluate } = renderAs('admin')
    await user.click(screen.getByRole('button', { name: /more actions/i }))
    await user.click(await screen.findByRole('menuitem', { name: /evaluate this answer/i }))
    expect(onEvaluate).toHaveBeenCalledTimes(1)
  })

  it('disables the menu item when isEvaluated is true', async () => {
    const user = userEvent.setup()
    const { onEvaluate } = renderAs('admin', { isEvaluated: true })
    await user.click(screen.getByRole('button', { name: /more actions/i }))
    const item = await screen.findByRole('menuitem', { name: /evaluate this answer/i })
    expect(item).toHaveAttribute('aria-disabled', 'true')
    await user.click(item)
    expect(onEvaluate).not.toHaveBeenCalled()
  })
})
