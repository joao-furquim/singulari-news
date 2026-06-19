import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// vi.hoisted ensures these are initialized before the mock factory runs
const mockClientPost = vi.hoisted(() => vi.fn());
const mockClientGet = vi.hoisted(() => vi.fn());
const mockLogin = vi.hoisted(() => vi.fn());
const mockSetPendingAction = vi.hoisted(() => vi.fn());

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
    pendingAction: null,
    setPendingAction: mockSetPendingAction,
  }),
}));

vi.mock('../../api/client', () => ({
  default: {
    post: mockClientPost,
    get: mockClientGet,
  },
}));

import { AuthModal } from '../auth/AuthModal';

const defaultProps = {
  open: true,
  onClose: vi.fn(),
  onSignUpSuccess: vi.fn(),
};

describe('AuthModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders sign in tab by default', () => {
    render(<AuthModal {...defaultProps} />);
    expect(screen.getByRole('tab', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('switches to create account tab on click', async () => {
    const user = userEvent.setup();
    render(<AuthModal {...defaultProps} />);
    await user.click(screen.getByRole('tab', { name: /create account/i }));
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
  });

  it('shows forgot password form when link is clicked', async () => {
    const user = userEvent.setup();
    render(<AuthModal {...defaultProps} />);
    await user.click(screen.getByText(/forgot your password/i));
    expect(screen.getByText(/send reset link/i)).toBeInTheDocument();
  });

  it('navigates back to sign in from forgot password', async () => {
    const user = userEvent.setup();
    render(<AuthModal {...defaultProps} />);
    await user.click(screen.getByText(/forgot your password/i));
    await user.click(screen.getByText(/back to sign in/i));
    expect(screen.getByRole('tab', { name: /sign in/i })).toBeInTheDocument();
  });

  it('resets form fields when modal is closed and reopened', async () => {
    const user = userEvent.setup();
    const { rerender } = render(<AuthModal {...defaultProps} />);
    const emailInput = screen.getByLabelText(/email/i);

    await user.type(emailInput, 'test@example.com');
    expect(emailInput).toHaveValue('test@example.com');

    rerender(<AuthModal {...defaultProps} open={false} />);
    rerender(<AuthModal {...defaultProps} open={true} />);

    expect(screen.getByLabelText(/email/i)).toHaveValue('');
  });

  it('calls client.post /login with correct credentials on submit', async () => {
    const mockUser = {
      id: 'u1', name: 'Test', email: 'admin@test.com',
      avatar_url: null, locale: 'en', role: 'user',
      must_change_password: false, created_at: '2026-01-01T00:00:00Z',
    };
    mockClientPost.mockResolvedValueOnce({
      data: { access_token: 'tok123', token_type: 'bearer', user: mockUser, preferences: [] },
    });
    mockClientGet.mockResolvedValueOnce({ data: [] });

    const user = userEvent.setup();
    render(<AuthModal {...defaultProps} />);

    await user.type(screen.getByLabelText(/email/i), 'admin@test.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockClientPost).toHaveBeenCalledWith('/login', {
        email: 'admin@test.com',
        password: 'password123',
      });
    });
  });
});
